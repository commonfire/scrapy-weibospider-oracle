#-*- coding:utf-8 -*-

    def start_getweiboinfo(response):   
        mainpageurl = 'http://weibo.com/u/'+str(WeiboSpider.start_uid)+'?from=otherprofile&wvr=3.6&loc=tagweibo'
        GetWeibopage.data['uid'] = WeiboSpider.start_uid
        getweibopage = GetWeibopage()
        for page in range(WeiboSpider.page_num): 
            GetWeibopage.data['page'] = page+1
            firstloadurl = mainpageurl + getweibopage.get_firstloadurl()
            yield  Request(url=firstloadurl,meta={'cookiejar':response.meta['cookiejar']},callback=parse_firstload)

            secondloadurl = mainpageurl + getweibopage.get_secondloadurl()
            yield  Request(url=secondloadurl,meta={'cookiejar':response.meta['cookiejar']},callback=parse_secondload)
           
            thirdloadurl = mainpageurl + getweibopage.get_thirdloadurl()
            yield  Request(url=thirdloadurl,meta={'cookiejar':response.meta['cookiejar']},callback=parse_thirdload)
        
    def parse_firstload(response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        total_pq =  analyzer.get_mainhtml(response.body)
        item['content'] = analyzer.get_content(total_pq)
        item['time'] = analyzer.get_time(total_pq)
        item['atuser'],item['repostuser'] = analyzer.get_atuser_repostuser(total_pq)
        return item


    def parse_secondload(response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        total_pq =  analyzer.get_mainhtml(response.body)
        item['content'] = analyzer.get_content(total_pq)
        item['time'] = analyzer.get_time(total_pq)
        item['atuser'],item['repostuser'] = analyzer.get_atuser_repostuser(total_pq)
        return item


    def parse_thirdload(response):
        item = WeibospiderItem()
        analyzer = Analyzer()
        total_pq =  analyzer.get_mainhtml(response.body)
        item['content'] = analyzer.get_content(total_pq)
        item['time'] = analyzer.get_time(total_pq)
        item['atuser'],item['repostuser'] = analyzer.get_atuser_repostuser(total_pq)
        return item
