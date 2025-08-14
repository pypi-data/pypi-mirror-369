#!/usr/bin/env python3
"""
Hostinger CLI - A comprehensive command-line interface for Hostinger API
"""

import click
import os
import sys
from .utils.config import ConfigManager
from .commands import billing, dns, domains, vps


@click.group()
@click.option('--api-key', envvar='HOSTINGER_API_KEY', help='Hostinger API key')
@click.option('--config-file', default='~/.hostinger-cli.json', help='Configuration file path')
@click.pass_context
def cli(ctx, api_key, config_file):
    """Hostinger CLI - Manage your Hostinger services from the command line"""
    ctx.ensure_object(dict)
    
    config_manager = ConfigManager(config_file)
    
    # If no API key provided, try to get from config
    if not api_key:
        api_key = config_manager.get_api_key()
    
    if not api_key:
        click.echo("Error: No API key provided. Use --api-key option, set HOSTINGER_API_KEY environment variable, or run 'hostinger configure'")
        sys.exit(1)
    
    ctx.obj['api_key'] = api_key
    ctx.obj['config_manager'] = config_manager


@cli.command()
@click.option('--api-key', prompt='Enter your Hostinger API key', hide_input=True)
@click.pass_context
def configure(ctx, api_key):
    """Configure the CLI with your API key"""
    config_manager = ctx.obj.get('config_manager') or ConfigManager()
    config_manager.set_api_key(api_key)
    click.echo("✅ API key saved successfully!")


@cli.command()
def version():
    """Show version information"""
    click.echo("Hostinger CLI v1.0.0")


# Add command groups
cli.add_command(billing.billing)
cli.add_command(dns.dns)
cli.add_command(domains.domains)
cli.add_command(vps.vps)


def main():
    """Entry point for the CLI"""
    cli(obj={})


if __name__ == '__main__':
    main()
