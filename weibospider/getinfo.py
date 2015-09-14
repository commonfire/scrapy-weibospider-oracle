#-*- coding: utf-8 -*-
import urllib
import base64
import rsa
import binascii

def get_pwd(password,servertime,nonce,pubkey):
    rsaPublickey = int(pubkey, 16)                                                                 
    key = rsa.PublicKey(rsaPublickey, 65537)  #创建公钥
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #拼接明文js文件中得到的
    passwd = rsa.encrypt(message, key)  #加密
    passwd = binascii.b2a_hex(passwd)   #将加密信息转换为16进制
    return passwd


def get_user(username):
    username_coded = urllib.quote(username)
    username = base64.encodestring(username_coded)[:-1]
    return username 


def get_follow_mainurl(uid):
    '''获取入口uid的关注列表页面'''
    url = 'http://weibo.com/%s/follow?' % str(uid)
    return url

def get_follower_mainurl(uid):
    '''获取入口uid的粉丝列表页面'''
    url = 'http://weibo.com/%s/fans?' % str(uid)
    return url

def get_mainurl(uid):
    '''获取入口uid的关注列表页面'''
    url = 'http://weibo.com/p/100505' + str(uid) + '/myfollow?' 
    return url

