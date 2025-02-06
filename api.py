from datetime import datetime, UTC
import json
import os
from typing import Optional
import pathlib

from beanie.operators import All
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse
from pymongo.errors import DuplicateKeyError

from models import (CollectionTool, Comment, Dataset, DatasetStatus, Submitter, User)
from oauth2 import require_user, require_admin
# from utils import disabled
from werkzeug.utils import secure_filename
import git
from config import config


api = APIRouter(prefix="/api")

@api.get('/git_sync')
async def git_sync():
    git_repo = git.Repo(config.ANALYSIS_DIR)
    git_repo.remotes.origin.pull()

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
    format: str = Form(""),
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

    acronym_aliases_list = acronym_aliases.split(",")

    if "*" in acronym_aliases_list:
        acronym_aliases_list.remove("*")
    if not len(acronym_aliases_list):
        acronym_aliases_list = ['']

    found = await Dataset.find(Dataset.acronym == acronym, Dataset.acronym_aliases == acronym_aliases_list).first_or_none()
    if found:
        name = acronym if len(acronym_aliases_list) == 0 else f"{acronym}.({'.'.join(acronym_aliases_list)})"
        raise HTTPException(
            status_code=400,
            detail=f"Dataset '{name}' already exists"
        )

    try:
        submitter = Submitter(json.loads(submitter))
        tags = tags.split(",")
        authors = authors.split(",")
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
            acronym_aliases=acronym_aliases_list,
            title=title,
            paper_title=paper_title,
            authors=authors,
            description=description,
            format=format,
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
    ret = []
    for dataset in datasets:
        _parents, _children = await dataset.get_related()
        _dict = dataset.to_dict()
        _dict.update({'parents': _parents, 'children': _children})
        ret.append(_dict)

    return ret


@api.get('/datasets/{acronym:path}/{aliases:path}')
async def dataset(acronym: str, aliases: str):
    aliases_list = [''] if aliases == "*" else aliases.split(",")

    dataset = await Dataset.find(Dataset.acronym == acronym, Dataset.acronym_aliases == aliases_list).first_or_none()
    
    if dataset is None:
        Dataset.not_found(acronym)

    alias_children = []
    alias_parents = []

    if dataset.acronym_aliases != ['']:
        alias_children = await Dataset.find(
            All(Dataset.acronym_aliases, dataset.acronym_aliases)
        ).to_list()
        alias_parents = await Dataset.find(
            Dataset.acronym_aliases == dataset.acronym_aliases[:-1]
        ).to_list()

    related = []
    origin = []
    same_origin = []

    if dataset.doi != "":
        related = await Dataset.find(Dataset.origins_doi == dataset.doi).to_list()
    if dataset.origins_doi != "":
        origin = await Dataset.find(Dataset.doi == dataset.origins_doi).to_list()
        same_origin = await Dataset.find(Dataset.origins_doi == dataset.origins_doi).to_list()

    return {
        'dataset': dataset.to_dict(),
        'related_datasets': [{'acronym': d.acronym, 'aliases': d.acronym_aliases} for d in related if d.acronym != dataset.acronym],
        'origin_datasets': [{'acronym': d.acronym, 'aliases': d.acronym_aliases} for d in origin if d.acronym != dataset.acronym],
        'same_origin_datasets': [{'acronym': d.acronym, 'aliases': d.acronym_aliases} for d in same_origin if d.acronym != dataset.acronym],
        'alias_children': [{'acronym': d.acronym, 'aliases': d.acronym_aliases} for d in alias_children if d.acronym_aliases != dataset.acronym_aliases],
        'alias_parents': [{'acronym': d.acronym, 'aliases': d.acronym_aliases} for d in alias_parents if d.acronym_aliases != dataset.acronym_aliases],
        'edit_analysis_url': dataset._git_edit_url()
    }

# FIXME: should probably be something like /api/datasets/{acronym:path}/download
@api.get('/files/{acronym:path}/{aliases:path}')
async def dataset_download(acronym: str, aliases: str):
    aliases_list = [''] if aliases == "*" else aliases.split(",")

    dataset = await Dataset.find(Dataset.acronym == acronym, Dataset.acronym_aliases == aliases_list).first_or_none()

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

