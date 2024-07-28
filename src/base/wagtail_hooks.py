from wagtail import hooks
from wagtail.admin.menu import MenuItem

@hooks.register("register_admin_menu_item")
def register_site_menu_item():
    return MenuItem(
        "Go back to site", "/?_=cms", icon_name='home', order=0,
    )