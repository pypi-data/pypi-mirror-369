"""
Billing management commands
"""

import click
from ..api_client import HostingerAPIClient
from ..utils.formatters import (
    format_catalog_items, format_subscriptions, format_key_value_pairs,
    format_table, format_json, print_success, print_error, print_info,
    format_price, format_date
)


@click.group()
def billing():
    """Manage billing and subscriptions"""
    pass


@billing.group()
def catalog():
    """Browse service catalog"""
    pass


@catalog.command()
@click.option('--category', type=click.Choice(['DOMAIN', 'VPS']), help='Filter by category')
@click.option('--name', help='Filter by name (wildcards supported)')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, category, name, output_format):
    """List catalog items"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        catalog_data = client.get_catalog_items(category, name)
        
        if output_format == 'json':
            click.echo(format_json(catalog_data))
        else:
            click.echo(format_catalog_items(catalog_data))
            
    except Exception as e:
        print_error(f"Failed to list catalog items: {str(e)}")


@billing.group()
def payment_methods():
    """Manage payment methods"""
    pass


@payment_methods.command()
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, output_format):
    """List payment methods"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        payment_methods_data = client.get_payment_methods()
        
        if output_format == 'json':
            click.echo(format_json(payment_methods_data))
        else:
            headers = ["ID", "Name", "Identifier", "Type", "Default", "Expired", "Suspended", "Created", "Expires"]
            table_data = []
            
            for pm in payment_methods_data:
                table_data.append({
                    "ID": pm.get('id', ''),
                    "Name": pm.get('name', ''),
                    "Identifier": pm.get('identifier', ''),
                    "Type": pm.get('payment_method', ''),
                    "Default": "✅" if pm.get('is_default', False) else "❌",
                    "Expired": "❌" if pm.get('is_expired', False) else "✅",
                    "Suspended": "❌" if pm.get('is_suspended', False) else "✅",
                    "Created": format_date(pm.get('created_at')),
                    "Expires": format_date(pm.get('expires_at'))
                })
            
            click.echo(format_table(table_data, headers))
            
    except Exception as e:
        print_error(f"Failed to list payment methods: {str(e)}")


@payment_methods.command()
@click.argument('payment_method_id', type=int)
@click.pass_context
def set_default(ctx, payment_method_id):
    """Set default payment method"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.set_default_payment_method(payment_method_id)
        print_success(f"Payment method {payment_method_id} set as default")
        
    except Exception as e:
        print_error(f"Failed to set default payment method: {str(e)}")


@payment_methods.command()
@click.argument('payment_method_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this payment method?')
@click.pass_context
def delete(ctx, payment_method_id):
    """Delete payment method"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.delete_payment_method(payment_method_id)
        print_success(f"Payment method {payment_method_id} deleted")
        
    except Exception as e:
        print_error(f"Failed to delete payment method: {str(e)}")


@billing.group()
def subscriptions():
    """Manage subscriptions"""
    pass


@subscriptions.command()
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def list(ctx, output_format):
    """List subscriptions"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        subscriptions_data = client.get_subscriptions()
        
        if output_format == 'json':
            click.echo(format_json(subscriptions_data))
        else:
            click.echo(format_subscriptions(subscriptions_data))
            
    except Exception as e:
        print_error(f"Failed to list subscriptions: {str(e)}")


@subscriptions.command()
@click.argument('subscription_id')
@click.option('--reason', default='other', type=click.Choice(['other']), help='Cancellation reason')
@click.option('--when', 'cancel_option', default='immediately', type=click.Choice(['immediately']), 
              help='When to cancel')
@click.confirmation_option(prompt='Are you sure you want to cancel this subscription?')
@click.pass_context
def cancel(ctx, subscription_id, reason, cancel_option):
    """Cancel subscription"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        client.cancel_subscription(subscription_id, reason, cancel_option)
        print_success(f"Subscription {subscription_id} cancelled")
        
    except Exception as e:
        print_error(f"Failed to cancel subscription: {str(e)}")


