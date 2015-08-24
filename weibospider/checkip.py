#-*-coding: utf-8 -*-
import urllib2,socket,time

check_url='http://www.sohu.com'

def check_proxy(protocol,ip_port):
    try:
        proxy_support = urllib2.ProxyHandler({protocol:ip_port})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
        req = urllib2.Request(check_url)
        time_start = time.time()
        src = urllib2.urlopen(req)
        time_end = time.time()
        return src.read()
    except urllib2.HTTPError,e:
        print 'Error code:',e.code
        return False
    except Exception,detail:
        print 'Error:',detail
        return False
        
def main():
    socket.setdefaulttimeout(30)
    protocol = 'http'
    ip_port = '117.136.234.6:80'
    result = check_proxy(protocol,ip_port)
    if result:
        print 'Work!!'
    else:
        print 'Failed!!'

if __name__ == '__main__':
    main()
