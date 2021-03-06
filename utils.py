#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:37:13 2020

@author: KakaHiguain@BDWM
"""
import datetime
from typing import List, Tuple

from bs4 import BeautifulSoup


SEPARATE_BAR = "======================"


def get_content_from_raw_string(content_string):
    parts = content_string.split('\u001B[')
    change_font = content_string.startswith('\u001B[')
    template = '{{"type":"ansi","bold":{},"underline":{},"fore_color":{},' \
               '"back_color":{},"content":"{}"}}'
    bold, underline, fore_color, back_color = 'false', 'false', 9, 9
    res = []
    for part in parts:
        pos = part.find('m')
        # The first part may not change font.
        if not change_font:
            pos = -1
            change_font = True
        if pos > -1:
            font_codes = part[:pos].split(';')
            if len(font_codes) == 1 and font_codes[0] == '':
                font_codes[0] = '0'
            for code in font_codes:
                code = int(code)
                if code in range(30, 40):
                    fore_color = code - 30 if code <= 37 else 9
                elif code in range(40, 50):
                    back_color = code - 40 if code <= 47 else 9
                elif code == 1:
                    bold = 'true'
                elif code == 4:
                    underline = 'true'
                elif code == 0:
                    bold, underline, fore_color, back_color = 'false', 'false', 9, 9
                else:
                    pass
        content = part[pos + 1:].replace("\\", '\\\\') \
                                .replace('\"', '\\\"') \
                                .replace('\n', '\\n')
        res.append(template.format(bold, underline, fore_color, back_color, content))

    return '[{}]'.format(','.join(res)).replace('\x1b', '')


def yes_or_no_prompt(prompt_string, func, **argv):
    ans = input('{}(yes/No)'.format(prompt_string))
    if ans and ans[0] in ['y', 'Y']:
        func(**argv)
    else:
        print('跳过~')


def wrap_separate_bar(s):
    return '{0}{1}{0}'.format(SEPARATE_BAR, s)


def format_string(s, format_code):
    return '\033[{}m{}\033[0m'.format(format_code, s)


def bold_string(s):
    return format_string(s, '1')


def bold_red(s):
    return format_string(s, '1;31')


def bold_green(s):
    return format_string(s, '1;32')


def bold_yellow(s):
    return format_string(s, '1;33')


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def parse_time_from_string(mail_time_str) -> datetime.datetime:
    return datetime.datetime(
        int(mail_time_str[0:4]), int(mail_time_str[5:7]), int(mail_time_str[8:10]),
        int(mail_time_str[11:13]), int(mail_time_str[14:16]), int(mail_time_str[17:19]))


def get_mail_postid_and_time(page_content) -> List[Tuple[int, datetime.datetime]]:
    soup = BeautifulSoup(page_content, features="html.parser")

    mails = soup.find_all('div', attrs={'class': 'list-item row-wrapper'})
    postids = []
    for mail in mails:
        if 'data-itemid' not in mail.attrs:
            continue
        mail_time_str = mail.find('span', attrs={'class': 'time l'}).text
        # 2020-08-06 16:05:31
        mail_datetime = parse_time_from_string(mail_time_str)
        postids.append((mail.attrs['data-itemid'], mail_datetime))
    return postids
