# -*- coding: utf-8 -*-
# @File : py_request.py
# @Author : mocobk
# @Email : mailmzb@qq.com
# @Time : 2020/6/25 5:26 下午
import argparse
import json
import re
import shlex
import traceback
import urllib.parse
from collections import namedtuple
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from pprint import pformat

import requests
from flask import g
from yapf.yapflib.yapf_api import FormatCode


def parse_url(full_url):
    """query以字典的形式返回"""
    urlparse = urllib.parse.urlparse(full_url)
    url = urlparse.scheme + '://' + urlparse.netloc + urlparse.path
    query_dict = dict(urllib.parse.parse_qsl(urlparse.query, keep_blank_values=True))
    return url, query_dict


class FiddlerRawParse:
    def __init__(self, raw_string):
        self.request_list = raw_string.strip().splitlines()
        self.ParsedContext = self.parse_string()

    def parse_string(self):
        ParsedContext = namedtuple('ParsedContext', ['method', 'url', 'query', 'data', 'headers'])
        first_line_list = self.request_list[0].split()
        method = first_line_list[0].lower()
        full_url = first_line_list[1]
        url, query = parse_url(full_url)
        headers = self.parse_header()
        data = self.parse_body()
        return ParsedContext(method=method, url=url, query=query, headers=headers, data=data)

    def parse_header(self):
        if '' in self.request_list:
            split_index = self.request_list.index('')
            header_list = self.request_list[1:split_index]
        else:
            header_list = self.request_list[1:]
        headers = {}
        for each in header_list:
            each_tuple = each.split(':', maxsplit=1)

            headers[each_tuple[0]] = each_tuple[1].strip()
        return headers

    def parse_body(self):
        data = ''
        if '' in self.request_list:
            split_index = self.request_list.index('')
            data = '\n'.join(self.request_list[split_index + 1:])
        return data


class CurlParse:
    def __init__(self, curl_command):
        self.curl_command = curl_command
        self.ParsedContext = self.parse_context()

    def parse_context(self):
        ParsedContext = namedtuple('ParsedContext', ['method', 'url', 'query', 'data', 'headers'])
        parser = argparse.ArgumentParser()
        parser.add_argument('command')
        parser.add_argument('url')
        parser.add_argument('-d', '--data')
        parser.add_argument('-b', '--data-binary', default=None)
        parser.add_argument('-X', default='')
        parser.add_argument('-H', '--header', action='append', default=[])
        parser.add_argument('--compressed', action='store_true')
        parser.add_argument('--insecure', action='store_true')

        tokens = shlex.split(self.curl_command)
        parsed_args = parser.parse_args(tokens)

        data = parsed_args.data or parsed_args.data_binary
        method = "get"
        if data:
            method = 'post'
        if parsed_args.X:
            method = parsed_args.X.lower()

        url, query = parse_url(parsed_args.url)

        headers = {}
        for curl_header in parsed_args.header:
            if curl_header.startswith(':'):
                occurrence = [m.start() for m in re.finditer(':', curl_header)]
                header_key, header_value = curl_header[:occurrence[1]], curl_header[occurrence[1] + 1:]
            else:
                header_key, header_value = curl_header.split(":", 1)
            headers[header_key] = header_value.strip()

        return ParsedContext(method=method, url=url, query=query, headers=headers, data=data)


def create_script(request_data: str):
    if request_data.startswith('curl'):
        parse_string = CurlParse(request_data).ParsedContext
    else:
        parse_string = FiddlerRawParse(request_data).ParsedContext
    url = parse_string.url
    method = parse_string.method
    headers = parse_string.headers
    params = parse_string.query
    data = parse_string.data

    script_headers = ['# -*- coding:utf-8 -*-', 'import requests']
    script_tail = ["if __name__ == '__main__':", '    print(response.status_code)\n']

    script_body = []
    method_params = []
    if headers:
        script_body.append('headers = ' + str(headers))
        method_params.append('headers=headers')
    if params:
        script_body.append('params = ' + str(params))
        method_params.append('params=params')
    if data:
        try:
            data = json.loads(data)  # 先判断是否是json
        except JSONDecodeError:
            parse_data = urllib.parse.parse_qsl(data, keep_blank_values=True)
            if parse_data:  # 再判断是否是url encoded
                data = dict(parse_data)

        script_body.append('data = ' + pformat(data, width=120))
        if 'json' in headers.get('Content-Type', ''):
            method_params.append('json=data')
        else:
            method_params.append('data=data')
    method_params = ', '.join(method_params)
    script_body.append('response = requests.{method}("{url}", {method_params})'.format(method=method, url=url,
                                                                                       method_params=method_params))
    script = '\n\n'.join(script_headers + script_body + script_tail)
    # 默认style_config='pep8'
    formatted_code, _ = FormatCode(script, style_config=dict(ALLOW_SPLIT_BEFORE_DICT_VALUE=False, COLUMN_LIMIT=120))
    return formatted_code


def convert(raw_string):
    try:
        # 兼容换行的模式
        raw_string = raw_string.replace("\\\n", "")
        script = create_script(raw_string)
    except:
        script = '解析出错啦！请检查输入格式是否有误。'
        traceback.print_exc()
    return script


def _request_wrapper(func):
    def _request(*args, **kwargs):
        # 避免用户重放 run 请求，以至于陷入死循环
        if 'url' in kwargs:
            url = kwargs['url']
        elif len(args) == 1:
            url = args[0]
        elif len(args) > 1:
            url = args[1]
        else:
            url = ''
        if '/tools/convert2req/run' in url:
            raise Exception('请求链接不合法')

        g.response = func(*args, **kwargs)
        return g.response

    return _request


for method in ['delete', 'get', 'head', 'options', 'patch', 'post', 'put', 'request']:
    """将原生的 requests 方法批量装饰，获取 response 对象到 g 变量"""
    setattr(requests, method, _request_wrapper(getattr(requests, method)))


@dataclass
class Code:
    code: str
    import_pattern = re.compile(r'^\s*(from.+)?import.+$', re.M)
    if_main_pattern = re.compile(r'''^if __name__ ?== ?['\"]__main__['\"]\s*:\s*$''', re.M)
    indent_pattern = re.compile(r'^\s+', re.M)

    @property
    def safe_code(self):
        return self.import_pattern.sub('', self.code)

    def run(self):

        # forbidden_fun = 'lambda *args, **kwargs: print_out.append("warning: {} function is not allowed")'
        # forbidden_exec = f"exec = {forbidden_fun.format('exec')}\neval = {forbidden_fun.format('eval')}\n"
        safe_code = self.safe_code

        # 将 if __name__ == '__main__': 去掉，避免运行不到
        code_split = self.if_main_pattern.split(safe_code, 1)
        if len(code_split) == 2:
            main, footer = code_split
            footer = self.indent_pattern.sub('', footer)
            safe_code = main + footer

        print_out = []

        def _print(*args):
            args = list(map(lambda x: str(x), args))
            print_out.append(' '.join(args))

        _exec = lambda *args, **kwargs: print_out.append("warning: exec function is not allowed")
        _eval = lambda *args, **kwargs: print_out.append("warning: eval function is not allowed")

        try:
            exec(safe_code, {**globals(), 'print': _print, 'print_out': print_out, 'exec': _exec, 'eval': _eval})
        except Exception as e:
            print_out.append(str(e))

        return '\n'.join(print_out)


if __name__ == '__main__':
    code = Code(__doc__)
    print(code.run())
    print(requests.get('https://www.baidu.com'))
