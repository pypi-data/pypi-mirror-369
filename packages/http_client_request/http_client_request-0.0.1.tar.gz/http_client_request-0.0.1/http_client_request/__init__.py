#!/usr/bin/env python3
# coding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__version__ = (0, 0, 1)
__all__ = ["request"]

from collections import UserString
from collections.abc import Buffer, Callable, Iterable, Mapping
from http.client import HTTPConnection, HTTPSConnection, HTTPResponse
from http.cookiejar import CookieJar
from http.cookies import SimpleCookie
from inspect import signature
from os import PathLike
from types import EllipsisType
from typing import cast, overload, Any, Final, Literal
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit, urlunsplit

from argtools import argcount
from cookietools import cookies_to_str, extract_cookies
from dicttools import get_all_items
from filewrap import bio_chunk_iter, SupportsRead
from http_request import normalize_request_args, SupportsGeturl
from http_response import decompress_response, parse_response
from yarl import URL


type string = Buffer | str | UserString

HTTP_CONNECTION_KWARGS: Final = signature(HTTPConnection).parameters.keys()
HTTPS_CONNECTION_KWARGS: Final = signature(HTTPSConnection).parameters.keys()

if "__del__" not in HTTPConnection.__dict__:
    setattr(HTTPConnection, "__del__", HTTPConnection.close)
if "__del__" not in HTTPSConnection.__dict__:
    setattr(HTTPSConnection, "__del__", HTTPSConnection.close)
if "__del__" not in HTTPResponse.__dict__:
    setattr(HTTPResponse, "__del__", HTTPResponse.close)


def get_host_pair(url: None | str, /) -> None | tuple[str, None | int]:
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    urlp = urlsplit(url)
    return urlp.hostname or "localhost", urlp.port


@overload
def request(
    url: string | SupportsGeturl | URL, 
    method: string = "GET", 
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None, 
    data: Any = None, 
    json: Any = None, 
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None, 
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None, 
    follow_redirects: bool = True, 
    raise_for_status: bool = True, 
    cookies: None | CookieJar | SimpleCookie = None, 
    proxies: None | str | dict[str, str] = None, 
    *, 
    parse: None | EllipsisType = None, 
    **request_kwargs, 
) -> HTTPResponse:
    ...
@overload
def request(
    url: string | SupportsGeturl | URL, 
    method: string = "GET", 
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None, 
    data: Any = None, 
    json: Any = None, 
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None, 
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None, 
    follow_redirects: bool = True, 
    raise_for_status: bool = True, 
    cookies: None | CookieJar | SimpleCookie = None, 
    proxies: None | str | dict[str, str] = None, 
    *, 
    parse: Literal[False], 
    **request_kwargs, 
) -> bytes:
    ...
@overload
def request(
    url: string | SupportsGeturl | URL, 
    method: string = "GET", 
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None, 
    data: Any = None, 
    json: Any = None, 
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None, 
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None, 
    follow_redirects: bool = True, 
    raise_for_status: bool = True, 
    cookies: None | CookieJar | SimpleCookie = None, 
    proxies: None | str | dict[str, str] = None, 
    *, 
    parse: Literal[True], 
    **request_kwargs, 
) -> bytes | str | dict | list | int | float | bool | None:
    ...
@overload
def request[T](
    url: string | SupportsGeturl | URL, 
    method: string = "GET", 
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None, 
    data: Any = None, 
    json: Any = None, 
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None, 
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None, 
    follow_redirects: bool = True, 
    raise_for_status: bool = True, 
    cookies: None | CookieJar | SimpleCookie = None, 
    proxies: None | str | dict[str, str] = None, 
    *, 
    parse: Callable[[HTTPResponse, bytes], T] | Callable[[HTTPResponse], T], 
    **request_kwargs, 
) -> T:
    ...
def request[T](
    url: string | SupportsGeturl | URL, 
    method: string = "GET", 
    params: None | string | Mapping | Iterable[tuple[Any, Any]] = None, 
    data: Any = None, 
    json: Any = None, 
    files: None | Mapping[string, Any] | Iterable[tuple[string, Any]] = None, 
    headers: None | Mapping[string, string] | Iterable[tuple[string, string]] = None, 
    follow_redirects: bool = True, 
    raise_for_status: bool = True, 
    cookies: None | CookieJar | SimpleCookie = None, 
    proxies: None | str | dict[str, str] = None, 
    *, 
    parse: None | EllipsisType| bool | Callable[[HTTPResponse, bytes], T] | Callable[[HTTPResponse], T] = None, 
    **request_kwargs, 
) -> HTTPResponse | bytes | str | dict | list | int | float | bool | None | T:
    if isinstance(proxies, str):
        http_proxy = https_proxy = get_host_pair(proxies)
    elif isinstance(proxies, dict):
        http_proxy = get_host_pair(proxies.get("http"))
        https_proxy = get_host_pair(proxies.get("https"))            
    if isinstance(data, PathLike):
        data = bio_chunk_iter(open(data, "rb"))
    elif isinstance(data, SupportsRead):
        data = bio_chunk_iter(data)
    request_args = normalize_request_args(
        method=method, 
        url=url, 
        params=params, 
        data=data, 
        json=json, 
        files=files, 
        headers=headers, 
    )
    url = request_args["url"]
    headers_ = request_args["headers"]
    need_set_cookie = "cookie" not in headers_
    response_cookies = CookieJar()
    connection: HTTPConnection | HTTPSConnection
    while True:
        if need_set_cookie:
            if cookies:
                headers_["cookie"] = cookies_to_str(cookies, url)
            elif response_cookies:
                headers_["cookie"] = cookies_to_str(response_cookies, url)
        urlp = urlsplit(url)
        request_kwargs["host"] = urlp.hostname
        request_kwargs["port"] = urlp.port
        if urlp.scheme == "https":
            connection = HTTPSConnection(**dict(get_all_items(request_kwargs, *HTTPS_CONNECTION_KWARGS)))
            if http_proxy:
                connection.set_tunnel(*http_proxy)
        else:
            connection = HTTPConnection(**dict(get_all_items(request_kwargs, *HTTP_CONNECTION_KWARGS)))
            if https_proxy:
                connection.set_tunnel(*https_proxy)
        connection.request(
            request_args["method"], 
            urlunsplit(urlp._replace(scheme="", netloc="")), 
            cast(Buffer | Iterable[Buffer], request_args["data"]), 
            headers_, 
        )
        response = connection.getresponse()
        setattr(response, "connection", connection)
        setattr(response, "url", url)
        setattr(response, "cookies", response_cookies)
        extract_cookies(response_cookies, url, response)
        if cookies is not None:
            extract_cookies(cookies, url, response) # type: ignore
        status_code = response.status
        if 300 <= status_code < 400 and follow_redirects:
            url = request_args["url"] = urljoin(url, response.headers["location"])
            if status_code == 303:
                request_args["method"] = "GET"
                request_args["data"] = None
            continue
        if status_code >= 400 and raise_for_status:
            raise HTTPError(
                url, 
                status_code, 
                response.reason, 
                response.headers, 
                response, 
            )
        if parse is None:
            return response
        elif parse is ...:
            response.close()
            return response
        if isinstance(parse, bool):
            content = decompress_response(response.read())
            if parse:
                return parse_response(response, content)
            return content
        ac = argcount(parse)
        if ac == 1:
            return cast(Callable[[HTTPResponse], T], parse)(response)
        else:
            return cast(Callable[[HTTPResponse, bytes], T], parse)(
                response, decompress_response(response.read()))

# TODO: 支持连接池
