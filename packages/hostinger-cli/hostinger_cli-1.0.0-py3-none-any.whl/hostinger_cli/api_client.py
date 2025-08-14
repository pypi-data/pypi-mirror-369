"""
Hostinger API Client
"""

import requests
import json
from typing import Dict, Any, Optional, List
import click


class HostingerAPIClient:
    """Client for interacting with the Hostinger API"""

    BASE_URL = "https://developers.hostinger.com"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def _make_request(self,
                      method: str,
                      endpoint: str,
                      data: Optional[Dict] = None,
                      params: Optional[Dict] = None) -> Dict[str,
                                                             Any]:
        """Make a request to the Hostinger API"""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, json=data, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise click.ClickException("❌ Unauthorized: Invalid API key")
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    errors = error_data.get('errors', {})
                    if errors:
                        error_msg = "\n".join(
                            [f"  {field}: {', '.join(msgs)}"
                             for field, msgs in errors.items()])
                        raise click.ClickException(
                            f"❌ Validation Error:\n{error_msg}")
                    else:
                        raise click.ClickException(
                            f"❌ Validation Error: {
                                error_data.get(
                                    'message', str(e))}")
                except json.JSONDecodeError:
                    raise click.ClickException(f"❌ Validation Error: {str(e)}")
            else:
                try:
                    error_data = response.json()
                    raise click.ClickException(
                        f"❌ API Error: {
                            error_data.get(
                                'message', str(e))}")
                except json.JSONDecodeError:
                    raise click.ClickException(f"❌ API Error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise click.ClickException(f"❌ Network Error: {str(e)}")

    # Billing endpoints
    def get_catalog_items(
            self,
            category: Optional[str] = None,
            name: Optional[str] = None) -> List[Dict]:
        """Get catalog items"""
        params = {}
        if category:
            params['category'] = category
        if name:
            params['name'] = name
        return self._make_request(
            'GET', '/api/billing/v1/catalog', params=params)

    def get_payment_methods(self) -> List[Dict]:
        """Get payment methods"""
        return self._make_request('GET', '/api/billing/v1/payment-methods')

    def set_default_payment_method(self, payment_method_id: int) -> Dict:
        """Set default payment method"""
        return self._make_request(
            'POST', f'/api/billing/v1/payment-methods/{payment_method_id}')

    def delete_payment_method(self, payment_method_id: int) -> Dict:
        """Delete payment method"""
        return self._make_request(
            'DELETE', f'/api/billing/v1/payment-methods/{payment_method_id}')

    def get_subscriptions(self) -> List[Dict]:
        """Get subscriptions"""
        return self._make_request('GET', '/api/billing/v1/subscriptions')

    def cancel_subscription(
            self,
            subscription_id: str,
            reason_code: str = "other",
            cancel_option: str = "immediately") -> Dict:
        """Cancel subscription"""
        data = {
            'reason_code': reason_code,
            'cancel_option': cancel_option
        }
        return self._make_request(
            'DELETE',
            f'/api/billing/v1/subscriptions/{subscription_id}',
            data=data)

    # DNS endpoints
    def get_dns_records(self, domain: str) -> List[Dict]:
        """Get DNS records for domain"""
        return self._make_request('GET', f'/api/dns/v1/zones/{domain}')

    def update_dns_records(
            self,
            domain: str,
            zone: List[Dict],
            overwrite: bool = True) -> Dict:
        """Update DNS records for domain"""
        data = {
            'overwrite': overwrite,
            'zone': zone
        }
        return self._make_request(
            'PUT', f'/api/dns/v1/zones/{domain}', data=data)

    def delete_dns_records(self, domain: str, filters: List[Dict]) -> Dict:
        """Delete DNS records for domain"""
        data = {'filters': filters}
        return self._make_request(
            'DELETE', f'/api/dns/v1/zones/{domain}', data=data)

    def reset_dns_records(
            self,
            domain: str,
            sync: bool = True,
            reset_email_records: bool = True,
            whitelisted_record_types: Optional[List[str]] = None) -> Dict:
        """Reset DNS records to default"""
        data = {
            'sync': sync,
            'reset_email_records': reset_email_records
        }
        if whitelisted_record_types:
            data['whitelisted_record_types'] = whitelisted_record_types
        return self._make_request(
            'POST', f'/api/dns/v1/zones/{domain}/reset', data=data)

    def validate_dns_records(
            self,
            domain: str,
            zone: List[Dict],
            overwrite: bool = True) -> Dict:
        """Validate DNS records"""
        data = {
            'overwrite': overwrite,
            'zone': zone
        }
        return self._make_request(
            'POST', f'/api/dns/v1/zones/{domain}/validate', data=data)

    def get_dns_snapshots(self, domain: str) -> List[Dict]:
        """Get DNS snapshots"""
        return self._make_request('GET', f'/api/dns/v1/snapshots/{domain}')

    def get_dns_snapshot(self, domain: str, snapshot_id: int) -> Dict:
        """Get specific DNS snapshot"""
        return self._make_request(
            'GET', f'/api/dns/v1/snapshots/{domain}/{snapshot_id}')

    def restore_dns_snapshot(self, domain: str, snapshot_id: int) -> Dict:
        """Restore DNS snapshot"""
        return self._make_request(
            'POST', f'/api/dns/v1/snapshots/{domain}/{snapshot_id}/restore')

    # Domain endpoints
    def check_domain_availability(
            self,
            domain: str,
            tlds: List[str],
            with_alternatives: bool = False) -> List[Dict]:
        """Check domain availability"""
        data = {
            'domain': domain,
            'tlds': tlds,
            'with_alternatives': with_alternatives
        }
        return self._make_request(
            'POST', '/api/domains/v1/availability', data=data)

    def get_domains(self) -> List[Dict]:
        """Get domain list"""
        return self._make_request('GET', '/api/domains/v1/portfolio')

    def get_domain_details(self, domain: str) -> Dict:
        """Get domain details"""
        return self._make_request('GET', f'/api/domains/v1/portfolio/{domain}')

    def purchase_domain(self,
                        domain: str,
                        item_id: str,
                        payment_method_id: Optional[int] = None,
                        domain_contacts: Optional[Dict] = None,
                        additional_details: Optional[Dict] = None,
                        coupons: Optional[List[str]] = None) -> Dict:
        """Purchase new domain"""
        data = {
            'domain': domain,
            'item_id': item_id
        }
        if payment_method_id:
            data['payment_method_id'] = payment_method_id
        if domain_contacts:
            data['domain_contacts'] = domain_contacts
        if additional_details:
            data['additional_details'] = additional_details
        if coupons:
            data['coupons'] = coupons

        return self._make_request(
            'POST', '/api/domains/v1/portfolio', data=data)

    def enable_domain_lock(self, domain: str) -> Dict:
        """Enable domain lock"""
        return self._make_request(
            'PUT', f'/api/domains/v1/portfolio/{domain}/domain-lock')

    def disable_domain_lock(self, domain: str) -> Dict:
        """Disable domain lock"""
        return self._make_request(
            'DELETE', f'/api/domains/v1/portfolio/{domain}/domain-lock')

    def enable_privacy_protection(self, domain: str) -> Dict:
        """Enable privacy protection"""
        return self._make_request(
            'PUT', f'/api/domains/v1/portfolio/{domain}/privacy-protection')

    def disable_privacy_protection(self, domain: str) -> Dict:
        """Disable privacy protection"""
        return self._make_request(
            'DELETE', f'/api/domains/v1/portfolio/{domain}/privacy-protection')

    def update_nameservers(
            self,
            domain: str,
            ns1: str,
            ns2: str,
            ns3: Optional[str] = None,
            ns4: Optional[str] = None) -> Dict:
        """Update domain nameservers"""
        data = {'ns1': ns1, 'ns2': ns2}
        if ns3:
            data['ns3'] = ns3
        if ns4:
            data['ns4'] = ns4
        return self._make_request(
            'PUT',
            f'/api/domains/v1/portfolio/{domain}/nameservers',
            data=data)

    # Domain forwarding
    def get_domain_forwarding(self, domain: str) -> Dict:
        """Get domain forwarding"""
        return self._make_request(
            'GET', f'/api/domains/v1/forwarding/{domain}')

    def create_domain_forwarding(
            self,
            domain: str,
            redirect_type: str,
            redirect_url: str) -> Dict:
        """Create domain forwarding"""
        data = {
            'domain': domain,
            'redirect_type': redirect_type,
            'redirect_url': redirect_url
        }
        return self._make_request(
            'POST', '/api/domains/v1/forwarding', data=data)

    def delete_domain_forwarding(self, domain: str) -> Dict:
        """Delete domain forwarding"""
        return self._make_request(
            'DELETE', f'/api/domains/v1/forwarding/{domain}')

    # WHOIS endpoints
    def get_whois_profiles(self, tld: Optional[str] = None) -> List[Dict]:
        """Get WHOIS profiles"""
        params = {}
        if tld:
            params['tld'] = tld
        return self._make_request(
            'GET', '/api/domains/v1/whois', params=params)

    def get_whois_profile(self, whois_id: int) -> Dict:
        """Get WHOIS profile"""
        return self._make_request('GET', f'/api/domains/v1/whois/{whois_id}')

    def create_whois_profile(
            self,
            tld: str,
            entity_type: str,
            country: str,
            whois_details: Dict,
            tld_details: Optional[Dict] = None) -> Dict:
        """Create WHOIS profile"""
        data = {
            'tld': tld,
            'entity_type': entity_type,
            'country': country,
            'whois_details': whois_details
        }
        if tld_details:
            data['tld_details'] = tld_details
        return self._make_request('POST', '/api/domains/v1/whois', data=data)

    def delete_whois_profile(self, whois_id: int) -> Dict:
        """Delete WHOIS profile"""
        return self._make_request(
            'DELETE', f'/api/domains/v1/whois/{whois_id}')

    def get_whois_profile_usage(self, whois_id: int) -> List[str]:
        """Get WHOIS profile usage"""
        return self._make_request(
            'GET', f'/api/domains/v1/whois/{whois_id}/usage')

    # VPS endpoints
    def get_data_centers(self) -> List[Dict]:
        """Get VPS data centers"""
        return self._make_request('GET', '/api/vps/v1/data-centers')

    def get_vps_list(self) -> List[Dict]:
        """Get VPS list"""
        return self._make_request('GET', '/api/vps/v1/virtual-machines')

    def get_vps_details(self, vm_id: int) -> Dict:
        """Get VPS details"""
        return self._make_request(
            'GET', f'/api/vps/v1/virtual-machines/{vm_id}')

    def purchase_vps(self,
                     item_id: str,
                     setup: Dict,
                     payment_method_id: Optional[int] = None,
                     coupons: Optional[List[str]] = None) -> Dict:
        """Purchase new VPS"""
        data = {
            'item_id': item_id,
            'setup': setup
        }
        if payment_method_id:
            data['payment_method_id'] = payment_method_id
        if coupons:
            data['coupons'] = coupons
        return self._make_request(
            'POST', '/api/vps/v1/virtual-machines', data=data)

    def start_vps(self, vm_id: int) -> Dict:
        """Start VPS"""
        return self._make_request(
            'POST', f'/api/vps/v1/virtual-machines/{vm_id}/start')

    def stop_vps(self, vm_id: int) -> Dict:
        """Stop VPS"""
        return self._make_request(
            'POST', f'/api/vps/v1/virtual-machines/{vm_id}/stop')

    def restart_vps(self, vm_id: int) -> Dict:
        """Restart VPS"""
        return self._make_request(
            'POST', f'/api/vps/v1/virtual-machines/{vm_id}/restart')

    def recreate_vps(
            self,
            vm_id: int,
            template_id: int,
            password: Optional[str] = None,
            post_install_script_id: Optional[int] = None) -> Dict:
        """Recreate VPS"""
        data = {'template_id': template_id}
        if password:
            data['password'] = password
        if post_install_script_id:
            data['post_install_script_id'] = post_install_script_id
        return self._make_request(
            'POST',
            f'/api/vps/v1/virtual-machines/{vm_id}/recreate',
            data=data)

    def get_vps_actions(self, vm_id: int, page: int = 1) -> Dict:
        """Get VPS actions"""
        params = {'page': page}
        return self._make_request(
            'GET',
            f'/api/vps/v1/virtual-machines/{vm_id}/actions',
            params=params)

    def get_vps_action_details(self, vm_id: int, action_id: int) -> Dict:
        """Get VPS action details"""
        return self._make_request(
            'GET', f'/api/vps/v1/virtual-machines/{vm_id}/actions/{action_id}')

    def get_vps_backups(self, vm_id: int, page: int = 1) -> Dict:
        """Get VPS backups"""
        params = {'page': page}
        return self._make_request(
            'GET',
            f'/api/vps/v1/virtual-machines/{vm_id}/backups',
            params=params)

    def restore_vps_backup(self, vm_id: int, backup_id: int) -> Dict:
        """Restore VPS backup"""
        return self._make_request(
            'POST',
            f'/api/vps/v1/virtual-machines/{vm_id}/backups/'
            f'{backup_id}/restore')

    def get_vps_metrics(
            self,
            vm_id: int,
            date_from: str,
            date_to: str) -> Dict:
        """Get VPS metrics"""
        params = {'date_from': date_from, 'date_to': date_to}
        return self._make_request(
            'GET',
            f'/api/vps/v1/virtual-machines/{vm_id}/metrics',
            params=params)

    def get_os_templates(self) -> List[Dict]:
        """Get OS templates"""
        return self._make_request('GET', '/api/vps/v1/templates')

    def get_os_template_details(self, template_id: int) -> Dict:
        """Get OS template details"""
        return self._make_request(
            'GET', f'/api/vps/v1/templates/{template_id}')

    # SSH Keys (Public Keys)
    def get_ssh_keys(self, page: int = 1) -> Dict:
        """Get SSH keys"""
        params = {'page': page}
        return self._make_request(
            'GET', '/api/vps/v1/public-keys', params=params)

    def create_ssh_key(self, name: str, key: str) -> Dict:
        """Create SSH key"""
        data = {'name': name, 'key': key}
        return self._make_request('POST', '/api/vps/v1/public-keys', data=data)

    def delete_ssh_key(self, key_id: int) -> Dict:
        """Delete SSH key"""
        return self._make_request(
            'DELETE', f'/api/vps/v1/public-keys/{key_id}')

    def attach_ssh_key(self, vm_id: int, key_ids: List[int]) -> Dict:
        """Attach SSH keys to VPS"""
        data = {'ids': key_ids}
        return self._make_request(
            'POST',
            f'/api/vps/v1/public-keys/attach/{vm_id}',
            data=data)

    def get_attached_ssh_keys(self, vm_id: int, page: int = 1) -> Dict:
        """Get attached SSH keys for VPS"""
        params = {'page': page}
        return self._make_request(
            'GET',
            f'/api/vps/v1/virtual-machines/{vm_id}/public-keys',
            params=params)
