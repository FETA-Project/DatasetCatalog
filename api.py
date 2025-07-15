from datetime import datetime, UTC
import json
import os
from typing import Optional
import pathlib

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pymongo.errors import DuplicateKeyError
from pathlib import Path

from models import (
    AnalysisStatus,
    CollectionTool,
    Comment,
    Dataset,
    DatasetStatus,
    Submitter,
    User,
)
from oauth2 import require_user, require_admin

# from utils import disabled
import git
from config import config
from s3_client import s3
from utils import ProgressPercentage


api = APIRouter(prefix="/api")


@api.get("/git_sync")
async def git_sync():
    """
    Pulls the latest analysis from git. This is called automatically by the
    scheduled task (or in CI of analysis repository) but can also be called manually.
    """
    git_repo = git.Repo(config.ANALYSIS_DIR)
    git_repo.remotes.origin.pull()


@api.get("/howto")
async def howto():
    """
    Returns the contents of the HOWTO.md file from the analysis directory.

    This file should contain instructions for how to contribute to the analysis.
    """
    howto_path = Path(config.ANALYSIS_DIR, "HOWTO.md")
    return FileResponse(howto_path)


# === USERS ===


@api.get("/users")
async def get_users(user: User = Depends(require_user)):
    """
    Retrieves a list of all users.

    This endpoint requires authentication and returns a list of user data
    in dictionary format. Each user in the list is represented as a dictionary
    containing their respective details.
    """

    users = await User.find().to_list()
    return [user.to_dict() for user in users]


@api.get("/users/me")
async def get_users_me(user: User = Depends(require_user)):
    """
    Retrieves the currently authenticated user.

    This endpoint requires authentication and returns the user data
    in dictionary format.
    """
    return user.to_dict()


@api.get("/users/{email}")
async def get_user(email: str, user: User = Depends(require_admin)):
    """
    Retrieves a user by their email address.

    This endpoint requires admin authentication and returns a user
    data in dictionary format.

    Args:
        email (str): The email address of the user to retrieve.

    Raises:
        HTTPException: If the user is not found.

    Returns:
        dict: The user data.
    """
    found = await User.find(User.email == email).first_or_none()
    if found is None:
        User.not_found(email)
    return found.to_dict()


@api.delete("/users/{email}")
async def delete_user(email: str, user: User = Depends(require_admin)):
    """
    Deletes a user by their email address.

    This endpoint requires admin authentication and deletes the user
    associated with the given email.

    Args:
        email (str): The email address of the user to delete.

    Raises:
        HTTPException: If the user is not found.

    Returns:
        dict: A message indicating the user has been deleted.
    """

    found = await User.find(User.email == email).first_or_none()
    if found is None:
        User.not_found()
    await found.delete()
    return {"message": f"User {email} deleted"}


@api.post("/users/me/edit")
async def edit_user_self(
    name: str = Form(""), surname: str = Form(""), user: User = Depends(require_user)
):
    """
    Edits the currently authenticated user.

    This endpoint requires authentication and updates the currently
    authenticated user with the provided name and/or surname.

    Args:
        name (str): The new name for the user.
        surname (str): The new surname for the user.

    Returns:
        dict: The updated user data.
    """
    if name != "":
        user.name = name
    if surname != "":
        user.surname = surname

    await user.save()

    return user.to_dict()


@api.post("/users/{email}/edit")
async def edit_user(
    email: str, is_admin: bool = Form(...), user: User = Depends(require_admin)
):
    """
    Edits another user's admin status.

    This endpoint requires admin authentication and updates another user's
    admin status.

    Args:
        email (str): The email address of the user to edit.
        is_admin (bool): The new admin status.

    Raises:
        HTTPException: If the user is not found or if the currently authenticated
            user is trying to change their own admin status.

    Returns:
        dict: A message indicating the user was updated.
    """
    if user.email == email:
        raise HTTPException(
            status_code=403, detail="Cannot change your own admin status."
        )
    found = await User.find(User.email == email).first_or_none()
    if found is None:
        User.not_found(email)

    found.is_admin = is_admin
    await found.save()

    return {"message": f"User {email} updated (admin = {is_admin})"}


# === REQUESTS/SUBMITS ===


