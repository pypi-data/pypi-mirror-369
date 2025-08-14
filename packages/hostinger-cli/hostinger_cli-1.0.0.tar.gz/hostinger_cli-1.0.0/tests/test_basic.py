"""
Basic tests for Hostinger CLI
"""

import pytest
from click.testing import CliRunner
from hostinger_cli.main import cli
from hostinger_cli import __version__


class TestBasic:
    """Basic functionality tests"""
    
    def test_version(self):
        """Test that version is defined"""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0
    
    def test_cli_help(self):
        """Test CLI help command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Hostinger CLI' in result.output
    
    def test_version_command(self):
        """Test version command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        assert 'Hostinger CLI' in result.output
    
    def test_domains_help(self):
        """Test domains help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['domains', '--help'])
        assert result.exit_code == 0
        assert 'Manage domains' in result.output
    
    def test_vps_help(self):
        """Test VPS help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['vps', '--help'])
        assert result.exit_code == 0
        assert 'Manage VPS instances' in result.output
    
    def test_dns_help(self):
        """Test DNS help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['dns', '--help'])
        assert result.exit_code == 0
        assert 'Manage DNS records' in result.output
    
    def test_billing_help(self):
        """Test billing help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['billing', '--help'])
        assert result.exit_code == 0
        assert 'Manage billing and subscriptions' in result.output


class TestAPIClient:
    """Test API client initialization"""
    
    def test_api_client_import(self):
        """Test that API client can be imported"""
        from hostinger_cli.api_client import HostingerAPIClient
        assert HostingerAPIClient is not None
    
    def test_api_client_init(self):
        """Test API client initialization"""
        from hostinger_cli.api_client import HostingerAPIClient
        
        client = HostingerAPIClient("test_api_key")
        assert client.api_key == "test_api_key"
        assert client.BASE_URL == "https://developers.hostinger.com"


class TestFormatters:
    """Test output formatters"""
    
    def test_formatters_import(self):
        """Test that formatters can be imported"""
        from hostinger_cli.utils.formatters import format_json, format_table
        assert format_json is not None
        assert format_table is not None
    
    def test_format_json(self):
        """Test JSON formatting"""
        from hostinger_cli.utils.formatters import format_json
        
        data = {"test": "value", "number": 123}
        result = format_json(data)
        assert '"test": "value"' in result
        assert '"number": 123' in result
    
    def test_format_table_empty(self):
        """Test table formatting with empty data"""
        from hostinger_cli.utils.formatters import format_table
        
        result = format_table([])
        assert result == "No data found"
    
    def test_format_table_with_data(self):
        """Test table formatting with data"""
        from hostinger_cli.utils.formatters import format_table
        
        data = [
            {"name": "test1", "value": "123"},
            {"name": "test2", "value": "456"}
        ]
        result = format_table(data)
        assert "test1" in result
        assert "test2" in result
        assert "123" in result
        assert "456" in result


class TestConfig:
    """Test configuration management"""
    
    def test_config_import(self):
        """Test that config manager can be imported"""
        from hostinger_cli.utils.config import ConfigManager
        assert ConfigManager is not None
    
    def test_config_manager_init(self):
        """Test config manager initialization"""
        from hostinger_cli.utils.config import ConfigManager
        
        config = ConfigManager("/tmp/test_config.json")
        assert config.config_file.name == "test_config.json"
        assert isinstance(config.config, dict)
