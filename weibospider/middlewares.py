#-*-coding: utf-8 -*-

import random
import base64
import logging
from  settings import PROXIES 

class RotateUserAgent():
    ''' Randomly rotate user agents based on a predefined list'''
    def __init__(self,user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))   #调用__init__方法，返回该类的对象

    def process_request(self,request,spider):
        request.headers.setdefault('USER_AGENTS',random.choice(self.user_agents))

class RotateHttpProxy():

    def process_request(self,request,spider):
        proxy = random.choice(PROXIES)
        request.meta['proxy'] = 'http://%s' % proxy['ip_port']
        if proxy['user_pass'] is not None:
            # setup basic authentication for the proxy
            encoded_user_pass = base64.encodestring(proxy['user_pass'])
            request.headers['Proxy-Authorization'] = 'Basic' + encoded_user_pass
   
    def process_exception(self,request,exception,spider):
        proxy = request.meta['proxy']
        logging.info('Removing failed proxy <%s>,%d proxies left' % (proxy,len(PROXIES)-1))  