@api.post("/requests")
async def upload(
    acronym: str = Form(...),
    versions: str = Form(""),
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
    label_name: str = Form(""),
    file: Optional[UploadFile | None] = File(None),
):
    # TODO: what if there is no s3? do i store files locally?

    """
    Create a new dataset and upload a file associated with it.

    Args:
        acronym (str): Unique identifier for the dataset.
        versions (str): Comma-separated list of dataset versions.
        title (str): Title of the dataset.
        paper_title (str): Title of the paper associated with the dataset.
        authors (str): Comma-separated list of authors of the dataset.
        description (str): Short description of the dataset.
        format (str): Format of the dataset.
        doi (str): DOI of the dataset.
        origins_doi (str): DOI of the paper associated with the dataset.
        submitter (str): JSON-serialized Submitter object.
        tags (str): Comma-separated list of tags for the dataset.
        url (str): URL of the dataset.
        label_name (str): Name of the label associated with the dataset.
        file (Optional[UploadFile | None]): File to upload.

    Returns:
        dict: A message indicating the dataset was saved.
    """
    versions_list = versions.split(",")
    versions_list = [v.strip() for v in versions_list if v.strip() != ""]

    if "*" in versions_list:
        versions_list.remove("*")
    if not len(versions_list):
        versions_list = [""]

    found = await Dataset.find(
        Dataset.acronym == acronym, Dataset.versions == versions_list
    ).first_or_none()
    if found:
        name = (
            acronym
            if len(versions_list) == 0
            else f"{acronym}.({'.'.join(versions_list)})"
        )
        raise HTTPException(status_code=400, detail=f"Dataset '{name}' already exists")

    try:
        submitter = Submitter(json.loads(submitter))
        tags = tags.split(",")
        authors = authors.split(",")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Wrong request format: {exc}")

    date_submitted = datetime.now(UTC)

    try:
        dataset = Dataset(
            acronym=acronym,
            versions=versions_list,
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
            label_name=label_name,
            # filename=filename,
            url=url,
        )

        if file is not None:
            dataset.filename = (
                f"{dataset.get_name()}{pathlib.Path(file.filename).suffix}"
            )
            if not config.DEV:
                progress = ProgressPercentage(dataset.filename, file.size)

                await run_in_threadpool(
                    s3.client.upload_fileobj,
                    Fileobj=file.file,
                    Bucket=config.S3_BUCKET,
                    Key=dataset.filename,
                    Callback=progress,
                )

        dataset.create_analysis()
        await dataset.insert()
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Request with acronym '{acronym}' exists: {str(exc)}",
        )
    except OSError:
        raise HTTPException(
            status_code=500, detail=f"Could not save dataset '{acronym}'"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Could not save dataset '{acronym}': {exc}"
        )


# === DATASETS ===
@api.get("/datasets")
async def datasets():
    """
    Returns a list of datasets with their children and analysis status.

    Each dataset is represented as a dictionary with the following keys:

    - acronym
    - versions
    - label_name
    - submitter
    - submitter_email
    - status
    - analysis_status
    - version_children
    - is_child

    The ``version_children`` key contains a list of dictionaries with the same keys
    as above, but only for the children of the dataset (i.e., the datasets with the
    same acronym and a larger version count).

    The ``is_child`` key is a boolean indicating whether the dataset is a child or
    parent.
    """
    datasets = await Dataset.find(Dataset.status != DatasetStatus.REQUESTED).to_list()

    ret = []
    child_ids = set()

    # Group datasets by acronym
    dataset_map = {}
    for dataset in datasets:
        if dataset.versions == [""]:
            dataset.versions = []
        dataset_map.setdefault(dataset.acronym, []).append(dataset)

    # Determine parents and children
    for acronym, dataset_list in dataset_map.items():
        dataset_list.sort(
            key=lambda d: len(d.versions)
        )  # Sort by version count (ascending)

        # The first dataset (smallest version count) is always a parent
        parent = dataset_list[0]
        if len(parent.versions) != 0:
            continue

        for dataset in dataset_list[1:]:  # All others are children
            child_ids.add(dataset.id)

    # Build response
    for dataset in datasets:
        _dict = dataset.to_dict()
        _dict.update(await dataset.get_related())
        _dict.update({"version_children": await dataset.get_version_related()})

        # Mark as child
        is_child = dataset.id in child_ids
        _dict.update({"is_child": is_child})

        ret.append(_dict)

    return ret


