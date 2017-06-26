## 本地测试

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


5.- 命令行分配任务
    - 新开终端，cd到当前目录，运行 `python manage.py shell`
    - from backend.tasks import *
    - from sentiment_analysis.celery import app
    - crawl_machine1.apply_async(args=('http://hotels.ctrip.com/hotel/2906601.html',))


---

## 服务器配置
- Ubuntu-16.04
- Python 2.7
- Scrapy 1.3.3
- django 1.11.1
- celery 3.1.25
- redis 3.0.6
- IP ：118.89.203.58
- 有`machine1`和`machine2`两个队列

### 数据库
- MySQL
- HOST: 118.89.203.58
- PORT: 3306
- username: ubuntu
- password: FUDAN14ss
- table： crawl

---

## 连接到服务器
1. 在`sentiment_analysis/settings.py`中修改`CELERY_RESULT_BACKEND`和`BROKER_URL`为`redis://118.89.203.58:6379/0`即可连接到服务器
2. cd到当前路径启动celery的worker，监听machine1队列   
    `celery -A sentiment_analysis worker --loglevel=info -Q machine1`
3. 打开`http://118.89.203.58:8001/admin/`添加任务到`machine1`队列，本地即可处理

