"""
DNS management commands
"""

import click
import json
from ..api_client import HostingerAPIClient
from ..utils.formatters import (
    format_dns_records, format_key_value_pairs, format_table, format_json,
    print_success, print_error, print_info, format_date
)


@click.group()
def dns():
    """Manage DNS records"""
    pass


@dns.command()
@click.argument('domain')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, domain, output_format):
    """List DNS records for domain"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        records = client.get_dns_records(domain)
        
        if output_format == 'json':
            click.echo(format_json(records))
        else:
            click.echo(format_dns_records(records))
            
    except Exception as e:
        print_error(f"Failed to list DNS records: {str(e)}")


@dns.command()
@click.argument('domain')
@click.argument('name')
@click.argument('record_type', type=click.Choice(['A', 'AAAA', 'CNAME', 'ALIAS', 'MX', 'TXT', 'NS', 'SOA', 'SRV', 'CAA']))
@click.argument('content')
@click.option('--ttl', default=14400, type=int, help='TTL in seconds')
@click.option('--overwrite', is_flag=True, help='Overwrite existing records')
@click.pass_context
def add(ctx, domain, name, record_type, content, ttl, overwrite):
    """Add DNS record"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    zone_data = [{
        'name': name,
        'type': record_type,
        'ttl': ttl,
        'records': [{'content': content}]
    }]
    
    try:
        client.update_dns_records(domain, zone_data, overwrite)
        print_success(f"DNS record added for {domain}")
        print_info(f"Added: {name} {record_type} {content}")
        
    except Exception as e:
        print_error(f"Failed to add DNS record: {str(e)}")


@dns.command()
@click.argument('domain')
@click.argument('name')
@click.argument('record_type', type=click.Choice(['A', 'AAAA', 'CNAME', 'ALIAS', 'MX', 'TXT', 'NS', 'SOA', 'SRV', 'CAA']))
@click.pass_context
def delete(ctx, domain, name, record_type):
    """Delete DNS records"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    filters = [{'name': name, 'type': record_type}]
    
    try:
        client.delete_dns_records(domain, filters)
        print_success(f"DNS records deleted for {domain}")
        print_info(f"Deleted: {name} {record_type}")
        
    except Exception as e:
        print_error(f"Failed to delete DNS records: {str(e)}")


@dns.command()
@click.argument('domain')
@click.argument('zone_file', type=click.File('r'))
@click.option('--overwrite', is_flag=True, help='Overwrite existing records')
@click.pass_context
def import_zone(ctx, domain, zone_file, overwrite):
    """Import DNS zone from JSON file"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        zone_data = json.load(zone_file)
        
        # Validate zone data structure
        if not isinstance(zone_data, list):
            raise ValueError("Zone file must contain a JSON array")
        
        client.update_dns_records(domain, zone_data, overwrite)
        print_success(f"DNS zone imported for {domain}")
        print_info(f"Imported {len(zone_data)} record sets")
        
    except json.JSONDecodeError:
        print_error("Invalid JSON in zone file")
    except Exception as e:
        print_error(f"Failed to import DNS zone: {str(e)}")


@dns.command()
@click.argument('domain')
@click.argument('zone_file', type=click.File('w'))
@click.pass_context
def export_zone(ctx, domain, zone_file):
    """Export DNS zone to JSON file"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        records = client.get_dns_records(domain)
        json.dump(records, zone_file, indent=2, default=str)
        print_success(f"DNS zone exported for {domain}")
        
    except Exception as e:
        print_error(f"Failed to export DNS zone: {str(e)}")


@dns.command()
@click.argument('domain')
@click.argument('zone_file', type=click.File('r'))
@click.option('--overwrite', is_flag=True, help='Overwrite existing records')
@click.pass_context
def validate(ctx, domain, zone_file, overwrite):
    """Validate DNS zone before applying"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        zone_data = json.load(zone_file)
        
        # Validate zone data structure
        if not isinstance(zone_data, list):
            raise ValueError("Zone file must contain a JSON array")
        
        client.validate_dns_records(domain, zone_data, overwrite)
        print_success(f"DNS zone validation passed for {domain}")
        
    except json.JSONDecodeError:
        print_error("Invalid JSON in zone file")
    except Exception as e:
        print_error(f"DNS zone validation failed: {str(e)}")