@api.get("/datasets/{acronym:path}/{versions:path}")
async def dataset(acronym: str, versions: str):
    """
    Get dataset by acronym and versions.

    If versions == "*", return the root dataset (the one with the smallest version count).
    """
    versions_list = [""] if versions == "*" else versions.split(",")

    dataset = await Dataset.find(
        Dataset.acronym == acronym, Dataset.versions == versions_list
    ).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    ret_dict = {
        "dataset": dataset.to_dict(),
        "edit_analysis_url": dataset._git_edit_url(),
        "version_children": await dataset.get_version_related(False),
    }

    # ret_dict.update(await dataset.get_related())

    return ret_dict


# FIXME: should probably be something like /api/datasets/{acronym:path}/download
@api.get("/files/{acronym:path}/{versions:path}")
async def dataset_download(acronym: str, versions: str):
    """
    Generate a presigned URL to download a dataset file.

    This endpoint retrieves the specified dataset by acronym and versions,
    and generates a presigned URL that allows downloading the file associated
    with the dataset from S3. The URL is valid for a limited time.

    Args:
        acronym (str): The unique identifier of the dataset.
        versions (str): A comma-separated list of dataset versions or "*" for
                        the root dataset.

    Raises:
        HTTPException: If the dataset or its file is not found.

    Returns:
        dict: A dictionary containing the presigned URL for the dataset file.
    """

    versions_list = [""] if versions == "*" else versions.split(",")

    dataset = await Dataset.find(
        Dataset.acronym == acronym, Dataset.versions == versions_list
    ).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    if dataset.filename is None:
        raise HTTPException(
            status_code=404, detail=f"File for dataset '{acronym}' not found"
        )

    if config.DEV:
        return {"filelink": "Using dev, no filelink available"}

    filelink = s3.client.generate_presigned_url(
        "get_object",
        Params={"Bucket": "katoda", "Key": dataset.filename},
        ExpiresIn=3600,
    )

    return {"filelink": filelink}


@api.get("/analysis_files/{acronym:path}/{versions:path}/{filename:path}")
async def analysis_files_download(acronym: str, versions: str, filename: str):
    """
    Download a file from a dataset's analysis directory.

    This endpoint retrieves the specified dataset by acronym and versions,
    and serves the specified file from the analysis directory of the dataset.

    Args:
        acronym (str): The unique identifier of the dataset.
        versions (str): A comma-separated list of dataset versions or "*" for
                        the root dataset.
        filename (str): The name of the file to be downloaded.

    Raises:
        HTTPException: If the dataset or the file is not found.

    Returns:
        FileResponse: The requested file, served with the correct Content-Type
                     and filename.
    """
    versions_list = [""] if versions == "*" else versions.split(",")

    dataset = await Dataset.find(
        Dataset.acronym == acronym, Dataset.versions == versions_list
    ).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    if filename not in dataset.get_files():
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' for dataset '{acronym}' not found",
        )

    filepath = pathlib.Path(dataset.get_analysis_path()).joinpath(filename)
    if filepath is None:
        raise HTTPException(
            status_code=404, detail=f"File for dataset '{acronym}' not found"
        )

    return FileResponse(
        os.path.abspath(filepath),
        media_type="application/octet-stream",
        filename=filename,
    )


