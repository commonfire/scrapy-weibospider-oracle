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
from scrapy.conf import settings
from settings import USER_NAME
#应用程序自定义模块
import getinfo
from analyzer import Analyzer
from dataoracle import OracleStore
from getpageload import GetWeibopage

logger = logging.getLogger(__name__)

class WeiboSpider(CrawlSpider):
    #settings.set('ITEM_PIPELINES',{'weibospider.user_imagepipelines.UserImagesPipeline':1,'weibospider.oracle_pipelines.WeibospiderPipeline':300},priority='spider')
    #ITEM_PIPELINES = {'weibospider.user_imagepipelines.UserImagesPipeline':1,'weibospider.oracle_pipelines.WeibospiderPipeline':300}
    name = 'userinfo'
    allowed_domains = ['weibo.com','sina.com.cn']
    settings = get_project_settings()
    #start_username = settings['USER_NAME']
    start_username = USER_NAME
    start_password = settings['PASS_WORD']
    start_uid = settings['UID']
    page_num = settings['PAGE_NUM']
    follow_page_num = settings['FOLLOW_PAGE_NUM']

    def __init__(self,uid = None):
        self.uid = uid

#    @classmethod
#    def from_crawler(cls,crawler,uid = None):
#        settings = crawler.settings
#        #print '!!!!!!',settings['PAGE_NUM']
#        return cls(uid)

    def closed(self,reason):
        db = OracleStore();conn = db.get_connection()
        sql = 'update t_spider_state set userinfostate = 1'
        db.insert_operation(conn,sql)
        print '------userinfo_spider closed------'

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
        #sql1 = "select * from t_user_keyword where keyword = '%s'" % str(self.keyword)
        #sql1 = '''select * from "t_user_keyword" where "keyword"='%s' and "userID" not in (select a."userID" from "t_user_keyword" a, "t_user_info" b where a."keyword" = '%s' and a."userID" = b."userID")''' % (str(self.keyword),str(self.keyword))
        #cursor1 = db.select_operation(conn,sql1)

        ##sql2 = "select count(*) from t_user_keyword where keyword = '%s'" % str((self.keyword))
        #sql2 = '''select count(*) from "t_user_keyword" where "keyword"='%s' and "userID" not in (select a."userID" from "t_user_keyword" a, "t_user_info" b where a."keyword" = '%s' and a."userID" = b."userID")''' % (str(self.keyword),str(self.keyword))
        #cursor2 = db.select_operation(conn,sql2)
        #count = cursor2.fetchone()
        
        #if count[0]:  #count[0]不为0，即有查询结果
        #    for i in range(1):    #(count[0]):
        #        for result in cursor1.fetchmany(1):
        #            if result[0]:
        mainpageurl = 'http://weibo.com/u/'+str(self.uid)+'?from=otherprofile&wvr=3.6&loc=tagweibo'
        GetWeibopage.data['uid'] = self.uid     #result[0]
        getweibopage = GetWeibopage()
        GetWeibopage.data['page'] = 1
        firstloadurl = mainpageurl + getweibopage.get_firstloadurl()
        yield  Request(url=firstloadurl,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.get_userurl)
        #else:
        #    yield None
        #db.close_connection(conn,cursor1,cursor2)

    def get_userurl(self,response):
        analyzer = Analyzer()
        total_pq =  analyzer.get_html(response.body,'script:contains("PCD_person_info")')
        user_property = analyzer.get_userproperty(total_pq)
        if user_property == 'icon_verify_co_v': #该账号为公众账号
            public_userinfo_url = analyzer.get_public_userinfohref(total_pq)
            yield Request(url=public_userinfo_url,meta={'cookiejar':response.meta['cookiejar'],'uid':response.meta['uid'],'user_property':user_property},callback=self.parse_public_userinfo)
        else:
            userinfo_url = analyzer.get_userinfohref(total_pq)
            yield Request(url=userinfo_url,meta={'cookiejar':response.meta['cookiejar'],'uid':response.meta['uid'],'user_property':user_property},callback=self.parse_userinfo)
        
    def parse_userinfo(self,response):
        '''解析非公众账号个人信息'''
        item = WeibospiderItem() 
        analyzer = Analyzer()
        try:
            total_pq1 = analyzer.get_html(response.body,'script:contains("pf_photo")')
            item['image_urls'] = analyzer.get_userphoto_url(total_pq1)

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
            item['image_urls'] = analyzer.get_userphoto_url(total_pq1)

            total_pq2 = analyzer.get_html(response.body,'script:contains("PCD_text_b")') 
            item['userinfo'] = analyzer.get_public_userinfo(total_pq2)
        except Exception,e:
            item['userinfo'] = {}.fromkeys(('联系人：'.decode('utf-8'),'电话：'.decode('utf-8'),'邮箱：'.decode('utf-8'),'友情链接：'.decode('utf-8')),'')   
            item['image_urls'] = None

        item['uid'] = response.meta['uid']
        item['user_property'] = response.meta['user_property']
        yield item