@api.get('/analysis_files/{acronym:path}/{aliases:path}/{filename:path}')
async def analysis_files_download(acronym: str, aliases: str, filename: str):
    aliases_list = [''] if aliases == "*" else aliases.split(",")

    dataset = await Dataset.find(Dataset.acronym == acronym, Dataset.acronym_aliases == aliases_list).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    if filename not in dataset.get_files():
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' for dataset '{acronym}' not found"
        )

    filepath = pathlib.Path(dataset.get_analysis_path()).joinpath(filename)
    if filepath is None:
        raise HTTPException(
            status_code=404,
            detail=f"File for dataset '{acronym}' not found"
        )

    return FileResponse(
        os.path.abspath(filepath),
        media_type="application/octet-stream",
        filename=filename
    )

@api.post('/datasets/{acronym:path}/{aliases:path}/edit')
async def dataset_edit(
    acronym: str,
    aliases: str,
    acronym_aliases: Optional[str] = Form(""),
    title: Optional[str] = Form(""),
    paper_title: Optional[str] = Form(""),
    authors: Optional[str] = Form(""),
    description: Optional[str] = Form(""),
    format: Optional[str] = Form(""),
    doi: Optional[str] = Form(""),
    origins_doi: Optional[str] = Form(""),
    submitter: Optional[str] = Form("{\"name\": \"\", \"email\": \"\"}"),
    tags: Optional[str] = Form(""),
    url: Optional[str] = Form(""),
):
    aliases_list = [''] if aliases == "*" else aliases.split(",")
    dataset = await Dataset.find(Dataset.acronym == acronym, Dataset.acronym_aliases == aliases_list).first_or_none()
    if dataset is None:
        Dataset.not_found(acronym)

    old_path = dataset.get_analysis_path()

    acronym_aliases_list = acronym_aliases.split(',')
    if "*" in acronym_aliases_list:
        acronym_aliases_list.remove("*")
    if not len(acronym_aliases_list):
        acronym_aliases_list = ['']

    if aliases_list != acronym_aliases_list:
        dataset.acronym_aliases = acronym_aliases_list
        found = await Dataset.find(Dataset.acronym == dataset.acronym, Dataset.acronym_aliases == dataset.acronym_aliases).first_or_none()
        if found:
            raise HTTPException(
                status_code=409,
                detail=f"Dataset with acronym '{dataset.acronym}' and aliases '{dataset.acronym_aliases}' already exists"
            )

    dataset.title = title
    
    dataset.paper_title = paper_title
    
    dataset.authors = authors.split(",")
    
    dataset.description = description

    dataset.format = format
    
    dataset.doi = doi
    
    dataset.origins_doi = origins_doi
    
    dataset.submitter = Submitter(json.loads(submitter))
    
    dataset.tags = tags.split(",")

    dataset.url = url

    try:
        await dataset.save()
        dataset.update_analysis(old_path=old_path)
    except Exception as exc:
        raise HTTPException(
        status_code=500,
        detail=f"Could not update dataset '{acronym}': {str(exc)}"
    )

    return {"message": f"Dataset {acronym} updated"}

@api.post('/datasets/{acronym:path}/{aliases:path}/upload')
async def dataset_upload_file(acronym: str, aliases: str, file: Optional[UploadFile | None] = File(None)):
    aliases_list = [''] if aliases == "*" else aliases.split(",")
    dataset = await Dataset.find(Dataset.acronym == acronym, Dataset.acronym_aliases == aliases_list).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    if dataset.filename is not None:
        os.remove(dataset.get_file_path())

    dataset.filename = f'{secure_filename(acronym)}{pathlib.Path(file.filename).suffix}'
    with open(dataset.get_file_path(), "wb") as f:
        f.write(file.file.read())

    await dataset.save()

    return {"message": f"File for dataset {acronym} uploaded"}


