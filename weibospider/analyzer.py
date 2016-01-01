# -*- coding: utf-8 -*-   
import re
import json
from pyquery import PyQuery as pq

class Analyzer:
    '''网页内容分析'''
    def __init__(self):
        self.content_list = []      #微博内容列表
        self.time_list = []         #微博发表时间列表
        self.timestamp_list = []    #微博发表时间戳列表
        self.atuser_list = []       #记录用户微博@用户
        self.repostuser_list = []   #记录微博转发用户
        self.follower_list = []     #某用户粉丝列表
        self.follow_list = []       #某用户关注列表
        self.childfollow_list = []  #某子用户关注列表
        self.userinfo_dict = {}.fromkeys(('昵称：'.decode('utf-8'),'所在地：'.decode('utf-8'),'性别：'.decode('utf-8'),'博客：'.decode('utf-8'),'个性域名：'.decode('utf-8'),'简介：'.decode('utf-8'),'生日：'.decode('utf-8'),'注册时间：'.decode('utf-8')),'')  #获取非公众账号基本信息
        self.public_userinfo_dict = {}.fromkeys(('联系人：'.decode('utf-8'),'电话：'.decode('utf-8'),'邮箱：'.decode('utf-8'),'友情链接：'.decode('utf-8')),'')  #获取公众账号基本信息
        self.keyuser_id = []          #与某关键词相关的用户uid
        self.keyuser_alias = []       #与某关键词相关的用户昵称
        self.keyuser_time = []        #与某关键词相关用户uid发表内容的时间
        self.keyuser_timestamp = []   #与某关键词相关用户uid发表内容的时间戳
        self.containsFirstTagWeibo = False #判断用户是否含第一个有'置顶'或'热帖'标签的微博

#########################################获取个人主页内容#################################
    def get_mainhtml(self,total): 
        '''获取个人主页中html内容'''
        total_pq = pq(unicode(total))  
	    #获取指定<script>
        total1 = total_pq('script:contains("WB_feed WB_feed_profile")').html()   
	    #利用正则匹配出大括号内的内容（json串）
        p=re.compile('{.*}',re.S)
        match = p.search(unicode(total1)) 
        if match:
            data1=match.group() 
            data2=json.loads(data1)
            data3=data2['html'].decode('utf-8')
            total_pq = pq(unicode(data3))
            return total_pq
        else:
            print "get_main_html wrong!"

    def get_content(self,total_pq):
        '''获取用户发表微博内容'''
        data = total_pq("div[node-type=feed_list_content]")
        i = 0
        for d in data :
            d = pq(d)
            if i == 0 and str(d("span")) != "": #不爬取置顶帖/热帖span.W_icon_feedpin/feedhot
                self.containsFirstTagWeibo = True
            else:
                if '//' in d.text():   #用户发表微博存在"转发"情况
                    p1=re.compile('(.*?)\s?//\s?<a',re.S)  #找出用户自己所发内容，不含//后面的转发内容
                    match = p1.search(d.outerHtml())
                    if match:
                        if match.group(1).strip() == '':  #发表内容为空
                            self.content_list.append('')
                        else:
                            data_pq = pq(match.group(1))
                            #print '~~~~~~~~~~~~',data_pq.outerHtml()
                            content = self.get_content_src(data_pq)
                            #print '1111111111', content
                            self.content_list.append(content)
                    else:
                        #用户发表的内容就是含有//本身
                        self.content_list.append(d.text())

                else: #用户直接发表微博，没有转发情况
                    content = self.get_content_src(d)                
                    self.content_list.append(content)
            i = i+1
        return self.content_list

    def get_content_src(self,data_pq):
        '''获取用户发表微博数据，包括表情符号'''
        content = []
        for item in list(data_pq.contents()):
            if 'Element img' not in str(item) and 'Element a' not in str(item) and 'Element span' not in str(item):  #不包含表情标签img和链接标签a
                content.append(str(item).strip())
            elif 'img' in str(item):  #爬取微博中表情内容
                parents = pq(item).outerHtml()
                if pq(parents).attr("title")==None:
                    print 'NOT Sina bulit-in image!'    #此时不是新浪系统的img，是用户发的手机内置表情
                else:
                    content.append(pq(parents).attr("title"))
        return ''.join(content)    #content列表转换为字符串
	
    def get_time(self,total_pq):
        '''获取用户发表微博时间'''
        datatime = total_pq('div.WB_from')
        beginIndex = 0;
        if self.containsFirstTagWeibo == True:  #判断是否含有置顶/热帖微博
            beginIndex = 1
        for i in range(beginIndex,len(datatime)):
            dt = pq(datatime.eq(i))
            if(dt.find('a').eq(0).attr('name')):  #注意不记录转发微博原文的发表时间
                time = dt.find('a').eq(0).attr('title')
                timestamp = dt.find('a').eq(0).attr('date') 
                self.time_list.append(time)
                self.timestamp_list.append(timestamp)
        return self.time_list,self.timestamp_list

    def get_atuser_repostuser(self,total_pq):
        '''获取用户微博中@的用户以及获取转发微博的一级源用户'''
        user = total_pq('div[node-type=feed_list_content]')
        for au in user:
            au = pq(au)
            if '//' in au.text():     #存在"转发"可能
                #p1 = re.compile('(<a.*?</a>)\s?//',re.S)
                p1 = re.compile('(.*?)\s?//\s?<a',re.S)  #获取第一个//之前的内容
                match1 = p1.search(au.html())
                if match1:       #记录用户微博中的"@用户"和"微博主题#xxx#,后续会处理只得到@用户"
                    if match1.group(1).strip() == '':  #发表内容为空
                        self.atuser_list.append('')
                    else:
                        atuser_set = pq(match1.group(1))('a').text()   
                        self.atuser_list.append(atuser_set)
                else:
                    self.atuser_list.append('')
                    
                p2 = re.compile('.*?//(<a.*?@(.+?)</a>)',re.S)
                match2 = p2.search(au.html())
                if match2:      #记录"转发"用户
                    self.repostuser_list.append(match2.group(2))
                else:
                    self.repostuser_list.append('')

            else:    #用户没有"转发"，直接发表微博
                atuser_set1 = au.find('a').text()   #记录用户微博中的"@用户"和"微博主题#xxx#"
                self.atuser_list.append(atuser_set1)
                
                repostuser = au.parents('div.WB_detail')  #记录"转发"用户，此时用户直接转发原始微博，不会有//
                ru = repostuser.find('div[node-type=feed_list_forwardContent]').find('a').eq(0).attr('nick-name') 
                if ru is not None:
                    self.repostuser_list.append(ru) 
                else:
                    self.repostuser_list.append('')
        return self.atuser_list,self.repostuser_list

