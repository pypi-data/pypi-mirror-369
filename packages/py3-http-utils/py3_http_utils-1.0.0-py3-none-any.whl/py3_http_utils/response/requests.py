#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
=================================================
作者：[郭磊]
手机：[15210720528]
Email：[174000902@qq.com]
Github：https://github.com/guolei19850528/py3_http_utils
=================================================
"""
from typing import Callable

from addict import Dict
from bs4 import BeautifulSoup
from requests import Response


class Handler(object):
    """
    Handler Class
    You can to inherit such to implement your own handlers
    """

    @staticmethod
    def handler(response: Response = None, pretreatment: Callable = None, *args, **kwargs):
        """
        default handler implement
        :param response: requests.Response instance
        :param pretreatment: pretreatment function
        :param args: args
        :param kwargs: kwargs
        :return:
        """
        if not isinstance(response, Response):
            raise TypeError(f"response:{response} must be Response instance")
        if isinstance(pretreatment, Callable):
            response = pretreatment(response)
        return response

    @staticmethod
    def text(response: Response = None, pretreatment: Callable = None, condition: Callable = None, *args, **kwargs):
        response = Handler.handler(response=response, pretreatment=pretreatment)
        if isinstance(condition, Callable):
            if condition(response):
                return response.text
        return None

    @staticmethod
    def content(response: Response = None, pretreatment: Callable = None, condition: Callable = None, *args, **kwargs):
        response = Handler.handler(response=response, pretreatment=pretreatment)
        if isinstance(condition, Callable):
            if condition(response):
                return response.content
        return None

    @staticmethod
    def json(response: Response = None, pretreatment: Callable = None, condition: Callable = None,
             json_kwargs: dict = None, *args, **kwargs):
        response = Handler.handler(response=response, pretreatment=pretreatment)
        if isinstance(condition, Callable):
            if condition(response):
                return response.json(**Dict(json_kwargs).to_dict())
        return None

    @staticmethod
    def json_addict(response: Response = None, pretreatment: Callable = None, condition: Callable = None,
                    json_kwargs: dict = None, *args, **kwargs):
        response = Handler.handler(response=response, pretreatment=pretreatment)
        if isinstance(condition, Callable):
            if condition(response):
                return Dict(response.json(**Dict(json_kwargs).to_dict()))
        return None

    @staticmethod
    def beautifulsoup(response: Response = None, pretreatment: Callable = None, condition: Callable = None,
                      beautifulsoup_kwargs: dict = None, *args, **kwargs):
        response = Handler.handler(response=response, pretreatment=pretreatment)
        if isinstance(condition, Callable):
            if condition(response):
                return BeautifulSoup(response.text, **Dict(beautifulsoup_kwargs).to_dict())
        return None
