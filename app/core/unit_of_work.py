from sqlalchemy.orm import Session


class UnitOfWork:
    def __init__(self, db: Session):
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._rollback()
        else:
            self._commit()

    def _commit(self):
        self.db.commit()

    def _rollback(self):
        self.db.rollback()

    def add(self, item):
        self.db.add(item)

    def delete(self, item):
        self.db.delete(item)

    def add_all(self, items):
        self.db.add_all(items)

    def query(self, *args, **kwargs):
        return self.db.query(*args, **kwargs)
