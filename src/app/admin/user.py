from sqladmin import ModelView

from src.app.entity import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.phone, User.email]
