#!/usr/bin/env python3
"""CLI for managing MQTT client operations."""

import click
from .cli_core import (
    create_client, handle_error, get_client_args
)


def create_mqtt_group():
    """Create and return the mqtt command group."""
    @click.group()
    @click.pass_context
    def mqtt(ctx):
        """Manage MQTT client settings."""
        pass

    @mqtt.command('activate')
    @click.pass_context
    def activate(ctx):
        """Activate MQTT client."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                _ = client.mqtt_client.activate()
                click.echo(click.style("MQTT client activated successfully!", fg="green"))
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @mqtt.command('deactivate')
    @click.pass_context
    def deactivate(ctx):
        """Deactivate MQTT client."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                _ = client.mqtt_client.deactivate()
                    
                click.echo(click.style("MQTT client deactivated successfully!", fg="yellow"))
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @mqtt.command('configure')
    @click.option('--broker-host', required=True, help='Broker hostname or IP address')
    @click.option('--broker-port', type=int, default=1883, help='Broker port number')
    @click.option('--broker-username', help='Broker authentication username')
    @click.option('--broker-password', help='Broker authentication password')
    @click.option('--keep-alive', type=int, default=60, help='Keep alive interval in seconds')
    @click.option('--use-tls', is_flag=True, help='Use TLS encryption')
    @click.pass_context
    def configure(ctx, broker_host, broker_port, broker_username, broker_password,
                 keep_alive, use_tls):
        """Configure MQTT broker settings."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                client.mqtt_client.configure(
                    host=broker_host,
                    port=broker_port,
                    username=broker_username,
                    password=broker_password,
                    use_tls=use_tls,
                    keep_alive_interval=keep_alive
                )
                    
                click.echo(click.style("MQTT broker configuration updated successfully!", fg="green"))
                click.echo("\nBroker Configuration:")
                click.echo(f"  Host: {broker_host}")
                click.echo(f"  Port: {broker_port}")
                click.echo(f"  TLS Enabled: {use_tls}")
                click.echo(f"  Keep Alive: {keep_alive}s")
                if broker_username:
                    click.echo("  Authentication: Enabled")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @mqtt.command('status')
    @click.pass_context
    def status(ctx):
        """Get MQTT client status."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                status = client.mqtt_client.get_state().get('status')
                click.echo("MQTT Client Status:")
                click.echo(f"  state: {click.style(status.get('state'), fg='green' if status.get('state') == 'active' else 'yellow')}")
                click.echo(f"  connectionStatus: {click.style(status.get('connectionStatus'), fg='green' if status.get('connectionStatus') == 'connected' else 'yellow')}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @mqtt.command('config')
    @click.pass_context
    def config(ctx):
        """Get MQTT client configuration."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                config = client.mqtt_client.get_state().get('config')
                click.echo("MQTT Client Configuration:")
                click.echo(f"  Host: {config.get('server').get('host')}")
                click.echo(f"  Port: {config.get('server').get('port')}")
                click.echo(f"  protocol: {config.get('server').get('protocol')}")
                click.echo(f"  alpnProtocol: {config.get('server').get('alpnProtocol')}")
                click.echo(f"  username: {config.get('username')}")
                click.echo(f"  password: {config.get('password')}")
                click.echo(f"  clientId: {config.get('clientId')}")
                click.echo(f"  keepAliveInterval: {config.get('keepAliveInterval')}s")
                click.echo(f"  connectTimeout: {config.get('connectTimeout')}s")
                click.echo(f"  cleanSession: {config.get('cleanSession')}")
                click.echo(f"  autoReconnect: {config.get('autoReconnect')}")
                click.echo(f"  deviceTopicPrefix: {config.get('deviceTopicPrefix')}")
                click.echo(f"  httpProxy: {config.get('httpProxy')}")
                click.echo(f"  httpsProxy: {config.get('httpsProxy')}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)
    
    return mqtt 