#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:37:13 2020

@author: KakaHiguain@BDWM
"""

from hashlib import md5
import json
import requests
import urllib.parse

from utils import get_content_from_raw_string, bold_green, bold_red


class BDWM:
    class RequestError(RuntimeError):
        pass

    _HOST = 'bbs.pku.edu.cn'
    _BOARD_MODES = {'topic', 'single'}
    _BOARD_CONFIG = 'board.json'
    _COLLECTION_BASE_PATH_PATTERN = "groups/GROUP_{}/{}"
    _POST_ACTION_NAME = {
        'mark': '保留',
        'unmark': '取消保留',
        'digest': '文摘',
        'undigest': '取消文摘',
        'top': '置顶',
        'untop': '取消置顶',
        'highlight': '高亮',
        'unhighlight': '取消高亮',
    }

    def __init__(self, id, passwd):
        self._id = id
        self._passwd = passwd
        self._session = requests.session()
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.122 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': self._HOST,
            'X-Requested-With': 'XMLHttpRequest',
        }
        skey, self._uid = self._login()
        self._cookie = 'skey={}; uid={}'.format(skey, self._uid)
        self._headers["Cookie"] = self._cookie
        with open(self._BOARD_CONFIG) as f:
            self._boards = json.load(f)

    def _get_board_info(self, board_name, key) -> int:
        if board_name not in self._boards:
            raise ValueError(bold_red('没有这个版面，或暂不支持这个版面'))
        return self._boards[board_name][key]

    def _get_action_url(self, action_name, **params):
        base_url = 'https://{}/v2/{}.php'.format(self._HOST, action_name)
        if not params:
            return base_url
        return base_url + '?' + urllib.parse.urlencode(params)
        
    def _login(self):
        token = md5('{1}{0}{1}'.format(self._id, self._passwd).encode('utf8'))
        data = {
            "username": self._id,
            "password": self._passwd,
            "keepalive": '0',
            "t": token.hexdigest()
        }
        self._get_response_data('ajax/login', data, '登录')
        
        requests.cookies.RequestsCookieJar()
        cookies_dict = self._session.cookies.get_dict()
        return cookies_dict['skey'], cookies_dict['uid']

    # Functions for getting page.
    def _get_page_content(self, url):
        return self._session.post(url, headers=self._headers).text
    
    def get_board_page(self, board_name, page: int = 1, mode='topic'):
        assert mode in self._BOARD_MODES, "Not a correct mode!"
        page_url = self._get_action_url(
            'thread', bid=self._get_board_info(board_name, 'id'), mode=mode, page=page)
        return self._get_page_content(page_url)

    def get_single_post_page(self, board_name, postid: int):
        page_url = self._get_action_url(
            'post-read-single', bid=self._get_board_info(board_name, 'id'), postid=postid)
        return self._get_page_content(page_url)

    def get_post_page(self, board_name, threadid: int):
        page_url = self._get_action_url(
            'post-read', bid=self._get_board_info(board_name, 'id'), threadid=threadid)
        return self._get_page_content(page_url)

    def get_mail_page(self, postid: int):
        page_url = self._get_action_url('mail-read', postid=postid)
        return self._get_page_content(page_url)

    def get_mail_list_page(self):
        page_url = self._get_action_url('mail')
        return self._get_page_content(page_url)

    # Functions for getting action response.
    def _get_response_data(self, relative_url, data: dict, action_string) -> dict:
        response_data = json.loads(
            self._session.post(self._get_action_url(relative_url), 
                               headers=self._headers,
                               data=data).text)
        if not response_data['success']:
            raise BDWM.RequestError(bold_red(action_string + '失败！'))
        return response_data

    @classmethod
    def _get_post_info(cls, mail_re, no_reply, parent_id):
        post_info = '"no_reply":{},"mail_re":{}'.format(str(no_reply).lower(), str(mail_re).lower())
        if parent_id:
            post_info += ',"parentid":{}'.format(parent_id)
        return '{{{}}}'.format(post_info)

    def create_post(self, board_name, title, content_string,
                    mail_re=True, no_reply=False, signature=None, parent_id: int = None):
        content = get_content_from_raw_string(content_string)
        bid = self._get_board_info(board_name, 'id')

        data = {
            'title': title,
            'content': content,
            'bid': bid,
            'postinfo': self._get_post_info(mail_re, no_reply, parent_id),
        }
        if signature is not None:
            data['signature'] = signature

        action = '回帖' if parent_id else '发帖'
        response_data = self._get_response_data('ajax/create_post', data, action)
        postid = response_data['result']['postid']
        post_link = self._get_action_url('post-read-single', bid=bid, postid=postid)
        print(bold_green(action + '成功！') + '帖子链接：{}'.format(post_link))
        return response_data['result']

    def reply_post(self, board_name, main_postid: int, main_title, content_string,
                   mail_re=True, no_reply=False, signature=None):
        """Reply to the post with main_postid and main_title"""
        return self.create_post(board_name, "Re: " + main_title, content_string,
                                mail_re, no_reply, signature, parent_id=main_postid)

    def edit_post(self, board_name, postid: int, title, content_string, signature=None):
        content = get_content_from_raw_string(content_string)
        bid = self._get_board_info(board_name, 'id')
        data = {
            'title': title,
            'content': content,
            'bid': bid,
            'postid': postid,
            'postinfo': '{}',
        }
        if signature is not None:
            data['signature'] = signature
        self._get_response_data('ajax/edit_post', data, '修改帖子')
        post_link = self._get_action_url('post-read-single', bid=bid, postid=postid)
        print(bold_green('修改帖子成功！') + '帖子链接：{}'.format(post_link))
        
    def forward_post(self, from_board_name, to_board_name, postid: int):
        data = {
            'from': 'post',
            'bid': self._get_board_info(from_board_name, 'id'),
            'postid': postid,
            'to': 'post',
            'tobid': self._get_board_info(to_board_name, 'id'),
        }
        self._get_response_data('ajax/forward', 
                                data, 
                                '转帖到{}版'.format(to_board_name))
        print(bold_green('已成功转发到{}版！'.format(to_board_name)))
    
    def operate_post(self, board_name, postid_list, action):
        assert action in self._POST_ACTION_NAME, '无效的帖子操作！'
        data = {
            "bid": self._get_board_info(board_name, 'id'),
            "list": '[{}]'.format(','.join(postid_list)),
            "action": action
        }
        self._get_response_data(
            'ajax/operate_post', data, 
            '{}帖子'.format(self._POST_ACTION_NAME[action]))
        print(bold_green('{}帖子成功！'.format(self._POST_ACTION_NAME[action])))

    def get_post_by_num(self, board_name, internal_postid: int):
        """Get information of a post from its board name and the postid inside this board"""
        data = {
            "bid": self._get_board_info(board_name, 'id'),
            "num": internal_postid,
        }
        return self._get_response_data('ajax/get_post_by_num', data, '按照序号查找版内帖子')

    def get_collection_items(self, path):
        data = {"path": path}
        collection_items = {}
        response_data = self._get_response_data('ajax/get_collection_items', data, '获取精华区目录')
        for directory in response_data["result"]:
            if directory["isdir"]:
                collection_items[directory["title"]] = directory['path']
        return collection_items

    def create_collection_dir(self, path, title, bms=''):
        data = {
            "base": path,
            "title": title,
            "bms": bms
        }
        response_data = self._get_response_data('ajax/create_collection_dir', data, '创建精华区目录')
        print(bold_green('已创建精华区目录 "{}"'.format(title)))
        return response_data['name']

    def add_new_collection(self, board_name, path, postid: int):
        data = {
            "from": "post",
            "bid": self._get_board_info(board_name, 'id'),
            "postid": postid,
            "base": path
        }
        response_data = self._get_response_data('ajax/collection_import', data, '添加精华区文件')
        print(bold_green('添加精华区文件成功！'))
        return response_data['name']

    def get_collection_dir_path(self, board_name, directory_path, create_if_not_exists=False):
        """Get the collection directory path for BDWM api, the input directory_path is the path
        we see on the website.
        For example, the api path of "历期起居注/2020年11月" collection directory in WMReview board
        is "groups/GROUP_0/WMReview/D5448A5D2/D86B358DF".
        If create_if_not_exists is False, we will raise error when the directory doesn't exist,
        otherwise we will create a new one.
        """
        section = self._get_board_info(board_name, 'section')
        current_api_path = self._COLLECTION_BASE_PATH_PATTERN.format(section, board_name)
        current_path = ''
        parts = directory_path.split('/')
        for dir_name in parts:
            if not dir_name:
                continue
            if not current_path:
                current_path = dir_name
            else:
                current_path = current_path + '/' + dir_name
            collection_items = self.get_collection_items(current_api_path)
            if dir_name not in collection_items:
                if not create_if_not_exists:
                    raise ValueError(bold_red('{}版精华区不存在目录：【{}】！'.format(
                        board_name, current_path)))
                sub_path = self.create_collection_dir(current_api_path, dir_name, bms=self._id)
            else:
                sub_path = collection_items[dir_name]
            current_api_path = current_api_path + '/' + sub_path

        return current_api_path