######################################获取粉丝列表########################################

    def get_followerhtml(self,total):
        '''获取粉丝列表页面中html内容'''	
        total_pq = pq(unicode(total)) 
        total1 = total_pq('script:contains("info_name W_fb W_f14")').html()        
        p = re.compile('{.*}',re.S)
        match = p.search(unicode(total1))
        if match:
            data1=match.group()
            data2=json.loads(data1)
            data3=data2['html'].decode('utf-8')
            total_pq = pq(unicode(data3))
            return total_pq
        else:
            print "get_follower_html wrong!"

    def get_follower(self,total_pq):
        '''获取某用户的粉丝uid'''
        try:
            data = total_pq("div.info_name")
            for dflr in data:
                dflr = pq(dflr)
                flr_uid = dflr.find('a').eq(0).attr('usercard')
                p = re.compile('id=(\d*)')
                match = p.search(unicode(flr_uid))
                if match:
                    self.follower_list.append(match.group(1))
                else:
                    print "get_follower wrong!"
        except Exception,e:
            print "Exception!:",e.message
        return self.follower_list
	    

####################################获取关注列表###########################################
    def get_followhtml(self,total):
        '''获取关注列表页面中html内容'''
        total_pq = pq(unicode(total))
        total1 = total_pq('script:contains("title W_fb W_autocut")').html()
        p = re.compile('{.*}',re.S)
        match = p.search(unicode(total1))
        if match:
            data1=match.group()
            data2=json.loads(data1)
            data3=data2['html'].decode('utf-8')
            total_pq = pq(unicode(data3))
            return total_pq
        else:
            print "get_follow_html wrong!"
    
    def get_follow(self,total_pq):
        '''获取某用户的关注uid'''
        try:
            data = total_pq("div.title")
            for dfl in data:
                dfl = pq(dfl)
                fl_uid = dfl.find('a').eq(0).attr('usercard')
                p = re.compile('id=(\d*)')
                match = p.search(unicode(fl_uid))
                if match:
                    self.follow_list.append(match.group(1))
                else:
                    print "get_follow wrong!"
        except Exception,e:
            print e.message
        return self.follow_list

    def get_childfollowhtml(self,total):
        '''获得子用户的关注列表页面html'''
        total_pq = self.get_followerhtml(total)  #和获取粉丝粉丝列表页面的方法相同
        return total_pq

    def get_childfollow(self,total_pq):
        '''获得子用户的关注用户'''
        self.childfollow_list = self.get_follower(total_pq)
        return self.childfollow_list

    def get_relation_pagenum(self,total_pq):
        '''获取关注/粉丝列表页面总数 '''
        data = total_pq('div.W_pages')
        follow_pagenum = data.find('a').eq(-2).text()
        return follow_pagenum

