# -*- coding: utf-8 -*-

"""AWS MP utils cli module."""

# Copyright (c) 2025 SUSE LLC
#
# This file is part of aws_mp_utils. aws_mp_utils provides an
# api and command line utilities for handling marketplace catalog API
# in the AWS Cloud.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import logging

import click

from aws_mp_utils.changeset import (
    get_change_set,
    get_change_set_status
)
from aws_mp_utils.scripts.container import container
from aws_mp_utils.scripts.image import image
from aws_mp_utils.scripts.offer import offer
from aws_mp_utils.scripts.cli_utils import (
    add_options,
    get_config,
    process_shared_options,
    shared_options,
    echo_style,
    get_mp_client,
    handle_errors
)


# -----------------------------------------------------------------------------
# license function
def print_license(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('GPLv3+')
    ctx.exit()


# -----------------------------------------------------------------------------
# Main function
@click.group()
@click.version_option()
@click.option(
    '--license',
    is_flag=True,
    callback=print_license,
    expose_value=False,
    is_eager=True,
    help='Show license information.'
)
@click.pass_context
def main(context):
    """
    The command line interface provides AWS Marketplace Catalog utilities.

    This includes handling change sets for images, containers and offers.
    """
    if context.obj is None:
        context.obj = {}
    pass


# -----------------------------------------------------------------------------
@main.command
@click.option(
    '--change-set-id',
    type=click.STRING,
    required=True,
    help='The unique identifier for the change set that you want to describe.'
)
@add_options(shared_options)
@click.pass_context
def describe_change_set(
    context,
    change_set_id,
    **kwargs
):
    """
    Returns a json dictionary with info about the given changeset.
    """
    process_shared_options(context.obj, kwargs)
    config_data = get_config(context.obj)
    logger = logging.getLogger('aws_mp_utils')
    logger.setLevel(config_data.log_level)

    client = get_mp_client(
        config_data.profile,
        config_data.region
    )

    with handle_errors(config_data.log_level, config_data.no_color):
        change_set = get_change_set(client, change_set_id)

    echo_style(json.dumps(change_set), config_data.no_color, fg='green')


# -----------------------------------------------------------------------------
@main.command(name='get-change-set-status')
@click.option(
    '--change-set-id',
    type=click.STRING,
    required=True,
    help='The unique identifier for the change set that you want to describe.'
)
@add_options(shared_options)
@click.pass_context
def describe_change_set_status(
    context,
    change_set_id,
    **kwargs
):
    """
    Returns a string value of the given change set status.

    Possible status values are:
        'PREPARING'|'APPLYING'|'SUCCEEDED'|'CANCELLED'|'FAILED'
    """
    process_shared_options(context.obj, kwargs)
    config_data = get_config(context.obj)
    logger = logging.getLogger('aws_mp_utils')
    logger.setLevel(config_data.log_level)

    client = get_mp_client(
        config_data.profile,
        config_data.region
    )

    with handle_errors(config_data.log_level, config_data.no_color):
        status = get_change_set_status(client, change_set_id)

    if status in ('preparing', 'applying'):
        color = 'yellow'
    elif status in ('cancelled', 'failed'):
        color = 'red'
    else:
        color = 'green'

    echo_style(status, config_data.no_color, fg=color)


main.add_command(image)
main.add_command(container)
main.add_command(offer)
