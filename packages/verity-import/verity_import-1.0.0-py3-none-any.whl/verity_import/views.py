
import requests
from datetime import datetime
from netbox.views import generic
from django.views.generic import View
from django.shortcuts import render
from django.http import JsonResponse
from django.utils.text import slugify
from ipam.models import VLAN, RIR, ASN, IPAddress, VRF
from extras.models import Tag
try:
    from netbox_bgp.models import BGPSession
    PLUGIN_AVAILABLE = True
except Exception:
    PLUGIN_AVAILABLE = False
from tenancy.models import Tenant
from . import filtersets, forms, models, tables


VERITY_TAG_NAME = 'VerityTag'


class VeritySourceView(generic.ObjectView):
    queryset = models.VeritySource.objects.all()


class VeritySourceListView(generic.ObjectListView):
    queryset = models.VeritySource.objects.all()
    table = tables.VeritySourceTable


class VeritySourceEditView(generic.ObjectEditView):
    queryset = models.VeritySource.objects.all()
    form = forms.VeritySourceForm


class VeritySourceDeleteView(generic.ObjectDeleteView):
    queryset = models.VeritySource.objects.all()


class VeritySourceLoginView(generic.ObjectView):
    queryset = models.VeritySourceLogin.objects.all()


class VeritySourceLoginListView(generic.ObjectListView):
    queryset = models.VeritySourceLogin.objects.all()
    table = tables.VeritySourceLoginTable
    filterset = filtersets.VeritySourceLoginFilterSet
    filterset_form = forms.VeritySourceLoginFilterForm


class VeritySourceLoginEditView(generic.ObjectEditView):
    queryset = models.VeritySourceLogin.objects.all()
    form = forms.VeritySourceLoginForm


class VeritySourceLoginDeleteView(generic.ObjectDeleteView):
    queryset = models.VeritySourceLogin.objects.all()


class VerityLastSyncTimeListView(generic.ObjectListView):
    queryset = models.VerityLastSyncTime.objects.all()
    table = tables.VerityLastSyncTimeTable


