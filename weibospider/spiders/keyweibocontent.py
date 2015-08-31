# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request,FormRequest
from scrapy.utils.project import get_project_settings
from weibospider.items import WeibospiderItem
import re
import base64
import rsa
import binascii
import time
import getinfo
from getpageload import GetWeibopage
from analyzer import Analyzer
from settings import USER_NAME
from dataoracle import OracleStore

class WeiboSpider(CrawlSpider):
    name = 'keyweibocontent'
    allowed_domains = ['weibo.com','sina.com.cn']
    settings = get_project_settings()
    #start_username = settings['USER_NAME']
    start_username = USER_NAME
    start_password = settings['PASS_WORD']
    start_uid = settings['UID']
    page_num = settings['PAGE_NUM']
    follow_page_num = settings['FOLLOW_PAGE_NUM']



    def __init__(self,uid = None):
        #self.keyword = keyword
        self.uid = uid

    def closed(self,reason):
        db = OracleStore()
        conn = db.get_connection()
        sql = '''update "t_spider_state" set "contentstate" = 1'''
        db.insert_operation(conn,sql)
        print '------keyweibocontent_spider closed------'                                                                                                                  
    
    def start_requests(self):
        username = WeiboSpider.start_username
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)' % username
        return [Request(url=url,method='get',callback=self.post_requests)]

    def post_requests(self,response):
        serverdata = re.findall('{"retcode":0,"servertime":(.*?),"pcid":.*?,"nonce":"(.*?)","pubkey":"(.*?)","rsakv":"(.*?)","exectime":.*}',response.body,re.I)[0]  #获取get请求的数据，用于post请求登录
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

        request = response.request.replace(url=login_url,meta={'cookiejar':1},method='get',callback=self.start_getweiboinfo)  #GET请求login_url获取返回的cookie，后续发送Request携带此cookie
        return request


    def start_getweiboinfo(self,response):
#        db = OracleStore()
#        conn = db.get_connection()
#        sql1 = '''select * from "t_user_keyword" where "keyword" = '%s' ''' % str((self.keyword)) 
#        cursor1 = db.select_operation(conn,sql1)
#        
#        sql2 = '''select count(*) from "t_user_keyword" where "keyword" = '%s' ''' % str((self.keyword))
#        cursor2 = db.select_operation(conn,sql2)
#        count = cursor2.fetchone()
#        
#        if count[0]:
#            for i in range(1):   #(count[0]):
#                for result in cursor1.fetchmany(1):
#                    if result[0]:
        mainpageurl = 'http://weibo.com/u/'+str(self.uid)+'?from=otherprofile&wvr=3.6&loc=tagweibo'
        GetWeibopage.data['uid'] = self.uid    #result[0]
        getweibopage = GetWeibopage()
        for page in range(WeiboSpider.page_num): 
            GetWeibopage.data['page'] = page+1
            firstloadurl = mainpageurl + getweibopage.get_firstloadurl()
            yield  Request(url=firstloadurl,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.parse_firstload)

            secondloadurl = mainpageurl + getweibopage.get_secondloadurl()
            yield  Request(url=secondloadurl,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.parse_secondload)
           
            thirdloadurl = mainpageurl + getweibopage.get_thirdloadurl()
            yield  Request(url=thirdloadurl,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.parse_thirdload)
#        else:
#            yield None
#        db.close_connection(conn,cursor1,cursor2)

    def parse_firstload(self,response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        total_pq =  analyzer.get_mainhtml(response.body)
        item['uid'] = response.meta['uid']
        item['content'] = analyzer.get_content(total_pq)
        item['time'] = analyzer.get_time(total_pq)
        item['atuser'],item['repostuser'] = analyzer.get_atuser_repostuser(total_pq)
        return item


    def parse_secondload(self,response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        total_pq =  analyzer.get_mainhtml(response.body)
        item['uid'] = response.meta['uid']
        item['content'] = analyzer.get_content(total_pq)
        item['time'] = analyzer.get_time(total_pq)
        item['atuser'],item['repostuser'] = analyzer.get_atuser_repostuser(total_pq)
        return item


    def parse_thirdload(self,response):        
        item = WeibospiderItem()
        analyzer = Analyzer()
        total_pq =  analyzer.get_mainhtml(response.body)
        item['uid'] = response.meta['uid']
        item['content'] = analyzer.get_content(total_pq)
        item['time'] = analyzer.get_time(total_pq)
        item['atuser'],item['repostuser'] = analyzer.get_atuser_repostuser(total_pq)
        return item

    
