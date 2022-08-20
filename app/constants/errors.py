class Error:
    """
    Constants for the errors
    """
    USER_EXIST_ERROR = {
        "text": "کاربری با این ایمیل در سیستم موجود است.",
        "status_code": 409,
        "code": 1
    }
    PERMISSION_DENIED_ERROR = {
        "text": "خطای دسترسی",
        "status_code": 401,
        "code": 2
    }
    USER_NOT_FOUND = {
        "text": "کاربری با این ایمیل در سیستم وجود ندارد.",
        "status_code": 404,
        "code": 3
    }
    CODE_EXPIRATION_OR_NOT_EXIST_ERROR = {
        "text": "کد اشتباه است یا منقضی شده است.",
        "status_code": 404,
        "code": 4
    }
    USER_PASS_WRONG_ERROR = {
        "text": "نام کاربری یا رمز عبور اشتباه است.",
        "status_code": 401,
        "code": 5
    }
    TOKEN_NOT_EXIST_OR_EXPIRATION_ERROR = {
        "text": "توکن منقضی شده است یا وجود ندارد.",
        "status_code": 403,
        "code": 6
    }
    INACTIVE_USER = {
        "text": "کاربر غیر فعال است.",
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
