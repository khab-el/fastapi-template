from sqladmin import ModelView

from src.app.entity import ProviderEntity


class ProviderEntityAdmin(ModelView, model=ProviderEntity):
    can_create = True
    name_plural = "Provider Entities"
    column_list = [
        ProviderEntity.id,
        ProviderEntity.primary_phone,
        ProviderEntity.secondary_phone,
        ProviderEntity.provider_contact,
        ProviderEntity.created_at,
        ProviderEntity.deleted_at,
    ]

    form_excluded_columns = [
        ProviderEntity.created_at,
        ProviderEntity.updated_at,
        ProviderEntity.deleted_at,
    ]
