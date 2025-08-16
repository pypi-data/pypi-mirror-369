# Ara_log

A simple, minimalistic python logger using the logging library as its basis.

## Installation

```
pip install ara_log
```

## Usage

```python
from ara_log import Log

log = Log(name="my_log.log", level="debug")

log.debug("This is a debug message")
log.info("This is an info message")
log.warning("This is a warning message")
log.error("This is an error message")
log.critical("This is a critical message")

log.set_level("info")
log.debug("This message will not be logged")
log.info("This message will be logged")
```