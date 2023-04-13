#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request, Response, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.api.jwt import CurrentUser, DependsUser, DependsSuperUser
from backend.app.api.service.user_service import UserService
from backend.app.common.pagination import Page
from backend.app.common.response.response_schema import response_base
from backend.app.schemas.token import Token
from backend.app.schemas.user import CreateUser, GetUserInfo, ResetPassword, Auth2, ELCode, UpdateUser

router = APIRouter()


@router.post('/login', summary='表单登录', response_model=Token, description='form 格式登录支持直接在 api 文档调试接口')
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token, is_super = await UserService.login(form_data)
    return Token(access_token=token, is_superuser=is_super)


# @router.post('/login', summary='用户登录', response_model=Token,
#            description='json 格式登录, 不支持api文档接口调试, 需使用第三方api工具, 例如: postman')
# async def user_login(obj: Auth):
#     token, is_super = await UserService.login(obj)
#     return Token(access_token=token, is_superuser=is_super)


@router.post('/login/email/captcha', summary='发送邮箱登录验证码')
async def user_login_email_captcha(request: Request, obj: ELCode):
    await UserService.send_login_email_captcha(request, obj)
    return response_base.response_200()


@router.post('/login/email', summary='邮箱登录', description='邮箱登录', response_model=Token)
async def user_login_email(request: Request, obj: Auth2):
    token, is_super = await UserService.login_email(request=request, obj=obj)
    return Token(access_token=token, is_superuser=is_super)


@router.post('/logout', summary='用户退出', dependencies=[DependsUser])
async def logout():
    return response_base.response_200()


@router.post('/register', summary='用户注册')
async def user_register(obj: CreateUser):
    await UserService.register(obj)
    return response_base.response_200()


@router.post('/password/reset/code', summary='发送密码重置验证码', description='可以通过用户名或者邮箱重置密码')
async def password_reset_captcha(username_or_email: str, response: Response):
    await UserService.get_pwd_rest_captcha(username_or_email=username_or_email, response=response)
    return response_base.response_200()


@router.post('/password/reset', summary='密码重置请求')
async def password_reset(obj: ResetPassword, request: Request, response: Response):
    await UserService.pwd_reset(obj=obj, request=request, response=response)
    return response_base.response_200()


@router.get('/password/reset/done', summary='重置密码完成')
def password_reset_done():
    return response_base.response_200()


@router.get('/{username}', summary='查看用户信息', dependencies=[DependsUser])
async def userinfo(username: str):
    current_user = await UserService.get_user_info(username)
    return response_base.response_200(data=current_user, exclude={'password'})


@router.put('/{username}', summary='更新用户信息')
async def update_userinfo(username: str, obj: UpdateUser, current_user: CurrentUser):
    count = await UserService.update(username=username, current_user=current_user, obj=obj)
    if count > 0:
        return response_base.response_200()
    return response_base.fail()


@router.put('/{username}/avatar', summary='更新头像')
async def update_avatar(username: str, avatar: UploadFile, current_user: CurrentUser):
    count = await UserService.update_avatar(username=username, current_user=current_user, avatar=avatar)
    if count > 0:
        return response_base.response_200()
    return response_base.fail()


@router.delete('/{username}/avatar', summary='删除头像文件')
async def delete_avatar(username: str, current_user: CurrentUser):
    count = await UserService.delete_avatar(username=username, current_user=current_user)
    if count > 0:
        return response_base.response_200()
    return response_base.fail()


@router.get('', summary='获取所有用户', dependencies=[DependsUser])
async def get_all_users() -> Page[GetUserInfo]:
    return await UserService.get_user_list()


@router.post('/{pk}/super', summary='修改用户超级权限', dependencies=[DependsSuperUser])
async def super_set(pk: int):
    count = await UserService.update_permission(pk)
    if count > 0:
        return response_base.response_200()
    return response_base.fail()


@router.post('/{pk}/action', summary='修改用户状态', dependencies=[DependsSuperUser])
async def active_set(pk: int):
    count = await UserService.update_active(pk)
    if count > 0:
        return response_base.response_200()
    return response_base.fail()


@router.delete('/{username}', summary='用户注销', description='用户注销 != 用户退出，注销之后用户将从数据库删除')
async def delete_user(username: str, current_user: CurrentUser):
    count = await UserService.delete(username=username, current_user=current_user)
    if count > 0:
        return response_base.response_200()
    return response_base.fail()