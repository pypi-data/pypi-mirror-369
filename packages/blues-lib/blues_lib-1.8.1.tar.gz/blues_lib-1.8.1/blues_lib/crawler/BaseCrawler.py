import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.model.Model import Model
from namespace.CrawlerName import CrawlerName
from crawler.Crawler import Crawler

class BaseCrawler(Crawler):

  NAME = CrawlerName.Engine.BASE
    
  def _invoke(self)->None:
    # implement the crawl logic
    model = Model(self._crawler_meta,self._bizdata)
    self._output:STDOut = self._crawl(model)
    
