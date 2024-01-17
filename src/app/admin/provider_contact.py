from sqladmin import ModelView

from src.app.entity import ProviderContact


class ProviderContactAdmin(ModelView, model=ProviderContact):
    can_create = True
    column_list = [
        ProviderContact.id,
        ProviderContact.name,
        ProviderContact.phone,
        ProviderContact.email,
        ProviderContact.created_at,
        ProviderContact.deleted_at,
    ]

    form_excluded_columns = [
        ProviderContact.created_at,
        ProviderContact.updated_at,
        ProviderContact.deleted_at,
    ]
