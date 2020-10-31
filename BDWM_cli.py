#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 19:22:48 2020

@author: KakaHiguain@BDWM
"""

import click

from BDWM import BDWM
from utils import read_file


@click.group()
def main():
    pass


@main.command()
@click.option('--id', required=True, help='Your BDWM ID')
@click.option('--password', help='The password of your BDWM ID')
@click.option('--password_file', help='The file containing your password')
@click.option('--board_name', required=True, help='The name of the board you want to post to')
@click.option('--title', required=True, help='The post title')
@click.option('--content', help='The post content')
@click.option('--content_file', help='The file containing the post content')
@click.option('--no_reply', type=click.BOOL, default=False, help='Not allow other people to reply')
@click.option('--parent_id', default=None, help='The thread id of the main post you reply to')
def post(id, password, password_file, board_name, title, content, content_file, no_reply, parent_id):
    if password ^ password_file:
        raise ValueError('Please specify either password or password_file, and not both')
    if content ^ content_file:
        raise ValueError('Please specify either content or content_file, and not both')

    if not password:
        password = read_file(password_file).strip('\n')
    bdwm = BDWM(id, password)
    if not content:
        content = read_file(content_file).strip('\n')
    bdwm.create_post(board_name, title, content, no_reply=no_reply, parent_id=parent_id)


@main.command()
@click.option('--id', required=True, help='Your BDWM ID')
@click.option('--password', help='The password of your BDWM ID')
@click.option('--password_file', help='The file containing your password')
@click.option('--board_name', required=True, help='The name of the board you want to post to')
@click.option('--postid', required=True, help='The id of the post you want to edit')
@click.option('--title', required=True, help='The post title')
@click.option('--content', help='The post content')
@click.option('--content_file', help='The file containing the post content')
def edit(id, password, password_file, board_name, title, postid, content, content_file):
    if password ^ password_file:
        raise ValueError('Please specify either password or password_file, and not both')
    if content ^ content_file:
        raise ValueError('Please specify either content or content_file, and not both')

    if not password:
        password = read_file(password_file).strip('\n')
    bdwm = BDWM(id, password)
    if not content:
        content = read_file(content_file).strip('\n')
    bdwm.edit_post(board_name, title, postid, content)
