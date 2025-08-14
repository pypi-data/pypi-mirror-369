"""
Output formatters for Hostinger CLI
"""

import json
from typing import Any, Dict, List
import click
from datetime import datetime


def format_json(data: Any, indent: int = 2) -> str:
    """Format data as JSON"""
    return json.dumps(data, indent=indent, default=str)


def format_table(data: List[Dict], headers: List[str] = None) -> str:
    """Format data as a simple table"""
    if not data:
        return "No data found"
    
    if headers is None:
        headers = list(data[0].keys()) if data else []
    
    # Calculate column widths
    widths = {}
    for header in headers:
        widths[header] = len(str(header))
        for row in data:
            value = str(row.get(header, ''))
            widths[header] = max(widths[header], len(value))
    
    # Build table
    lines = []
    
    # Header
    header_line = " | ".join(str(header).ljust(widths[header]) for header in headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # Rows
    for row in data:
        row_line = " | ".join(str(row.get(header, '')).ljust(widths[header]) for header in headers)
        lines.append(row_line)
    
    return "\n".join(lines)


def format_key_value_pairs(data: Dict, title: str = None) -> str:
    """Format data as key-value pairs"""
    lines = []
    
    if title:
        lines.append(f"📋 {title}")
        lines.append("=" * (len(title) + 3))
    
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, indent=2, default=str)
        lines.append(f"{key}: {value}")
    
    return "\n".join(lines)


def format_domain_list(domains: List[Dict]) -> str:
    """Format domain list"""
    if not domains:
        return "No domains found"
    
    headers = ["ID", "Domain", "Type", "Status", "Created", "Expires"]
    table_data = []
    
    for domain in domains:
        table_data.append({
            "ID": domain.get('id', ''),
            "Domain": domain.get('domain', 'N/A'),
            "Type": domain.get('type', ''),
            "Status": domain.get('status', ''),
            "Created": format_date(domain.get('created_at')),
            "Expires": format_date(domain.get('expires_at'))
        })
    
    return format_table(table_data, headers)


def format_vps_list(vps_list: List[Dict]) -> str:
    """Format VPS list"""
    if not vps_list:
        return "No VPS instances found"
    
    headers = ["ID", "Hostname", "Plan", "State", "CPUs", "Memory", "Disk", "IPv4"]
    table_data = []
    
    for vps in vps_list:
        ipv4_addr = ""
        if vps.get('ipv4') and len(vps['ipv4']) > 0:
            ipv4_addr = vps['ipv4'][0].get('address', '')
        
        table_data.append({
            "ID": vps.get('id', ''),
            "Hostname": vps.get('hostname', ''),
            "Plan": vps.get('plan', ''),
            "State": format_status(vps.get('state', '')),
            "CPUs": vps.get('cpus', ''),
            "Memory": f"{vps.get('memory', 0)}MB",
            "Disk": f"{vps.get('disk', 0)}MB",
            "IPv4": ipv4_addr
        })
    
    return format_table(table_data, headers)


def format_dns_records(records: List[Dict]) -> str:
    """Format DNS records"""
    if not records:
        return "No DNS records found"
    
    lines = []
    for record in records:
        lines.append(f"🌐 {record.get('name', '@')} ({record.get('type', '')})")
        lines.append(f"   TTL: {record.get('ttl', '')}")
        
        record_list = record.get('records', [])
        for i, rec in enumerate(record_list):
            content = rec.get('content', '')
            disabled = " (DISABLED)" if rec.get('is_disabled', False) else ""
            lines.append(f"   → {content}{disabled}")
        lines.append("")
    
    return "\n".join(lines)


def format_catalog_items(items: List[Dict]) -> str:
    """Format catalog items"""
    if not items:
        return "No catalog items found"
    
    lines = []
    for item in items:
        lines.append(f"🛍️  {item.get('name', '')}")
        lines.append(f"   ID: {item.get('id', '')}")
        lines.append(f"   Category: {item.get('category', '')}")
        
        prices = item.get('prices', [])
        if prices:
            lines.append("   Prices:")
            for price in prices:
                period = f"{price.get('period', '')} {price.get('period_unit', '')}"
                amount = format_price(price.get('price', 0), price.get('currency', 'USD'))
                lines.append(f"     • {price.get('name', '')}: {amount} / {period}")
        lines.append("")
    
    return "\n".join(lines)


def format_subscriptions(subscriptions: List[Dict]) -> str:
    """Format subscriptions"""
    if not subscriptions:
        return "No subscriptions found"
    
    headers = ["ID", "Name", "Status", "Currency", "Price", "Next Billing", "Auto Renew"]
    table_data = []
    
    for sub in subscriptions:
        table_data.append({
            "ID": sub.get('id', ''),
            "Name": sub.get('name', ''),
            "Status": format_status(sub.get('status', '')),
            "Currency": sub.get('currency_code', ''),
            "Price": format_price(sub.get('total_price', 0), sub.get('currency_code', 'USD')),
            "Next Billing": format_date(sub.get('next_billing_at')),
            "Auto Renew": "✅" if sub.get('is_auto_renewed', False) else "❌"
        })
    
    return format_table(table_data, headers)


def format_date(date_str: str) -> str:
    """Format date string"""
    if not date_str:
        return "N/A"
    
    try:
        # Parse ISO format datetime
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except (ValueError, AttributeError):
        return str(date_str)


def format_price(price_cents: int, currency: str = 'USD') -> str:
    """Format price from cents to currency"""
    if price_cents is None:
        return "N/A"
    
    price = price_cents / 100
    return f"{currency} {price:.2f}"


def format_status(status: str) -> str:
    """Format status with emoji"""
    status_map = {
        'active': '🟢 Active',
        'running': '🟢 Running',
        'stopped': '🔴 Stopped',
        'stopping': '🟡 Stopping',
        'starting': '🟡 Starting',
        'pending': '🟡 Pending',
        'error': '🔴 Error',
        'suspended': '🟠 Suspended',
        'cancelled': '🔴 Cancelled',
        'expired': '🔴 Expired',
        'completed': '✅ Completed',
        'failed': '❌ Failed'
    }
    
    return status_map.get(status.lower(), f"⚪ {status.title()}")


def print_success(message: str):
    """Print success message"""
    click.echo(f"✅ {message}")


def print_error(message: str):
    """Print error message"""
    click.echo(f"❌ {message}", err=True)


def print_warning(message: str):
    """Print warning message"""
    click.echo(f"⚠️  {message}")


def print_info(message: str):
    """Print info message"""
    click.echo(f"ℹ️  {message}")
