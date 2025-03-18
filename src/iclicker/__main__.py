from . import connection 
from . import websockets
from getpass import getpass
import logging
import sys

logger = logging.getLogger(__name__)

def pre_wait():
    logger.info("Waiting for class")

def post_wait():
    logger.info("Found class")

def prompt():
    try:
        return int(input("Choose a class to be polled: "))
    except ValueError:
        return prompt()
    except KeyboardInterrupt:
        logger.info("Stopping connection")
        exit(0)

def main():
    logger_format = "[%(levelname)s]\t(%(asctime)s) %(message)s"
    date_format = "%H:%M:%S"
    logging.basicConfig(level=logging.INFO, format=logger_format, datefmt=date_format)
    args = sys.argv
    if len(sys.argv) != 2:
        logging.error("Unexpected number of arguments.")
        logging.info("Usage: iclicker <email>")
        exit(0)
    user = args[1]
    password = getpass()
    keys = connection.connect(user, 
                    password, 
                    [pre_wait, post_wait], 
                    prompt, 2)
    websockets.connect(keys)

if __name__ == "__main__":
    main()
