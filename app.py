import argparse
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import api
from auth import auth
from config import config
from database import init_db
from models import User
from s3_client import s3

app = FastAPI(
    openapi="3.0.2",
    openapi_url="/docs/openapi.json",
    docs_url='/docs',
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
app.include_router(auth)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-s3', action='store_true', help='for testing')
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


    # test_ndvm()

app.mount("/", StaticFiles(directory=config.STATIC_DIR, html=True))

if __name__ == "__main__":
    s3.prepare_s3(parse_args().no_s3)
    uvicorn.run(app, host="0.0.0.0", port=8000)
    s3.cleanup_s3()
