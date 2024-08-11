import argparse
from datetime import datetime
import subprocess

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import api
from auth import auth
from config import config
from database import init_db
from models import User
from update_db_from_csv import update_db_from_csv


app = FastAPI()

origins = [
    config.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api)
app.include_router(auth)

def test_ndvm():
    from ndvm_api import NDVM_API
    ndvm_api = NDVM_API()

    from models import Dataset, Config, CSVConfig, Submitter, DatasetType
    testDataset = Dataset(
        title="test",
        description="test",
        doi="test",
        submitter=Submitter(name='test', surname='test', email='test'),
        dataset_type=DatasetType.CSV,
        config=Config(
            csv_config=CSVConfig(
                classes=2,
                multiclass=False,
                sampling_limit=5000,
                delimiter=',',
                delete_nan=True,
                delete_duplicated=True,
                label_name="",
            ),
            redundancy_config=None,
            association_config=None,
            similarity=None,
        ),
        dataset_path = "/usr/local/bin/NDVM/ndvm/sample_dataset/combined-doh-http.csv",
    )

    ndvm_api.create_report(testDataset, 'test-config')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', type=str)
    return parser.parse_args()

@app.on_event("startup")
async def start_db():
    await init_db()

    admin = await User.find(User.is_admin == True).first_or_none()
    if admin is None:
        print("No admin user found, creating default (admin:admin)")
        admin = User(
            email="admin",
            name="admin",
            surname="admin",
            created_at=datetime.utcnow(),
            is_admin=True,
        )
        admin.set_password('admin')
        await admin.save()

    csv = parse_args().csv
    if csv:
        print(f"Found --csv flag, importing data from CSV '{csv}'")
        await update_db_from_csv(csv)

    # test_ndvm()

app.mount("/", StaticFiles(directory=config.STATIC_DIR, html=True))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
