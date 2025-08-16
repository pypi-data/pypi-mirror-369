#!/usr/bin/env python3
"""CLI for managing device operations."""

import click
from .cli_core import (
    create_client, handle_error, get_client_args
)


def create_device_group():
    """Create and return the device command group."""
    @click.group()
    @click.pass_context
    def device(ctx):
        """Manage device operations."""
        pass

    @device.command('info')
    @click.pass_context
    def get_info(ctx):
        """Get device information including model, firmware, and capabilities."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                info = client.device.get_info()
                click.echo("Device Information:")
                for key, value in info.items():
                    click.echo(f"   {key}: {value}")
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @device.command('health')
    @click.pass_context
    def check_health(ctx):
        """Check if the device is responsive and healthy."""
        try:
            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.device.check_health()
                
                if not result:
                    return handle_error(ctx, "Device is not healthy")
                    
                click.echo(click.style("Device is healthy!", fg="green"))
                return 0
        except Exception as e:
            return handle_error(ctx, e)

    @device.command('restart')
    @click.option('--force', is_flag=True, help='Force restart without confirmation')
    @click.pass_context
    def restart(ctx, force):
        """Restart the device (requires confirmation unless --force is used)."""
        try:
            if not force and not click.confirm('Are you sure you want to restart the device?'):
                click.echo('Restart cancelled.')
                return 0

            with create_client(**get_client_args(ctx.obj)) as client:
                result = client.device.restart()

                if not result:
                    return handle_error(ctx, "Failed to restart device")
                    
                click.echo(click.style(
                    "Device restart initiated. The device will be unavailable for a few minutes.",
                    fg="yellow"
                ))
                return 0
        except Exception as e:
            return handle_error(ctx, e)
    
    return device
