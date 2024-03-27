from app.llms.utils.validators import ObjectValidator


class BaseService:
    def __init__(self, repository) -> None:
        self._repository = repository
        self.validator = ObjectValidator(self._repository)

    def get(self, pk):
        return self._repository.get_by_id(pk)

    def get_by_uuid(self, uuid):
        return self._repository.get_by_uuid(uuid)

    def get_list(self, skip, limit):
        return self._repository.get_multi(skip, limit)

    def add(self, schema):
        return self._repository.create(schema)

    def update(self, db_obj, schema):
        return self._repository.update(db_obj, schema)

    def remove(self, pk):
        return self._repository.delete(pk)