#########################################解析微博用户的个人信息##########################################
    def get_html(self,total,condition):
        '''获得爬取网页中html内容'''
        total_pq = pq(unicode(total))
        #获取指定<script>
        total1 = total_pq(condition).html()
        #利用正则匹配出大括号内的内容（json串）
        p=re.compile('{.*}',re.S)
        match = p.search(unicode(total1))
        if match:
            data1=match.group()
            data2=json.loads(data1)
            data3=data2['html'].decode('utf-8')
            total_pq = pq(unicode(data3))
            return total_pq
        else:
            print "get_html wrong!"                                            
   
    
    def get_userinfohref(self,total_pq):
        '''获取微博非公众账号用户的个人信息请求链接'''
        href = total_pq("div.PCD_person_info").children('a').attr('href')
        url = "http://weibo.com"+href
        return url

    def get_public_userinfohref(self,total_pq):
        '''获取微博公众账号用户的个人信息请求链接'''
        href = total_pq("div.PCD_person_info").children('a').attr('href')
        return href
        

    def get_userinfo(self,total_pq):
        '''解析微博非公众用户个人详细信息'''
        user_li = total_pq("div.WB_innerwrap").eq(0).children(".m_wrap").children("ul").find('li')
        for li in user_li:
            li = pq(li)
            #self.userinfo_dict[li.find('span').eq(0).text()] = li.find('span').eq(1).text()
            self.userinfo_dict[li.find('span').eq(0).text()] = re.sub('\n','',li.find('span').eq(1).text())    
        return self.userinfo_dict

    def get_public_userinfo(self,total_pq):
        '''解析微博公众用户个人详细信息'''
        user_li = total_pq("div.WB_innerwrap").eq(0).children(".m_wrap").children("ul").find('li')
        for li in user_li:
            li = pq(li)
            if li.find('span').eq(0).text() == "友情链接：":
                link_list = []
                list = li.find('span').eq(1).find('a')
                for a in list:
                    link_list.append(pq(a).text())
                self.public_userinfo_dict['友情链接：'.decode('utf-8')] = link_list 
            else:
                self.public_userinfo_dict[li.find('span').eq(0).text()] = re.sub('\n','',li.find('span').eq(1).text())    
        return self.public_userinfo_dict


    def get_userproperty(self,total_pq):
        '''获取用户属性（V字认证，达人）''' 
        property = total_pq("span.icon_bed").children("a").attr("class")
        if property: # property不为None
            list = property.split(" ")
            return list[1]
        else:
            return ''
     

    def get_userphoto_url(self,total_pq):
        '''获取微博用户头像的url地址'''
        url = total_pq("div.pf_photo").find('img').attr('src')
        return url

    def get_keyuser(self,total_pq):
        '''获取关键词相关用户uid及昵称'''
        data1 = total_pq("div.feed_content")
        data2 = total_pq("div.content").children("div.feed_from")
        for dku in data1:
            dku = pq(dku)
            alias = dku.find('a').eq(0).attr('nick-name')   #获取用户昵称
            self.keyuser_alias.append(alias)

            href = dku.find('a').eq(0).attr('usercard')     #获取用户uid
            p = re.compile("id=(\d*)&",re.S)
            match = p.search(unicode(href))
            if match:
                  self.keyuser_id.append(match.group(1))
            else:
                print "get_keyuser wrong!!"

        for dku in data2:
            dku = pq(dku)
            time = dku.find('a').eq(0).attr("title")
            timestamp = dku.find('a').eq(0).attr("date")
            self.keyuser_time.append(time)
            self.keyuser_timestamp.append(timestamp)
        return self.keyuser_id,self.keyuser_alias,self.keyuser_time,self.keyuser_timestamp

