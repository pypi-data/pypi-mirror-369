#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: logwrapper.py
Author: YJ
Email: yj1516268@outlook.com
Created Time: 2021-04-25 08:54:08

Description: Generate logger
"""

import logging
import os
from logging import handlers


def get_logger(logfolder: str, config: dict):
    """Initialize the log module and get logger

    :logfolder: str -- Log folder name
    :config: dict   -- Log Configuration Parameters
    :return: logger

    """
    LEVEL = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    # Get config
    to_console = config.get('to_console', False)  # Output to console?
    console_level = config.get('console_level', 'DEBUG')  # Console log level
    to_file = config.get('to_file', True)  # Output to file?
    file_level = config.get(
        'file_level', ['INFO', 'WARNING', 'ERROR'])  # Choose File handler
    backup_count = config.get('backup_count', 10)  # Count of backup log files
    log_format = config.get('format', '%(message)s')  # Define log format

    # Define variable
    sep = os.path.sep

    # Create and set up a logger
    logger = logging.getLogger()
    logger.setLevel(LEVEL['INFO'])
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')

    # Output to file
    if to_file:
        # If the log folder does not exist, create it
        if not os.path.exists(logfolder):
            os.makedirs(logfolder)

        # Instantiate the rotated file handler
        # INFO Level
        if 'info' in file_level or 'info'.upper() in file_level:
            info_logfile = '{}{}{}'.format(logfolder, sep, 'info.log')
            info_filehandler = handlers.TimedRotatingFileHandler(
                filename=info_logfile,
                when='midnight',
                interval=1,
                backupCount=backup_count,
                encoding='UTF-8')
            info_filehandler.setLevel(LEVEL['INFO'])
            info_filehandler.setFormatter(formatter)
            logger.addHandler(info_filehandler)

        # WARNING Level
        if 'warning' in file_level or 'warning'.upper() in file_level:
            warning_logfile = '{}{}{}'.format(logfolder, sep, 'warning.log')
            warning_filehandler = handlers.TimedRotatingFileHandler(
                filename=warning_logfile,
                when='midnight',
                interval=1,
                backupCount=backup_count,
                encoding='UTF-8')
            warning_filehandler.setLevel(LEVEL['WARNING'])
            warning_filehandler.setFormatter(formatter)
            logger.addHandler(warning_filehandler)

        # ERROR Level
        if 'error' in file_level or 'error'.upper() in file_level:
            error_logfile = '{}{}{}'.format(logfolder, sep, 'error.log')
            error_filehandler = handlers.TimedRotatingFileHandler(
                filename=error_logfile,
                when='midnight',
                interval=1,
                backupCount=backup_count,
                encoding='UTF-8')
            error_filehandler.setLevel(LEVEL['ERROR'])
            error_filehandler.setFormatter(formatter)
            logger.addHandler(error_filehandler)

        # CRITICAL Level
        if 'critical' in file_level or 'critical'.upper() in file_level:
            critical_logfile = '{}{}{}'.format(logfolder, sep, 'critical.log')
            critical_filehandler = handlers.TimedRotatingFileHandler(
                filename=critical_logfile,
                when='midnight',
                interval=1,
                backupCount=backup_count,
                encoding='UTF-8')
            critical_filehandler.setLevel(LEVEL['CRITICAL'])
            critical_filehandler.setFormatter(formatter)
            logger.addHandler(critical_filehandler)

    # Output to console
    if to_console:
        # # Instantiate a stream handler
        consolehandler = logging.StreamHandler()
        consolehandler.setLevel(LEVEL[console_level.upper()])
        consolehandler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(consolehandler)

    return logger
