"""
Domain management commands
"""

import click
from ..api_client import HostingerAPIClient
from ..utils.formatters import (
    format_domain_list, format_key_value_pairs, format_table, format_json,
    print_success, print_error, print_info
)


@click.group()
def domains():
    """Manage domains"""
    pass


@domains.command()
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, output_format):
    """List all domains"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        domains_data = client.get_domains()
        
        if output_format == 'json':
            click.echo(format_json(domains_data))
        else:
            click.echo(format_domain_list(domains_data))
            
    except Exception as e:
        print_error(f"Failed to list domains: {str(e)}")


@domains.command()
@click.argument('domain')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def show(ctx, domain, output_format):
    """Show domain details"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        domain_data = client.get_domain_details(domain)
        
        if output_format == 'json':
            click.echo(format_json(domain_data))
        else:
            click.echo(format_key_value_pairs(domain_data, f"Domain: {domain}"))
            
    except Exception as e:
        print_error(f"Failed to get domain details: {str(e)}")


@domains.command()
@click.argument('domain')
@click.argument('tlds', nargs=-1, required=True)
@click.option('--with-alternatives', is_flag=True, help='Show alternative domains')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def check(ctx, domain, tlds, with_alternatives, output_format):
    """Check domain availability"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        availability_data = client.check_domain_availability(
            domain=domain,
            tlds=list(tlds),
            with_alternatives=with_alternatives
        )
        
        if output_format == 'json':
            click.echo(format_json(availability_data))
        else:
            headers = ["Domain", "Available", "Alternative", "Restriction"]
            table_data = []
            
            for item in availability_data:
                table_data.append({
                    "Domain": item.get('domain', 'N/A'),
                    "Available": "✅ Yes" if item.get('is_available') else "❌ No",
                    "Alternative": "✅ Yes" if item.get('is_alternative') else "❌ No",
                    "Restriction": item.get('restriction', 'None')
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to check domain availability: {str(e)}")


@domains.command()
@click.argument('domain')
@click.argument('item-id')
@click.option('--payment-method-id', type=int, help='Payment method ID')
@click.option('--owner-id', type=int, help='Owner WHOIS contact ID')
@click.option('--admin-id', type=int, help='Admin WHOIS contact ID')
@click.option('--billing-id', type=int, help='Billing WHOIS contact ID')
@click.option('--tech-id', type=int, help='Tech WHOIS contact ID')
@click.option('--coupon', multiple=True, help='Coupon codes')
@click.pass_context
def purchase(ctx, domain, item_id, payment_method_id, owner_id, admin_id, billing_id, tech_id, coupon):
    """Purchase a new domain"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    domain_contacts = None
    if any([owner_id, admin_id, billing_id, tech_id]):
        domain_contacts = {}
        if owner_id:
            domain_contacts['owner_id'] = owner_id
        if admin_id:
            domain_contacts['admin_id'] = admin_id
        if billing_id:
            domain_contacts['billing_id'] = billing_id
        if tech_id:
            domain_contacts['tech_id'] = tech_id
    
    try:
        order_data = client.purchase_domain(
            domain=domain,
            item_id=item_id,
            payment_method_id=payment_method_id,
            domain_contacts=domain_contacts,
            coupons=list(coupon) if coupon else None
        )
        
        print_success(f"Domain purchase initiated for {domain}")
        click.echo(format_key_value_pairs(order_data, "Order Details"))
        
    except Exception as e:
        print_error(f"Failed to purchase domain: {str(e)}")


@domains.command()
@click.argument('domain')
@click.pass_context
def lock(ctx, domain):
    """Enable domain lock"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.enable_domain_lock(domain)
        print_success(f"Domain lock enabled for {domain}")
        
    except Exception as e:
        print_error(f"Failed to enable domain lock: {str(e)}")


@domains.command()
@click.argument('domain')
@click.pass_context
def unlock(ctx, domain):
    """Disable domain lock"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.disable_domain_lock(domain)
        print_success(f"Domain lock disabled for {domain}")
        
    except Exception as e:
        print_error(f"Failed to disable domain lock: {str(e)}")


@domains.command()
@click.argument('domain')
@click.pass_context
def enable_privacy(ctx, domain):
    """Enable privacy protection"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.enable_privacy_protection(domain)
        print_success(f"Privacy protection enabled for {domain}")
        
    except Exception as e:
        print_error(f"Failed to enable privacy protection: {str(e)}")


@domains.command()
@click.argument('domain')
@click.pass_context
def disable_privacy(ctx, domain):
    """Disable privacy protection"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.disable_privacy_protection(domain)
        print_success(f"Privacy protection disabled for {domain}")
        
    except Exception as e:
        print_error(f"Failed to disable privacy protection: {str(e)}")


