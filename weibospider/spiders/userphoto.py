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
    name = 'userphoto'
    allowed_domains = ['weibo.com','sina.com.cn']
    settings = get_project_settings()
    #start_username = settings['USER_NAME']
    start_username = USER_NAME
    start_password = settings['PASS_WORD']
    start_uid = settings['UID']
    page_num = settings['PAGE_NUM']
    follow_page_num = settings['FOLLOW_PAGE_NUM']

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

        request = response.request.replace(url=login_url,meta={'cookiejar':1},method='get',callback=self.get_userinfo)  #GET请求login_url获取返回的cookie，后续发送Request携带此cookie
        return request

##########################获取用户基本信息#############################
    def get_userinfo(self,response):
        db = OracleStore()
        conn = db.get_connection()
        sql1 = "select * from t_user_info where imagestate = 0"
        cursor1 = db.select_operation(conn,sql1)

        sql2 = "select count(*) from t_user_info where imagestate = 0"
        cursor2 = db.select_operation(conn,sql2)
        count = cursor2.fetchone()

        for i in range(count[0]):
            for result in cursor1.fetchmany(1):
                if result[0]:
                    mainpageurl = 'http://weibo.com/u/'+str(result[0])+'?from=otherprofile&wvr=3.6&loc=tagweibo'
                    GetWeibopage.data['uid'] = result[0]   #result[1]
                    getweibopage = GetWeibopage()
                    GetWeibopage.data['page'] = 1
                    firstloadurl = mainpageurl + getweibopage.get_firstloadurl()
                    yield  Request(url=firstloadurl,meta={'cookiejar':response.meta['cookiejar'],'uid':result[0]},callback=self.get_userurl)

    def get_userurl(self,response):
        analyzer = Analyzer()
        total_pq =  analyzer.get_html(response.body,'script:contains("PCD_person_info")')
        userinfo_url = analyzer.get_userinfohref(total_pq)
        return  Request(url=userinfo_url,meta={'cookiejar':response.meta['cookiejar'],'uid':response.meta['uid']},callback=self.parse_userinfo)
        
    def parse_userinfo(self,response):
        item = WeibospiderItem() 
        analyzer = Analyzer()
       # try:
        total_pq1 = analyzer.get_html(response.body,'script:contains("pf_photo")')
        item['image_urls'] = analyzer.get_userphoto_url(total_pq1)

            #total_pq2 = analyzer.get_html(response.body,'script:contains("PCD_text_b")') 
            #item['userinfo'] = analyzer.get_userinfo(total_pq2)
        #except Exception,e:
            #item['userinfo'] = {}.fromkeys(('昵称：'.decode('utf-8'),'所在地：'.decode('utf-8'),'性别：'.decode('utf-8'),'博客：'.decode('utf-8'),'个性域名：'.decode('utf-8'),'简介：'.decode('utf-8'    ),'生日：'.decode('utf-8'),'注册时间：'.decode('utf-8')),' ')   
            #item['image_urls'] = ' '
        item['uid'] = response.meta['uid']
        return item
######################################################################

