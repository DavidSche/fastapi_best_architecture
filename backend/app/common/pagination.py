#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import math
from typing import TypeVar, Generic, Sequence

from fastapi import Query
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from pydantic import BaseModel

T = TypeVar("T")

"""
重写分页库：fastapi-pagination 
使用方法：example link: https://github.com/uriyyo/fastapi-pagination/tree/main/examples
"""


class Params(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(20, gt=0, le=100, description="Page size")  # 默认 20 条记录

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size,
            offset=self.size * (self.page - 1),
        )


class Page(AbstractPage[T], Generic[T]):
    data: Sequence[T]  # 数据
    total: int  # 总数据数
    page: int  # 第n页
    size: int  # 每页数量
    total_pages: int  # 总页数
    links: dict  # 跳转链接

    __params_type__ = Params  # 使用自定义的Params

    @classmethod
    def create(
            cls,
            data: Sequence[T],
            total: int,
            params: Params,
    ) -> Page[T]:
        page = params.page
        size = params.size
        total_pages = math.ceil(total / params.size)
        links = {
            "first": f"?page=1$size={size}",
            "last": f"?page={math.ceil(total / params.size)}&size={size}" if total > 0 else 1,
            "next": f"?page={page + 1}&size={size}" if (page + 1) <= total_pages else "null",
            "prev": f"?page={page - 1}&size={size}" if (page - 1) >= 1 else "null",
        }
        return cls(
            data=data,
            total=total,
            page=params.page,
            size=params.size,
            total_pages=total_pages,
            links=links
        )