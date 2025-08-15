from netbox.plugins import PluginConfig


class VerityImportConfig(PluginConfig):
    name = 'verity_import'
    verbose_name = 'Verity'
    description = 'Import a Verity system into Netbox'
    version = '1.0.1'
    base_url = 'verity-import'


config = VerityImportConfig