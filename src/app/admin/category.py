from sqladmin import ModelView

from src.app.entity import Category


class CategoryAdmin(ModelView, model=Category):
    can_create = True
    column_list = [
        Category.id,
        Category.category_title,
        Category.parent_category,
        Category.service,
    ]

    form_columns = [
        Category.category_title,
        Category.category_description,
        Category.parent_category_id,
        Category.parent_category,
        Category.service,
    ]
