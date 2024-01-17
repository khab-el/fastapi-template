from sqladmin import ModelView

from src.app.entity import Category


class CategoryAdmin(ModelView, model=Category):
    can_create = True
    name_plural = "Categories"
    column_list = [
        Category.id,
        Category.category_title,
        Category.parent_category,
        Category.service,
    ]

    form_excluded_columns = [
        Category.created_at,
        Category.updated_at,
        Category.deleted_at,
    ]

    form_ajax_refs = {
        "parent_category": {
            "fields": ("id", "category_title"),
            "order_by": "id",
        },
        "service": {
            "fields": ("id", "name"),
            "order_by": "id",
        },
    }

    column_labels = {Category.service: "Service"}
