# -*- coding: utf-8 -*-
#python标准模块
import re
import base64
import binascii
import logging
#python第三方模块
import rsa
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request,FormRequest
from scrapy.utils.project import get_project_settings
from weibospider.items import WeibospiderItem
from scrapy.settings import Settings
from settings import USER_NAME
#应用程序自定义模块
import getinfo
from analyzer import Analyzer
from dataoracle import OracleStore
from getpageload import GetWeibopage

logger = logging.getLogger(__name__)

class WeiboSpider(CrawlSpider):
    '''输入用户uid列表，返回列表中所有uid的用户基本信息'''
    name = 'userinfo_list'
    allowed_domains = ['weibo.com','sina.com.cn']
    settings = get_project_settings()
    #start_username = settings['USER_NAME']
    start_username = USER_NAME
    start_password = settings['PASS_WORD']
    #start_uid = settings['UID']
    page_num = settings['PAGE_NUM']
    follow_page_num = settings['FOLLOW_PAGE_NUM']

    def __init__(self,uid_listformat_str = None): #uid_listformat为类似列表形式"[1,2,3]"字符串
        self.uid_list = list(eval(uid_listformat_str))

#    @classmethod
#    def from_crawler(cls,crawler,uid = None):
#        settings = crawler.settings
#        #print '!!!!!!',settings['PAGE_NUM']
#        return cls(uid)

    def closed(self,reason):
        db = OracleStore();conn = db.get_connection()
        sql = 'update t_spider_state set userinfostate = 1'
        db.insert_operation(conn,sql)
        print '------userinfo_list_spider closed------'

    def start_requests(self):
        username = WeiboSpider.start_username
        username = getinfo.get_user(username)
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)' % username
        return [Request(url=url,method='get',callback=self.post_requests)]

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

        request = response.request.replace(url=login_url,meta={'cookiejar':1},method='get',callback=self.get_userinfo)  #GET请求login_url获取返回的cookie，后续发送Request携带此cookie
        return request

##########################获取用户基本信息#############################
    def get_userinfo(self,response):
        #db = OracleStore();conn = db.get_connection()
        for uid in self.uid_list:
            #sql = "select count(*) from (select userID from t_user_info where userID='%s' union select userID from t_publicuser_info where userID='%s')" % (uid,uid)
            #cursor = db.select_operation(conn,sql);count = cursor.fetchone()
            #if not count[0]:   #没有爬取过该uid用户
            print "!!scraping each uid:",uid
            mainpageurl = 'http://weibo.com/u/'+str(uid)+'?from=otherprofile&wvr=3.6&loc=tagweibo'
            GetWeibopage.data['uid'] = uid     
            getweibopage = GetWeibopage()
            GetWeibopage.data['page'] = 1
            firstloadurl = mainpageurl + getweibopage.get_firstloadurl()
            yield  Request(url=firstloadurl,meta={'cookiejar':response.meta['cookiejar'],'uid':uid},callback=self.get_userurl)
            #else:
            #    yield None
            #cursor.close()
        #db.close_connection(conn)

    def get_userurl(self,response):
        analyzer = Analyzer()
        total_pq =  analyzer.get_html(response.body,'script:contains("PCD_person_info")')
        user_property = analyzer.get_userproperty(total_pq)
        if user_property == 'icon_verify_co_v': #该账号为公众账号
            public_userinfo_url = analyzer.get_public_userinfohref(total_pq)
            yield Request(url=public_userinfo_url,meta={'cookiejar':response.meta['cookiejar'],'uid':response.meta['uid'],'user_property':user_property},callback=self.parse_public_userinfo)
        else:  #该账号为个人账号
            userinfo_url = analyzer.get_userinfohref(total_pq)
            yield Request(url=userinfo_url,meta={'cookiejar':response.meta['cookiejar'],'uid':response.meta['uid'],'user_property':user_property},callback=self.parse_userinfo)
         
    def parse_userinfo(self,response):
        item = WeibospiderItem() 
        analyzer = Analyzer()
        try:
            total_pq1 = analyzer.get_html(response.body,'script:contains("pf_photo")')
            #item['image_urls'] = analyzer.get_userphoto_url(total_pq1)
            item['image_urls'] = None 

            total_pq2 = analyzer.get_html(response.body,'script:contains("PCD_text_b")') 
            item['userinfo'] = analyzer.get_userinfo(total_pq2)
        except Exception,e:
            item['userinfo'] = {}.fromkeys(('昵称：'.decode('utf-8'),'所在地：'.decode('utf-8'),'性别：'.decode('utf-8'),'博客：'.decode('utf-8'),'个性域名：'.decode('utf-8'),'简介：'.decode('utf-8'),'生日：'.decode('utf-8'),'注册时间：'.decode('utf-8')),'')   
            item['image_urls'] = None
        item['uid'] = response.meta['uid']
        item['user_property'] = response.meta['user_property']
        yield item

    def parse_public_userinfo(self,response):  
        '''解析公众账号个人信息'''
        item = WeibospiderItem()
        analyzer = Analyzer()
        try:
            total_pq1 = analyzer.get_html(response.body,'script:contains("pf_photo")')
            #item['image_urls'] = analyzer.get_userphoto_url(total_pq1)
            item['image_urls'] = None 
            item['userAlias_public'] = total_pq1("div.PCD_header")("h1").text() 
            
            total_pq2 = analyzer.get_html(response.body,'script:contains("PCD_text_b")') 
            item['userinfo'] = analyzer.get_public_userinfo(total_pq2)
        except Exception,e:
            item['userinfo'] = {}.fromkeys(('联系人：'.decode('utf-8'),'电话：'.decode('utf-8'),'邮箱：'.decode('utf-8'),'友情链接：'.decode('utf-8')),'')   
            item['image_urls'] = None
            item['userAlias_public'] = ""

        item['uid'] = response.meta['uid']
        item['user_property'] = response.meta['user_property']
        yield item
      
