# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request,FormRequest
from scrapy.utils.project import get_project_settings
from weibospider.items import WeibospiderItem
import re
import sys
import base64
import rsa
import binascii
import time
import getinfo
from getpageload import GetWeibopage
from getsearchpage import GetSearchpage
from analyzer import Analyzer
from settings import USER_NAME
from dataoracle import OracleStore

reload(sys)
sys.setdefaultencoding('utf-8')

class WeiboSpider(CrawlSpider):
    '''输入关键词，获取关键词相关用户'''
    name = 'keyuser'
    allowed_domains = ['weibo.com','sina.com.cn']
    settings = get_project_settings()
    #start_username = settings['USER_NAME']
    start_username = USER_NAME
    start_password = settings['PASS_WORD']
    #start_uid = settings['UID']
    page_num = settings['PAGE_NUM']
    follow_page_num = settings['FOLLOW_PAGE_NUM']
    search_page_num = settings['SEARCH_PAGE_NUM']

    def __init__(self,keyword = None):
        self.keyword = keyword
   
    def closed(self,reason):
        db = OracleStore();conn = db.get_connection()
        sql = 'update t_spider_state set searchstate=1'
        db.insert_operation(conn,sql)
        print '------keyuser_spider closed------'

    def start_requests(self):
        username = WeiboSpider.start_username
        username = getinfo.get_user(username)
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)' % username
        yield Request(url=url,method='get',callback=self.post_requests)

    def post_requests(self,response):
        serverdata = re.findall('{"retcode":0,"servertime":(.*?),"pcid":.*?,"nonce":"(.*?)","pubkey":"(.*?)","rsakv":"(.*?)","is_openlock":.*,"exectime":.*}',response.body,re.I)[0] #获取get请求的数据，用于post请求登录
        servertime = serverdata[0]
        nonce = serverdata[1]
        pubkey = serverdata[2]
        rsakv = serverdata[3]
        username= WeiboSpider.start_username
        password = WeiboSpider.start_password
        formdata = {
            'entry': 'weibo',  
            'gateway': '1',  
            'from': '',  
            'ssosimplelogin': '1',  
            'vsnf': '1',  
            'vsnval': '',  
            'su': getinfo.get_user(username),  
            'service': 'miniblog',  
            'servertime': servertime,  
            'nonce': nonce,  
            'pwencode': 'rsa2',  
            'sp': getinfo.get_pwd(password,servertime,nonce,pubkey),  
            'encoding': 'UTF-8',  
            'prelt': '115',  
            'rsakv': rsakv, 
            'url':'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack', 
            'returntype': 'META'
            }
        headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0 Chrome/20.0.1132.57 Safari/536.11'} 
        return [FormRequest(url='http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.4)',formdata=formdata,headers=headers,callback=self.get_cookie)]

     
    def get_cookie(self, response):
        p = re.compile('location\.replace\(\'(.*)\'\)')
        try:
            login_url = p.search(response.body).group(1)
            ret_res = re.search('retcode=0',login_url)
            if ret_res:
                print 'Login Success!!!!'
            else:
                print 'Login Fail!!!!'
        except:
            print 'Login Error!!!!'

        request = response.request.replace(url=login_url,meta={'cookiejar':1},method='get',callback=self.get_searchpage)  #GET请求login_url获取返回的cookie，后续发送Request携带此cookie
        return request

##########################根据关键词请求页面内容#############################
    def get_searchpage(self,response):
        main_url = "http://s.weibo.com/weibo/"
        getsearchpage = GetSearchpage()
        keyword = self.keyword  
        for page in range(WeiboSpider.search_page_num):
            getsearchpage.data['page'] = page+1 
            search_url = main_url + getsearchpage.get_searchurl(keyword)
            yield  Request(url=search_url,meta={'cookiejar':response.meta['cookiejar'],'keyword':unicode(keyword)},callback=self.parse_keyuser)
        
    def parse_keyuser(self,response):
        item = WeibospiderItem() 
        analyzer = Analyzer()
        total_pq = analyzer.get_html(response.body,'script:contains("feed_content wbcon")')
        item['keyword_uid'],item['keyword_alias'],item['keyword_time'],item['keyword_timestamp'] =analyzer.get_keyuser(total_pq)
        item['keyword'] = response.meta['keyword']
        return item


