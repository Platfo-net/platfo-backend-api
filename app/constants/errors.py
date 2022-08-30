class Error:
    """
    Constants for the errors
    """
    USER_EXIST_ERROR = {
        "text": "There is a user with this email",
        "status_code": 409,
        "code": 1
    }
    PERMISSION_DENIED_ERROR = {
        "text": "Permission denied",
        "status_code": 401,
        "code": 2
    }
    USER_NOT_FOUND = {
        "text": "There is no user with this email",
        "status_code": 404,
        "code": 3
    }
    CODE_EXPIRATION_OR_NOT_EXIST_ERROR = {
        "text": "Wrong or expired code",
        "status_code": 404,
        "code": 4
    }
    USER_PASS_WRONG_ERROR = {
        "text": "Wrong username or password",
        "status_code": 401,
        "code": 5
    }
    TOKEN_NOT_EXIST_OR_EXPIRATION_ERROR = {
        "text": "Invalid token",
        "status_code": 403,
        "code": 6
    }
    INACTIVE_USER = {
        "text": "Inactive user",
        "status_code": 400,
        "code": 7
    }
    CONNECTION_NOT_FOUND = {
        "text": "Connection not found.",
        "status_code": 404,
        "code": 8
    }
    INVALID_CONNECTION_ID = {
        "text": "Invalid Connection Id.",
        "status_code": 404,
        "code": 9
    }
    PROBLEM_WITH_INSTAGRAM_CONNECTION = {
        "text": "problem with instagram connection.",
        "status_code": 400,
        "code": 10
    }
    INVALID_TRANSACTION_STATUS = {
        "text": "invalid transaction status.",
        "status_code": 400,
        "code": 11
    }
    NO_USER_WITH_THE_GIVEN_ID = {
        "text": "There is no user with the given id.",
        "status_code": 409,
        "code": 12
    }
    ACCOUNT_NOT_FOUND = {
        "text": "There is no account with the given id.",
        "status_code": 404,
        "code": 13
    }

    NO_CHATFLOW_WITH_THE_GIVEN_ID = {
        "text": "There is no chatflow with the given id.",
        "status_code": 409,
        "code": 14
    }
    NO_NODE_WITH_THE_GIVEN_ID = {
        "text": "There is no node with the given id.",
        "status_code": 404,
        "code": 15
    }
    NO_CHATFLOW_RELATED_TO_THIS_NODE = {
        "text": "There is no chatflow related to this node.",
        "status_code": 404,
        "code": 16
    }
    NO_NEXT_MOVE = {
        "text": "There is no next move.",
        "status_code": 404,
        "code": 17
    }
    NOT_AUTHENTICATED = {
        "text": "not authenticated.",
        "status_code": 401,
        "code": 18
    }
    NOT_AUTHORIZED = {
        "text": "not authorized.",
        "status_code": 401,
        "code": 19
    }
    ACCOUNT_NOT_FOUND_PERMISSION_DENIED = {
        "text": "There is no account with the given id.",
        "status_code": 404,
        "code": 20
    }

    # Notification errors

    NOTIFICATON_NOT_FOUND = {
        "text": "Notification not found",
        "status_code": 404,
        "code": 50
    }
    NOTIFICATION_ALREADY_READED = {
        "text": "Notification already readed",
        "status_code": 400,
        "code": 51
    }

    # Category errors

    CATEGORY_NOT_FOUND = {
        "text": "Category not found",
        "status_code": 404,
        "code": 60
    }

    # Content errors

    CONTENT_NOT_FOUND = {
        "text": "Content not found",
        "status_code": 404,
        "code": 70
    }
