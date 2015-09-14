#-*-coding: utf-8 -*-
import sys
import urllib

reload(sys)
sys.setdefaultencoding('utf-8')


class GetWeibopage:
    data = {
        '_rnd':'',
        '_k':'',
        '_t':'0',
        'count':'50',
        'end_id':'',
        'max_id':'',
        'page':'',
        'pagebar':'',
        'pre_page':'',
        'uid':'',
    }

    relation_data = {  #获取子用户粉丝和关注时的url参数,不用同下（主用户获取方式）因为V字认证用户用下方法无法获取
        'page':''
    }
   
    follow_data = {    #获取主用户粉丝和关注时的url参数
        'cfs':'',
        't':'1',
        'Pl_Official_RelationMyfollow__104_page':''      
    }
    
    def get_firstloadurl(self):
        GetWeibopage.data['pre_page'] = GetWeibopage.data['page']-1
        return urllib.urlencode(GetWeibopage.data)

    def get_secondloadurl(self):
        GetWeibopage.data['count'] = '15'
        GetWeibopage.data['pagebar'] = '0'
        GetWeibopage.data['pre_page'] = GetWeibopage.data['page']
        return urllib.urlencode(GetWeibopage.data)

    def get_thirdloadurl(self):
        GetWeibopage.data['count'] = '15'
        GetWeibopage.data['pagebar'] = '1'
        GetWeibopage.data['pre_page'] = GetWeibopage.data['page']
        return urllib.urlencode(GetWeibopage.data)

    def get_relation_paramurl(self):
        return urllib.urlencode(GetWeibopage.relation_data)

    def get_follow_paramurl(self):
        return urllib.urlencode(GetWeibopage.follow_data)
