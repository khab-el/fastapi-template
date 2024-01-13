from sqladmin import ModelView
from sqlalchemy import orm

from src.app.entity import User


# # Create a registry to hold mapper details.
# mapper_registry = orm.registry()


# # Declare a class that will become an ORM model.
# class UserHelper:
#     pass


# mapper_registry.map_imperatively(UserHelper, User)
# mapper = orm.Mapper(User)s

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.phone, User.email]
