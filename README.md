# iHome

bh-iHome project iHome 前后端分离接口项目练习 redis 文档
https://redis-py.readthedocs.io/en/stable/

celery 异步发送短信 
### 1.创建task文件夹，里面放置celery初始化，发送任务函数 
### 2.返回主业务（发送短信），修改发送短信方法，改用sms_send.delay()来放入队列发送 
###3.在worker处启动celery
####celery -A xxx（任务名） workder -l info