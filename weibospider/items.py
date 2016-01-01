# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from  scrapy import Field,Item

class WeibospiderItem(Item):
    # define the fields for your item here like:
    uid = Field()                  #微博用户uid
    content = Field()              #微博发表内容
    time = Field()                 #微博发表时间
    timestamp = Field()            #微博发表时间戳
    
    atuser_nickname_list = Field()  #微博@用户（昵称列表）
    atuser_uid = Field()            #微博@用户（uid） 
    atuser_nickname = Field()       #微博@用户（昵称）
    
    repost_user = Field()          #微博转发用户（昵称）
    repostuser_uid = Field()       #微博转发用户（uid）
    
    follow_uid_list = Field()      #关注用户uid列表
    follower_uid_list = Field()    #粉丝用户uid列表
    
    userinfo = Field()             #用户基本信息
    image_urls = Field()           #用户头像图片链接
    user_property = Field()        #用户属性，如达人，公众账号
    userAlias_public =  Field()           #公众账号昵称
    
    keyword_uid = Field()          #与关键词相关的用户uid
    keyword_alias = Field()        #与关键词相关的用户uid
    keyword_time = Field()         #与关键词相关用户发表微博时间
    keyword_timestamp = Field()    #与关键词相关用户发表微博时间戳
    keyword = Field()              #搜索的关键词
