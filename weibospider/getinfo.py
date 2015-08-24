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
    username_ = urllib.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username 

def get_followflag(filename):
    f = open(filename)
    tag = 0
    for line in f:
        if tag == 0:
            flag = line.strip()
            tag += 1
        else:
            stopflag = line.strip()
    return flag,stopflag 

def set_followflag(filename,newflag,stopflag):
    f = open(filename,'w')
    f.write(newflag+'\n'+stopflag+'\n')

######################################################
def get_fuwflag(filename):
    f = open(filename)
    tag = 1
    for line in f:
        if tag == 1:
            follow_flag = line.strip()
            tag += 1
        if tag == 2:
            userinfo_flag = line.strip()
            tag +=1
        else:
            weibocontent_flag = line.strip()
    return follow_flag,userinfo_flag,weibocontent_flag 
        
def set_fuwflag(filename,follow_flag,userinfo_flag,weibocontent_flag):
    f = open(filename,'w')
    f.write(follow_flag+'\n'+userinfo_flag+'\n'+weibocontent_flag+'\n')
   


def get_url(uid):
    '''获取入口uid的关注列表页面'''
    url = 'http://weibo.com/p/100505' + str(uid) + '/myfollow?' 
    return url
 
