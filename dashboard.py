from collections import OrderedDict
from functools import wraps
import json
from typing import Any
import requests
from fastapi import APIRouter, FastAPI, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import doi as pydoi
from pymongo.errors import DuplicateKeyError

from models import (
    Dataset,
    DatasetStatus
)
import uvicorn

import pandas as pd

import ndvm.metric1
import ndvm.metric2
import ndvm.metric3

def disabled(status_code: int = 405, content: str = 'Sorry, function is not enabled at this time.'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> JSONResponse:
            return JSONResponse(status_code=status_code, content=content)

        return wrapper

    return decorator

STATIC_DIR = "frontend/dist"
UPLOAD_DIR = "upload"

app = FastAPI()
api = APIRouter(prefix="/api")

def eval_metrics(dataset, label):
    # Basic info
    samples = []
    df_dataset = pd.read_csv(dataset, delimiter=",")
    classes = len(df_dataset[label].value_counts())
    for item in df_dataset[label].value_counts():
        samples.append(item)
    features = len(df_dataset.drop(columns=[label]).columns)
    duplicated = df_dataset[df_dataset.drop(columns=[label]).duplicated()].shape[0]

    # advanced metrics
    print("Running Metric 1 - Redundancy ...")
    redundancy = ndvm.metric1.redundancy(df_dataset, label)
    # print("Running Metric 2 - Association ...")
    # association = ndvm.metric2.label_association(df_dataset, label)
    # print("Running Metric 3 - Class Similarity ...")
    # similarity = ndvm.metric3.class_similarity(df_dataset, df_dataset.drop(columns=[label]).columns, label)

    report = OrderedDict(
        {
            "Classes": classes,
            "Samples": samples,
            "Features": features,
            "Duplicated Flows": duplicated,
            "Redundancy": redundancy,
            # "Association": association,
            # "Similarity": similarity,
        }
    )

    return report


@api.get('/requests')
async def get_requests():
    datasets = [ 
        Dataset.from_dict(ds).to_dict()
        for ds in Dataset.collection().find(
            {"status": DatasetStatus.REQUESTED.value}
        )
    ]
    return datasets


@api.post('/requests')
async def upload(
    title: str = Form(...),
    description: str = Form(""),
    doi: str = Form(...),
    requester_name: str = Form(...),
    requester_email: str = Form(...),
    tags: str = Form(...),
    # file: UploadFile = File(...)
    ):
    # filename = f'{secure_filename(name)}{Path(file.filename).suffix}'
    # with open(f"{UPLOAD_DIR}/{filename}", "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)

    # dataset = Dataset(name, description, f"{UPLOAD_DIR}/{filename}")

    # clean_doi = pydoi.find_doi_in_text(doi)
    # if clean_doi:
    #     doi = clean_doi

    try:
        repo = pydoi.validate_doi(doi)
        repo = doi
        response = requests.get(repo+"?download")
        if response.status_code == 200:
            print(response)
            metadata = response.json()
    except ValueError:
        metadata = "Could not load metadata"

    dataset = Dataset(
        title=title,
        description=description,
        doi=doi,
        requester_name=requester_name,
        requester_email=requester_email,
        metadata=metadata,
        tags=tags.split(","),
    )
    # report = eval_metrics(dataset.location, "is_doh")
    # dataset.report = report
    try:
        Dataset.collection().insert_one(dataset.to_dict())
    except DuplicateKeyError:
        raise HTTPException(
        status_code=401,
        detail=f"Request with title '{title}' exists"
    )

    return {"message": f"{title} requested for analysis"}


@api.head('/requests/{title}')
@disabled()
async def request_accept(title: str):
    print(title)
    ds = Dataset.from_dict(Dataset.collection().find_one({"title": title}))
    print(ds.to_dict())
    Dataset.collection().update_one(
        {"title": title, "status": DatasetStatus.REQUESTED.value},
        { "$set": {"status": DatasetStatus.ACCEPTED.value} }
    )
    # TODO: change requested to analyzing
    return {"message": f"Request for {title} accepted"}


@api.delete('/requests/{title}')
async def request_reject(title: str):
    result = Dataset.collection().delete_one({"title": title, "status": DatasetStatus.REQUESTED.value})
    print(result.deleted_count)
    return {"message": f"Request for {title} rejected"}


@api.get('/datasets')
async def datasets():
    datasets = [ 
        Dataset.from_dict(ds).to_dict()
        for ds in Dataset.collection().find(
            {"status": {"$ne": DatasetStatus.REQUESTED.value}}
        )
    ]
    return datasets


@api.get('/datasets/{title}')
async def dataset(title: str):
    print(title)
    dataset = Dataset.from_dict(
        Dataset.collection().find_one({"title": title})
    )
    return dataset.to_dict()


@api.delete('/datasets/{title}')
@disabled()
async def delete(title: str):
    result = Dataset.collection().delete_one({"title": title})
    print(result.deleted_count)
    return {"message": f"Dataset {title} deleted"}


@api.get('/metrics')
@disabled()
async def metrics():
    dataset = Dataset(
        name="Combined DOH HTTP",
        description="Combined DOH HTTP dataset",
        location="upload/combined-doh-http-reduced.csv",
    )
    df_dataset = dataset.location
    df_dataset = pd.read_csv(df_dataset, delimiter=",")
    report = eval_metrics(df_dataset, "is_doh")
    dataset.report = report
    return dataset.to_dict()


app.include_router(api)
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
