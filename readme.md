# 分布式爬虫系统

## 设计文档

1. 功能概述
    - 电商酒店网页自动结构化：支持输入[携程酒店](http://hotels.ctrip.com)或[艺龙酒店](http://hotel.elong.com/)等网站具体的某一家具体酒店的url，例如[徐州枫叶红商务宾馆](http://hotels.ctrip.com/hotel/2906601.html)和[上海中福大酒店](http://hotel.elong.com/30201106/)，系统将自动结构化数据到爬取网站、酒店、房间类型、顾客、评论等5张表中
    - 新闻博客网页自动正文提取：

2. 设计思路
    - 爬虫
        - 选择`Scrapy`作为爬虫框架，针对网站的反爬虫机制，我们在`Scrapy`中引入了`Selenium`以模拟用户实际浏览网页的行为，并且在切换页面时设置了必要的阻塞时间，这样既保证了爬虫的运行效率，也避免了被反爬虫机制屏蔽。
        - 在爬虫运行时，使用预先编辑好的`XPath`规则从网页中提取出特定的数据，因此不同的电商酒店网站，可以提取出相同的结构化的数据。提取的结构化数据通过`Django`的数据库模块进行`ORM`映射，存入`MySQL`数据库中。
        - 针对url去重问题，我们在`CrawlWebsite`表中设置了字段`lock`，在爬取前会先进行依次查询，如果`lock`为`True`表示当前已经有相同url的执行任务，则当前任务会直接终止。`CrawlWebsite`表中有字段`lastest_time`记录了该url最后一次更新的时间。
    - 分布式策略
        - 选择`Celery`作为分布式处理模块，每一个爬取任务都是作为一个`Task`传递给消息中间件`broker`，这里我们选择`Redis`作为`broker`的实现，因此每一个`Task`生成后都会进入`broker`的队列中等待被执行
        - 执行`Task`的是`worker`，`worker`在消息队列中选择一个任务开始爬取，而`worker`支持多进程，在其启动时可以指定运行的进程数，默认为机器的cpu数，例如在进程数设置为4时，`worker`会在队列中选择4个任务并发执行。另外可以在多台机器上添加多个`worker`，这样添加任务是同一个入口，但是任务在多个机器上分布执行，即使在单个机器上也可以分布式执行。所以无论是升级单台机器的配置进行纵向的分布式扩容，还是添加多台机器监听同一个消息队列实现横向的分布式扩容，都是非常容易的，整个系统的分布式处理能力也非常强。
        - 我们还设置两个消息队列，这里为了方便命名为`machine1`和`machine2`。用户在选择执行任务时可以选择将任务添加到哪一个消息队列中。在实际应用中，可将其中一个消息队列的权限提升作为一个类似vip的队列，相应的队列的`worker`并发能力也更强一些。系统支持添加更多的消息队列，只需要添加新的`Task`并进行简单的设置。该功能可满足实际应用中不同级别处理等应用场景。
        - `celery`支持对每一个任务状态的监控，因此在任务出现错误时可以自动取消、重试或提醒。`celery`也支持定时任务，只需要开启`beat`，定时任务在定期更新爬取网站的数据时非常有用
        - `Hadoop`
    - 界面
        - 选择`Django`作为Web框架，用户输入url进行任务分配；查看任务运行状态；添加定时任务、周期性任务；以及查看结构化的数据都在`admin`界面进行。
        - 整个前台部署在云服务器上，用户可直接在线分配任务、查看编辑任务、查看爬取的结果或在线添加`worker`
    - 服务器配置
        - Ubuntu-16.04
        - Python 2.7
        - Scrapy 1.3.3
        - django 1.11.1
        - celery 3.1.25
        - redis 3.0.6
        - IP ：118.89.203.58
        - 有`machine1`和`machine2`两个队列    
    - 数据库
        - MySQL
        - host: 118.89.203.58
        - port: 3306
        - username: ubuntu
        - password: FUDAN14ss
        - table： crawl

3. 添加`worker`的方法
    - cd到当前路径启动`celery`的`worker`，监听`machine1`队列   
    `celery -A sentiment_analysis worker --loglevel=info -Q machine1`

---


#### 本地测试

1. 启动Redis服务

2. cd到当前路径启动celery beat   
    ` celery -A sentiment_analysis beat `

3. cd到当前路径启动celery的worker，监听machine1队列   
    `celery -A sentiment_analysis worker --loglevel=info -Q machine1`

4. cd到当前路径启动开发服务器  
    ` python manage.py runserver `
    - 打开 ` http://localhost:8000/admin/ `
    - 账号： `fudan14ss`
    - 密码： `FUDAN14ss`
    - 设置`Periodic tasks`，其中`backend.tasks.crawl_machine1`是将任务添加到队列1，`backend.tasks.crawl_machine2`添加到队列2。在`Arguments`中添加参数，例如
    `["http://hotels.ctrip.com/hotel/2906601.html"]`。`save`保存结果


5. 命令行分配任务
    - 新开终端，cd到当前目录，运行 `python manage.py shell`
    - from backend.tasks import *
    - from sentiment_analysis.celery import app
    - crawl_machine1.apply_async(args=('http://hotels.ctrip.com/hotel/2906601.html',))

#### 连接到服务器
1. 在`sentiment_analysis/settings.py`中修改`CELERY_RESULT_BACKEND`和`BROKER_URL`为`redis://118.89.203.58:6379/0`即可连接到服务器
2. cd到当前路径启动celery的worker，监听machine1队列   
    `celery -A sentiment_analysis worker --loglevel=info -Q machine1`
3. 打开`http://118.89.203.58:8001/admin/`添加任务到`machine1`队列，本地即可处理

