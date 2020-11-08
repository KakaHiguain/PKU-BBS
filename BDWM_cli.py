#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 19:22:48 2020

@author: KakaHiguain@BDWM
"""

import click

from BDWM import BDWM
from utils import read_file


def _get_bdwm_client(id, password, password_file):
    if not password:
        if not password_file:
            raise ValueError('Please specify password or password_file')
        password = read_file(password_file).strip('\n')
    return BDWM(id, password)


@click.group()
def main():
    pass


@main.command()
@click.option('--id', required=True, help='Your BDWM ID')
@click.option('--password', help='The password of your BDWM ID')
@click.option('--password-file', help='The file containing your password')
@click.option('--board', required=True, help='The name of the board you want to post to')
@click.option('--title', required=True, help='The post title')
@click.option('--content', help='The post content')
@click.option('--content-file', help='The file containing the post content')
@click.option('--no-reply', type=click.BOOL, default=False, help='Not allow other people to reply')
@click.option('--parent-id', default=None, help='The thread id of the main post you reply to')
def post(id, password, password_file, board, title, content, content_file, no_reply, parent_id):
    bdwm = _get_bdwm_client(id, password, password_file)
    if not content:
        content = read_file(content_file) if content_file else ''
    bdwm.create_post(board, title, content, no_reply=no_reply, parent_id=parent_id)


@main.command()
@click.option('--id', required=True, help='Your BDWM ID')
@click.option('--password', help='The password of your BDWM ID')
@click.option('--password-file', help='The file containing your password')
@click.option('--board', required=True, help='The name of the board you want to post to')
@click.option('--postid', required=True, help='The ID of the post you want to edit')
@click.option('--title', required=True, help='The post title')
@click.option('--content', help='The post content')
@click.option('--content-file', help='The file containing the post content')
def edit(id, password, password_file, board, postid, title, content, content_file):
    bdwm = _get_bdwm_client(id, password, password_file)
    if not content:
        content = read_file(content_file) if content_file else ''
    bdwm.edit_post(board, postid, title, content)


@main.command()
@click.option('--id', required=True, help='Your BDWM ID')
@click.option('--password', help='The password of your BDWM ID')
@click.option('--password-file', help='The file containing your password')
@click.option('--board', required=True, help='The name of the board you want to import collection')
@click.option('--path', required=True, help='Collection path we see on the website')
@click.option('--postids', required=True,
              help='The IDs of the post you want to collect, split by ","')
@click.option('--create-if-not-exists', is_flag=True, default=False,
              help='Create a new sub-directory if the path does not exists.')
def import_collection(id, password, password_file, board, path, postids, create_if_not_exists):
    bdwm = _get_bdwm_client(id, password, password_file)
    api_path = bdwm.get_collection_dir_path(board, path, create_if_not_exists)

    for postid in postids.split(','):
        bdwm.add_new_collection(board, api_path, int(postid))


if __name__ == '__main__':
    main()
