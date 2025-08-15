from netbox.plugins import PluginMenuButton, PluginMenuItem#, PluginMenu
from netbox.choices import ButtonColorChoices

veritysource_buttons = [
    PluginMenuButton(
        link='plugins:verity_import:veritysource_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]

veritysourcelogin_buttons = [
    PluginMenuButton(
        link='plugins:verity_import:veritysourcelogin_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]


menu_items = (
    PluginMenuItem(
        link='plugins:verity_import:veritysource_list',
        link_text='Controllers',
        buttons=veritysource_buttons
    ),
    PluginMenuItem(
        link='plugins:verity_import:veritysourcelogin_list',
        link_text='Credentials',
        buttons=veritysourcelogin_buttons
    ),
    PluginMenuItem(
        link='plugins:verity_import:veritylastsynctime_list',
        link_text='Status'
    ),
)

# menu = PluginMenu(
#     label="Verity Import",
#     groups=(("Verity Import", _menu_items),),
#     icon_class="mdi mdi-bootstrap",
# )
