
from core.models import models_list


class MyDBRouter(object):

    def db_for_read(self, model, **hints):
        if model in models_list:
            return "platfo"
        return None

    def db_for_write(self, model, **hints):
        if model in models_list:
            return "platfo"
        return None
    
