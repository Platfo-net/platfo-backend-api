from fastapi import HTTPException


def raise_http_exception(exception: dict):
    raise HTTPException(
        status_code=exception["status_code"],
        detail=exception["text"],
    )
