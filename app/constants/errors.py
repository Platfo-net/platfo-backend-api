class Error:
    """
    Constants for the errors
    """

    UNEXPECTED_ERROR = {
        'text': 'Unexcpected error happen during the action.',
        'status_code': 500,
        'code': 0,
        'description': "",
    }
    USER_EXIST_ERROR = {
        'text': 'There is a user with this email or phone number',
        'status_code': 400,
        'code': 1,
        'description': "",
    }

    PERMISSION_DENIED_ERROR = {
        'text': 'Permission denied',
        'status_code': 401,
        'code': 2,
    }
    USER_NOT_FOUND = {
        'text': 'There is no user with this email',
        'status_code': 404,
        'code': 3,
    }
    USER_NOT_FOUND_BY_PHONE = {
        'text': 'There is no user with this phone',
        'status_code': 404,
        'code': 20,
    }
    CODE_EXPIRATION_OR_NOT_EXIST_ERROR = {
        'text': 'Wrong or expired code',
        'status_code': 404,
        'code': 4,
    }
    USER_PASS_WRONG_ERROR = {
        'text': 'Wrong username or password',
        'status_code': 401,
        'code': 5,
    }
    TOKEN_NOT_EXIST_OR_EXPIRATION_ERROR = {
        'text': 'Invalid token',
        'status_code': 403,
        'code': 6,
    }
    INACTIVE_USER = {'text': 'Inactive user', 'status_code': 400, 'code': 7}
    CONNECTION_NOT_FOUND = {
        'text': 'Connection not found.',
        'status_code': 404,
        'code': 8,
    }
    INVALID_CONNECTION_ID = {
        'text': 'Invalid Connection Id.',
        'status_code': 404,
        'code': 9,
    }
    PROBLEM_WITH_INSTAGRAM_CONNECTION = {
        'text': 'problem with instagram connection.',
        'status_code': 400,
        'code': 10,
    }
    INVALID_TRANSACTION_STATUS = {
        'text': 'invalid transaction status.',
        'status_code': 400,
        'code': 11,
    }
    NO_USER_WITH_THE_GIVEN_ID = {
        'text': 'There is no user with the given id.',
        'status_code': 409,
        'code': 12,
    }
    ACCOUNT_NOT_FOUND = {
        'text': 'There is no account with the given id.',
        'status_code': 404,
        'code': 13,
    }
    INVALID_CODE_OR_TOKEN = {
        'text': 'Invalid code or token',
        'status_code': 400,
        'code': 14,
    }

    ACTIVATION_CODE_HAVE_BEEN_ALREADY_SENT = {
        'text': 'Activation code has been already sent to you.',
        'status_code': 400,
        'code': 15,
    }
    RESET_PASSWORD_CODE_HAVE_BEEN_ALREADY_SENT = {
        'text': 'Reset password code has been already sent to you.',
        'status_code': 400,
        'code': 16,
    }
    NOT_ACCEPTABLE_PASSWORD = {
        'text': 'Your password is not acceptable',
        'status_code': 400,
        'code': 17,
    }
    USER_IS_ACTIVE = {
        'text': 'User is active',
        'status_code': 400,
        'code': 18,
    }
    EMAIL_NOT_VERIFIED = {
        'text': 'Email not verified',
        'status_code': 400,
        'code': 19,
    }

    NO_CHATFLOW_WITH_THE_GIVEN_ID = {
        'text': 'There is no chatflow with the given id.',
        'status_code': 404,
        'code': 31,
    }
    NO_NODE_WITH_THE_GIVEN_ID = {
        'text': 'There is no node with the given id.',
        'status_code': 404,
        'code': 32,
    }
    NO_CHATFLOW_RELATED_TO_THIS_NODE = {
        'text': 'There is no chatflow related to this node.',
        'status_code': 404,
        'code': 33,
    }
    NO_NEXT_MOVE = {'text': 'There is no next move.', 'status_code': 404, 'code': 34}
    NOT_AUTHENTICATED = {'text': 'not authenticated.', 'status_code': 401, 'code': 35}
    NOT_AUTHORIZED = {'text': 'not authorized.', 'status_code': 401, 'code': 36}
    ACCOUNT_NOT_FOUND_PERMISSION_DENIED = {
        'text': 'There is no account with the given id.',
        'status_code': 404,
        'code': 20,
    }

    # Notification errors

    NOTIFICATON_NOT_FOUND = {
        'text': 'Notification not found',
        'status_code': 404,
        'code': 50,
    }
    NOTIFICATION_ALREADY_READED = {
        'text': 'Notification already readed',
        'status_code': 400,
        'code': 51,
    }

    # Category errors

    CATEGORY_NOT_FOUND = {'text': 'Category not found', 'status_code': 404, 'code': 60}

    # Content errors

    CONTENT_NOT_FOUND = {'text': 'Content not found', 'status_code': 404, 'code': 70}

    CONNECTION_EXIST = {
        'text': 'Connection already exist.',
        'status_code': 400,
        'code': 80,
    }
    INVALID_DETAILS = {'text': 'Invalid Detail', 'status_code': 400, 'code': 81}
    INVALID_FIELDS_OPERATORS = {
        'text': 'Invalid fields or operators',
        'status_code': 400,
        'code': 90,
    }

    LEAD_NOT_FOUND = {
        'text': 'Lead not found!',
        'status_code': 404,
        'code': 91,
    }

    CAMPAIGN_NOT_FOUND = {
        'text': 'Campaign not found!',
        'status_code': 404,
        'code': 92,
    }

    CAMPAIGN_NOT_FOUND_ACCESS_DENIED = {
        'text': 'Campaign not found!',
        'status_code': 404,
        'code': 93,
    }

    CAMPAIGN_ALREADY_ACTIVE = {
        'text': 'Campaign already activated!',
        'status_code': 400,
        'code': 93,
    }
    DRAFT_CAMPAIGN_DOESNT_HAVE_CONTACT = {
        'text': 'Draft campaign doesnt have contacts.',
        'status_code': 400,
        'code': 94,
    }

    LEADS_DO_NOT_BELONGS_TO_THIS_PAGE = {
        'text': 'Leads do not belong to this page',
        'status_code': 400,
        'code': 104,
    }

    PLAN_NOT_FOUND = {
        'text': 'Plan not found!',
        'status_code': 404,
        'code': 120,
    }
    PLAN_NOT_ACTIVE = {
        'text': 'Plan not active!',
        'status_code': 404,
        'code': 120,
    }

    INVOICE_NOT_FOUND = {
        'text': 'Invoice not found!',
        'status_code': 404,
        'code': 130,
    }

    INVOICE_CANNOT_DELETE_STATUS_FAILED = {
        'text': 'Failed invoices cannot be deleted!',
        'status_code': 400,
        'code': 131,
    }

    INVOICE_CANNOT_DELETE_STATUS_SUCCESS = {
        'text': 'SUCCEED invoices cannot be deleted!',
        'status_code': 400,
        'code': 132,
    }

    INVALID_TIMEFRAME = {
        'text': 'Invalid Timeframe',
        'status_code': 400,
        'code': 140,
    }

    # telegram bot errors

    INVALID_TELEGRAM_BOT = {
        "text": "Invalid telegram bot",
        "status_code": 400,
        "code": 150,
    }

    TELEGRAM_BOT_EXIST_IN_SYSTEM = {
        "text": "This bot has been already added to this system",
        "status_code": 400,
        "code": 151,
    }

    TELEGRAM_SERVER_SET_WEBHOOK_ERROR = {
        "text": "There is some problems with server, please try again later!",
        "status_code": 400,
        "code": 152,
    }
    TELEGRAM_BOT_NOT_FOUNT = {
        "text": "Bot not found.",
        "status_code": 404,
        "code": 153,
    }
    TELEGRAM_BOT_NOT_FOUNT_ACCESS_DENIED = {
        "text": "Bot not found.",
        "status_code": 404,
        "code": 154,
    }

    # ------------

    # shop errors

    SHOP_CATEGORY_NOT_FOUND_ERROR = {
        "text": "Category not found",
        "status_code": 404,
        "code": 160,
    }

    SHOP_PRODUCT_NOT_FOUND_ERROR = {
        "text": "Category not found",
        "status_code": 404,
        "code": 161,
    }

    SHOP_SHOP_NOT_FOUND_ERROR = {
        "text": "Shop not found",
        "status_code": 404,
        "code": 162,
    }

    SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR = {
        "text": "Shop not found",
        "status_code": 404,
        "code": 163,
    }

    SHOP_SHOP_HAS_BEEN_ALREADY_CONNECTED_TO_SUPPORT_ACCOUNT = {
        "text": "Shop has been already connected to support account",
        "status_code": 400,
        "code": 164,
    }

    SHOP_SHOP_IS_EXIST = {
        "text": "There is another shop with the same title.",
        "status_code": 400,
        "code": 165,
    }

    SHOP_INVALID_SUPPORT_TOKEN = {
        "text": "Invalid support token.",
        "status_code": 400,
        "code": 166,
    }
    SHOP_SHOP_HAS_BEEN_ALREADY_CONNECTED_TO_TELEGRAM_BOT = {
        "text": "Shop has been already connected to telegram bot",
        "status_code": 400,
        "code": 167,
    }

    SHOP_CATEGORY_NOT_FOUND_ERROR_ACCESS_DENIED = {
        "text": "Category not found",
        "status_code": 404,
        "code": 168,
    }

    SHOP_PRODUCT_NOT_FOUND_ERROR_ACCESS_DENIED = {
        "text": "Category not found",
        "status_code": 404,
        "code": 169,
    }

    SHOP_CATEGORY_NOT_FOUND_IN_THIS_SHOP = {
        "text": "Category not found in this shop",
        "status_code": 404,
        "code": 170,
    }

    SHOP_CATEGORY_OR_SHOP_NOT_PROVIDED = {
        "text": "category and shop not provided. You should provide at least one of them.",
        "status_code": 400,
        "code": 171,
    }

    SHOP_ORDER_NOT_FOUND = {
        "text": "Order not found.",
        "status_code": 404,
        "code": 172,
    }

    # lead
    LEAD_TELEGRAM_LEAD_NOT_FOUND = {
        "text": "Lead not found",
        "status_code": 404,
        "code": 190,
    }
    LEAD_TELEGRAM_LEAD_NOT_FOUND_ACCESS_DENIED = {
        "text": "Lead not found",
        "status_code": 404,
        "code": 191,
    }
