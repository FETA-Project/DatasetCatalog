from datetime import datetime
from enum import Enum
import os
import pathlib
import shutil
from threading import Thread
from typing import Optional
import git

import pymongo
from beanie import Document, Indexed
from fastapi import HTTPException
import toml
from typing_extensions import TypedDict
from werkzeug.utils import secure_filename

from config import config
from utils import hash_password, verify_password


class Comment(Document):
    # id: str
    parent_id: str = None
    belongs_to: str
    text: str
    author: str
    date: datetime
    edited: bool = False
    deleted: bool = False

    async def get_parent(self) -> Optional["Comment"]:
        if self.parent_id is not None:
            return await Comment.find(Comment.id == self.parent_id).first()

        return None

    # get all children of this comment recursively
    async def get_children(self) -> list["Comment"]:
        children = await Comment.find(Comment.parent_id == str(self.id)).to_list()

        for i, child in enumerate(children):
            _child = child.dict()
            _child.update({
                "id": str(child.id),
                "children": await child.get_children()
            })
            children[i] = _child

        children.sort(key=lambda x: x["date"], reverse=True)
        return children

    def not_found(comment_id: str):
        raise HTTPException(
            status_code=404,
            detail=f"Comment with id '{comment_id}' does not exist"
        )



class DatasetStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    ANALYZING = "analyzing"
    DONE = "done"


class Submitter(TypedDict):
    name: str
    email: str


class Dataset(Document):
    acronym: str
    acronym_aliases: Optional[list[str]] = []
    title: Optional[str] = "Unknown"
    paper_title: Optional[str] = "Unknown"
    authors: Optional[list[str]] = ["Unknown"]
    description: Optional[str] = ""
    format: Optional[str] = ""
    doi: Optional[str] = ""
    origins_doi: Optional[str] =""
    submitter: Submitter
    date_submitted: Optional[datetime] = None
    status: DatasetStatus = DatasetStatus.REQUESTED
    tags: Optional[list[str]] = []
    filename: Optional[str | None] = None
    url: Optional[str | None] = None

    class Settings:
        name = "datasets"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "acronym": self.acronym,
            "acronym_aliases": sorted(self.acronym_aliases),
            "title": self.title,
            "paper_title": self.paper_title,
            "authors": self.authors,
            "description": self.description,
            "format": self.format,
            "doi": self.doi,
            "origins_doi": self.origins_doi,
            "date_submitted": self.date_submitted,
            "submitter": self.submitter,
            "status": self.status.value,
            "tags": self.tags,
            "filename": self.filename,
            "url": self.url,
            "analysis": self.get_analysis()
        }

    def get_name(self) -> str:
        return secure_filename(f"{self.acronym}.{'.'.join(sorted(self.acronym_aliases))}")

    def to_toml_dict(self) -> dict:
        toml_dict = self.to_dict()
        toml_dict['acronym_aliases'] = ", ".join(toml_dict['acronym_aliases'])
        toml_dict['authors'] = ", ".join(toml_dict['authors'])
        toml_dict['tags'] = ", ".join(toml_dict['tags'])
        toml_dict['submitter'] = f"{toml_dict['submitter']['name']} <{toml_dict['submitter']['email']}>"
        toml_dict.pop('id')
        toml_dict.pop('status')
        toml_dict.pop('analysis')
        return toml_dict

    def get_file_path(self) -> str | None:
        if self.filename is None:
            return None

        return os.path.join(config.DATASET_DIR, self.filename)

    def get_analysis_path(self) -> str:
        return os.path.join(config.ANALYSIS_DIR, self.get_name())

    def get_analysis(self) -> Optional['Analysis']:
        _path = os.path.join(self.get_analysis_path(), 'analysis.toml')

        if not os.path.exists(_path):
            return None
    
        return Analysis(_path)

    def update_analysis(self, old_path: str|None = None) -> None:
        if old_path is not None:
            # FIXME: what if this fails?
            os.rename(old_path, self.get_analysis_path())

        _analysis = self.get_analysis()
        if _analysis is None:
            self.create_analysis()
            return

        _analysis.analysis.update(self.to_toml_dict())

        _path = self.get_analysis_path()
        commented_lines = []
        with open(pathlib.Path(_path, 'analysis.toml'), 'r') as f:
            lines = f.readlines()
            commented_lines = [line for line in lines if line.startswith("#")]

        with open(pathlib.Path(_path, 'analysis.toml'), 'w') as f:
            toml.dump(_analysis.analysis, f)
            f.writelines(commented_lines)

        Thread(target=self._git_push).start()

    def create_analysis(self) -> None:
        # auth: glpat-N479bezbS7zPZsFnMMxL
        if not os.path.exists(config.ANALYSIS_DIR):
            try:
                os.mkdir(config.ANALYSIS_DIR)
            except OSError:
                print(f"Creation of the directory {config.ANALYSIS_DIR} failed: {str(exc)}")

        _path = self.get_analysis_path()
        if _path is None or os.path.exists(_path):
            return

        try:
            os.mkdir(_path)

            shutil.copy(
                pathlib.Path(config.ANALYSIS_DIR, 'analysis_example.toml'),
                pathlib.Path(_path, 'analysis.toml')
            )
        except OSError as exc:
            print(f"Creation of the directory {_path} failed: {str(exc)}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not create directory '{_path}': {str(exc)}"
            )

        self.update_analysis()

    def _git_push(self):
        try:
            git_repo = git.Repo(config.ANALYSIS_DIR)
            git_repo.index.add([self.get_name()])
            git_repo.index.commit(f"Add analysis for {self.get_name()}")
            git_repo.remotes.origin.pull()
            git_repo.remotes.origin.push().raise_if_error()
        except Exception as exc:
            print(f"Failed to push analysis for {self.acronym} to git: {str(exc)}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not push analysis to git: {str(exc)}"
            )

    def _git_edit_url(self):
        _edit = f"/-/edit/main/{self.get_name()}/analysis.toml?ref_type=heads"
        return f"{config.GIT_URL}{_edit}"
        #https://gitlab.com/tranquiloSan/katoda-test/-/edit/main/asdf/analysis.toml?ref_type=heads

    def not_found(acronym: str):
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with acronym '{acronym}' does not exist"
        )

class User(Document):
    email: Indexed(str, index_type=pymongo.TEXT, unique=True)
    password_hash: Optional[str]
    name: str
    surname: str
    created_at: datetime
    is_admin: bool = False

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def verify_password(self, password: str):
        return verify_password(password, self.password_hash)

    def to_dict(self):
        return {
            "email": self.email,
            "name": self.name,
            "surname": self.surname,
            "created_at": self.created_at,
            "is_admin": self.is_admin
        }

    def check_admin(self):
        if not self.is_admin:
            raise HTTPException(
                status_code=401,
                detail='Admin required!'
            )

    def not_found(email: str):
        raise HTTPException(
            status_code=404,
            detail=f"User with email '{email}' does not exist"
        )


class Analysis:  # pylint: disable=too-few-public-methods

    def __init__(self, file):
        self.path = os.path.abspath(os.path.dirname(file))
        self.dirname = os.path.split(self.path)[1]

        try:
            self.analysis = toml.load(file)
        except toml.decoder.TomlDecodeError as exc:
            print(f"Could not load analysis '{self.dirname}': {exc}")
            self.analysis = dict({'Analysis Error': {'Error Message': str(exc)}})
            
