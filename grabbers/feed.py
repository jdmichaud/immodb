# -*- coding: utf-8 -*-
import re
import sys
import time
import logging
import itertools
import requests
from lxml import html

from db import loaddata
from db import writedb
from db import addentries, addentry

logging.getLogger("requests").setLevel(logging.WARNING)

FIREFOX_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'

databases = []

class Feed(object):
  def __init__(self):
    logging.info("loading %s..." % self.db_filename)
    self.db = loaddata(self.db_filename)
    self.last_db_backup = 0
    databases.append((self.db_filename, self.db))
    logging.info("building search space...")
    for key, value in self.parameter_space.iteritems():
      self.parameter_space[key] = value() if callable(value) else value

  def load_insee_code(self):
    with open('comsimp2014.txt', 'r') as f:
      return [code[3] + code[4] for code in [[token for token in line.split('\t')] for line in f.readlines()[1:]]]

  def load_postal_code(self):
    return [78000]

  def get_next_url(self, url, params):
    # Get a combination of all the params together and use them to replace the placeholders in the url
    for c in itertools.product(*[[(key, value) for value in values] for key, values in params.iteritems()]):
      completed_url = url
      params = {}
      for placeholder in c:
        completed_url = completed_url.replace(placeholder[0], str(placeholder[1]))
        params[placeholder[0]] = str(placeholder[1])
      yield (completed_url, params)

  def load_page(self, url):
    page = None
    while page is None:
      try:
        logging.info('fetching %s' % url)
        user_agent = {'User-agent': FIREFOX_USER_AGENT}
        page = requests.get(url, timeout=2, headers = user_agent)
      except:
        # If the site becomes recalcitrant
        logging.info('timeout fetching %s' % url)
        time.sleep(10)
    tree = html.fromstring(page.text)
    return tree

  def fetch(self, thread_number=1):
    if self.sanity_check():
      timestamp = int(time.time())
      for url, params in self.get_next_url(self.root_url + self.url_params, self.parameter_space):
        for page in self.fetch_one_url(url):
          addentries(self.db, self.parse(page, params), timestamp)
    else:
      print "sanity check failed, bailing out..."

###############################################################################
#                                SeLoger.com                                  #
###############################################################################
class SeLoger(Feed):
  def __init__(self, dbfilename):
    self.root_url = 'http://www.seloger.fr/'
    self.url_params = 'list.htm?ci=__code_postal__&idtt=__code_transaction__&idtypebien=__type_bien__&nb_pieces=__nb_piece__'
    self.db_name = 'seloger.csv'
    self.parameter_space = {
      '__code_postal__': lambda: self.filter_postal_code(self.transform_insee_code(self.load_insee_code())),
      '__code_transaction__': [2], # 1: location, 2: vente
      '__nb_piece__': [1, 2, 3, 4, 5, '5+'],
      '__type_bien__': [1], #[1,2], # Appartement: 1 et Maison: 2
    }
    self.db_filename = dbfilename
    self.db = {}
    super(SeLoger, self).__init__()

  def transform_insee_code(self, insee_codes):
    return [insee_code[:2] + '0' + insee_code[2:] for insee_code in insee_codes]

  def filter_postal_code(self, seloger_codes):
    known_postal_code = self.get_known_postal_code()
    #return [code for code in seloger_codes[seloger_codes.index('700216'):] if code in known_postal_code]
    #return [code for code in seloger_codes if code in known_postal_code and int(code) > 690233]
    return [code for code in seloger_codes if code in known_postal_code]

  def get_known_postal_code(self):
    return set([x[1] for x in self.db])

  def parse_annonce(self, article, params):
    # get the id
    aid = re.match('annonce-(\d+)-\d+', article.get('id')).group(1)
    # the type de bien and number of pieces
    descr = article.xpath(".//div[@class='listing_infos']/h2/a/text()")[0]
    res = re.match('(.*) (\d+).*', descr)
    if res is None:
      print descr
    type_bien = res.group(1)
    nb_pieces = res.group(2)
    # the price
    amount_list = article.xpath(".//a[@class='amount']/text()")
    price = str(''.join([c for c in amount_list[0] if c.isdigit()])) if amount_list else '?' # some amount are empty ...
    # and the surface
    properties = article.xpath(".//ul[@class='property_list']/li/text()")
    surface = '?'
    for property in properties:
      # replace , with . as it is easier to deal with in excel
      res = re.match('(.+)\s*m\xb2.*', property)
      if res is not None:
        surface = res.group(1).strip().replace(',', '.')
    return (aid, params['__code_postal__'], type_bien, nb_pieces, surface, price)

  def parse(self, page, params):
    return [self.parse_annonce(article, params) for article in page.xpath("//section[@class='liste_resultat']/article")]

  def fetch_one_url(self, url):
    for page_number in xrange(1, 250):
      page = self.load_page(url + "&LISTING-LISTpg=%i" % page_number)
      result = page.xpath("//section[@class='liste_resultat']/article")
      result_from_other_town = page.xpath("//div[@class='annonce_prox_bloc']") == []
      if not result or result_from_other_town: return # no result, bail
      results = result[0].getchildren()
      if len(results) == 0: return # no results, bail
      yield page

  def sanity_check(self):
    # Check that when looking for INSEE code without a result, the page
    # displaying results *CLOSES* to the original search still shows up
    # the same
    # 390490 is Saint-Loup. A small village with not much result
    # but near to Tavaux so Tavaux result will show up,
    # We wan't to check we are able to catch that.
    page = self.load_page("http://www.seloger.com/list.htm?idtt=2&ci=390490")
    # we check the presence of a div with class annonce_prox_bloc
    if page.xpath("//div[@class='annonce_prox_bloc']") != []:
      return True
    return False

###############################################################################
#                              ExplorImmo.fr                                  #
###############################################################################
class Explorimmmo(Feed):
  pass

if __name__ == '__main__':
  seloger = SeLoger()
  print [x for x in seloger.get_next_url(seloger.root_url + seloger.url_params, seloger.parameter_space)][666]

def load_page(url):
  page = requests.get(url)
  tree = html.fromstring(page.text)
  return tree
#www.seloger.com/list.htm?ci=780646&idq=all&idtt=2&idtypebien=1&idtypebien=2&&ci=780646&idq=all&&pxmin=2000000&&tri=initial&&&nb_pieces=1&nb_pieces=2&nb_pieces=3&nb_pieces=4&nb_pieces=4%2b
