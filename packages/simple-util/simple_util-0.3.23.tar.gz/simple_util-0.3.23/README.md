## 使用方法：
pip install simple-util
```python
from simple_util import SUtil

# 比较两个列表，返回删除的列表和新增的列表
print(SUtil.parse_diffrent_list([1,2,3], [1,2,3,4]))
([], [4])

# 将列表进行拆分
SUtil.slice_data([1,2,3,4],2)
输出：[[1, 2], [3, 4]]


# 安全删除列表中的元素
from simple_util import DeleteSafeList
a=[1,2,3,45,6,56,78]
safeDelete = DeleteSafeList(a)

for item in safeDelete:
    if item ==45:
        safeDelete.RemoveCurrent()
print(a)
# [1, 2, 3, 6, 56, 78]


```
# 日期处理函数
```python
from simple_util import DateUtil
# 获取指定日期的指定小时到指定小时的时间，如果endHour小于beginHour，则结束时间为第二天
print(DateUtil.datetime_range(datetime.now(),beginHour=22,willHour=10))
# 计算从当前时间到未来时间，返回时间戳(精确到秒)，如果传入负数，则返回从过去到当前的时间戳
print(DateUtil.timestamp_from_now(minutes=-5))
```


# 雪花算法生成Id
```python
from simple_util import SnowflakeIDGenerator
print(SnowflakeIDGenerator().get_next_id())
```

# 日志
```python
from simple_util.slogger import create_logger

logger,handler = create_logger(logging.DEBUG,'appName','production',filename='log/app',file_type='log',backupCount=5,maxBytes=10485760,mutiple_process=False)

# mutiple_process 是否多进程，多进程需要生成不同的文件

logger.info('hello world',extra={"logCategory":'http'})
```
### 日志进阶用法，设置traceId：
```python
from simple_util.slogger import user_id,user_info,new_trace
req_trace_id = request.headers.get("X-Trace-ID") or str(uuid4())
new_trace(req_trace_id)
user_id.set('login user id')
# user_info用于存储用户自定义的信息，方便在其他地方取用
user_info.set({'name':'login user name','email':'login user email'})

```
### 日志自定义打印格式：
```python

class JsonFormatter(logging.Formatter):
    def format(self, record):
        # 构建日志记录的字典
        log_record = {
            "appName":appName,
            "serverAddr":os.environ.get('IP',localIp),
            "cluster": env,
            "levelname": record.levelname,
            "filename": record.filename,
            "lineno": record.lineno,
            "traceId": record.trace_id,
            "sessionId": record.session_id,
            "userId":record.userid,
            "seqId": record.seq,
            "message": record.getMessage(),
            "CreateTime": self.formatTime(record, self.datefmt),
            "createdOn": int(time.time() * 1000)  # 添加 Unix 时间戳
        }
        # 将字典转换为 JSON 字符串
        return json.dumps(log_record, ensure_ascii=False)

from simple_util.slogger import create_logger

logger,handler = create_logger(logging.DEBUG,'appName','production',filname='log/app',file_type='log',backupCount=5,maxBytes=10485760)
handler.setFormatter(JsonFormatter())
logger.info('hello world')
```