@billing.command()
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def overview(ctx, output_format):
    """Show billing overview"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        # Get payment methods and subscriptions
        payment_methods_data = client.get_payment_methods()
        subscriptions_data = client.get_subscriptions()
        
        if output_format == 'json':
            overview_data = {
                'payment_methods': payment_methods_data,
                'subscriptions': subscriptions_data
            }
            click.echo(format_json(overview_data))
        else:
            click.echo("💳 Payment Methods:")
            if payment_methods_data:
                for pm in payment_methods_data:
                    status = "✅ Default" if pm.get('is_default') else "⚪ Available"
                    if pm.get('is_expired'):
                        status = "❌ Expired"
                    elif pm.get('is_suspended'):
                        status = "🟠 Suspended"
                    
                    click.echo(f"  • {pm.get('name', '')} ({pm.get('identifier', '')}) - {status}")
            else:
                click.echo("  No payment methods found")
            
            click.echo("\n📋 Active Subscriptions:")
            if subscriptions_data:
                active_subs = [s for s in subscriptions_data if s.get('status') == 'active']
                if active_subs:
                    for sub in active_subs:
                        price = format_price(sub.get('total_price', 0), sub.get('currency_code', 'USD'))
                        renewal = format_date(sub.get('next_billing_at'))
                        click.echo(f"  • {sub.get('name', '')} - {price} (next: {renewal})")
                else:
                    click.echo("  No active subscriptions")
            else:
                click.echo("  No subscriptions found")
                
            # Show summary stats
            total_monthly_cost = sum(s.get('total_price', 0) for s in subscriptions_data if s.get('status') == 'active')
            click.echo(f"\n💰 Total Monthly Cost: {format_price(total_monthly_cost, 'USD')}")
            
    except Exception as e:
        print_error(f"Failed to get billing overview: {str(e)}")


@billing.command()
@click.option('--category', type=click.Choice(['DOMAIN', 'VPS']), help='Show prices for category')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def pricing(ctx, category, output_format):
    """Show pricing information"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        catalog_data = client.get_catalog_items(category)
        
        if output_format == 'json':
            click.echo(format_json(catalog_data))
        else:
            click.echo(f"💰 Pricing {f'({category})' if category else '(All Categories)'}")
            click.echo("=" * 50)
            
            for item in catalog_data:
                click.echo(f"\n🛍️  {item.get('name', '')} ({item.get('category', '')})")
                click.echo(f"   ID: {item.get('id', '')}")
                
                prices = item.get('prices', [])
                if prices:
                    for price in prices:
                        period = f"{price.get('period', '')} {price.get('period_unit', '')}"
                        amount = format_price(price.get('price', 0), price.get('currency', 'USD'))
                        first_period = price.get('first_period_price')
                        
                        if first_period and first_period != price.get('price'):
                            first_amount = format_price(first_period, price.get('currency', 'USD'))
                            click.echo(f"   💳 {price.get('name', '')}: {first_amount} first, then {amount} / {period}")
                        else:
                            click.echo(f"   💳 {price.get('name', '')}: {amount} / {period}")
                else:
                    click.echo("   No pricing information available")
            
    except Exception as e:
        print_error(f"Failed to get pricing information: {str(e)}")


@billing.command()
@click.argument('search_term')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def search(ctx, search_term, output_format):
    """Search catalog items"""
    client = HostingerAPIClient(ctx.obj['api_key'])
    
    try:
        # Search using wildcards
        search_pattern = f"*{search_term}*"
        catalog_data = client.get_catalog_items(name=search_pattern)
        
        if output_format == 'json':
            click.echo(format_json(catalog_data))
        else:
            if catalog_data:
                click.echo(f"🔍 Search results for '{search_term}':")
                click.echo(format_catalog_items(catalog_data))
            else:
                print_info(f"No items found matching '{search_term}'")
            
    except Exception as e:
        print_error(f"Failed to search catalog: {str(e)}")
