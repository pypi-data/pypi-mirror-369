import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from type.model.Model import Model
from crawler.Crawler import Crawler
from namespace.CrawlerName import CrawlerName

class LoopCrawler(Crawler):

  NAME = CrawlerName.Engine.LOOP
  
  def _setup(self):
    super()._setup()

    briefs = self._summary_conf.get(CrawlerName.Field.BRIEFS.value) 
    print('-->briefs',briefs)
    self._briefs:list[dict] = briefs if isinstance(briefs,list) else None
    self._urls:list[str] = self._summary_conf.get(CrawlerName.Field.URLS.value)
    if not self._briefs and not self._urls:
      raise Exception(f'[{self.NAME}] Failed to crawl - briefs and urls are empty')

  def _invoke(self)->STDOut:
    # crawl by briefs
    if self._briefs:
      rows = self._invoke_by_briefs()
    elif self._urls:
      rows = self._invoke_by_urls()
    # no rows is not a error
    self._output = STDOut(200,'done',rows)
  
  def _invoke_by_briefs(self)->list[dict]:
    rows:list[dict] = []
    for idx,brief in enumerate(self._briefs):
      is_last = idx == len(self._briefs) - 1
      url_key = self._summary_conf.get(CrawlerName.Field.BRIEFS_URL_KEY.value) or CrawlerName.Field.URL.value
      if url := brief.get(url_key):
        stdout = self._invoke_one(url,is_last)
        self._merge(stdout,rows,brief)
      else:
        self._logger.warning(f'[{self.NAME}] Skip to crawl - {idx}th brief url is missing')
    
    # merge the biref to the rows
    return rows

  def _invoke_by_urls(self)->list[dict]:
    rows:list[dict] = []
    for idx,url in enumerate(self._urls):
      is_last = idx == len(self._urls) - 1
      stdout = self._invoke_one(url,is_last)
      self._append(stdout,rows)
    return rows
    
  def _invoke_one(self,url:str,is_last:bool)->STDOut:
    model:Model = self._get_model(url,is_last)
    return self._crawl(model)
  
  def _merge(self,stdout:STDOut,rows:list[dict],biref:dict):
    if stdout.code == 200 and (data:=stdout.data):
      sub_rows = data if isinstance(data, list) else [data]
      for row in sub_rows:
        row.update(biref)
      rows.extend(sub_rows)

  def _append(self,stdout:STDOut,rows:list[dict]):
    if stdout.code == 200 and (data:=stdout.data):
      rows.extend(data) if isinstance(data, list) else rows.append(data)
  
  def _get_model(self,url:str,is_last:bool)->Model:
    bizdata = {
      **self._bizdata,
      CrawlerName.Field.URL.value:url, # crawl the next url
    } 
    
    # remove the teardown to avoid to quit the browser before crawl all urls
    meta = {**self._crawler_meta} 
    
    # the last one remain the teardown nodes : the browser will be quit after the last url crawled
    if not is_last:
      meta.pop(CrawlerName.Field.TEARDOWN.value,None)

    return Model(meta,bizdata)