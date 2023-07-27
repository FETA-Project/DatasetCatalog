from enum import Enum
from pymongo import MongoClient
from pymongo.collection import Collection

_client = MongoClient('localhost', 27017)
_db = _client.dashboard

_datasets = _db.datasets
_datasets.create_index('title', unique=True)


class DatasetStatus(Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    ANALYZING = "analyzing"
    DONE = "done"


class Dataset():
    def __init__(
            self,
            title,
            description,
            doi,
            requester_name,
            requester_email,
            date=None,
            origins_doi=[],
            status=DatasetStatus.REQUESTED,
            metadata="",
            tags=[],
            location=None,
            report = {}
        ):
        self.title = title
        self.description = description
        self.doi = doi
        self.origins_doi = origins_doi
        self.date = date
        self.requester_name = requester_name
        self.requester_email = requester_email
        self.status = status
        self.metadata = metadata
        self.tags = tags
        self.location = location
        self.report = report

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "doi": self.doi,
            "origins_doi": self.origins_doi,
            "date": self.date,
            "requester": {
                "name": self.requester_name,
                "email": self.requester_email
            },
            "status": self.status.value,
            "metadata": self.metadata,
            "tags": self.tags,
            "location": self.location,
            "report": self.report
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data.get("title"),
            description=data.get("description"),
            doi=data.get("doi"),
            origins_doi=data.get("origins_doi"),
            date=data.get("date"),
            requester_name=data.get("requester").get("name"),
            requester_email=data.get("requester").get("email"),
            status=DatasetStatus(data.get("status")),
            metadata=data.get("metadata"),
            tags=data.get("tags"),
            location=data.get("location"),
            report=data.get("report")
        )

    @staticmethod
    def collection() -> Collection:
        return _datasets