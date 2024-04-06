from app.llms.utils.exceptions import AuthError, NotFoundError


class ObjectValidator:

    def __init__(self, repository):
        self.repository = repository

    def validate_exists(self, uuid):
        obj = self.repository.get_by_uuid(uuid)
        if not obj:
            raise NotFoundError(detail=f"{type(obj).__name__} not found")
        return obj

    def validate_generic_exists(self, uuid, model):
        obj = self.repository.session.query(model).filter(model.uuid == uuid).first()
        if not obj:
            raise NotFoundError(detail=f"{type(obj).__name__} not found")
        return obj

    def validate_user_ownership(self, obj, current_user):
        if obj.user_id != current_user.id:
            raise AuthError(detail=f"Unauthorized ownership {type(obj).__name__}")
