"""
Copyright (c) 2024-now LeslieLiang All rights reserved.
Build Date: 2024-12-19
Author: LeslieLiang
Description: API 请求客户端
"""

from __future__ import annotations

from json import JSONDecodeError
from typing import Literal

import requests
from requests.exceptions import HTTPError

from .getter_filter import GetterFilter
from .result import (
    CreateResult,
    DestroyResult,
    ErrorResult,
    GetResult,
    SelectResult,
    UpdateResult,
)


class Client:
    def __init__(self, host: str, token: str):
        if not host or not isinstance(host, str):
            raise ValueError('host type error')

        self.host = host.rstrip('/')
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }

    def get_requester(self, db_name: str):
        """
        获取请求器对象

        Args:
            db_name: 数据表名称
        Returns:
            请求器对象
        """

        if not db_name or not isinstance(db_name, str):
            raise ValueError('db_name type error')

        return Requester(client=self, db_name=db_name)


class Requester:
    def __init__(self, client: Client, db_name: str):
        self.client = client
        self.db_name = db_name

    def __generate__api_path(self, method: str):
        """
        格式化API路径

        Args:
            method: 请求方法
        Returns:
            格式化后的API路径
        """

        return f'{self.client.host}/api/{self.db_name}:{method}'

    def __request(
        self,
        method: Literal['list', 'get', 'create', 'update', 'destroy'],
        **kwargs,
    ):
        """
        发送请求

        Args:
            method: 请求方法
        """

        headers = self.client.headers
        if 'headers' in kwargs and isinstance(headers, dict):
            headers = {**headers, **kwargs.pop('headers')}

        resp = requests.get(
            self.__generate__api_path(method),
            headers=headers,
            **kwargs,
        )

        try:
            resp_json: dict = resp.json()
        except JSONDecodeError as e:
            raise HTTPError(f'请求失败，状态码：{resp.status_code}') from e

        return resp_json

    def select(
        self, page=1, page_size=20, filters: GetterFilter = None, as_result=False
    ):
        """
        获取列表数据

        Args:
            page: 页码
            page_size: 每页数量
            filters: 过滤/排序等条件
            as_result: 是否返回结果对象
        Returns:
            响应数据
        """

        params = {
            'page': page,
            'pageSize': page_size,
        }

        if filters and isinstance(filters, GetterFilter):
            params.update(filters.get_query(flatten=True))

        resp = self.__request('list', params=params)
        if as_result is not True:
            return resp

        if 'errors' in resp:
            return ErrorResult(**resp)

        return SelectResult(**resp)

    def get(self, filters: GetterFilter = None, as_result=False):
        """
        获取单条数据

        Args:
            filters: 过滤条件
            as_result: 是否返回结果对象
        Returns:
            响应数据
        """

        params = {}
        if filters and isinstance(filters, GetterFilter):
            params.update(filters.get_query(flatten=True))

        resp = self.__request('get', params=params)
        if as_result is not True:
            return resp

        if 'errors' in resp:
            return ErrorResult(**resp)

        return GetResult(**resp)

    def create(
        self,
        record: dict,
        whitelist: list[str] = None,
        blacklist: list[str] = None,
        as_result=False,
    ):
        """
        创建数据

        Args:
            record: 要创建的数据
            whitelist: 白名单字段
            blacklist: 黑名单字段
            as_result: 是否返回结果对象
        Returns:
            响应数据
        """

        if not record or not isinstance(record, dict):
            raise ValueError('record type error')

        params = {}
        if whitelist and isinstance(whitelist, list):
            params['whitelist'] = ','.join(whitelist)

        if blacklist and isinstance(blacklist, list):
            params['blacklist'] = ','.join(blacklist)

        resp = self.__request('create', params=params, json=record)
        if as_result is not True:
            return resp

        if 'errors' in resp:
            return ErrorResult(**resp)

        return CreateResult(**resp)

    def update(
        self,
        filters: GetterFilter,
        record: dict,
        whitelist: list[str] = None,
        blacklist: list[str] = None,
        as_result=False,
    ):
        """
        更新数据

        Args:
            filters: 过滤条件
            record: 要更新的数据
            whitelist: 白名单字段
            blacklist: 黑名单字段
            as_result: 是否返回结果对象
        Returns:
            响应数据
        """

        if not filters or not isinstance(filters, GetterFilter):
            raise ValueError('filters type error')

        if not record or not isinstance(record, dict):
            raise ValueError('record type error')

        params = {}
        if whitelist and isinstance(whitelist, list):
            params['whitelist'] = ','.join(whitelist)

        if blacklist and isinstance(blacklist, list):
            params['blacklist'] = ','.join(blacklist)

        params.update(filters.get_query(flatten=True))

        resp = self.__request('update', params=params, json=record)
        if as_result is not True:
            return resp

        if 'errors' in resp:
            return ErrorResult(**resp)

        return UpdateResult(**resp)

    def destroy(self, filters: GetterFilter, as_result=False):
        """
        删除数据

        Args:
            filters: 过滤条件
            as_result: 是否返回结果对象
        Returns:
            响应数据
        """

        if not filters or not isinstance(filters, GetterFilter):
            raise ValueError('filters type error')

        params = filters.get_query(flatten=True)

        resp = self.__request('destroy', params=params)
        if as_result is not True:
            return resp

        if 'errors' in resp:
            return ErrorResult(**resp)

        return DestroyResult(**resp)
