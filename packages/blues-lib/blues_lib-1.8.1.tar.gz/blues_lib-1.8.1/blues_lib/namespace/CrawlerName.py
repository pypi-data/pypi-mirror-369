import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from namespace.NSEnum import NSEnum
from namespace.EnumNS import EnumNS

class CrawlerName(EnumNS):
  # it's a filed level namespace

  # crawler engine
  class Engine(NSEnum):
    BASE = "BASE"
    LOOP = "LOOP"
    DEPTH = "DEPTH"

  # static fields 
  class Field(NSEnum):
    PREV = "prev" # {dict} the prev node's config
    MAPPING = "mapping" # {dict} the mapping config

    POST = "post" # {dict} the post node's config
    PROCESSOR = "processor" # {dict} the processor config

    SUMMARY = "summary" # {dict} the info about the crawler
    # field in SUMMARY
    TYPE = "type" # {str} the type of crawler
    COUNT = "count" # {int} the count of crawler
    URLS = "urls" # {list[str]} the urls to crawl
    BRIEFS = "briefs" # {list[dict]} the briefs to crawl
    BRIEFS_URL_KEY = "briefs_url_key" # {str} the page url key in the brief dict

    CRAWLER = "crawler" # {dict} the bhv executor's config
    # field in CRAWLER
    SETUP = "setup" # {dict} the setup config
    DATA = "data" # {dict} the attr to save the crawled data dict
    TEARDOWN = "teardown" # {dict} the teardown config

    # field in SETUP
    URL = "url" # {str} the url to crawl

    # field in DATA
    LOGGEDIN = "loggedin" # {bool} is logged
    CKFILE = "ckfile" # {str} is local file to save the cookie file
    