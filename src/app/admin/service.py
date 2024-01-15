from sqladmin import ModelView

from src.app.entity import Service


class ServiceAdmin(ModelView, model=Service):
    can_create = True
    column_list = [
        Service.id,
        Service.name,
        Service.category,
        Service.created_at,
        Service.deleted_at,
    ]

    form_excluded_columns = [
        Service.created_at,
        Service.updated_at,
        Service.deleted_at,
    ]
