from typing import Any

import inflect
from sqlalchemy.orm import declarative_base

p = inflect.engine()

Base = declarative_base()
