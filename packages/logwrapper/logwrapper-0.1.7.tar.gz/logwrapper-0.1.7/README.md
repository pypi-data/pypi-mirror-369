# README

<!-- File: README.md -->
<!-- Author: YJ -->
<!-- Email: yj1516268@outlook.com -->
<!-- Created Time: 2021-04-23 16:46:31 -->

---

## Table of Contents

<!-- vim-markdown-toc GFM -->

* [Configuration](#configuration)
* [Usage](#usage)

<!-- vim-markdown-toc -->

---

Python log wrapper

---

## Configuration

Configuration file example (toml format)

```toml
[log]
to_console = true
console_level = 'DEBUG'
to_file = true
file_level = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
backup_count = 10
format = '%(asctime)s | %(levelname)-8s | <%(threadName)s> %(module)s.%(funcName)s [%(lineno)d]: %(message)s'
```

- `to_console`: whether to output log to STDOUT, 'true' or 'false', use it during debugging, and close it during formal deployment
- `console_level`: console log level (string), optional values are 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
- `to_file`: whether to output log to file, 'true' or 'false'
- `file_level`: file log level (list), fill in 'INFO', 'WARNING', 'ERROR', 'CRITICAL' according to the actual situation
- `backup_count`: log backup count
- `format`: log format, '8' represents the string length, '-' represents left alignment (default right alignment)

## Usage

```python
from logwrapper import get_logger

log_conf = {
    'to_console': True,
    'console_level': 'DEBUG',
    'to_file': True,
    'file_level': ['WARNING', 'ERROR', 'CRITICAL'],
    'backup_count': 10,
    'format':
    '''%(asctime)s | %(levelname)-8s | <%(threadName)s> '''
    '''%(module)s.%(funcName)s [%(lineno)d]: %(message)s'''
}


def main():
    """docstring for main"""
    logger = get_logger(logfolder='logs', config=log_conf)

    logger.warning('Warning text')
    logger.error('Error text')
    logger.critical('Critical text')


if __name__ == "__main__":
    main()
```