@dns.command()
@click.argument('domain')
@click.option('--reset-email', is_flag=True, default=True, help='Reset email records')
@click.option('--whitelist', multiple=True, help='Record types to preserve (e.g. MX, TXT)')
@click.confirmation_option(prompt='Are you sure you want to reset DNS records to default?')
@click.pass_context
def reset(ctx, domain, reset_email, whitelist):
    """Reset DNS records to default"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.reset_dns_records(
            domain=domain,
            reset_email_records=reset_email,
            whitelisted_record_types=list(whitelist) if whitelist else None
        )
        print_success(f"DNS records reset to default for {domain}")
        
    except Exception as e:
        print_error(f"Failed to reset DNS records: {str(e)}")


@dns.group()
def snapshots():
    """Manage DNS snapshots"""
    pass


@snapshots.command()
@click.argument('domain')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, domain, output_format):
    """List DNS snapshots"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        snapshots_data = client.get_dns_snapshots(domain)
        
        if output_format == 'json':
            click.echo(format_json(snapshots_data))
        else:
            headers = ["ID", "Reason", "Created"]
            table_data = []
            
            for snapshot in snapshots_data:
                table_data.append({
                    "ID": snapshot.get('id', ''),
                    "Reason": snapshot.get('reason', ''),
                    "Created": format_date(snapshot.get('created_at'))
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to list DNS snapshots: {str(e)}")


@snapshots.command()
@click.argument('domain')
@click.argument('snapshot_id', type=int)
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def show(ctx, domain, snapshot_id, output_format):
    """Show DNS snapshot content"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        snapshot_data = client.get_dns_snapshot(domain, snapshot_id)
        
        if output_format == 'json':
            click.echo(format_json(snapshot_data))
        else:
            click.echo(format_key_value_pairs(snapshot_data, f"DNS Snapshot {snapshot_id}"))
            
            if 'snapshot' in snapshot_data:
                click.echo("\n📋 Snapshot Contents:")
                click.echo(format_dns_records(snapshot_data['snapshot']))
            
    except Exception as e:
        print_error(f"Failed to get DNS snapshot: {str(e)}")


@snapshots.command()
@click.argument('domain')
@click.argument('snapshot_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to restore this DNS snapshot?')
@click.pass_context
def restore(ctx, domain, snapshot_id):
    """Restore DNS snapshot"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.restore_dns_snapshot(domain, snapshot_id)
        print_success(f"DNS snapshot {snapshot_id} restored for {domain}")
        
    except Exception as e:
        print_error(f"Failed to restore DNS snapshot: {str(e)}")


@dns.command()
@click.argument('domain')
@click.argument('name')
@click.argument('record_type', type=click.Choice(['A', 'AAAA', 'CNAME', 'ALIAS', 'MX', 'TXT', 'NS', 'SOA', 'SRV', 'CAA']))
@click.argument('old_content')
@click.argument('new_content')
@click.option('--ttl', type=int, help='New TTL in seconds')
@click.pass_context
def update(ctx, domain, name, record_type, old_content, new_content, ttl):
    """Update specific DNS record"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        # First, get current records
        current_records = client.get_dns_records(domain)
        
        # Find and update the specific record
        updated = False
        for record in current_records:
            if record.get('name') == name and record.get('type') == record_type:
                for rec in record.get('records', []):
                    if rec.get('content') == old_content:
                        rec['content'] = new_content
                        updated = True
                        
                if ttl:
                    record['ttl'] = ttl
                
                if updated:
                    break
        
        if not updated:
            print_error(f"Record not found: {name} {record_type} {old_content}")
            return
        
        # Update the DNS zone
        client.update_dns_records(domain, current_records, overwrite=True)
        print_success(f"DNS record updated for {domain}")
        print_info(f"Updated: {name} {record_type} {old_content} → {new_content}")
        
    except Exception as e:
        print_error(f"Failed to update DNS record: {str(e)}")


@dns.command()
@click.argument('domain')
@click.argument('record_type', type=click.Choice(['A', 'AAAA', 'CNAME', 'ALIAS', 'MX', 'TXT', 'NS', 'SOA', 'SRV', 'CAA']))
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def filter(ctx, domain, record_type, output_format):
    """Filter DNS records by type"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        records = client.get_dns_records(domain)
        filtered_records = [r for r in records if r.get('type') == record_type]
        
        if output_format == 'json':
            click.echo(format_json(filtered_records))
        else:
            if filtered_records:
                click.echo(f"🔍 {record_type} records for {domain}:")
                click.echo(format_dns_records(filtered_records))
            else:
                print_info(f"No {record_type} records found for {domain}")
            
    except Exception as e:
        print_error(f"Failed to filter DNS records: {str(e)}")
