def ok_response(message: str = ""):
    """
    Returns a 200 OK response with an optional message.
    """
    return {"message": message} if message else None
