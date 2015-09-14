# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import logging
import cx_Oracle
import sys
from scrapy.utils.project import get_project_settings
import getinfo
import re
reload(sys)
sys.setdefaultencoding('utf8')


class WeibospiderPipeline(object):
    
    settings = get_project_settings()
    start_uid = settings['UID']

    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        dbargs = dict(
            user = settings['ORACLE_USER'],
            password = settings['ORACLE_PASSWD'],
            dsn = settings['ORACLE_DSN'],
        )
        dbpool = adbapi.ConnectionPool('cx_Oracle',**dbargs)
        return cls(dbpool)
   
    def process_item(self,item,spider):
        if spider.name == 'keyweibocontent':
            d = self.dbpool.runInteraction(self._keyweibocontent_insert,item,spider)  
        elif spider.name == 'userfollow':
            d = self.dbpool.runInteraction(self._userfollow_insert,item,spider)  
        elif spider.name == 'userinfo':
            d = self.dbpool.runInteraction(self._userinfo_insert,item,spider)  
        else: #spider.name == 'keyuser':
            d = self.dbpool.runInteraction(self._keyuser_insert,item,spider)
        d.addErrback(self._handle_error,item,spider) 
        d.addBoth(lambda _:item)
        return d

    def _userfollow_insert(self,conn,item,spider): 
        if len(item['follow_uid_list']) and not len(item['follower_uid_list']):
            for i in range(len(item['follow_uid_list'])):
                conn.execute('''insert into "t_user_follow"("userID","followID") values(:1,:2)''',(str(item['uid']),item['follow_uid_list'][i]))
        
        if len(item['follower_uid_list']) and not len(item['follow_uid_list']):
            for i in range(len(item['follower_uid_list'])):
                conn.execute('''insert into "t_user_follower"("userID","followerID") values(:1,:2)''',(str(item['uid']),item['follower_uid_list'][i]))


    def _keyweibocontent_insert(self,conn,item,spider):
        #插入发表微博内容和时间
        for i in range(len(item['content'])):
            if "'" in item['content'][i]:
                content_tmp = item['content'][i].replace("'","\'")
                conn.execute('''insert into "t_user_weibocontent"("userID","content","publishTime","repostuser","repostuserID","id") values(:1,:2,to_date(:3,'YYYY-MM-DD HH24:MI'),:4,:5,(select nvl("MAX"("id"),0)+1 as "id" from "t_user_weibocontent"))''',[str(item['uid']),item['content'][i],item['time'][i],item['repost_user'][i],item['repostuser_uid'][i]])
            else:
                conn.execute('''insert into "t_user_weibocontent"("userID","content","publishTime","repostuser","repostuserID","id") values(:1,:2,to_date(:3,'YYYY-MM-DD HH24:MI'),:4,:5,(select nvl("MAX"("id"),0)+1 as "id" from "t_user_weibocontent"))''',[str(item['uid']),item['content'][i],item['time'][i],item['repost_user'][i],item['repostuser_uid'][i]])

            if item['atuser_nickname_uid'][i] != {}:
                for key in item['atuser_nickname_uid'][i].keys():
                    conn.execute('''insert into "t_user_weibocontent_atuser"("userID","publishTime","atuser","atuserID") values(:1,to_date(:2,'YYYY-MM-DD HH24:MI'),:3,:4)''',[str(item['uid']),item['time'][i],key,item['atuser_nickname_uid'][i][key]])

        


    def _userinfo_insert(self,conn,item,spider):
        #将微博用户个人信息插入数据库 
        if 'png' not in item['image_urls']:
            imageurl = "image/userphoto/"+str(item['uid'])+".jpg"
        else:
            imageurl = "image/userphoto/"+tmp[tmp.rindex('/')+1:tmp.rindex('.')]+".jpg"
             
        conn.execute('''insert into "t_user_info"("userID","userAlias","location","sex","blog","domain","brief","birthday","registertime","imageurl") values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)''',[str(item['uid']),item['userinfo']['昵称：'.decode('utf-8')],item['userinfo']['所在地：'.decode('utf-8')],item['userinfo']['性别：'.decode('utf-8')],item['userinfo']['博客：'.decode('utf-8')],item['userinfo'.decode('utf-8')]['个性域名：'.decode('utf-8')],item['userinfo']['简介：'.decode('utf-8')],item['userinfo']['生日：'.decode('utf-8')],item['userinfo']['注册时间：'.decode('utf-8')],imageurl])
        
#        if 'png' not in item['image_urls']: 
#            conn.execute("insert into t_user_info_copy(imageurl) value(%s) where userID = %s",("image/userphoto/"+str(item['uid'])+".jpg",str(item['uid'])))
#        else:
#            tmp = item['image_urls']
#            conn.execute("insert into t_user_info_copy(imageurl) value(%s) where userID = %s",("image/userphoto/"+tmp[tmp.rindex('/')+1:tmp.rindex('.')]+".jpg",str(item['uid'])))
        #conn.execute("update t_user_info set imagestate = 1 where userID = "+str(item['uid']))
        #conn.execute("update t_user_follow set infostate=1 where followID = "+item['uid'])

    def _keyuser_insert(self,conn,item,spider):
        #将关键词相关用户uid插入数据库
        for i in range(len(item['keyword_uid'])):
            conn.execute('''insert into "t_user_keyword"("userID","keyword","userAlias","time") values(:1,:2,:3,to_date(:4,'YYYY-MM-DD HH24:MI'))''',[item['keyword_uid'][i],str(item['keyword']),item['keyword_alias'][i],item['keyword_time'][i]])

    def _handle_error(self,failure,item,spider):
        logging.error(failure)

         
