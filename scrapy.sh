cd /home/hadoop_user/scrapy-weibospider/
if [ "$#" -eq 2 ];then
    python /home/hadoop_user/scrapy-weibospider/crawler.py $1 $2 
else
    python /home/hadoop_user/scrapy-weibospider/crawler.py $1 $2 $3
fi
