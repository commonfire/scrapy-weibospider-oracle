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
from dataoracle import OracleStore

class WeiboSpider(CrawlSpider):
    name = 'userfollow'
    allowed_domains = ['weibo.com','sina.com.cn']
    settings = get_project_settings()
    start_username = settings['USER_NAME']
    start_password = settings['PASS_WORD']
    start_uid = settings['UID']
    page_num = settings['PAGE_NUM']
    follow_page_num = settings['FOLLOW_PAGE_NUM']

    def __init__(self,uid = None):
        self.uid = uid
    
    def start_requests(self):
        username = WeiboSpider.start_username
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)' % username
        return [Request(url=url,method='get',callback=self.post_requests)]

    def post_requests(self,response):
        serverdata = re.findall('{"retcode":0,"servertime":(.*?),"pcid":.*?,"nonce":"(.*?)","pubkey":"(.*?)","rsakv":"(.*?)","exectime":.*}',response.body,re.I)[0]  #获取get请求的数据，用于post请求登录
        #print '!!!!GET responsebody:',response.body
        #print '!!!!serverdata',serverdata[0]
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
        #print 'response:~~~~~~~~~~~~~~~',response.body
        p = re.compile('location\.replace\(\'(.*)\'\)')
        try:
            login_url = p.search(response.body).group(1)
            #print '==============',login_url 
            ret_res = re.search('retcode=0',login_url)
            if ret_res:
                print 'Login Success!!!!'
            else:
                print 'Login Fail!!!!'
        except:
            print 'Login Error!!!!'

        request = response.request.replace(url=login_url,meta={'cookiejar':1},method='get',callback=self.get_follow)  #GET请求login_url获取返回的cookie，后续发送Request携带此cookie
        return request

    def get_follow(self,response):
        getweibopage = GetWeibopage()
        for page in range(WeiboSpider.follow_page_num,0,-1):
            #GetWeibopage.followdata['Pl_Official_RelationMyfollow__108_page'] = page
            GetWeibopage.followdata['page'] = page
            follow_url = getinfo.get_url(self.uid) + getweibopage.get_followurl()
            yield Request(url=follow_url,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.parse_follow)

#    def parse_follow_follow(self,response):
#        '''获取某用户关注用户的关注用户 '''
#        item = WeibospiderItem()
#        analyzer = Analyzer()
#        total_pq = analyzer.get_childfollowhtml(response.body)
#        item['uid'] = response.meta['uid']
#        item['followuidlist'] = analyzer.get_childfollow(total_pq)
#        return item


    def parse_follow(self,response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        getweibopage = GetWeibopage()
        total_pq = analyzer.get_childfollowhtml(response.body)
        item['uid'] = response.meta['uid']
        item['followuidlist'] = analyzer.get_childfollow(total_pq) 
        yield item
        if self.uid == response.meta['uid']:
            db = OracleStore()
            conn = db.get_connection()
            for follow_uid in item['followuidlist']:
                sql = """select count(*) from "t_user_follow" where "userID"='%s'""" % str(follow_uid)
                cursor = db.select_operation(conn,sql)
                count = cursor.fetchone()
                if not count[0]:  #count[0]为0，即该账户没有获取过
                    for page in range(WeiboSpider.follow_page_num,0,-1):
                        GetWeibopage.followdata['page'] = page
                        follow_url = getinfo.get_url(follow_uid) + getweibopage.get_followurl()
                        yield Request(url=follow_url,meta={'cookiejar':response.meta['cookiejar'],'uid':follow_uid},callback=self.parse_follow)
                else:
                    print 'uid existed!',follow_uid
                    yield None
            db.close_connection(conn,cursor)












