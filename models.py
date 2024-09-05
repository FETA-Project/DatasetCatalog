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
    acronym: Indexed(str, index_type=pymongo.TEXT, unique=True)
    acronym_aliases: Optional[list[str]] = []
    title: Optional[str] = "Unknown"
    paper_title: Optional[str] = "Unknown"
    authors: Optional[list[str]] = ["Unknown"]
    description: Optional[str] = ""
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
            "acronym": self.acronym,
            "acronym_aliases": self.acronym_aliases,
            "title": self.title,
            "paper_title": self.paper_title,
            "authors": self.authors,
            "description": self.description,
            "doi": self.doi,
            "origins_doi": self.origins_doi,
            "date_submitted": self.date_submitted,
            "submitter": self.submitter,
            "status": self.status.value,
            "tags": self.tags,
            "filename": self.filename,
            "url": self.url
        }
    
    def new_analysis_dict(self) -> dict:
        toml_dict = self.to_dict()
        toml_dict['acronym_aliases'] = ", ".join(toml_dict['acronym_aliases'])
        toml_dict['authors'] = ", ".join(toml_dict['authors'])
        toml_dict['tags'] = ", ".join(toml_dict['tags'])
        toml_dict['submitter'] = f"{toml_dict['submitter']['name']} <{toml_dict['submitter']['email']}>"
        return toml_dict

    def new_analysis_example(self) -> str:
        return \
"""
# [generic_info]
# data_collection_year = "2022"
# data_collection_tool = "CICFlowMeter-V3"
# feature_extraction_tool = "CICFlowMeter-V3"
# classes = 80
# features = 80
# known_issues = \"\"\"
# Dataset is affected by issues described in: https://intrusion-detection.distrinet-research.be/WTMC2021/extended_doc.html
# Wrong feature name: Unnamed: 0
# Network features contains raw ip addresses and ports which are not ideal
# Unstandard csv headers format (leading space)
# \"\"\"
# dataset_organization = \"\"\"
# - e.g. per day
# - e.g. Each class per file
# Notes
# \"\"\"
# per_class_data = \"\"\"
# {"Apple iTunes": 926,
#  "Google Authentication": 872,
#  "SUKL eRecept": 800,
#  "Xiaomi Account API": 710,
#  "Kaspersky": 700,
#  "Redmine (CESNET, MFF UK, KIV ZCU)": 682}
# \"\"\"

# [dataset_analysis]
# drift_workflow = "name_of_jupyter_notebook.ipynb"
# drift_manual = "name_of_jupyter_notebook.ipynb"
# redundancy = \"\"\"
# ...
# \"\"\"
"""

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

            with open(os.path.join(_path, "analysis.toml"), "w") as f:
                toml.dump(self.new_analysis_dict(), f)
                f.write(self.new_analysis_example())
        except OSError as exc:
            print(f"Creation of the directory {_path} failed: {str(exc)}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not create directory '{_path}': {str(exc)}"
            )

        Thread(target=self._git_push).start()

    def _git_push(self):
        try:
            git_repo = git.Repo(config.ANALYSIS_DIR)
            git_repo.index.add([secure_filename(self.acronym)])
            git_repo.index.commit(f"Add analysis for {self.acronym}")
            git_repo.remotes.origin.pull()
            git_repo.remotes.origin.push().raise_if_error()
        except Exception as exc:
            print(f"Failed to push analysis for {self.acronym} to git: {str(exc)}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not push analysis to git: {str(exc)}"
            )

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

        try:
            self.analysis = toml.load(file)
        except toml.decoder.TomlDecodeError as exc:
            print(f"Could not load analysis '{self.dirname}': {exc}")
            self.analysis = dict({'Analysis Error': {'Error Message': str(exc)}})
            