@domains.command()
@click.argument('domain')
@click.argument('ns1')
@click.argument('ns2')
@click.option('--ns3', help='Third nameserver')
@click.option('--ns4', help='Fourth nameserver')
@click.pass_context
def set_nameservers(ctx, domain, ns1, ns2, ns3, ns4):
    """Update domain nameservers"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.update_nameservers(domain, ns1, ns2, ns3, ns4)
        print_success(f"Nameservers updated for {domain}")
        
    except Exception as e:
        print_error(f"Failed to update nameservers: {str(e)}")


@domains.group()
def forwarding():
    """Manage domain forwarding"""
    pass


@forwarding.command()
@click.argument('domain')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def show(ctx, domain, output_format):
    """Show domain forwarding"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        forwarding_data = client.get_domain_forwarding(domain)
        
        if output_format == 'json':
            click.echo(format_json(forwarding_data))
        else:
            click.echo(format_key_value_pairs(forwarding_data, f"Forwarding for {domain}"))
            
    except Exception as e:
        print_error(f"Failed to get domain forwarding: {str(e)}")


@forwarding.command()
@click.argument('domain')
@click.argument('redirect_url')
@click.option('--type', 'redirect_type', default='301', type=click.Choice(['301', '302']),
              help='Redirect type')
@click.pass_context
def create(ctx, domain, redirect_url, redirect_type):
    """Create domain forwarding"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        forwarding_data = client.create_domain_forwarding(domain, redirect_type, redirect_url)
        print_success(f"Domain forwarding created for {domain}")
        click.echo(format_key_value_pairs(forwarding_data))
        
    except Exception as e:
        print_error(f"Failed to create domain forwarding: {str(e)}")


@forwarding.command()
@click.argument('domain')
@click.pass_context
def delete(ctx, domain):
    """Delete domain forwarding"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.delete_domain_forwarding(domain)
        print_success(f"Domain forwarding deleted for {domain}")
        
    except Exception as e:
        print_error(f"Failed to delete domain forwarding: {str(e)}")


@domains.group()
def whois():
    """Manage WHOIS profiles"""
    pass


@whois.command()
@click.option('--tld', help='Filter by TLD')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, tld, output_format):
    """List WHOIS profiles"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        profiles = client.get_whois_profiles(tld)
        
        if output_format == 'json':
            click.echo(format_json(profiles))
        else:
            headers = ["ID", "TLD", "Entity Type", "Country", "Created"]
            table_data = []
            
            for profile in profiles:
                table_data.append({
                    "ID": profile.get('id', ''),
                    "TLD": profile.get('tld', ''),
                    "Entity Type": profile.get('entity_type', ''),
                    "Country": profile.get('country', ''),
                    "Created": profile.get('created_at', '')
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to list WHOIS profiles: {str(e)}")


@whois.command()
@click.argument('whois_id', type=int)
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def show(ctx, whois_id, output_format):
    """Show WHOIS profile"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        profile = client.get_whois_profile(whois_id)
        
        if output_format == 'json':
            click.echo(format_json(profile))
        else:
            click.echo(format_key_value_pairs(profile, f"WHOIS Profile {whois_id}"))
            
    except Exception as e:
        print_error(f"Failed to get WHOIS profile: {str(e)}")


@whois.command()
@click.argument('whois_id', type=int)
@click.pass_context
def delete(ctx, whois_id):
    """Delete WHOIS profile"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.delete_whois_profile(whois_id)
        print_success(f"WHOIS profile {whois_id} deleted")
        
    except Exception as e:
        print_error(f"Failed to delete WHOIS profile: {str(e)}")


@whois.command()
@click.argument('whois_id', type=int)
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def usage(ctx, whois_id, output_format):
    """Show WHOIS profile usage"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        usage_data = client.get_whois_profile_usage(whois_id)
        
        if output_format == 'json':
            click.echo(format_json(usage_data))
        else:
            if usage_data:
                click.echo(f"WHOIS profile {whois_id} is used by:")
                for domain in usage_data:
                    click.echo(f"  • {domain}")
            else:
                print_info(f"WHOIS profile {whois_id} is not used by any domains")
                
    except Exception as e:
        print_error(f"Failed to get WHOIS profile usage: {str(e)}")
