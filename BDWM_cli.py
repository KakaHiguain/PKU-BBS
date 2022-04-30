#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 19:22:48 2020

@author: KakaHiguain@BDWM
"""

import datetime

import click
import dateutil.parser

from BDWM import BDWM
from utils import read_file, get_mail_postid_and_time, get_postid_list_from_internal_postids


def _get_bdwm_client(id, password_file):
    password = read_file(password_file).strip('\n') if password_file else None
    if not password:
        password = click.prompt('请输入密码 (不会显示)：', hide_input=True)
    return BDWM(id, password)


def _common_options(func):
    decorators = [
        click.option('--id', required=True, prompt='北大未名用户名', default='PES'),
        click.option('-pf', '--password-file', help='The file containing your password'),
    ]
    for decorator in reversed(decorators):
        func = decorator(func)
    return func


@click.group()
def main():
    pass


@main.command()
@_common_options
@click.option('-b', '--board', required=True, help='The name of the board you want to post to')
@click.option('--title', required=True, help='The post title')
@click.option('--content', help='The post content')
@click.option('--content-file', help='The file containing the post content')
@click.option('--no-reply', is_flag=True, default=False, help='Not allow other people to reply')
@click.option('--parent-id', default=None, help='The thread id of the main post you reply to')
def post(id, password_file, board, title, content, content_file, no_reply, parent_id):
    bdwm = _get_bdwm_client(id, password_file)
    if not content:
        content = read_file(content_file) if content_file else ''
    bdwm.create_post(board, title, content, no_reply=no_reply, parent_id=parent_id)


@main.command()
@_common_options
@click.option('-b', '--board', required=True, help='The name of the board you want to post to')
@click.option('--postid', required=True, help='The ID of the post you want to edit')
@click.option('--title', required=True, help='The post title')
@click.option('--content', help='The post content')
@click.option('--content-file', help='The file containing the post content')
def edit(id, password_file, board, postid, title, content, content_file):
    bdwm = _get_bdwm_client(id, password_file)
    if not content:
        content = read_file(content_file) if content_file else ''
    bdwm.edit_post(board, postid, title, content)


@main.command()
@_common_options
@click.option('-b', '--board', required=True, help='The name of the board you want to import collection')
@click.option('--path', required=True, help='Collection path we see on the website')
@click.option('--postids', help='The IDs of the post you want to collect, split by ","')
@click.option('--in-postids', 'internal_postids',
              help='The internal IDs of the post you want to collect, split by "," ,'
                   'You can use ~ to represent consecutive postids.'
                   'For example: 11233,12345~12349,12351~12352.')
@click.option('--sort', is_flag=True, default=False, help='Sort the posts by their ids')
@click.option('--create-if-not-exists', is_flag=True, default=False,
              help='Create a new sub-directory if the path does not exists.')
def import_collection(
        id, password_file, board, path, postids, internal_postids, sort, create_if_not_exists):
    bdwm = _get_bdwm_client(id, password_file)
    api_path = bdwm.get_collection_dir_path(board, path, create_if_not_exists)

    if not postids:
        if not internal_postids:
            raise ValueError('Please specify postids or internal postids')
        postid_list = get_postid_list_from_internal_postids(bdwm, board, internal_postids)
    else:
        postid_list = postids.split(',')

    if sort:
        postid_list.sort()

    for postid in postid_list:
        bdwm.add_new_collection(board, api_path, int(postid))


def _parse_datetime(ctx, param, value) -> datetime.datetime:
    return dateutil.parser.parse(value)


@main.command()
@_common_options
@click.option('-b', '--board', required=True, prompt='转发的目标版面')
@click.option('--start', required=True, callback=_parse_datetime, prompt='开始时间, MM/DD HH:MM')
@click.option('--end', required=True, callback=_parse_datetime, prompt='结束时间, MM/DD HH:MM')
@click.option('--start-post', default='', prompt='转发前发的帖')
@click.option('--end-post', default='', prompt='转发后发的帖')
def forward_mail_within_time_range(id, password_file, board, start, end, start_post, end_post):
    if start > end:
        raise ValueError('Start time can not later than end time!')
    bdwm = _get_bdwm_client(id, password_file)
    # 2020-08-06 16:05:31
    page = 1
    finished = False
    postids = []
    while not finished:
        mails = get_mail_postid_and_time(bdwm.get_mail_content(page=page))
        for mail in mails:
            if mail[1] < start:
                finished = True
                break
            if mail[1] > end:
                continue
            postids.append(mail[0])
        page += 1

    if start_post:
        bdwm.create_post(board, start_post)
    for postid in reversed(postids):
        bdwm.forward_mail_to_board(board, postid)
    if end_post:
        bdwm.create_post(board, end_post)


if __name__ == '__main__':
    main()
