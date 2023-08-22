#!/usr/bin/env python3

import logging

logging.basicConfig(
    filename="/home/rsp/programs/myeditorial/test_logging.log",
    level=logging.DEBUG,
    format="%(asctime)s = %(levelname)s - %(message)s",
)

logging.info("This is a test log message.")
print("Log message written. Check the log file")
