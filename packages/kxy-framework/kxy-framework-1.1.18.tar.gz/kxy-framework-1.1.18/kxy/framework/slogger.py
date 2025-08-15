import json
import logging
import os
import time
import uuid

from .util import SUtil
from .DailyRotatingFileHandler import DailyRotatingFileHandler
from .context import trace_id,session_id,seq,user_id,last_log_time

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = trace_id.get()
        record.session_id = session_id.get()
        record.userid = user_id.get()
        cur_seq = seq.get()
        record.seq = cur_seq
        seq.set(cur_seq+1)
        return True
def new_trace(traceId=''):
    if not traceId:
        traceId = uuid.uuid4().hex[:16]
    trace_id.set(traceId)
    session_id.set(uuid.uuid4().hex[:16])
    seq.set(0)

from logging import Logger
class slogger(Logger):
    def __init__(self, logger:Logger, level=0):
        super().__init__(logger.name,logger.level)
        self.logger = logger
        self.parent = logger.parent
        self.propagate = logger.propagate
        self.handlers = logger.handlers
        self.disabled = logger.disabled
    def _add_log_category(self, log_method, msg, logCategory='default', *args, **kwargs):
        """通用的日志分类添加方法"""
        extra = kwargs.get('extra', {})
        extra["logCategory"] = logCategory
        kwargs['extra'] = extra
        return log_method(msg, *args, **kwargs)
    
    def info(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.info, msg, logCategory, *args, **kwargs)
    
    def debug(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.debug, msg, logCategory, *args, **kwargs)
    
    def warning(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.warning, msg, logCategory, *args, **kwargs)
    
    def error(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.error, msg, logCategory, *args, **kwargs)
    
    def critical(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.critical, msg, logCategory, *args, **kwargs)
    
    def exception(self, msg, logCategory='default', *args, **kwargs):
        return self._add_log_category(self.logger.exception, msg, logCategory, *args, **kwargs)

def create_logger(logLeve,appName,env,filename='log/app',file_type='log',backupCount=5,maxBytes=10485760,mutiple_process=False):
    localIp = SUtil.get_local_ip()
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            # 计算与上次日志的时间间隔
            current_time = time.time()
            prev_time = last_log_time.get()
            duration = current_time - prev_time if prev_time > 0 else 0
            last_log_time.set(current_time)
            
            # 构建日志记录的字典
            log_record = {
                "appName":appName,
                "serverAddr":os.environ.get('IP',localIp),
                "cluster": env,
                "level": record.levelname,
                "filename": record.filename,
                "lineno": record.lineno,
                "traceId": record.trace_id,
                "sessionId": record.session_id,
                "userId":record.userid,
                "seqId": record.seq,
                "message": record.getMessage(),
                "CreateTime": self.formatTime(record, self.datefmt),
                "createdOn": int(time.time() * 1000),  # 添加 Unix 时间戳
                "duration": int(duration * 10000000)  # 添加持续时间，单位毫秒，保留2位小数
            }
            if hasattr(record, 'logCategory'):
                log_record["logCategory"] = record.logCategory
            else:
                log_record["logCategory"] = "Default"
            # 将字典转换为 JSON 字符串
            return json.dumps(log_record, ensure_ascii=False)
        
    logging.basicConfig(
        level=logLeve
    )
    _logger = logging.getLogger(appName)
    _logger.setLevel(logLeve)
    # 创建一个 RotatingFileHandler 对象
    # 确保 log 目录存在
    if '/' in filename:
        floder = filename.split('/')[0]
        os.makedirs(floder, exist_ok=True)
    handler = DailyRotatingFileHandler(
        filename=filename,
        file_type=file_type,
        when='midnight',
        interval=300,
        backupCount=backupCount,
        maxBytes=maxBytes,  # 10MB
        mutiple_process = mutiple_process
    )
    formatter = JsonFormatter()

    # 设置日志记录级别
    handler.setLevel(logLeve)
    handler.setFormatter(formatter)
    handler.addFilter(TraceIdFilter())

    _logger.addHandler(handler)
    logger = slogger(_logger)
    return logger,handler