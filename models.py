from datetime import datetime
from enum import Enum
import os
import pathlib
import shutil
from threading import Thread
from typing import Any, Optional, Tuple
import git

import pymongo
from beanie import Document, Indexed
import tomlkit
import tomlkit.exceptions
from typing_extensions import TypedDict
from werkzeug.utils import secure_filename

from config import config
from exceptions import (
    CommentNotFound,
    DatasetNotFound,
    GitError,
    UserNotFound,
    AnalysisError,
    UserNotAdmin,
    CollectionNotFound,
)
from utils import ProgressPercentage


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
            _child.update({"id": str(child.id), "children": await child.get_children()})
            children[i] = _child

        children.sort(key=lambda x: x["date"], reverse=True)
        return children

    def not_found(comment_id: str):
        raise CommentNotFound(
            status_code=404, detail=f"Comment with id '{comment_id}' does not exist"
        )


class DatasetStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    ANALYZING = "analyzing"
    DONE = "done"


class AnalysisStatus(str, Enum):
    REQUESTED = "Requested"
    IN_PROGRESS = "In Progress"
    COMPLETES = "Completed"

    @classmethod
    def _missing_(self, _: Any):
        return self.REQUESTED


class Submitter(TypedDict):
    name: str
    email: str


class Dataset(Document):
    acronym: str
    versions: Optional[list[str]] = []
    title: Optional[str] = "Unknown"
    paper_title: Optional[str] = "Unknown"
    authors: Optional[list[str]] = ["Unknown"]
    description: Optional[str] = ""
    format: Optional[str] = ""
    doi: Optional[str] = ""
    origins_doi: Optional[str] = ""
    submitter: Submitter
    status: DatasetStatus = DatasetStatus.REQUESTED
    analysis_status: AnalysisStatus = AnalysisStatus.REQUESTED
    date_submitted: Optional[datetime] = None
    tags: Optional[list[str]] = []
    filename: Optional[str | None] = None
    url: Optional[str | None] = None
    label_name: Optional[str] = ""

    class Settings:
        name = "datasets"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "acronym": self.acronym,
            "versions": self.versions,
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
            "analysis_status": self.analysis_status.value,
            "tags": self.tags,
            "filename": self.filename,
            "url": self.url,
            "analysis": self.get_analysis(),
            "files": self.get_files(),
            "label_name": self.label_name,
        }

    @staticmethod
    def _is_sublist(a, b):
        for i in range(len(b) - len(a) + 1):
            if b[i : i + len(a)] == a:
                return True
        return False

    def is_parent(self, other):
        return self._is_sublist(self.versions, other.versions)

    def is_child(self, other):
        return self._is_sublist(other.versions, self.versions)

    def is_sibling(self, other):
        return other.versions[:-1] == (self.versions[:-1])

    async def get_version_related(
        self, is_parent: bool = True
    ) -> list[Tuple[str, str]]:
        if is_parent:
            if len(self.versions) != 0 and self.versions != [""]:
                return []

        return [
            {
                "acronym": dataset.acronym,
                "versions": [] if dataset.versions == [""] else dataset.versions,
                "analysis_status": dataset.analysis_status.value,
                "description": dataset.description,
                "title": dataset.title,
            }
            for dataset in await Dataset.find(
                Dataset.acronym == self.acronym, Dataset.versions != self.versions
            ).to_list()
        ]

    async def get_related(self) -> tuple[list["Dataset"], list["Dataset"]]:
        version_parents = []
        version_children = []
        version_siblings = []

        all_datasets = await Dataset.find().to_list()
        for d in all_datasets:
            if d.is_parent(self):
                version_parents.append(d)
            elif d.is_child(self):
                version_children.append(d)
            elif d.is_sibling(self):
                version_siblings.append(d)

        return {
            "version_parents": [
                {"acronym": d.acronym, "versions": d.versions}
                for d in version_parents
                if d.versions != self.versions
            ],
            "version_children": [
                {"acronym": d.acronym, "versions": d.versions}
                for d in version_children
                if d.versions != self.versions
            ],
            "version_siblings": [
                {"acronym": d.acronym, "versions": d.versions}
                for d in version_siblings
                if (d.versions != self.versions and d.acronym != self.acronym)
                and len(d.versions) > 1
            ],
        }

    def get_files(self) -> list[str]:
        if not os.path.exists(self.get_analysis_path()):
            return []

        files = []
        for file in pathlib.Path(self.get_analysis_path()).iterdir():
            if file.is_dir():
                continue
            elif file.name == "analysis.toml":
                continue
            elif file.suffix == ".ipynb":
                continue
            files.append(file.name)
        return files

    def get_name(self) -> str:
        if len(self.versions) == 0:
            return secure_filename(self.acronym)
        return secure_filename(f"{self.acronym}.{'.'.join(self.versions)}")

    def to_toml_dict(self) -> dict:
        toml_dict = self.to_dict()
        toml_dict["versions"] = ", ".join(toml_dict["versions"])
        toml_dict["authors"] = ", ".join(toml_dict["authors"])
        toml_dict["tags"] = ", ".join(toml_dict["tags"])
        toml_dict["submitter"] = (
            f"{toml_dict['submitter']['name']} <{toml_dict['submitter']['email']}>"
        )
        toml_dict.pop("id")
        toml_dict.pop("status")
        toml_dict.pop("analysis")

        # Change all None values to empty string for toml
        toml_dict = {k: ("" if v is None else v) for k, v in toml_dict.items()}
        return toml_dict

    def get_file_path(self) -> str | None:
        if self.filename is None:
            return None

        return os.path.join(config.DATASET_DIR, self.filename)

    def get_analysis_path(self) -> str:
        return os.path.join(config.ANALYSIS_DIR, self.get_name())

    def get_analysis(self) -> Optional["Analysis"]:
        _path = os.path.join(self.get_analysis_path(), "analysis.toml")

        if not os.path.exists(_path):
            # TODO: maybe create analysis?
            return Analysis()

        analysis = Analysis(_path)
        if analysis.error:
            Thread(target=self._git_push).start()

        return analysis

    def update_analysis(self, old_path: str | None = None) -> None:
        if old_path is not None:
            # FIXME: what if this fails?
            # TODO: check if rename causes to show error message in UI
            os.rename(old_path, self.get_analysis_path())

        _analysis = self.get_analysis()
        if _analysis is None:
            self.create_analysis()
            return

        _analysis.analysis.update(self.to_toml_dict())
        _path = self.get_analysis_path()

        commented_lines = []
        with open(pathlib.Path(_path, "analysis.toml"), "r") as f:
            lines = f.readlines()
            commented_lines = [line for line in lines if line.startswith("#")]

        with open(pathlib.Path(_path, "analysis.toml"), "w") as f:
            tomlkit.dump(_analysis.analysis, f)
            f.writelines(commented_lines)

        Thread(target=self._git_push).start()

    def create_analysis(self) -> None:
        # auth: glpat-N479bezbS7zPZsFnMMxL
        if not os.path.exists(config.ANALYSIS_DIR):
            try:
                os.mkdir(config.ANALYSIS_DIR)
            except OSError as exc:
                print(
                    f"Creation of the directory {config.ANALYSIS_DIR} failed: {str(exc)}"
                )

        _path = self.get_analysis_path()
        if _path is None or os.path.exists(_path):
            return

        try:
            os.mkdir(_path)

            shutil.copy(
                pathlib.Path(config.ANALYSIS_DIR, "analysis_example.toml"),
                pathlib.Path(_path, "analysis.toml"),
            )
        except OSError as exc:
            print(f"Creation of the directory {_path} failed: {str(exc)}")
            raise AnalysisError(
                status_code=500,
                detail=f"Could not create directory '{_path}': {str(exc)}",
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
            raise GitError(
                status_code=500, detail=f"Could not push analysis to git: {str(exc)}"
            )

    def _git_edit_url(self):
        _edit = f"/-/edit/main/{self.get_name()}/analysis.toml?ref_type=heads"
        return f"{config.GIT_URL}{_edit}"

    def not_found(acronym: str, versions: list[str] = []):
        name = acronym if len(versions) == 0 else f"{acronym}.({'.'.join(versions)})"
        raise DatasetNotFound(
            status_code=404, detail=f"Dataset '{name}' does not exist"
        )


class User(Document):
    email: str
    name: str
    surname: str
    created_at: datetime
    is_admin: bool = False

    def to_dict(self):
        return {
            "email": self.email,
            "name": self.name,
            "surname": self.surname,
            "created_at": self.created_at,
            "is_admin": self.is_admin,
        }

    def check_admin(self):
        if not self.is_admin:
            raise UserNotAdmin(status_code=401, detail="Admin required!")

    def not_found(email: str):
        raise UserNotFound(
            status_code=404, detail=f"User with email '{email}' does not exist"
        )


class CollectionTool(Document):
    name: Indexed(str, index_type=pymongo.TEXT, unique=True)
    url: Optional[str] = ""
    description: Optional[str] = ""
    known_issues: Optional[str] = ""

    def not_found(name: str):
        raise CollectionNotFound(
            status_code=404, detail=f"Collection tool '{name}' does not exist"
        )


class Analysis:  # pylint: disable=too-few-public-methods
    def __init__(self, file=None):
        if file is None:
            self.path = ""
            self.dirname = ""
            self.error = True
            self.analysis = {
                "Analysis Error": {"Message": "No analysis.toml file found"}
            }
            return

        self.path = os.path.abspath(os.path.dirname(file))
        self.dirname = os.path.split(self.path)[1]
        self.error = False

        if not os.path.exists(self.path):
            self.analysis = {
                "Analysis Error": {"Message": "No analysis.toml file found"}
            }
            return

        _file = pathlib.Path(self.path, "analysis.toml")
        try:
            with open(_file, "rb") as f:
                self.analysis = tomlkit.load(f)
        except tomlkit.exceptions.ParseError as exc:
            print(f"Could not load analysis '{self.dirname}': {exc}")
            self.error = True
            _lines = open(_file, "r").readlines()
            with open(_file, "w") as f:
                for line in _lines:
                    if not line.startswith("#"):
                        line = f"### {line}"
                    f.write(line)
                f.write("\n")
                tomlkit.dump(
                    {
                        "Analysis Error": {
                            "Message": str(exc),
                            "Attention": "Original lines will be commented out (###) in the analysis.toml file",
                        }
                    },
                    f,
                )
