from logging import Logger


class KxyLogger(Logger):
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