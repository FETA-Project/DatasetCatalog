from datetime import datetime
from enum import Enum
import os
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

# from analysis import Analysis
from config import config
from utils import hash_password, verify_password


class DatasetStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    ANALYZING = "analyzing"
    DONE = "done"


class Submitter(TypedDict):
    name: str
    email: str


class Dataset(Document):
    acronym: Indexed(str, index_type=pymongo.TEXT, unique=True)
    title: Optional[str] = "Unknown"
    paper_title: Optional[str] = "Unknown"
    author: Optional[str] = "Unknown"
    description: Optional[str] = ""
    doi: Optional[str] = ""
    origins_doi: Optional[str] =""
    submitter: Submitter
    date_submitted: Optional[datetime] = None
    status: DatasetStatus = DatasetStatus.REQUESTED
    tags: Optional[list[str]] = []
    filename: Optional[str | None] = None

    class Settings:
        name = "datasets"

    def to_dict(self) -> dict:
        return {
            "acronym": self.acronym,
            "title": self.title,
            "paper_title": self.paper_title,
            "author": self.author,
            "description": self.description,
            "doi": self.doi,
            "origins_doi": self.origins_doi,
            "date_submitted": self.date_submitted,
            "submitter": self.submitter,
            "status": self.status.value,
            "tags": self.tags,
            "filename": self.filename,
        }

    def get_file_path(self) -> str | None:
        if self.filename is None:
            return None

        return os.path.join(config.DATASET_DIR, self.filename)

    def get_analysis_path(self) -> str:
        return os.path.join(config.ANALYSIS_DIR, secure_filename(self.acronym))

    def get_analysis(self) -> Optional['Analysis']:
        _path = os.path.join(self.get_analysis_path(), 'analysis.toml')

        if not os.path.exists(_path):
            return None
    
        return Analysis(_path)

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
            shutil.copy("analysis_example.toml", os.path.join(_path, "analysis.toml"))
        except OSError as exc:
            print(f"Creation of the directory {_path} failed: {str(exc)}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not create directory '{_path}': {str(exc)}"
            )

        try:
            self._git_push()
        except Exception as exc:
            print(f"Failed to push analysis for {self.acronym} to git: {str(exc)}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not push analysis to git: {str(exc)}"
            )

    def _git_push(self):
        git_repo = git.Repo(config.ANALYSIS_DIR)
        git_repo.index.add([secure_filename(self.acronym)])
        git_repo.index.commit(f"Add analysis for {self.acronym}")
        # TODO: pull/push in thread or something
        git_repo.remotes.origin.pull()
        git_repo.remotes.origin.push().raise_if_error()

    def _git_edit_url(self):
        _edit = f"/-/edit/main/{secure_filename(self.acronym)}/analysis.toml?ref_type=heads"
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

        self.analysis = toml.load(file)