@api.post("/datasets/{curr_acronym:path}/{curr_versions:path}/edit")
async def dataset_edit(
    curr_acronym: str,
    curr_versions: str,
    acronym: Optional[str] = Form(""),
    versions: Optional[str] = Form(""),
    title: Optional[str] = Form(""),
    paper_title: Optional[str] = Form(""),
    authors: Optional[str] = Form(""),
    description: Optional[str] = Form(""),
    format: Optional[str] = Form(""),
    doi: Optional[str] = Form(""),
    origins_doi: Optional[str] = Form(""),
    # submitter: Optional[str] = Form('{"name": "", "email": ""}'),
    tags: Optional[str] = Form(""),
    url: Optional[str] = Form(""),
    analysis_status: Optional[str] = Form(""),
    label_name: Optional[str] = Form(""),
    user: User = Depends(require_user),
):
    """
    Edit an existing dataset.

    This endpoint retrieves the specified dataset by acronym and versions,
    and updates the dataset with the provided information. If the dataset is
    not found, a 404 error is raised.

    If the user is not an admin and the user email does not match the email of
    the dataset submitter, a 401 error is raised.

    Args:
        curr_acronym (str): The current acronym of the dataset.
        curr_versions (str): The current versions of the dataset, or "*" for
                             the root dataset.
        acronym (str): The new acronym of the dataset.
        versions (str): The new versions of the dataset, or "*" for the root
                        dataset.
        title (str): The new title of the dataset.
        paper_title (str): The new title of the paper associated with the
                           dataset.
        authors (str): The new authors of the dataset, comma-separated.
        description (str): The new description of the dataset.
        format (str): The new format of the dataset.
        doi (str): The new DOI of the dataset.
        origins_doi (str): The new DOI of the paper associated with the
                           dataset.
        tags (str): The new tags of the dataset, comma-separated.
        url (str): The new URL of the dataset.
        analysis_status (str): The new analysis status of the dataset.
        label_name (str): The new label name associated with the dataset.
        user (User): The user performing the request.

    Raises:
        HTTPException: If the dataset or its file is not found, or if the user
                      is not authorized to edit the dataset.
        HTTPException: If the dataset with the new acronym and versions already
                      exists.

    Returns:
        dict: A message indicating the dataset was updated.
    """
    curr_versions_list = [""] if curr_versions == "*" else curr_versions.split(",")
    dataset = await Dataset.find(
        Dataset.acronym == curr_acronym, Dataset.versions == curr_versions_list
    ).first_or_none()
    if dataset is None:
        Dataset.not_found(curr_acronym)

    if not user.is_admin and user.email != dataset.submitter["email"]:
        raise HTTPException(
            status_code=401,
            detail="You are not authorized to edit this dataset.",
        )

    old_path = dataset.get_analysis_path()

    versions_list = versions.split(",")
    versions_list = [v.strip() for v in versions_list if v.strip() != ""]

    if "*" in versions_list:
        versions_list.remove("*")

    if not len(versions_list):
        versions_list = [""]

    if curr_versions_list != versions_list or curr_acronym != acronym:
        dataset.versions = versions_list
        dataset.acronym = acronym
        found = await Dataset.find(
            Dataset.acronym == dataset.acronym, Dataset.versions == dataset.versions
        ).first_or_none()
        if found:
            raise HTTPException(
                status_code=409,
                detail=f"Dataset with acronym '{dataset.acronym}' and versions '{dataset.versions}' already exists",
            )

    dataset.title = title

    dataset.paper_title = paper_title

    dataset.authors = authors.split(",")

    dataset.description = description

    dataset.format = format

    dataset.doi = doi

    dataset.origins_doi = origins_doi

    # dataset.submitter = Submitter(json.loads(submitter))

    dataset.tags = tags.split(",")

    dataset.url = url

    dataset.analysis_status = AnalysisStatus(analysis_status)

    dataset.label_name = label_name

    try:
        await dataset.save()
        dataset.update_analysis(old_path=old_path)

        if dataset.filename is not None and dataset.filename != dataset.get_name():
            _new_filename = (
                f"{dataset.get_name()}{pathlib.Path(dataset.filename).suffix}"
            )
            if not config.DEV:
                s3.client.copy_object(
                    Bucket=config.S3_BUCKET,
                    CopySource={"Bucket": "katoda", "Key": dataset.filename},
                    Key=_new_filename,
                )
                s3.client.delete_object(Bucket=config.S3_BUCKET, Key=dataset.filename)

            dataset.filename = _new_filename
            await dataset.save()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not update dataset '{curr_acronym}': {str(exc)}",
        )

    return {"message": f"Dataset {curr_acronym} updated"}


@api.post("/datasets/{acronym:path}/{versions:path}/upload")
async def dataset_upload_file(
    acronym: str,
    versions: str,
    file: Optional[UploadFile | None] = File(None),
    user: User = Depends(require_user),
):
    """
    Upload a file to a dataset.

    Args:
        acronym (str): The acronym of the dataset to which to upload the file.
        versions (str): A comma-separated list of dataset versions, or "*" for the
            root dataset.
        file (UploadFile, optional): The file to be uploaded. Defaults to None.
        user (User, optional): The user performing the action. Defaults to
            `Depends(require_user)`.

    Raises:
        HTTPException: If the dataset or file is not found, or if the user is not
            authorized to edit the dataset.

    Returns:
        dict: A dictionary containing a message indicating the success of the
            upload.
    """
    versions_list = [""] if versions == "*" else versions.split(",")
    dataset = await Dataset.find(
        Dataset.acronym == acronym, Dataset.versions == versions_list
    ).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    if not user.is_admin and user.email != dataset.submitter.email:
        raise HTTPException(
            status_code=401,
            detail="You are not authorized to edit this dataset.",
        )

    old_filename = dataset.filename

    dataset.filename = f"{dataset.get_name()}{pathlib.Path(file.filename).suffix}"

    if not config.DEV or True:
        progress = ProgressPercentage(dataset.filename, file.size)

        await run_in_threadpool(
            s3.client.upload_fileobj,
            Fileobj=file.file,
            Bucket=config.S3_BUCKET,
            Key=dataset.filename,
            Callback=progress,
        )

        if old_filename is not None and old_filename != dataset.filename:
            s3.client.delete_object(Bucket=config.S3_BUCKET, Key=old_filename)

    await dataset.save()

    return {"message": f"File for dataset {acronym} uploaded"}


