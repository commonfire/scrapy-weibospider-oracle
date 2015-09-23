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
    name = 'userfollow!!!'
    allowed_domains = ['weibo.com','sina.com.cn']
    settings = get_project_settings()
    start_username = settings['USER_NAME']
    start_password = settings['PASS_WORD']
    start_uid = settings['UID']
    page_num = settings['PAGE_NUM']
    follow_page_num = settings['FOLLOW_PAGE_NUM']
    follower_page_num = settings['FOLLOWER_PAGE_NUM']

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

        request = response.request.replace(url=login_url,meta={'cookiejar':1},method='get',callback=self.get_relation)  #GET请求login_url获取返回的cookie，后续发送Request携带此cookie
        return request

#    def get_relation_pagenum(self,response):
        

    def get_relation(self,response):
        '''获取用户粉丝或关注请求'''
        getweibopage = GetWeibopage()
        for page in range(WeiboSpider.follow_page_num,0,-1):
            GetWeibopage.relation_data['page'] = page
            follow_url = getinfo.get_follow_mainurl(self.uid) + getweibopage.get_relation_paramurl()
            yield Request(url=follow_url,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.parse_follow)

        for page in range(WeiboSpider.follower_page_num,0,-1):
            GetWeibopage.relation_data['page'] = page
            follower_url = getinfo.get_follower_mainurl(self.uid) + getweibopage.get_relation_paramurl()
            yield Request(url=follower_url,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.parse_follower)


    def parse_follow(self,response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        getweibopage = GetWeibopage()
        total_follow_pq = analyzer.get_childfollowhtml(response.body)
        item['uid'] = response.meta['uid']
        item['follow_uid_list'] = analyzer.get_childfollow(total_follow_pq) 
        item['follower_uid_list'] = []
        yield item

        if self.uid == response.meta['uid'] and len(item['follow_uid_list']):
            db = OracleStore()
            conn = db.get_connection()

            for follow_uid in item['follow_uid_list']:
                #获取关注用户的关注用户
                sql1 = """select count(*) from t_user_follow where userID=%s""" % str(follow_uid)
                cursor1 = db.select_operation(conn,sql1)
                count1 = cursor1.fetchone()
                follow_scraped = count1[0]
                cursor1.close()
                if not follow_scraped:  #scraped为0，即该账户没有获取过
                    for page in range(WeiboSpider.follow_page_num,0,-1):
                        GetWeibopage.relation_data['page'] = page
                        follow_url = getinfo.get_follow_mainurl(follow_uid) + getweibopage.get_relation_paramurl()
                        yield Request(url=follow_url,meta={'cookiejar':response.meta['cookiejar'],'uid':follow_uid},callback=self.parse_follow)
                else:
                    print 'follow_uid existed!',follow_uid
                    yield None

                #获取关注用户的粉丝用户
                sql2 = """select count(*) from t_user_follower where userID =%s""" % str(follow_uid)
                cursor2 = db.select_operation(conn,sql2)
                count2 = cursor2.fetchone()
                follower_scraped = count2[0]
                cursor2.close()
                if not follower_scraped:  #scraped为0，即该账户没有获取过
                    for page in range(WeiboSpider.follower_page_num,0,-1):
                        GetWeibopage.relation_data['page'] = page
                        follower_url = getinfo.get_follower_mainurl(follow_uid) + getweibopage.get_relation_paramurl()
                        yield Request(url=follower_url,meta={'cookiejar':response.meta['cookiejar'],'uid':follow_uid},callback=self.parse_follower)
                else:
                    print 'follower_uid existed!',follow_uid
                    yield None

            conn.close()



    def parse_follower(self,response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        getweibopage = GetWeibopage()
        total_follower_pq = analyzer.get_followerhtml(response.body)
        item['uid'] = response.meta['uid']
        item['follower_uid_list'] = analyzer.get_follower(total_follower_pq)
        item['follow_uid_list'] = []    
        yield item

        if self.uid == response.meta['uid'] and len(item['follower_uid_list']):
            db = OracleStore()
            conn = db.get_connection()

            for follower_uid in item['follower_uid_list']:
                #获取粉丝用户的关注用户
                sql1 = """select count(*) from t_user_follow where userID=%s""" % str(follower_uid)
                cursor1 = db.select_operation(conn,sql1)
                count1 = cursor1.fetchone()
                follower_scraped = count1[0]
                cursor1.close()
                if not follower_scraped:  #scraped为0，即该账户没有获取过
                    for page in range(WeiboSpider.follow_page_num,0,-1):
                        GetWeibopage.relation_data['page'] = page
                        follow_url = getinfo.get_follow_mainurl(follower_uid) + getweibopage.get_relation_paramurl()
                        yield Request(url=follow_url,meta={'cookiejar':response.meta['cookiejar'],'uid':follower_uid},callback=self.parse_follow)
                else:
                    print 'follow_uid existed!',follower_uid
                    yield None

                #获取粉丝用户的粉丝用户
                sql2 = """select count(*) from t_user_follower where userID=%s""" % str(follower_uid)
                cursor2 = db.select_operation(conn,sql2)
                count2 = cursor2.fetchone()
                follower_scraped = count2[0]
                cursor2.close()
                if not follower_scraped:  #scraped为0，即该账户没有获取过
                    for page in range(WeiboSpider.follower_page_num,0,-1):
                        GetWeibopage.relation_data['page'] = page
                        follower_url = getinfo.get_follower_mainurl(follower_uid) + getweibopage.get_relation_paramurl()
                        yield Request(url=follower_url,meta={'cookiejar':response.meta['cookiejar'],'uid':follower_uid},callback=self.parse_follower)
                else:
                    print 'follower_uid existed!',follower_uid
                    yield None

            conn.close()

