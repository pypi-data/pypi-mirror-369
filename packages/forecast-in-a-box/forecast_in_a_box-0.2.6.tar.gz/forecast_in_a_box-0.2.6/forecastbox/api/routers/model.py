# (C) Copyright 2024- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

"""Models API Router."""

import asyncio
import logging
import os
import shutil
import tempfile
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from forecastbox.api.utils import get_model_path
from forecastbox.config import config
from forecastbox.db.model import (delete_download, finish_edit, get_download, get_edit, start_download, start_editing,
                                  update_progress)
from forecastbox.models.model import Model, ModelExtra, get_extra_information, model_info, set_extra_information
from forecastbox.schemas.model import ModelDownload
from pydantic import BaseModel

from ..types import ModelName, ModelSpecification
from .admin import get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["model"],
    responses={404: {"description": "Not found"}},
)

Category = str

# section: MODEL DOWNLOAD


class DownloadResponse(BaseModel):
    """Response model for model download operations."""

    download_id: str | None
    """*DEPRECATED* Unique identifier for the download operation, if applicable."""
    message: str
    """Message describing the status of the download operation."""
    status: Literal["not_downloaded", "in_progress", "errored", "completed"]
    """Current status of the download operation."""
    progress: float
    """Progress of the download operation as a percentage (0.00 to 100.00)."""
    error: str | None = None
    """Error message if the download operation failed, otherwise None."""


async def download_file(model_id: str, url: str, download_path: str) -> None:
    """Download a file from a given URL and save it to the specified path.

    This function updates the download progress in the database.

    Parameters
    ----------
    model_id : str
        Identifier of the model
    url : str
        URL of the file to download.
    download_path : str
        Path where the downloaded file will be saved.
    """
    try:
        tempfile_path = tempfile.NamedTemporaryFile(prefix="model_", suffix=".ckpt", delete=False)

        async with httpx.AsyncClient(follow_redirects=True) as client_http:
            logger.debug(f"download of {model_id=} about to start from {url=} into {tempfile_path.name=}")
            async with client_http.stream("GET", url) as response:
                response.raise_for_status()
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 1024 * 1024  # 1MB chunks for efficiency
                file_path = tempfile_path.name
                with open(file_path, "wb") as file:
                    async for chunk in response.aiter_bytes(chunk_size):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            progress = float(downloaded) / total * 100 if total else 0.0
                            await update_progress(model_id, int(progress), None)
                logger.debug(f"Download finished for {model_id=}, total bytes: {downloaded}")
                shutil.move(file_path, download_path)
        await update_progress(model_id, 100, None)
    except Exception as e:
        await update_progress(model_id, -1, repr(e))


def download2response(model_download: ModelDownload | None) -> DownloadResponse:
    if model_download:
        if model_download.error:
            progress = 0.0
            message = "Download failed. To retry, call delete_model first"
            status = "errored"
        elif model_download.progress >= 100:
            progress = 100.0
            message = "Download already completed."
            status = "completed"
        else:
            progress = float(model_download.progress)
            message = "Download in progress."
            status = "in_progress"
        return DownloadResponse(
            download_id=model_download.model_id,
            message=message,
            status=status,
            progress=progress,
            error=model_download.error,
        )

    return DownloadResponse(
        download_id=None,
        message="Model not downloaded.",
        status="not_downloaded",
        progress=0.00,
    )


# section: MODEL AVAILABILITY


def model_downloaded(model_id: str) -> bool:
    """Check if a model is downloaded."""
    model_path = get_model_path(model_id.replace("_", "/"))
    return model_path.exists()


@router.get("/available")
async def get_available_models() -> dict[Category, list[ModelName]]:
    """Get a list of available models sorted into categories.

    Returns
    -------
    dict[Category, list[ModelName]]
        Dictionary containing model categories and their models
        Only shows models that are already downloaded
    """
    models = defaultdict(list)

    for model in Path(config.api.data_path).glob("**/*.ckpt"):
        if not model.is_file():
            continue
        model_path = model.relative_to(config.api.data_path)
        category, name = model_path.parts[:-1], model_path.name
        models["/".join(category)].append(name.replace(".ckpt", ""))

    return models


async def get_manifest() -> str:
    manifest_path = os.path.join(config.api.model_repository, "MANIFEST")
    async with httpx.AsyncClient() as client:
        response = await client.get(manifest_path)
        response.raise_for_status()
        return response.text


async def all_available_models() -> dict[Category, list[ModelName]]:
    """Get a list of available models sorted into categories.

    Will show all models in the manifest, regardless of whether they are downloaded or not.

    Returns
    -------
    dict[Category, list[ModelName]]
        Dictionary containing model categories and their models
    """

    # TODO consider reusing client with `download_file` bg task
    response = await get_manifest()

    models = defaultdict(list)

    # TODO: Improve category assignment
    for model in response.split("\n"):
        model = model.strip()
        if not model or model.startswith("#"):
            continue

        if "/" not in model:
            cat = ""
            name = model
        else:
            cat, name = model.split("/", 1)
        models[cat].append(name)
    return models


class ModelDetails(BaseModel):
    download: DownloadResponse
    editable: bool


