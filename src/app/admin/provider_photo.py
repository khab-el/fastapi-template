from sqladmin import ModelView

from src.app.entity import ProviderPhoto


class ProviderPhotoAdmin(ModelView, model=ProviderPhoto):
    can_create = True
    column_list = [
        ProviderPhoto.id,
        ProviderPhoto.picture_path,
        ProviderPhoto.provider_contact,
    ]

    form_columns = [
        ProviderPhoto.picture_path,
        ProviderPhoto.provider_contact_id,
        ProviderPhoto.provider_contact,
    ]
