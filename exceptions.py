from fastapi import HTTPException


class DatasetNotFound(HTTPException):
    pass


class GitError(HTTPException):
    pass


class CollectionNotFound(HTTPException):
    pass


class AnalysisError(HTTPException):
    pass


class CommentNotFound(HTTPException):
    pass


class UserNotFound(HTTPException):
    pass


class UserNotAdmin(HTTPException):
    pass
