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

    followdata = {
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

    def get_followurl(self):
        return urllib.urlencode(GetWeibopage.followdata)



