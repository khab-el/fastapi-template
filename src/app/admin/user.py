from sqladmin import ModelView

from src.app.entity import User


class UserAdmin(ModelView, model=User):
    can_create = True
    column_list = [User.id, User.username, User.phone, User.email]
    form_excluded_columns = [
        User.created_at,
        User.updated_at,
        User.deleted_at,
    ]

    # async def insert_model(self, request, data):
    #     from src.app.modules import AsyncDBClient
    #     user = User(**data)
    #     db_session = await anext(AsyncDBClient.get_db_session())
    #     return await user.save(db_session)
