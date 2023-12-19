import logging
import traceback
from functools import wraps

from app import services, schemas
from app.db.session import SessionLocal


def monitored_task(fn):
    @wraps(fn)
    def wrap(*args, **kwargs):
        return_value = None
        logging.info(f"Started to run the {fn.__name__}")
        error = None
        stacktrace = None
        try:
            return_value = fn(*args, **kwargs)
        except Exception as e:
            stacktrace = traceback.format_exc()
            error = e
        is_successful = error is None
        db = SessionLocal()
        task_result_in = schemas.monitoring.TaskResultCreate(function_name=fn.__name__, stacktrace=stacktrace,
                                                             is_successful=is_successful)

        services.monitoring.task_result.create(
            db,
            obj_in=task_result_in
        )
        db.close()
        logging.info("Finished running => {name} with success={success}".format(
            name=fn.__name__, success=not bool(error)
        ))
        if stacktrace:
            logging.error(stacktrace)
        return return_value

    return wrap
