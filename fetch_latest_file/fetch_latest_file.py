#!/usr/bin/env python3
import re
import os
import sys
import time
import arrow
import shutil
from pathlib import Path
import json
import inquirer
import click
import subprocess
from . import cli
from .config import pass_config


@cli.command()
@pass_config
def fetch(config):
    pass

def _get_files(config, shell):
    files = list(filter(bool, shell(["ls", "-tr", config['path']])))
    for file in files:
        if re.findall(config.get('regex', '.*'), file):
            yield file

def transfer(config, filename):
    subprocess.run([
        "rsync",
        f"{config['host']}:{config['path']}/{filename}",
        config['destination'],
        "-arP"
    ])

@cli.command(help="Choose specific file to download")
@pass_config
def choose(config):
    with config.shell() as (config, shell):
        files = list(_get_files(config, shell))
        answer = inquirer.prompt([
            inquirer.List('file', "Please choose:", choices=list(reversed(files)))
        ])
        if not answer:
            sys.exit(0)
        file = answer['file']
        transfer(config, file)

@cli.command()
@click.option('-f', '--filename', required=True)
@click.option('-H', '--host', required=True)
@click.option('-U', '--username', required=False)
@click.option('-r', '--regex', required=True, default=".*")
@click.option('-p', '--path', required=True)
@click.option('-d', '--destination', required=True)
@pass_config
def add(config, filename, host, username, regex, path, destination):
    config.add(
        filename=filename,
        host=host,
        username=username,
        path=path,
        regex=regex,
        destination=destination,
        )
    click.secho("Added host.", fg='green')

@cli.command(default_command=True)
@pass_config
def fetch(config):
    with config.shell() as (config, shell):
        files = list(_get_files(config, shell))
        if not files:
            click.secho("No files found.")
            sys.exit(1)
        file = files[-1]
        transfer(config, file)
