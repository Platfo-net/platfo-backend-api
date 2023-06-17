from fastapi import HTTPException


def raise_http_exception(exception: dict, headers=None, logger=None):
    if logger:
        logger.info(
            "login_access_token_by_email",
            extra={
                "tags": {
                    "status_code": exception["status_code"],
                    "message": exception["text"],
                    "code": exception["code"],
                    "description": exception.get("description", None),
                }},
        )
    raise HTTPException(
        status_code=exception['status_code'],
        detail=exception['text'],
        headers=headers,
    )
