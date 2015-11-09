#-*- coding: utf-8 -*-
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import re

class UserImagesPipeline(ImagesPipeline):
   
    def file_path(self,request,response=None,info=None):
        p1 = re.compile('.cn/(\d*?)/')
        match1 = p1.search(request.url)
        if(match1):
            return 'full/%s.jpg' % match1.group(1)
        else:
            p2 = re.compile('face/(.*?).png')  #微博用户头像可能是新浪默认头像，url为：http://img.t.sinajs.cn/t5/style/images/face/male_180.png形式
            match2 = p2.search(request.url)
            if(match2):
                return 'full/%s.jpg' % match2.group(1)
            else:
                print "get image_name wrong!!"

    def thumb_path(self,request,thumb_id,response=None,info=None):
        p1 = re.compile('.cn/(\d*?)/')
        match1 = p1.search(request.url) 
        if(match1):
            return 'thumbs/%s/%s_thumbnail.jpg' % (thumb_id,match1.group(1))
        else:
            p2 = re.compile('face/(.*?).png')  #微博用户头像可能是新浪默认头像，url为：http://img.t.sinajs.cn/t5/style/images/face/male_180.png形式
            match2 = p2.search(request.url)
            if(match2):
                return 'thumbs/%s/%s_thumbnail.jpg' % (thumb_id,match2.group(1))
            else:
                print "get image_name wrong!!"


    def get_media_requests(self,item,info):
        if 'image_urls' in item and item['image_urls']: #item中有image_urls字段且其不为None
            image_url = item['image_urls']
            yield scrapy.Request(image_url)

    def item_completed(self,results,item,info):
        image_paths = [x['path'] for isTrue,x in results if isTrue]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item
