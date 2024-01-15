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

    form_columns = [
        ProviderEnity.address,
        ProviderEnity.primary_phone,
        ProviderEnity.secondary_phone,
        ProviderEnity.lat,
        ProviderEnity.lon,
        ProviderEnity.provider_contact_id,
        ProviderEnity.provider_contact,
        ProviderEnity.service,
    ]