@api.delete('/datasets/{acronym:path}/{aliases:path}')
async def delete(acronym: str, aliases: str, user_email: str = Depends(require_admin)):
    aliases_list = [''] if aliases == "*" else aliases.split(",")
    dataset = await Dataset.find(Dataset.acronym == acronym, Dataset.acronym_aliases == aliases_list).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    await dataset.delete()
    # TODO: also delete analysis?
    return {"message": f"Dataset {acronym} deleted"}


@api.post('/comments')
async def create_comment(
    text: str = Form(...),
    author: str = Form(...),
    belongs_to: str = Form(...),
    parent_id: Optional[str] = Form(None)):

    dataset = await Dataset.find(Dataset.acronym == belongs_to).first_or_none()

    if dataset is None:
        Dataset.not_found(belongs_to)

    comment = Comment(
        parent_id=parent_id,
        belongs_to=belongs_to,
        text=text,
        author=author,
        date=datetime.now(UTC)
    )

    await comment.insert()

    return comment

@api.post('/comments/{comment_id}')
async def edit_comment(
    comment_id: str,
    text: str = Form(...),
    # user_email: str = Depends(require_admin)
    ):

    comment = await Comment.get(comment_id)
    if comment is None:
        Comment.not_found(comment_id)

    comment.text = text
    comment.edited = True

    await comment.save()

    return comment

@api.get('/comments/{acronym:path}')
async def comments(acronym: str):
    dataset = await Dataset.find(Dataset.acronym == acronym).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    # root_comments = await Comment.find(Comment.belongs_to == acronym).to_list()
    root_comments: list = await Comment.find(Comment.belongs_to == acronym, Comment.parent_id == None).to_list()

    for i, comment in enumerate(root_comments):
        _comment = comment.dict()
        _comment.update({
            "id": str(comment.id),
            "children": await comment.get_children()
        })
        root_comments[i] = _comment

    root_comments.sort(key=lambda x: x['date'], reverse=True)
    return root_comments

# async def comments_delete(acronym: str, comment_id: str, user_email: str = Depends(require_admin)):
@api.delete('/comments/{comment_id}')
async def comments_delete(comment_id: str):
    comment = await Comment.get(comment_id)

    if comment is None:
        print("not found: ", comment_id)
        # Comment.not_found(comment_id)

    comment.deleted = True
    comment.text = "<deleted>"
    comment.author = "<deleted>"

    await comment.save()

    return {"message": f"Comment {comment_id} deleted"}

@api.get('/collectionTools')
async def get_collection_tools():
    return await CollectionTool.find().to_list()

@api.get('/collectionTools/{name}')
async def get_collection_tool(name: str):
    return await CollectionTool.find(CollectionTool.name == name).first_or_none()

@api.post('/collectionTools')
async def create_collection_tool(name: str = Form(...), url: str = Form(""), description: str = Form(""), known_issues: str = Form("")):
    if await CollectionTool.find(CollectionTool.name == name).first_or_none():
        raise HTTPException(status_code=400, detail="Collection tool already exists")

    new_collection_tool = CollectionTool(
        name=name,
        url=url,
        description=description,
        known_issues=known_issues
    )

    await new_collection_tool.insert()

    return new_collection_tool

@api.post('/collectionTools/{name}')
async def edit_collection_tool(name: str, url: str = Form(""), description: str = Form(""), known_issues: str = Form("")):
    collection_tool = await CollectionTool.find(CollectionTool.name == name).first_or_none()

    if collection_tool is None:
        CollectionTool.not_found(name)

    collection_tool.url = url
    collection_tool.description = description
    collection_tool.known_issues = known_issues

    await collection_tool.save()

    return collection_tool

@api.delete('/collectionTools/{name}')
async def delete_collection_tool(name: str):
    collection_tool = await CollectionTool.find(CollectionTool.name == name).first_or_none()

    if collection_tool is None:
        CollectionTool.not_found(name)

    await collection_tool.delete()

    return {"message": f"Collection tool {name} deleted"}
