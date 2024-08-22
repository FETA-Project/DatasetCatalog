from datetime import datetime, UTC
import json
import os
from typing import Optional
import pathlib

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pymongo.errors import DuplicateKeyError

from models import (Dataset, DatasetStatus, Submitter, User)
from oauth2 import require_user, require_admin
# from utils import disabled
from werkzeug.utils import secure_filename

api = APIRouter(prefix="/api")


# === USERS ===

@api.get('/users')
async def get_users(user_email: str = Depends(require_admin)):
    users = await User.find().to_list()
    return [user.to_dict() for user in users]


@api.get('/users/me')
async def get_users_me(user_email: str = Depends(require_user)):
    user = await User.find(User.email == user_email).first_or_none()
    return user.to_dict()


@api.get('/users/{email}')
async def get_user(email: str, user_email: str = Depends(require_admin)):
    found = await User.find(User.email == email).first_or_none()
    if found is None:
        User.not_found(email)
    return found.to_dict()


@api.delete('/users/{email}')
async def delete_user(email: str, user_email: str = Depends(require_admin)):
    user = await User.find(User.email == email).first_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"message": f"User {email} deleted"}


# === REQUESTS/SUBMITS ===

@api.get('/requests')
async def get_requests():
    requests = await Dataset.find(Dataset.status == DatasetStatus.REQUESTED).to_list()
    return requests


@api.post('/requests')
async def upload(
    acronym: str = Form(...),
    acronym_aliases: str = Form(""),
    title: str = Form(""),
    paper_title: str = Form(""),
    authors: str = Form(""),
    description: str = Form(""),
    doi: str = Form(""),
    origins_doi: str = Form(""),
    submitter: str = Form(""),
    tags: str = Form(""),
    url: str = Form(""),
    file: Optional[UploadFile | None] = File(None),
    ):

    # TODO: add support for file upload from url
    # if no filename
    # download from url

    try:
        submitter = Submitter(json.loads(submitter))
        tags = tags.split(",")
        authors = authors.split(",")
        acronym_aliases = acronym_aliases.split(",")
    except Exception as exc:
        raise HTTPException(
        status_code=400,
        detail=f"Wrong request format: {exc}"
    )

    date_submitted = datetime.now(UTC)

    if file is not None:
        filename = f'{secure_filename(acronym)}{pathlib.Path(file.filename).suffix}'
    else:
        filename = None

    try:
        dataset = Dataset(
            acronym=acronym,
            acronym_aliases=acronym_aliases,
            title=title,
            paper_title=paper_title,
            authors=authors,
            description=description,
            doi=doi,
            origins_doi=origins_doi,
            submitter=submitter,
            date_submitted=date_submitted,
            status=DatasetStatus.ACCEPTED,
            tags=tags,
            filename=filename,
            url=url,
        )

        if filename is not None:    
            with open(dataset.get_file_path(), "wb") as f:
                f.write(file.file.read())

        dataset.create_analysis()
        await dataset.insert()
    except DuplicateKeyError as exc:
        raise HTTPException(
        status_code=401,
        detail=f"Request with acronym '{acronym}' exists: {str(exc)}"
    )
    except OSError:
        raise HTTPException(
        status_code=500,
        detail=f"Could not save dataset '{acronym}'"
    )
    except Exception as exc:
        raise HTTPException(
        status_code=500,
        detail=f"Could not save dataset '{acronym}': {exc}"
    )

    # try:
    #     repo = pydoi.validate_doi(doi)
    #     repo = doi
    #     response = requests.get(repo+"?download")
    #     if response.status_code == 200:
    #         print(response)
    #         metadata = response.json()
    # except ValueError:
    #     metadata = "Could not load metadata"