@api.delete("/datasets/{acronym:path}/{versions:path}")
async def delete(acronym: str, versions: str, user: User = Depends(require_admin)):
    """
    Delete a dataset.

    Args:
        acronym (str): The acronym of the dataset to be deleted.
        versions (str): A comma-separated list of dataset versions, or "*" for the
            root dataset.
        user (User, optional): The user performing the action. Defaults to
            `Depends(require_admin)`.

    Raises:
        HTTPException: If the dataset is not found, or if the user is not
            authorized to delete the dataset.

    Returns:
        dict: A dictionary containing a message indicating the success of the
            deletion.
    """
    versions_list = [""] if versions == "*" else versions.split(",")
    dataset = await Dataset.find(
        Dataset.acronym == acronym, Dataset.versions == versions_list
    ).first_or_none()

    if not config.DEV:
        if dataset.filename is not None:
            s3.client.delete_object(Bucket=config.S3_BUCKET, Key=dataset.filename)

    await dataset.delete()
    # TODO: also delete analysis?
    return {"message": f"Dataset {acronym} deleted"}


# === COMMENTS ===


@api.post("/comments")
async def create_comment(
    text: str = Form(...),
    author: User = Depends(require_user),
    belongs_to: str = Form(...),
    parent_id: Optional[str] = Form(None),
):
    """
    Create a new comment associated with a dataset.

    Args:
        text (str): The content of the comment.
        author (User): The author of the comment, automatically derived from the
            current authenticated user.
        belongs_to (str): The acronym of the dataset the comment belongs to.
        parent_id (Optional[str]): The ID of the parent comment, if this is a reply.

    Raises:
        HTTPException: If the dataset the comment belongs to is not found.

    Returns:
        Comment: The created comment object.
    """

    dataset = await Dataset.find(Dataset.acronym == belongs_to).first_or_none()

    if dataset is None:
        Dataset.not_found(belongs_to)

    comment = Comment(
        parent_id=parent_id,
        belongs_to=belongs_to,
        text=text,
        author=author.email,
        date=datetime.now(UTC),
    )

    await comment.insert()

    return comment


@api.post("/comments/{comment_id}")
async def edit_comment(
    comment_id: str,
    text: str = Form(...),
    author: User = Depends(require_user),
    # user_email: str = Depends(require_admin)
):
    """
    Edit an existing comment.

    Args:
        comment_id (str): The ID of the comment to be edited.
        text (str): The new text content for the comment.
        author (User): The user attempting to edit the comment, automatically derived
            from the current authenticated user.

    Raises:
        HTTPException: If the comment is not found or if the user is not authorized
            to edit the comment.

    Returns:
        Comment: The updated comment object.
    """

    comment = await Comment.get(comment_id)
    if comment is None:
        Comment.not_found(comment_id)

    if author.email != comment.author:
        raise HTTPException(
            status_code=401,
            detail="You are not authorized to edit this comment.",
        )

    comment.text = text
    comment.edited = True

    await comment.save()

    return comment


@api.get("/comments/{acronym:path}")
async def comments(acronym: str):
    """
    Retrieve all comments for a given dataset.

    Args:
        acronym (str): The unique identifier for the dataset.

    Raises:
        HTTPException: If the dataset is not found.

    Returns:
        list: A list of comment objects, sorted in descending order of date.
    """
    dataset = await Dataset.find(Dataset.acronym == acronym).first_or_none()

    if dataset is None:
        Dataset.not_found(acronym)

    # root_comments = await Comment.find(Comment.belongs_to == acronym).to_list()
    root_comments: list = await Comment.find(
        Comment.belongs_to == acronym,
        Comment.parent_id == None,  # noqa: E711
    ).to_list()

    for i, comment in enumerate(root_comments):
        _comment = comment.dict()
        _comment.update(
            {"id": str(comment.id), "children": await comment.get_children()}
        )
        root_comments[i] = _comment

    root_comments.sort(key=lambda x: x["date"], reverse=True)
    return root_comments


