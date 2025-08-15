"""Module to handle large file downloads in chunks via FastAPI with optional server-side compression."""

import logging
import mimetypes
import pathlib
import tempfile
from collections.abc import Generator
from http import HTTPStatus
from typing import Optional

from fastapi import Depends, Header, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import DirectoryPath, FilePath

from pyninja.executors import auth
from pyninja.features import certificates
from pyninja.modules import exceptions

LOGGER = logging.getLogger("uvicorn.default")
BEARER_AUTH = HTTPBearer()


async def get_certificate(
    request: Request,
    name: Optional[str] = None,
    raw: bool = False,
    apikey: HTTPAuthorizationCredentials = Depends(BEARER_AUTH),
):
    """API handler to download a large file or directory as a compressed archive.

    Args:
        - request: Reference to the FastAPI request object.
        - name: Name of the certificate to retrieve.
        - raw: If True, returns raw certificate data instead of parsed model.
        - apikey: API Key to authenticate the request.
    """
    await auth.level_1(request, apikey)
    cert_response = certificates.get_all_certificates()
    if cert_response.status_code == HTTPStatus.OK:
        raise exceptions.APIResponse(
            status_code=cert_response.status_code,
            detail=cert_response.certificates,
        )
    raise exceptions.APIResponse(
        status_code=cert_response.status_code,
        detail=cert_response.description,
    )
