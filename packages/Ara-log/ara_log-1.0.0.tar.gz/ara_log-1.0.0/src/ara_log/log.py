import logging

class Log:
    _levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    
    def __init__(self, name="ara.log", level="warning"):
        level = self._levels.get(level, None)
        if level is None:
            raise ValueError(f"Invalid log level: {level}")
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # create console handler and set level
        self.ch = logging.StreamHandler()
        self.ch.setLevel(level)

        # create formatter
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')

        # add formatter to ch
        self.ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(self.ch)


    def debug(self, msg):
        self.logger.debug(msg)


    def info(self, msg):
        self.logger.info(msg)


    def warning(self, msg):
        self.logger.warning(msg)


    def error(self, msg):
        self.logger.error(msg)


    def critical(self, msg):
        self.logger.critical(msg)
     
   
    def set_level(self, level):
        level = self._levels.get(level, None)
        if level is None:
            raise ValueError(f"Invalid log level: {level}")
        
        self.logger.setLevel(level)
        self.ch.setLevel(level)
        