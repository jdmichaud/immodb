import db
import sys
import feed
import atexit
import logging

from db import writedb
from feed import databases
from feed import SeLoger

logging.getLogger("requests").setLevel(logging.WARNING)

def update_feed():
  pass

def exit_handler():
  for filename, database in databases:
    print 'writing %s...' % filename
    writedb(filename, database)

def setup_logger():
  # create logger with 'spam_application'
  logger = logging.getLogger('')
  logger.setLevel(logging.DEBUG)
  # create file handler which logs even debug messages
  fh = logging.FileHandler('immodb.log')
  fh.setLevel(logging.DEBUG)
  # create console handler with a higher log level
  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
  # create formatter and add it to the handlers
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  fh.setFormatter(formatter)
  ch.setFormatter(formatter)
  # add the handlers to the logger
  # logger.addHandler(fh)
  logger.addHandler(ch)

def main(feed_name):
  setup_logger()
  seloger = getattr(feed, feed_name)()
  seloger.fetch()

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "usage: shell.py FeedName"
    sys.exit(1)

  atexit.register(exit_handler)
  main(sys.argv[1])
