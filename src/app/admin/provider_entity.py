from sqladmin import ModelView

from src.app.entity import ProviderEnity


class ProviderEnityAdmin(ModelView, model=ProviderEnity):
    can_create = True
    column_list = [
        ProviderEnity.id,
        ProviderEnity.primary_phone,
        ProviderEnity.secondary_phone,
        ProviderEnity.provider_contact,
        ProviderEnity.created_at,
        ProviderEnity.deleted_at,
    ]

    form_excluded_columns = [
        ProviderEnity.created_at,
        ProviderEnity.updated_at,
        ProviderEnity.deleted_at,
    ]
