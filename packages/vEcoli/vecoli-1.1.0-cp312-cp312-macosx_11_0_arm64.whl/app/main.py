"""
- base sim (cached)
- antibiotic
- biomanufacturing
- batch variant endpoint
- design specific endpoints.
- downsampling ...
- biocyc id
- api to download the data
- marimo instead of Jupyter notebooks....(auth). ... also on gov cloud.
- endpoint to send sql like queries to parquet files back to client

# TODO: mount nfs driver for local dev
# TODO: add more routers, ie; antibiotics, etc

"""
import csv
import io
import logging
import os
from pathlib import Path

import marimo
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette import templating
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

logger = logging.getLogger(__name__)


APP_VERSION = "0.0.1"
APP_TITLE = "sms-api"
APP_ORIGINS = [
    "http://0.0.0.0:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8888",
    "http://127.0.0.1:4200",
    "http://127.0.0.1:4201",
    "http://127.0.0.1:4202",
    "http://localhost:4200",
    "http://localhost:4201",
    "http://localhost:4202",
    "http://localhost:8888",
    "http://localhost:8000",
    "http://localhost:3001",
    "https://sms.cam.uchc.edu",
]


app = FastAPI(
    title=APP_TITLE, 
    version=APP_VERSION
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
def root():
    return {"name": APP_TITLE}


# getOutputsPath(expId)
# fileresponse

@app.get("/download-tsv")
def download_tsv():
    return FileResponse(
        path="path/to/your_file.tsv",
        media_type="text/tab-separated-values",
        filename="your_file.tsv"
    )


@app.get("/export-tsv")
def export_tsv(data):
    # Simulated data
    # data = [
    #     {"id": 1, "name": "Alice", "score": 95},
    #     {"id": 2, "name": "Bob", "score": 88},
    # ]

    # Create a TSV in memory
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=data[0].keys(), delimiter='\t')
    writer.writeheader()
    writer.writerows(data)
    buffer.seek(0)

    # Return TSV as a downloadable file
    return StreamingResponse(
        buffer,
        media_type="text/tab-separated-values",
        headers={
            "Content-Disposition": "attachment; filename=results.tsv"
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="auto")  # noqa: S104 binding to all interfaces
    logger.info("API Gateway Server started")
