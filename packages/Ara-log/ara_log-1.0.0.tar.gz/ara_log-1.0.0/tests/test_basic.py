# Test if the module can be imported
def test_import():
   import ara_log

# Test if the module can be initialized
def test_run_callable():
   from ara_log import Log
   log = Log()
   
# Test if the module can be used
def test_run():
   from ara_log import Log
   log = Log()
   log.debug("This is a debug message")
   log.info("This is an info message")
   log.warning("This is a warning message")
   log.error("This is an error message")
   log.critical("This is a critical message")
   