# async def comments_delete(acronym: str, comment_id: str, user_email: str = Depends(require_admin)):
@api.delete("/comments/{comment_id}")
async def comments_delete(comment_id: str, author: User = Depends(require_user)):
    """
    Delete a comment.

    Args:
        comment_id (str): The unique identifier for the comment.
        author (User): The authenticated user making the request.

    Raises:
        HTTPException: If the comment is not found or if the user is not authorized to delete the comment.

    Returns:
        dict: A dictionary containing a message with the comment ID and the phrase "deleted".
    """
    comment = await Comment.get(comment_id)

    if comment is None:
        print("not found: ", comment_id)
        # Comment.not_found(comment_id)

    if not author.is_admin and author.email != comment.author:
        raise HTTPException(
            status_code=401,
            detail="You are not authorized to delete this comment.",
        )

    comment.deleted = True
    if author.is_admin and author.email != comment.author:
        comment.text = "<removed by admin>"
        comment.author = "<removed>"
    else:
        comment.text = "<deleted>"
        comment.author = "<deleted>"

    await comment.save()

    return {"message": f"Comment {comment_id} deleted"}


# === COLLECTION TOOLS ===


@api.get("/collectionTools")
async def get_collection_tools():
    """
    Get a list of all collection tools.

    Returns:
        list: A list of CollectionTool objects.
    """
    return await CollectionTool.find().to_list()


@api.get("/collectionTools/{name}")
async def get_collection_tool(name: str):
    """
    Retrieve a collection tool by its name.

    Args:
        name (str): The name of the collection tool to retrieve.

    Returns:
        CollectionTool or None: The collection tool object if found, otherwise None.
    """

    return await CollectionTool.find(CollectionTool.name == name).first_or_none()


@api.post("/collectionTools")
async def create_collection_tool(
    name: str = Form(...),
    url: str = Form(""),
    description: str = Form(""),
    known_issues: str = Form(""),
):
    """
    Create a new collection tool.

    Args:
        name (str): The name of the collection tool. Must be unique.
        url (str): The URL for the collection tool. Defaults to an empty string.
        description (str): The description of the collection tool. Defaults to an empty string.
        known_issues (str): Any known issues with the collection tool. Defaults to an empty string.

    Raises:
        HTTPException: If a collection tool with the same name already exists.

    Returns:
        CollectionTool: The newly created CollectionTool object.
    """
    if await CollectionTool.find(CollectionTool.name == name).first_or_none():
        raise HTTPException(status_code=400, detail="Collection tool already exists")

    new_collection_tool = CollectionTool(
        name=name, url=url, description=description, known_issues=known_issues
    )

    await new_collection_tool.insert()

    return new_collection_tool


@api.post("/collectionTools/{name}")
async def edit_collection_tool(
    name: str,
    url: str = Form(""),
    description: str = Form(""),
    known_issues: str = Form(""),
    user: User = Depends(require_admin),
):
    """
    Edit an existing collection tool.

    Args:
        name (str): The name of the collection tool to edit.
        url (str): The new URL for the collection tool. Defaults to an empty string.
        description (str): The new description for the collection tool. Defaults to an empty string.
        known_issues (str): The new known issues for the collection tool. Defaults to an empty string.
        user (User): The authenticated user making the request. Must be an admin.

    Raises:
        HTTPException: If the collection tool is not found.

    Returns:
        CollectionTool: The edited CollectionTool object.
    """
    collection_tool = await CollectionTool.find(
        CollectionTool.name == name
    ).first_or_none()

    if collection_tool is None:
        CollectionTool.not_found(name)

    collection_tool.url = url
    collection_tool.description = description
    collection_tool.known_issues = known_issues

    await collection_tool.save()

    return collection_tool


@api.delete("/collectionTools/{name}")
async def delete_collection_tool(name: str, user: User = Depends(require_admin)):
    """
    Delete an existing collection tool.

    Args:
        name (str): The name of the collection tool to delete.
        user (User): The authenticated user making the request. Must be an admin.

    Raises:
        HTTPException: If the collection tool is not found.

    Returns:
        dict[str, str]: A dictionary with a message indicating that the collection tool has been deleted.
    """
    collection_tool = await CollectionTool.find(
        CollectionTool.name == name
    ).first_or_none()

    if collection_tool is None:
        CollectionTool.not_found(name)

    await collection_tool.delete()

    return {"message": f"Collection tool {name} deleted"}
