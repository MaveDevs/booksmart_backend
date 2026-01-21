from sqladmin import ModelView

class UserAdmin(ModelView, model=None): 
    column_list = ["id", "email", "is_active"]
    icon = "fa-solid fa-user"