@api.head('/requests/{acronym:path}')
async def request_accept(acronym: str, user_email: str = Depends(require_admin)):
    dataset = await Dataset.find(Dataset.acronym == acronym).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    dataset.status = DatasetStatus.ACCEPTED
    # TODO: push analysis to git
    await dataset.save()

    # TODO: change requested to analyzing
    return {"message": f"Request for {acronym} accepted"}


@api.delete('/requests/{acronym:path}')
async def request_reject(acronym: str, user_email: str = Depends(require_user)):
    user = await User.find(User.email == user_email).first_or_none()

    request = await Dataset.find(Dataset.acronym == acronym).first_or_none()

    if request is None:
        Dataset.not_found(acronym)

    if request.submitter.get('email') != user.email:
        user.check_admin()

    await request.delete()

    return {"message": f"Request for {acronym} rejected"}


# === DATASETS ===

@api.get('/datasets')
async def datasets():
    datasets = await Dataset.find(Dataset.status != DatasetStatus.REQUESTED).to_list()
    return datasets


@api.get('/datasets/{acronym:path}')
async def dataset(acronym: str):
    dataset = await Dataset.find(Dataset.acronym == acronym).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    analysis = dataset.get_analysis()

    related = []
    origin = []

    if dataset.doi != "":
        related = await Dataset.find(Dataset.origins_doi == dataset.doi).to_list()
    if dataset.origins_doi != "":
        origin = await Dataset.find(Dataset.doi == dataset.origins_doi).to_list()
        same_origin = await Dataset.find(Dataset.origins_doi == dataset.origins_doi).to_list()

    return {
        'dataset': dataset,
        'related_datasets': [d.acronym for d in related if d.acronym != dataset.acronym],
        'origin_datasets': [d.acronym for d in origin if d.acronym != dataset.acronym],
        'same_origin_datasets': [d.acronym for d in same_origin if d.acronym != dataset.acronym],
        'analysis': analysis if analysis is not None else {},
        'edit_analysis_url': dataset._git_edit_url()
    }

# FIXME: should probably be something like /api/datasets/{acronym:path}/download
@api.get('/files/{acronym:path}')
async def dataset_download(acronym: str):
    dataset = await Dataset.find(Dataset.acronym == acronym).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    filepath = dataset.get_file_path()
    if filepath is None:
        raise HTTPException(
            status_code=404,
            detail=f"File for dataset '{acronym}' not found"
        )

    return FileResponse(
        os.path.abspath(filepath),
        media_type="application/octet-stream",
        filename=dataset.filename
    )

@api.post('/datasets/{acronym:path}/edit')
async def dataset_edit(
    acronym: str,
    acronym_aliases: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    paper_title: Optional[str] = Form(None),
    authors: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    doi: Optional[str] = Form(None),
    origins_doi: Optional[str] = Form(None),
    submitter: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
):
    dataset = await Dataset.find(Dataset.acronym == acronym).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    if acronym_aliases is not None:
        dataset.acronym_aliases = acronym_aliases.split(",")

    if title is not None:
        dataset.title = title
    
    if paper_title is not None:
        dataset.paper_title = paper_title
    
    if authors is not None:
        dataset.authors = authors.split(",")
    
    if description is not None:
        dataset.description = description
    
    if doi is not None:
        dataset.doi = doi
    
    if origins_doi is not None:
        dataset.origins_doi = origins_doi
    
    if submitter is not None:
        dataset.submitter = Submitter(json.loads(submitter))
    
    if tags is not None:
        dataset.tags = tags.split(",")

    try:
        await dataset.save()
    except Exception as exc:
        raise HTTPException(
        status_code=500,
        detail=f"Could not update dataset '{acronym}': {str(exc)}"
    )

    return {"message": f"Dataset {acronym} updated"}



@api.delete('/datasets/{acronym:path}')
async def delete(acronym: str, user_email: str = Depends(require_admin)):
    dataset = await Dataset.find(Dataset.acronym == acronym).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    await dataset.delete()
    # TODO: also delete analysis?
    return {"message": f"Dataset {acronym} deleted"}
