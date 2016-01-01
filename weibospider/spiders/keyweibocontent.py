# -*- coding: utf-8 -*-
#python标准模块
import re
import base64
import rsa
import binascii
import logging
from urllib import quote
#python第三方模块
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request,FormRequest
from scrapy.utils.project import get_project_settings
from weibospider.items import WeibospiderItem
from settings import USER_NAME
#应用程序自定义模块
import getinfo
from getpageload import GetWeibopage
from analyzer import Analyzer
from friendcircle import FriendCircle
from dataoracle import OracleStore

logger = logging.getLogger(__name__)


class WeiboSpider(CrawlSpider):
    '''输入用户uid，获取用法发表微博内容，主要用于关键词搜索出的用户'''
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
        self.atuser_dict = {}

    def closed(self,reason):
        db = OracleStore()
        conn = db.get_connection()
        cur = conn.cursor()
        for key in self.atuser_dict.keys(): #插入@用户uid信息
            sql= """update t_user_weibocontent_atuser set atuserID = %s where userID = %s and atuser = '%s'""" % (self.atuser_dict.get(key),self.uid,key)
            cur.execute(sql)
            conn.commit()

        sql = '''update t_spider_state set contentstate = 1'''
        db.insert_operation(conn,sql)
        #logger.info('------keyweibocontent_spider closed------')                                                                                                                 
        print '------keyweibocontent_spider closed------'                                                                                                               
    
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
        mainpageurl = 'http://weibo.com/u/'+str(self.uid)+'?from=otherprofile&wvr=3.6&loc=tagweibo&is_all=1&'
        GetWeibopage.data['uid'] = self.uid    #result[0]
        getweibopage = GetWeibopage()
        for page in range(WeiboSpider.page_num): 
            GetWeibopage.data['page'] = page+1
            firstloadurl = mainpageurl + getweibopage.get_firstloadurl()
            yield  Request(url=firstloadurl,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.parse_load)

            secondloadurl = mainpageurl + getweibopage.get_secondloadurl()
            yield  Request(url=secondloadurl,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.parse_load)
           
            thirdloadurl = mainpageurl + getweibopage.get_thirdloadurl()
            yield  Request(url=thirdloadurl,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid},callback=self.parse_load)           

#        else:
#            yield None
#        db.close_connection(conn,cursor1,cursor2)

    def parse_load(self,response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        friendcircle = FriendCircle()
        total_pq =  analyzer.get_mainhtml(response.body)
        item['uid'] = response.meta['uid']
        item['content'] = analyzer.get_content(total_pq)
        item['time'],item['timestamp'] = analyzer.get_time(total_pq)
        atuser_info,item['repost_user'] = analyzer.get_atuser_repostuser(total_pq)
        atuser_list = friendcircle.atuser_parser(atuser_info)
        item['atuser_nickname_list'] = atuser_list
        #item['atuser_uid']= ""
        yield item
       
#        for atuser_inlist in atuser_list:
#            if atuser_inlist != []:
#                for atuser in atuser_inlist:
#                    uid_url = "http://s.weibo.com/user/"+quote(quote(str(atuser)))+"&Refer=SUer_box"
#                    yield Request(url=uid_url,meta={'cookiejar':response.meta['cookiejar'],'uid':self.uid,'atuser_nickname':atuser},callback=self.atuser_uid_parser)
#            else:
#                continue

        #item['atuser_nickname_uid'] = friendcircle.atuser_uid_parser(atuser_list)
        #item['repostuser_uid'] = friendcircle.repostuser_uid_parser(item['repost_user'])
        #return item

    def atuser_uid_parser(self,response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        friendcircle = FriendCircle()
        total_pq = analyzer.get_html(response.body,'script:contains("W_face_radius")') 
        uid = friendcircle.get_user_uid(total_pq)
        self.atuser_dict[response.meta['atuser_nickname']] = uid
        #item['atuser_uid'] = uid
        #item['uid'] = response.meta['uid']
        #item['atuser_nickname'] = response.meta['atuser_nickname']
        #yield item