class VeritySyncView(View):

    def vnetc_login(self, address, credentials):
        resp = requests.post(f'{address}api/auth', json=credentials)
        if not resp.ok:
            raise Exception("Unable to log in into vNetC")
        data = resp.json()
        return data.get('token')

    def get_vnetc_config(self, address, credentials):
        token = self.vnetc_login(address, credentials)

        if token is None:
            raise Exception("Weird...no token in successful login response...")
        response = requests.get(f'{address}api/config/', headers={'Cookie': f'ivn_api={token}'})
        if not response.ok:
            raise Exception(f"Unable to retrieve vNetC's configuration: {response.text}")
        return response.json()

    def service_to_vlan(self, vnetc_services):
        for service_name, service in vnetc_services.items():
            if service["vlan"] is not None:
                vlan = VLAN(
                    vid=service["vlan"],
                    name=service_name
                )
                if service["tenant"] is not None:
                    tenant = Tenant.objects.get(name=service["tenant"])
                    if tenant is None:
                        raise Exception(f'Tenant {service["tenant"]} referenced by service {service_name} does not exist in Netbox')
                    vlan.tenant = tenant
                vlan.save()
                vlan.tags.add(VERITY_TAG_NAME)
                vlan.save()

    def tenant_to_tenant_and_vrf(self, vnetc_tenants):
        for tenant_name, tenant in vnetc_tenants.items():
            tenant_netbox = Tenant(
                name=tenant_name,
                slug=slugify(tenant_name)
            )
            tenant_netbox.save()
            tenant_netbox.tags.add(VERITY_TAG_NAME)
            tenant_netbox.save()
            vrf = VRF(
                name=tenant["vrf_name"],
                tenant=tenant_netbox
            )
            vrf.save()
            vrf.tags.add(VERITY_TAG_NAME)
            vrf.save()

    def find_switchpoint_from_gateway_name(self, gateway_name, vnetc_config):
        # Check if any gateway_profile references this gateway
        gp = None
        for gateway_profile_name, gateway_profile in vnetc_config["gateway_profile"].items():
            for external_gateway in gateway_profile["external_gateways"]:
                if external_gateway["gateway"] == gateway_name:
                    gp = gateway_profile_name
                    break
        if gp is None:
            raise Exception(f'Verity system is not fully configured! Gateway {gateway_name} is not referenced by any gateway profile!')
        # Check if any bundle references the gateway_profile we found in previous step
        b = None
        for bundle_name, bundle in vnetc_config["endpoint_bundle"].items():
            for eth_port_path in bundle["eth_port_paths"]:
                if eth_port_path["eth_port_num_gateway_profile"] == gp:
                    b = bundle_name
                    break
        if b is None:
            raise Exception(f'Verity system is not fully configured! Gateway profile {gp} is not referenced by any bundle!')
        # Check if any switchpoint references the bundle we found in previous step
        for switchpoint in vnetc_config["switchpoint"].values():
            if switchpoint["connected_bundle"] == b:
                return switchpoint
        raise Exception(f'Verity system is not fully configured! Bundle {b} is not referenced by any switchpoint!')

    def get_or_create_asn(self, as_number):
        try:
            asn = ASN.objects.get(asn=as_number)
        except ASN.DoesNotExist:
            rir = RIR.objects.get(name="VerityRIR")
            if rir is None:
                raise Exception('RIR VerityRIR not available in Netbox!')
            asn = ASN(
                asn=as_number,
                rir=rir
            )
            asn.save()
            asn.tags.add(VERITY_TAG_NAME)
            asn.save()
        return asn

    def get_or_create_ip_address(self, ip_address):
        try:
            ip = IPAddress.objects.get(address=ip_address)
        except IPAddress.DoesNotExist:
            ip = IPAddress(
                address=ip_address
            )
            ip.save()
            ip.tags.add(VERITY_TAG_NAME)
            ip.save()
        return ip

    def get_session_params(self, gateway, vnetc_config):
        params = {}

        if gateway["source_ip_address"]:
            params["local_address"] = self.get_or_create_ip_address(gateway["source_ip_address"])
        else:
            try:
                switchpoint = self.find_switchpoint_from_gateway_name(gateway['name'], vnetc_config)
                params["local_address"] = self.get_or_create_ip_address(switchpoint["switch_router_id_ip_mask"])
            except Exception:
                return None

        if gateway["neighbor_ip_address"]:
            params["remote_address"] = self.get_or_create_ip_address(gateway["neighbor_ip_address"])
        else:
            return None

        if gateway["local_as_number"]:
            params["local_as"] = self.get_or_create_asn(gateway["local_as_number"])
        else:
            try:
                switchpoint = self.find_switchpoint_from_gateway_name(gateway['name'], vnetc_config)
                params["local_as"] = self.get_or_create_asn(switchpoint["bgp_as_number"])
            except Exception:
                return None

        if gateway["neighbor_as_number"]:
            params["remote_as"] = self.get_or_create_asn(gateway["neighbor_as_number"])
        else:
            return None

        if gateway["tenant"]:
            tenant = Tenant.objects.get(name=gateway["tenant"])
            if tenant is None:
                return None
            params["tenant"] = tenant
        params["name"] = gateway['name']
        return params

    def gateway_to_session(self, gateways, vnetc_config):
        for gateway in gateways:
            params = self.get_session_params(gateway, vnetc_config)
            if params is None:
                continue
            session = BGPSession(**params)
            session.save()
            session.tags.add(VERITY_TAG_NAME)
            session.save()

    def get_netbox_config(self):
        verity_tag = Tag.objects.get(name=VERITY_TAG_NAME)
        if verity_tag is None:
            verity_tag = Tag(name=VERITY_TAG_NAME)
            verity_tag.save()
        sessions = BGPSession.objects.filter(tags=verity_tag)
        vlans = VLAN.objects.filter(tags=verity_tag)
        asns = ASN.objects.filter(tags=verity_tag)
        rirs = RIR.objects.filter(tags=verity_tag)
        ip_addresses = IPAddress.objects.filter(tags=verity_tag)
        vrfs = VRF.objects.filter(tags=verity_tag)
        tenants = Tenant.objects.filter(tags=verity_tag)
        return {
            "sessions": sessions,
            "vlans": vlans,
            "asns": asns,
            "rirs": rirs,
            "ip_addresses": ip_addresses,
            "vrfs": vrfs,
            "tenants": tenants
        }

    def compare_services(self, vnetc_services, netbox_vlans):
        for service_name, service in vnetc_services.items():
            if service["vlan"] is not None:
                try:
                    netbox_vlan = netbox_vlans.get(name=service_name)
                except:
                    netbox_vlan = None
                if netbox_vlan is None:
                    vlan = VLAN(
                        vid=service["vlan"],
                        name=service_name
                    )
                    if service["tenant"] is not None:
                        try:
                            tenant = Tenant.objects.get(name=service["tenant"])
                        except:
                            tenant = None
                        if tenant is None:
                            tenant = Tenant(
                                name=service["tenant"],
                                slug=slugify(service["tenant"])
                            )
                            tenant.save()
                            tenant.tags.add(VERITY_TAG_NAME)
                            tenant.save()
                        vlan.tenant = tenant
                    vlan.save()
                    vlan.tags.add(VERITY_TAG_NAME)
                    vlan.save()
                else:
                    # If it already exists check for any field change
                    if netbox_vlan.vid != service["vlan"]:
                        netbox_vlan.vid = service["vlan"]
                    if service["tenant"]:
                        try:
                            tenant = Tenant.objects.get(name=service["tenant"])
                        except:
                            tenant = None
                        if tenant is None:
                            tenant = Tenant(
                                name=service["tenant"],
                                slug=slugify(service["tenant"])
                            )
                            tenant.save()
                            tenant.tags.add(VERITY_TAG_NAME)
                            tenant.save()
                        netbox_vlan.tenant = tenant
                    else:
                        netbox_vlan.tenant = None
                    netbox_vlan.save()
        # Check objects that have to be deleted because not in the vNetC anymore
        for vlan in netbox_vlans:
            if vlan.name not in vnetc_services:
                vlan.delete()

    def compare_vrfs(self, vnetc_tenants, netbox_vrfs):
        for tenant_name, tenant in vnetc_tenants.items():
            try:
                netbox_vrf = netbox_vrfs.get(name=tenant["vrf_name"])
            except:
                netbox_vrf = None
            if netbox_vrf is None:
                try:
                    tenant_tmp = Tenant.objects.get(name=tenant_name)
                except:
                    tenant_tmp = None
                if tenant_tmp is None:
                    tenant_tmp = Tenant(
                        name=tenant_name,
                        slug=slugify(tenant_name)
                    )
                    tenant_tmp.save()
                    tenant_tmp.tags.add(VERITY_TAG_NAME)
                    tenant_tmp.save()
                vrf = VRF(
                    name=tenant["vrf_name"],
                    tenant=tenant_tmp
                )
                vrf.save()
                vrf.tags.add(VERITY_TAG_NAME)
                vrf.save()
            else:
                try:
                    tenant_tmp = Tenant.objects.get(name=tenant_name)
                except:
                    tenant_tmp = None
                if tenant_tmp is None:
                    tenant_tmp = Tenant(
                        name=tenant_name,
                        slug=slugify(tenant_name)
                    )
                    tenant_tmp.save()
                    tenant_tmp.tags.add(VERITY_TAG_NAME)
                    tenant_tmp.save()
                netbox_vrf.tenant = tenant_tmp
                netbox_vrf.save()
        # Check objects that have to be deleted because not in the vNetC anymore
        available_vnetc_vrfs = set(map(lambda x: x["vrf_name"], vnetc_tenants.values()))
        for vrf in netbox_vrfs:
            if vrf.name not in available_vnetc_vrfs:
                # In Verity a tenant is a vrf, so if the vrf is not in verity anymore we should delete the tenant as
                # well but given that the tenant could be referenced by other objects in netbox, we need to take care
                # of it at the very end
                vrf.delete()

    def compare_sessions(self, vnetc_gateways, netbox_sessions, vnetc_config):
        for gateway_name, gateway in vnetc_gateways.items():
            try:
                netbox_session = netbox_sessions.get(name=gateway_name)
            except:
                netbox_session = None
            if netbox_session is None:
                self.gateway_to_session([gateway], vnetc_config)
            else:
                # The session already exists, check for different fields
                params_new = self.get_session_params(gateway, vnetc_config)
                if params_new is not None:
                    if params_new["tenant"] is None:
                        tenant_tmp = Tenant(
                            name=gateway["tenant"],
                            slug=slugify(gateway["tenant"])
                        )
                        tenant_tmp.save()
                        tenant_tmp.tags.add(VERITY_TAG_NAME)
                        tenant_tmp.save()
                    netbox_session.tenant = tenant_tmp
                    if params_new["local_address"] != netbox_session.local_address:
                        netbox_session.local_address = params_new["local_address"]
                    if params_new["remote_address"] != netbox_session.remote_address:
                        netbox_session.remote_address = params_new["remote_address"]
                    if params_new["local_as"] != netbox_session.local_as:
                        netbox_session.local_as = params_new["local_as"]
                    if params_new["remote_as"] != netbox_session.remote_as:
                        netbox_session.remote_as = params_new["remote_as"]
                    netbox_session.save()
                else:
                    # The change that happened on the system, can't be reproduced on NetBox, so the object will be
                    # deleted
                    netbox_session.delete()
        # Check objects that have to be deleted because not in the vNetC anymore
        for netbox_session in netbox_sessions:
            if netbox_session.name not in vnetc_gateways:
                netbox_session.delete()

    def compare_tenants(self, vnetc_tenants, netbox_tenants):
        for tenant_name in vnetc_tenants.keys():
            try:
                netbox_tenant = netbox_tenants.get(name=tenant_name)
            except:
                netbox_tenant = None
            if netbox_tenant is None:
                tenant_tmp = Tenant(
                    name=tenant_name,
                    slug=slugify(tenant_name)
                )
                tenant_tmp.save()
                tenant_tmp.tags.add(VERITY_TAG_NAME)
                tenant_tmp.save()
            # If the tenant already exists we do nothing given that we care about the name only, which was the search
            # key
        # Check objects that have to be deleted because not in the vNetC anymore
        for tenant in netbox_tenants:
            if tenant.name not in vnetc_tenants:
                tenant.delete()

    def compare_ip_addresses(self, netbox_ip_addresses):
        # Let's grab the new sessions
        # At this point we know the tag has already been created
        new_sessions = BGPSession.objects.filter(tags=Tag.objects.get(name=VERITY_TAG_NAME))
        for netbox_ip_address in netbox_ip_addresses:
            found = False
            for session in new_sessions:
                if session.local_address == netbox_ip_address or session.remote_address == netbox_ip_address:
                    found = True
                    break
            if not found:
                # The ip address is not referenced by any session, delete it
                netbox_ip_address.delete()

    def compare_asns(self, netbox_asns):
        # Let's grab the new sessions
        # At this point we know the tag has already been created
        new_sessions = BGPSession.objects.filter(tags=Tag.objects.get(name=VERITY_TAG_NAME))
        for netbox_asn in netbox_asns:
            found = False
            for session in new_sessions:
                if session.local_as == netbox_asn or session.remote_as == netbox_asn:
                    found = True
                    break
            if not found:
                # The asn is not referenced by any session, delete it
                netbox_asn.delete()

    def compare_config(self, vnetc_config, netbox_config):
        # Let's compare first things that are not referenced by any object type
        # VLANs, VRFs and sessions
        self.compare_services(vnetc_config["service"], netbox_config["vlans"])
        self.compare_vrfs(vnetc_config["tenant"], netbox_config["vrfs"])
        # Needs to be tested on a system with fully configured gateways
        self.compare_sessions(vnetc_config["gateway"], netbox_config["sessions"], vnetc_config)

        # Now tenants, that should be deleted, should not be referenced anywhere
        # Tenants that are supposed to be created have already been created if referenced in the new config
        # We need to create the one that are not referenced anywhere
        self.compare_tenants(vnetc_config["tenant"], netbox_config["tenants"])

        # Given that verity tagged ip addresses and asns are created for gateways only
        # the new ones that needed to be created, had already been created,
        # so we just need to remove the ones that are not referenced anymore
        self.compare_ip_addresses(netbox_config["ip_addresses"])
        self.compare_asns(netbox_config["asns"])

    def post(self, request):

        vnetc = request.POST.get("vnetc")
        username = request.POST.get("username")
        password = request.POST.get("password")

        context = {
            'success': False,
            'message': None
        }

        if PLUGIN_AVAILABLE:
            try:
                vnetc_config = self.get_vnetc_config(
                    vnetc,
                    {
                        "auth": {
                            "username": username,
                            "password": password
                        }
                    }
                )

                if "gateway" not in vnetc_config or "tenant" not in vnetc_config:
                    raise Exception("Verity plugin supports datacenter systems only!")

                self.compare_config(vnetc_config, self.get_netbox_config())

                models.VerityLastSyncTime(
                    timestamp=datetime.now(),
                    verity_source=models.VeritySource.objects.get(verity_url=vnetc)
                ).save()

                context["success"] = True
                context["message"] = "Import successfull!"
            except Exception as e:
                context["success"] = False
                context["message"] = f"Import failed: {e}"
        else:
            context["success"] = False
            context["message"] = "Import failed: Netbox BGP plugin is not installed!"

        return render(request, 'verity_import/sync_result.html', context)
