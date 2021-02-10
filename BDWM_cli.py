#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 19:22:48 2020

@author: KakaHiguain@BDWM
"""

from typing import List

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


def _get_postid_list_from_internal_postids(bdwm, board, internal_postids) -> List[str]:
    parts = internal_postids.split(',')
    internal_postid_list = []
    for part in parts:
        pos = part.find('~')
        if pos == -1:
            internal_postid_list.append(int(part))
        else:
            left_bound, right_bound = int(part[:pos]), int(part[pos + 1:])
            if left_bound > right_bound:
                raise ValueError('Invalid interval: {}!'.format(part))
            internal_postid_list.extend(range(left_bound, right_bound + 1))

    postid_list = []
    for internal_postid in internal_postid_list:
        post_info = bdwm.get_post_by_num(board, internal_postid)
        postid_list.append(post_info['list'][0]['postid'])

    return postid_list


@main.command()
@click.option('--id', required=True, help='Your BDWM ID')
@click.option('--password', help='The password of your BDWM ID')
@click.option('--password-file', help='The file containing your password')
@click.option('--board', required=True, help='The name of the board you want to import collection')
@click.option('--path', required=True, help='Collection path we see on the website')
@click.option('--postids', help='The IDs of the post you want to collect, split by ","')
@click.option('--in-postids', 'internal_postids',
              help='The internal IDs of the post you want to collect, split by "," ,'
                   'You can use ~ to represent consecutive postids.'
                   'For example: 11233,12345~12349,12351~12352.')
@click.option('--sort', is_flag=True, default=False, help='Sort the posts by their ids')
@click.option('--create-if-not-exists', is_flag=True, default=False,
              help='Create a new sub-directory if the path does not exists.')
def import_collection(id, password, password_file, board, path, postids, internal_postids,
                      sort, create_if_not_exists):
    bdwm = _get_bdwm_client(id, password, password_file)
    api_path = bdwm.get_collection_dir_path(board, path, create_if_not_exists)

    if not postids:
        if not internal_postids:
            raise ValueError('Please specify postids or internal postids')
        postid_list = _get_postid_list_from_internal_postids(bdwm, board, internal_postids)
    else:
        postid_list = postids.split(',')

    if sort:
        postid_list.sort()

    for postid in postid_list:
        bdwm.add_new_collection(board, api_path, int(postid))


@main.command()
@click.option('--id', required=True, help='Your BDWM ID')
@click.option('--password', help='The password of your BDWM ID')
@click.option('--password-file', help='The file containing your password')
@click.option('--board', required=True, help='The name of the board you want to post to')
# TODO: Add validation.
@click.option('--start-datetime', required=True, help='The start date and time, YYYYMMDDHHMMSS')
@click.option('--end-datetime', required=True, help='The end date and time, YYYYMMDDHHMMSS')
def forward_mail_within_time_range(id, password, password_file, board, start_datetime, end_datetime):
    bdwm = _get_bdwm_client(id, password, password_file)
    # TBD

if __name__ == '__main__':
    main()
