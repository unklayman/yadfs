#!/usr/bin/env python3.5
import click
from client.client import Client

# CLI
@click.group(invoke_without_command=False)
@click.pass_context
def cli(ctx):
    pass

@cli.command()
@click.argument('path', default="/")
def ls(path):
    """List directory contents"""
    cl = Client()
    dir_ls = cl.list_dir(path)
    print(dir_ls)

@cli.command()
@click.argument('path')
def mkdir(path):
    """Create a directory"""
    cl = Client()
    res = cl.create_dir(path)
    print(res)

@cli.command()
@click.argument('path')
def rmdir(path):
    """Remove a directory"""
    cl = Client()
    res = cl.delete_dir(path)
    print(res)

@cli.command()
@click.argument('path')
def upload(path):
    """Create a file"""
    cl = Client()
    res = cl.create_file(path)
    print(res)

@cli.command()
@click.argument('path')
def rm(path):
    """Delete a file"""
    cl = Client()
    res = cl.delete_file(path)
    print(res)

@cli.command()
@click.argument('path')
def status(path):
    """Check if path refers to file or directory"""
    cl = Client()
    res = cl.path_status(path)
    print(res)

@cli.command()
@click.argument('path')
def download(path):
    """Download a file"""
    cl = Client()
    res = cl.download_file(path)
    print(res)

if __name__ == '__main__':
    cli()