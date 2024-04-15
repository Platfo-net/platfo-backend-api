from app.llms.utils.validators import ObjectValidator


class BaseService:
    def __init__(self, repository) -> None:
        self._repository = repository
        self.session = repository.session
        self.validator = ObjectValidator(self._repository)

    def get(self, pk):
        return self._repository.get_by_id(pk)

    def get_by_uuid(self, uuid):
        return self._repository.get_by_uuid(uuid)

    def get_list(self):
        return self._repository.get_multi()

    def get_list_by_user_id(self, user_id):
        return self._repository.get_multi_by_user_id(user_id)

    def add(self, schema):
        return self._repository.create(schema)

    def add_atomic(self, schema):
        return self._repository.create_atomic(schema)

    def update(self, db_obj, schema):
        return self._repository.update(db_obj, schema)

    def remove(self, pk):
        return self._repository.delete(pk)
