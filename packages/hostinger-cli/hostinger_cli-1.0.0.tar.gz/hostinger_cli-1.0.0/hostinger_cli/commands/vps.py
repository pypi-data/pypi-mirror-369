"""
VPS management commands
"""

import click
from datetime import datetime, timedelta
from ..api_client import HostingerAPIClient
from ..utils.formatters import (
    format_vps_list, format_key_value_pairs, format_table, format_json,
    print_success, print_error, print_info, format_date
)


@click.group()
def vps():
    """Manage VPS instances"""
    pass


@vps.command()
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, output_format):
    """List all VPS instances"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        vps_data = client.get_vps_list()
        
        if output_format == 'json':
            click.echo(format_json(vps_data))
        else:
            click.echo(format_vps_list(vps_data))
            
    except Exception as e:
        print_error(f"Failed to list VPS instances: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def show(ctx, vm_id, output_format):
    """Show VPS details"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        vps_data = client.get_vps_details(vm_id)
        
        if output_format == 'json':
            click.echo(format_json(vps_data))
        else:
            click.echo(format_key_value_pairs(vps_data, f"VPS {vm_id}"))
            
    except Exception as e:
        print_error(f"Failed to get VPS details: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.pass_context
def start(ctx, vm_id):
    """Start VPS"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        action = client.start_vps(vm_id)
        print_success(f"Start command sent to VPS {vm_id}")
        print_info(f"Action ID: {action.get('id')}")
        
    except Exception as e:
        print_error(f"Failed to start VPS: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.pass_context
def stop(ctx, vm_id):
    """Stop VPS"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        action = client.stop_vps(vm_id)
        print_success(f"Stop command sent to VPS {vm_id}")
        print_info(f"Action ID: {action.get('id')}")
        
    except Exception as e:
        print_error(f"Failed to stop VPS: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.pass_context
def restart(ctx, vm_id):
    """Restart VPS"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        action = client.restart_vps(vm_id)
        print_success(f"Restart command sent to VPS {vm_id}")
        print_info(f"Action ID: {action.get('id')}")
        
    except Exception as e:
        print_error(f"Failed to restart VPS: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.argument('template_id', type=int)
@click.option('--password', prompt=True, hide_input=True, help='Root password')
@click.option('--post-install-script-id', type=int, help='Post-install script ID')
@click.confirmation_option(prompt='Are you sure you want to recreate this VPS? All data will be lost!')
@click.pass_context
def recreate(ctx, vm_id, template_id, password, post_install_script_id):
    """Recreate VPS (WARNING: This will destroy all data!)"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        action = client.recreate_vps(vm_id, template_id, password, post_install_script_id)
        print_success(f"Recreate command sent to VPS {vm_id}")
        print_info(f"Action ID: {action.get('id')}")
        
    except Exception as e:
        print_error(f"Failed to recreate VPS: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.option('--page', default=1, help='Page number')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def actions(ctx, vm_id, page, output_format):
    """List VPS actions"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        actions_data = client.get_vps_actions(vm_id, page)
        
        if output_format == 'json':
            click.echo(format_json(actions_data))
        else:
            headers = ["ID", "Name", "State", "Created", "Updated"]
            table_data = []
            
            for action in actions_data.get('data', []):
                table_data.append({
                    "ID": action.get('id', ''),
                    "Name": action.get('name', ''),
                    "State": action.get('state', ''),
                    "Created": format_date(action.get('created_at')),
                    "Updated": format_date(action.get('updated_at'))
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to list VPS actions: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.argument('action_id', type=int)
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def action(ctx, vm_id, action_id, output_format):
    """Show action details"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        action_data = client.get_vps_action_details(vm_id, action_id)
        
        if output_format == 'json':
            click.echo(format_json(action_data))
        else:
            click.echo(format_key_value_pairs(action_data, f"Action {action_id}"))
            
    except Exception as e:
        print_error(f"Failed to get action details: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.option('--page', default=1, help='Page number')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def backups(ctx, vm_id, page, output_format):
    """List VPS backups"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        backups_data = client.get_vps_backups(vm_id, page)
        
        if output_format == 'json':
            click.echo(format_json(backups_data))
        else:
            headers = ["ID", "Location", "Created"]
            table_data = []
            
            for backup in backups_data.get('data', []):
                table_data.append({
                    "ID": backup.get('id', ''),
                    "Location": backup.get('location', ''),
                    "Created": format_date(backup.get('created_at'))
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to list VPS backups: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.argument('backup_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to restore this backup? Current data will be overwritten!')
@click.pass_context
def restore_backup(ctx, vm_id, backup_id):
    """Restore VPS from backup"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        action = client.restore_vps_backup(vm_id, backup_id)
        print_success(f"Backup restore initiated for VPS {vm_id}")
        print_info(f"Action ID: {action.get('id')}")
        
    except Exception as e:
        print_error(f"Failed to restore backup: {str(e)}")


@vps.command()
@click.argument('vm_id', type=int)
@click.option('--days', default=7, help='Number of days to get metrics for')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def metrics(ctx, vm_id, days, output_format):
    """Get VPS metrics"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    date_from = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    date_to = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    try:
        metrics_data = client.get_vps_metrics(vm_id, date_from, date_to)
        
        if output_format == 'json':
            click.echo(format_json(metrics_data))
        else:
            click.echo(format_key_value_pairs(metrics_data, f"VPS {vm_id} Metrics ({days} days)"))
            
    except Exception as e:
        print_error(f"Failed to get VPS metrics: {str(e)}")


@vps.group()
def templates():
    """Manage OS templates"""
    pass


@templates.command()
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, output_format):
    """List OS templates"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        templates_data = client.get_os_templates()
        
        if output_format == 'json':
            click.echo(format_json(templates_data))
        else:
            headers = ["ID", "Name", "Description"]
            table_data = []
            
            for template in templates_data:
                table_data.append({
                    "ID": template.get('id', ''),
                    "Name": template.get('name', ''),
                    "Description": template.get('description', '')
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to list OS templates: {str(e)}")


@templates.command()
@click.argument('template_id', type=int)
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def show(ctx, template_id, output_format):
    """Show OS template details"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        template_data = client.get_os_template_details(template_id)
        
        if output_format == 'json':
            click.echo(format_json(template_data))
        else:
            click.echo(format_key_value_pairs(template_data, f"Template {template_id}"))
            
    except Exception as e:
        print_error(f"Failed to get template details: {str(e)}")


@vps.group()
def ssh_keys():
    """Manage SSH keys"""
    pass


@ssh_keys.command()
@click.option('--page', default=1, help='Page number')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, page, output_format):
    """List SSH keys"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        keys_data = client.get_ssh_keys(page)
        
        if output_format == 'json':
            click.echo(format_json(keys_data))
        else:
            headers = ["ID", "Name", "Key (truncated)"]
            table_data = []
            
            for key in keys_data.get('data', []):
                key_preview = key.get('key', '')[:50] + '...' if len(key.get('key', '')) > 50 else key.get('key', '')
                table_data.append({
                    "ID": key.get('id', ''),
                    "Name": key.get('name', ''),
                    "Key (truncated)": key_preview
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to list SSH keys: {str(e)}")


@ssh_keys.command()
@click.argument('name')
@click.option('--key-file', type=click.File('r'), help='Read key from file')
@click.option('--key', help='SSH public key content')
@click.pass_context
def create(ctx, name, key_file, key):
    """Create SSH key"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    if key_file:
        key = key_file.read().strip()
    elif not key:
        key = click.prompt('Enter SSH public key')
    
    try:
        key_data = client.create_ssh_key(name, key)
        print_success(f"SSH key '{name}' created")
        click.echo(format_key_value_pairs(key_data))
        
    except Exception as e:
        print_error(f"Failed to create SSH key: {str(e)}")


@ssh_keys.command()
@click.argument('key_id', type=int)
@click.pass_context
def delete(ctx, key_id):
    """Delete SSH key"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.delete_ssh_key(key_id)
        print_success(f"SSH key {key_id} deleted")
        
    except Exception as e:
        print_error(f"Failed to delete SSH key: {str(e)}")


@ssh_keys.command()
@click.argument('vm_id', type=int)
@click.argument('key_ids', nargs=-1, type=int, required=True)
@click.pass_context
def attach(ctx, vm_id, key_ids):
    """Attach SSH keys to VPS"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        action = client.attach_ssh_key(vm_id, list(key_ids))
        print_success(f"SSH keys attached to VPS {vm_id}")
        print_info(f"Action ID: {action.get('id')}")
        
    except Exception as e:
        print_error(f"Failed to attach SSH keys: {str(e)}")


@ssh_keys.command()
@click.argument('vm_id', type=int)
@click.option('--page', default=1, help='Page number')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def attached(ctx, vm_id, page, output_format):
    """List SSH keys attached to VPS"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        keys_data = client.get_attached_ssh_keys(vm_id, page)
        
        if output_format == 'json':
            click.echo(format_json(keys_data))
        else:
            headers = ["ID", "Name", "Key (truncated)"]
            table_data = []
            
            for key in keys_data.get('data', []):
                key_preview = key.get('key', '')[:50] + '...' if len(key.get('key', '')) > 50 else key.get('key', '')
                table_data.append({
                    "ID": key.get('id', ''),
                    "Name": key.get('name', ''),
                    "Key (truncated)": key_preview
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to list attached SSH keys: {str(e)}")


@vps.command()
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def datacenters(ctx, output_format):
    """List data centers"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        datacenters_data = client.get_data_centers()
        
        if output_format == 'json':
            click.echo(format_json(datacenters_data))
        else:
            headers = ["ID", "Name", "City", "Country", "Continent"]
            table_data = []
            
            for dc in datacenters_data:
                table_data.append({
                    "ID": dc.get('id', ''),
                    "Name": dc.get('name', ''),
                    "City": dc.get('city', ''),
                    "Country": dc.get('location', ''),
                    "Continent": dc.get('continent', '')
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to list data centers: {str(e)}")
