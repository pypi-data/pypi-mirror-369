#!/usr/bin/env python

import pandas as pd
import click
import re
import os
from google.protobuf.json_format import MessageToDict


class FakeDataSource:

    def __init__(self, value):
        self.value = value


def set_pandas_display():
    """Reset the default display parameters for printing pandas dataframes.

    By default pandas chooses very small column widths and shows only
    a few rows, etc.  The TS cli prints information in dataframes in
    some cases, so we'll reset these parameters to more appropriate
    values.
    """
    pd.set_option('display.width', 220)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 120)


def protobuf_to_dict(obj):
    """Helper Function to take a protobuf object and return a Python dict"""

    info = MessageToDict(obj, preserving_proto_field_name=True)
    info = pd.json_normalize(info, sep='.').to_dict(orient='records')
    if isinstance(info, list) and len(info) > 0:
        info = info[0]
    return info


def match_columns(columns, exprs):
    """
    """
    keep = []
    for col in columns:
        if col in keep:
            continue
        for expr in exprs:
            if col in keep:
                continue
            if re.match(expr, col):
                keep.append(col)
    return keep


def chunk_array(array, n):
    """Yield successive n-sized chunks from list 'array'."""
    for i in range(0, len(array), n):
        yield array[i:i + n].copy()


def get_author(author, raise_on_failure=False):
    """Read author from an environment variable, or return as-is.

    If the user sets author to 'TERRASCOPE_AUTHOR', we'll read that
    variable and return its value.  Otherwise, we'll assume the user
    has already set it and just return what we were given.
    """

    env_var = 'TERRASCOPE_AUTHOR'
    if author == env_var:
        author = os.environ.get(author, None)
        if raise_on_failure and author is None:
            raise RuntimeError(f"Environment variable '{env_var}' is not set")

    return author


def override_manifest_param(name, value, manifest_dict, do_overwrite=False):
    """
    """

    # If the user provided a value, use it, otherwise get it from the manifest.
    if value is None:

        value = manifest_dict.get(name, None)
        if value is None:
            raise ValueError(f"Must provide parameter '{name}' in the manifest, or on the command line")

    if do_overwrite:
        manifest_dict[name] = value

    return value


def increment_version(current_version, level='patch'):

    major, minor, patch = [int(v) for v in current_version.split('.')]
    if level == 'patch':
        patch += 1
    elif level == 'minor':
        minor += 1
        patch = 0
    elif level == 'major':
        major += 1
        minor = 0
        patch = 0

    new_version = '.'.join([str(major), str(minor), str(patch)])
    return new_version


def set_version(version_input, manifest, do_overwrite=False):
    """
    """
    manifest_version = manifest['metadata']['version']

    if version_input:
        if version_input in ['patch', 'minor', 'major']:
            new_version = increment_version(manifest_version, level=version_input)
        else:
            new_version = version_input
    else:
        new_version = manifest_version

    if do_overwrite:
        manifest['metadata']['version'] = new_version

    return new_version


def echo_highlight_suffix(message, suffix, color):

    click.echo(message, nl=False)
    click.secho(f"{suffix}", fg=color)
