class SearchOperator:
    GT = {"name": "GT", "description": "Greater than"}

    GTE = {"name": "GTE", "description": "Greater than or equal to"}

    LT = {"name": "LT", "description": "Less than"}

    LTE = {"name": "LTE", "description": "Less than or equal to"}

    EQ = {"name": "EQ", "description": "Equal to"}

    NEQ = {"name": "NEQ", "description": "Not equal to"}

    items = [GT["name"], GTE["name"], LT["name"], LTE["name"], EQ["name"], NEQ["name"]]