@router.get("")
async def get_models(admin=Depends(get_admin_user)) -> dict[str, ModelDetails]:
    """Fetch a dictionary of models with their details.

    Parameters
    ----------
    admin : Depends
        Dependency to check if the user is an admin.

    Returns
    -------
    ModelsResponse
        Response model containing a list of models with their details.
    """
    models = {}
    available_models = await all_available_models()

    # TODO: Improve category assignment
    for category, model_names in available_models.items():
        for model_name in model_names:
            model_id = f"{category}/{model_name}" if category else model_name

            not_in_edit = (await get_edit(model_id)) is None

            existing_download = await get_download(f"{category}_{model_name}" if category else model_name)
            download = download2response(existing_download)

            if is_model_downloaded := model_downloaded(model_id):
                download.status = "completed"

            models[model_id] = ModelDetails(download=download, editable=not_in_edit and is_model_downloaded)

    return models


@router.post("/{model_id}/download")
async def download(model_id: str, background_tasks: BackgroundTasks, admin=Depends(get_admin_user)) -> DownloadResponse:
    """Download a model."""

    repo = config.api.model_repository.removesuffix("/")
    model_path = f"{repo}/{model_id.replace('_', '/')}.ckpt"

    existing_download = await get_download(model_id)
    if existing_download:
        return download2response(existing_download)

    model_download_path = Path(get_model_path(model_id.replace("_", "/")))
    model_download_path.parent.mkdir(parents=True, exist_ok=True)

    if model_download_path.exists():
        return DownloadResponse(
            download_id=None,
            message="Download already completed.",
            status="completed",
            progress=100.00,
        )

    await start_download(model_id)
    background_tasks.add_task(download_file, model_id, model_path, model_download_path)
    return DownloadResponse(
        download_id=model_id,
        message="Download started.",
        status="in_progress",
        progress=0.00,
    )


@router.delete("/{model_id}")
async def delete_model(model_id: str, admin=Depends(get_admin_user)) -> DownloadResponse:
    """Delete a model."""

    await delete_download(model_id)
    model_path = get_model_path(model_id.replace("_", "/"))
    if not model_path.exists():
        # TODO if path is not expected to exist (ie failed download), return OK
        return DownloadResponse(
            download_id=None,
            message="Model not found.",
            status="not_downloaded",
            progress=0.00,
        )

    os.remove(model_path)

    return DownloadResponse(
        download_id=None,
        message="Model deleted.",
        status="not_downloaded",
        progress=0.00,
    )

@router.post("/flush")
async def flush_inprogress_downloads(admin=Depends(get_admin_user)) -> None:
    """For flushing the model downloads table -- primarily makes sense at the startup time"""
    await delete_download(None)

# section: MODEL EDIT


@router.get("/{model_id}/metadata")
async def get_model_metadata(model_id: str, admin=Depends(get_admin_user)) -> ModelExtra:
    """Get metadata for a specific model.

    Parameters
    ----------
    model_id : str
        Model to load, directory separated by underscores
    admin : Depends
        Dependency to check if the user is an admin.

    Returns
    -------
    ModelExtra
        Extra model metadata
    """
    model_path = get_model_path(model_id.replace("_", "/"))

    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")

    metadata = get_extra_information(model_path).model_dump()
    metadata.pop("version", None)
    return metadata


async def _update_model_metadata(model_id: str, metadata: ModelExtra) -> ModelExtra:
    """Update metadata for a specific model.

    Parameters
    ----------
    model_id : str
        Model to load, directory separated by underscores
    metadata : dict
        Metadata to update

    Returns
    -------
    ModelExtra
        Updated model metadata
    """

    model_path = get_model_path(model_id.replace("_", "/"))

    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")

    # Run the sync function in a thread to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, set_extra_information, model_path, metadata)
    await finish_edit(model_id)

    return metadata


@router.patch("/{model_id}/metadata")
async def patch_model_metadata(
    model_id: str, metadata: ModelExtra, background_tasks: BackgroundTasks, admin=Depends(get_admin_user)
) -> None:
    """Patch metadata for a specific model.

    Parameters
    ----------
    model_id : str
        Model to load, directory separated by underscores
    metadata : dict
        Metadata to patch
    background_tasks : BackgroundTasks
        Background tasks to run the update in the background
    admin : Depends
        Dependency to check if the user is an admin.

    """
    if not model_downloaded(model_id):
        raise HTTPException(status_code=404, detail="Model not found")

    start_editing(model_id, metadata.model_dump())
    background_tasks.add_task(_update_model_metadata, model_id, metadata)


# section: MODEL INFO


# Model Info
@lru_cache(maxsize=128)
@router.get("/{model_id}/info")
async def get_model_info(model_id: str, admin=Depends(get_admin_user)) -> dict[str, Any]:
    """Get basic information about a model.

    Parameters
    ----------
    model_id : str
        Model to load, directory separated by underscores
    admin : Depends
        Dependency to check if the user is an admin.

    Returns
    -------
    dict[str, Any]
            Dictionary containing model information
    """
    return model_info(get_model_path(model_id.replace("_", "/")))


@router.post("/specification")
async def get_model_spec(modelspec: ModelSpecification, admin=Depends(get_admin_user)) -> dict[str, Any]:
    """Get the Qubed model spec as a json.

    Parameters
    ----------
    modelspec : ModelSpecification
        Model Specification
    admin : Depends
        Dependency to check if the user is an admin.

    Returns
    -------
    dict[str, Any]
            Json Dump of the Qubed model spec
    """

    model_dict = dict(lead_time=modelspec.lead_time, date=modelspec.date, ensemble_members=modelspec.ensemble_members)

    return Model(checkpoint_path=get_model_path(modelspec.model), **model_dict).qube().to_json()
