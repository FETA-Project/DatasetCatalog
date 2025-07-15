import argparse
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import api
from config import config
from database import init_db
from models import User
from s3_client import s3

VERSION = "0.0.7"

app = FastAPI(
    openapi="3.0.2",
    openapi_url="/docs/openapi.json",
    docs_url="/docs",
)

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dev", action="store_true", help="for testing (running as admin)"
    )
    parser.add_argument(
        "--dev-user", action="store_true", help="for testing (running as test user)"
    )
    return parser.parse_args()


@app.on_event("startup")
async def start_db():
    await init_db()

    if config.DEV:
        print("Using dev config, setting up admin and test users")
        _admin = await User.find(User.email == "admin").first_or_none()
        if _admin is None:
            admin = User(
                email="admin",
                name="admin",
                surname="admin",
                created_at=datetime.utcnow(),
                is_admin=True,
            )
            await admin.save()

        _test = await User.find(User.email == "test").first_or_none()
        if _test is None:
            test_user = User(
                email="test",
                name="",
                surname="",
                created_at=datetime.utcnow(),
                is_admin=False,
            )
            await test_user.save()

    # test_ndvm()


app.mount("/", StaticFiles(directory=config.STATIC_DIR, html=True))

if __name__ == "__main__":
    args = parse_args()
    config.DEV = args.dev or args.dev_user
    config.DEV_USER = "admin" if args.dev else "test"
    s3.prepare_s3(no_s3=config.DEV)
    uvicorn.run(app, host="0.0.0.0", port=8000)
    s3.cleanup_s3()
