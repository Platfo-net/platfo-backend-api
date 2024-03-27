class BaseService:
    def __init__(self, repository) -> None:
        self._repository = repository

    def get(self, pk: int):
        return self._repository.get_by_id(pk)

    def get_by_uuid(self, uuid: int):
        return self._repository.get_by_uuid(uuid)

    def get_list(self, schema):
        return self._repository.get_multi(schema)

    def add(self, schema):
        return self._repository.create(schema)

    def update(self, db_obj, schema):
        return self._repository.update(db_obj, schema)

    def remove(self, pk: int):
        return self._repository.delete(pk)
