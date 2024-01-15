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
    #     user = User(**data)
    #     user.save(request.state.db_session, user)
    #     return await super().insert_model(request, data)
