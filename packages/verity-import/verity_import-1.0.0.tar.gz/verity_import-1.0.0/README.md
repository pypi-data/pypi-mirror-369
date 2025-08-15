# Verity Netbox Plugin

## Verity

Verity is a multivendor network automation platform that automates the provisioning and operation of  data center and campus enterprise networks.

Verity simplifies the management of Open Networking and SONiC hardware platforms through an intent-based design system, allowing operators to program their network using high level abstractions common in the public cloud.

Verity is delivered as 2-3 virtual machines containing isolated application containers.  Future versions of Verity will support installation on k8s via Helm.

## Overview

This plugin supports one was synchronization of configuration objects between Verity and NetBox.  Objects created in Verity (via GUI or API) will appear in the Netbox system.  Changes to Verity objects in Netbox will be overwritten automatically.  This implies that configuration for Verity is currently limited to Verity itself.  Future versions of this plugin may support bi-directional syncronization of objects/intent.

This plugin communicates directly to the Verity REST API v2.x (OAS 3.0) via HTTPS.

## NetBox Compatibility

| Netbox Version | Plugin Version |
| -------------- | -------------- |
| 4.3.4 <        | 1.0            |
| 4.3.4 >=       | >1.0           |

## Screenshots

Coming soon.

## Documentation

Full documentation for this plugin can be found at [Verity Docs](https://docs.be-net.com).

### Controllers

Controllers URL must be the full address, including 'http://' or 'https://' at the beginning and a '/' at the end.

## Installation

Our plugin depends on [this](https://github.com/netbox-community/netbox-bgp) other plugin, so install it first, then:

```bash
source /opt/netbox/venv/bin/activate
pip install verity-import
```

Enable the plugin in **/opt/netbox/netbox/netbox/configuration.py**:

```python
PLUGINS = ['verity_import']
```

Run the following commands to make sure NetBox data schema is up to date, always in the same virtual environment:

```bash
python3 /opt/netbox/netbox/manage.py migrate
python3 /opt/netbox/netbox/manage.py collectstatic
```

Restart NetBox:

`
sudo systemctl restart netbox netbox-rq
`

In case the previous command does not work, reboot the machine.
