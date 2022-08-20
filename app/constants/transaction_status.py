class TransactionStatus:
    """
    Constants for the transaction status
    """
    PENDING = {
        "name": "pending",
        "value": "Pending"
    }
    FAILED = {
        "name": "failed",
        "value": "Failed"
    }
    SUCCESS = {
        "name": "success",
        "value": "Success"
    }

    VALID_STATUS = [SUCCESS["value"], FAILED["value"], PENDING["value"]]