#    def get_follow(self,response):
#        getweibopage = GetWeibopage()
#        for page in range(WeiboSpider.follow_page_num,0,-1):
#            GetWeibopage.followdata['Pl_Official_RelationMyfollow__108_page'] = page
#            follow_url = getinfo.get_url(WeiboSpider.start_uid) + getweibopage.get_followurl()
#            yield Request(url=follow_url,meta={'cookiejar':response.meta['cookiejar']},callback=self.parse_follow)
#
#
#    def parse_follow(self,response):
#        #print '************************ source request url:',response.request.url
#        item = WeibospiderItem()
#        analyzer = Analyzer()
#        total_pq = analyzer.get_followhtml(response.body)
#        #item['followuidlist'] = analyzer.get_follow(total_pq) 
#        followlist = analyzer.get_follow(total_pq)
#        #item['userinfo'] = {} 
#        oldflag,stopflag= getinfo.get_followflag(WeiboSpider.filename)
#
#        p = re.compile('.*_page=(\d).*',re.S)
#        current_page = p.search(response.request.url).group(1)  #获取当前关注用户列表页页数
#        
#        if int(current_page) == 1:
#            getinfo.set_followflag(WeiboSpider.filename,followlist[0],'False')
#            print 'page is equal 1 '
#        else:
#            print 'page is NOT equal 1'
#        
#        for follow_uid in followlist[:2]:
#            print '%%%%%%%%%%%%%%%%%%%%%%%%%%',follow_uid
#            #item['uid'] = follow_uid
#            if follow_uid != oldflag:                       #对于已爬uid不进行重复爬取，即增量爬取
#                #爬取该uid用户主页微博内容
#                if stopflag == 'False':
#                    getinfo.set_followflag(WeiboSpider.filename,followlist[0],'True')
#                    mainpageurl = 'http://weibo.com/u/'+str(follow_uid)+'?from=otherprofile&wvr=3.6&loc=tagweibo'
#                    GetWeibopage.data['uid'] = follow_uid
#                    getweibopage = GetWeibopage()
#                    for page in range(WeiboSpider.page_num):
#                        GetWeibopage.data['page'] = page+1
#                        #当页第一次加载
#                        #当页第二次加载
#                        #当页第三次加载
#                        thirdloadurl = mainpageurl + getweibopage.get_thirdloadurl()
#                        if int(GetWeibopage.data['pagebar']) == 1 and page == WeiboSpider.page_num-1:    #在最后一页最后一次加载时，获取用户基本信息
#                            print 'hhhhhhhhhhhhhhhhhhhh',followlist
#                            yield  Request(url=thirdloadurl,meta={'cookiejar':response.meta['cookiejar'],'item':item,'uid':follow_uid,'followlist':followlist},callback=self.get_userurl)
#                            #continue
#                        #yield  Request(url=thirdloadurl,meta={'cookiejar':response.meta['cookiejar'],'item':item,'uid':follow_uid},callback=self.parse_thirdload)
#
#                        #firstloadurl = mainpageurl + getweibopage.get_firstloadurl()
#                        #yield  Request(url=firstloadurl,meta={'cookiejar':response.meta['cookiejar'],'item':item,'uid':follow_uid},callback=self.parse_firstload)
#                else:
#                    break
#            else:
#                break
#
#    def start_getweiboinfo(self,response):
#        mainpageurl = 'http://weibo.com/u/'+str(WeiboSpider.start_uid)+'?from=otherprofile&wvr=3.6&loc=tagweibo'
#        GetWeibopage.data['uid'] = WeiboSpider.start_uid
#        getweibopage = GetWeibopage()
#        for page in range(WeiboSpider.page_num): 
#            GetWeibopage.data['page'] = page+1
#            firstloadurl = mainpageurl + getweibopage.get_firstloadurl()
#            yield  Request(url=firstloadurl,meta={'cookiejar':response.meta['cookiejar']},callback=self.parse_firstload)
#
#            secondloadurl = mainpageurl + getweibopage.get_secondloadurl()
#            yield  Request(url=secondloadurl,meta={'cookiejar':response.meta['cookiejar']},callback=self.parse_secondload)
#           
#            thirdloadurl = mainpageurl + getweibopage.get_thirdloadurl()
#            yield  Request(url=thirdloadurl,meta={'cookiejar':response.meta['cookiejar']},callback=self.parse_thirdload)
#        
#    def parse_firstload(self,response):
#        item = response.meta['item']
#        item['uid'] = response.meta['uid']
#        analyzer = Analyzer()
#        total_pq =  analyzer.get_mainhtml(response.body)
#        item['content'] = analyzer.get_content(total_pq)
#        item['time'] = analyzer.get_time(total_pq)
#        item['atuser'],item['repostuser'] = analyzer.get_atuser_repostuser(total_pq)
#        return item
#
#
#    def parse_secondload(self,response):
#        item = response.meta['item']
#        analyzer = Analyzer()
#        total_pq =  analyzer.get_mainhtml(response.body)
#        item['content'] = analyzer.get_content(total_pq)
#        item['time'] = analyzer.get_time(total_pq)
#        item['atuser'],item['repostuser'] = analyzer.get_atuser_repostuser(total_pq)
#        return item
#
#
#    def parse_thirdload(self,response):        
#        item = response.meta['item']
#        #print 'UUUUUUUUUUUUUUUUUUUUUUUUU',response.meta['item'],'OOOOOOOOOOOOOOOOOOO',item['userinfo'],"PPPPPPPPPPPPPPPPPPPPP"
#        item['uid'] = response.meta['uid']
#        item['followuidlist'] = response.meta['followlist']
#        #item['userinfo'] = response.meta['userinfo']
#        #print '{{{{{{{{{{{{{{{{{{{{{{{',response.meta['userinfo']
#        analyzer = Analyzer()
#        total_pq =  analyzer.get_mainhtml(response.body)
#        item['content'] = analyzer.get_content(total_pq)
#        item['time'] = analyzer.get_time(total_pq)
#        item['atuser'],item['repostuser'] = analyzer.get_atuser_repostuser(total_pq)
#        return item
#
#    
