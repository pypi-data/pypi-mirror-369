import sys,os,re
from abc import abstractmethod
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.executor.Executor import Executor
from behavior.BhvExecutor import BhvExecutor
from type.output.STDOut import STDOut
from type.model.Model import Model
from sele.browser.Browser import Browser 
from namespace.CrawlerName import CrawlerName

class Crawler(Executor):

  def __init__(self,model:Model,browser:Browser) -> None:
    '''
    @param model {Model} : the model of crawler
    @param browser {Browser} : the browser instance to use
    '''
    super().__init__()
    self._model:Model = model
    self._browser:Browser = browser
    self._output:STDOut = None

  def execute(self)->STDOut:
    # Template method: define the cal structure
    self._setup()
    self._invoke()
    self._slice()
    self._log()
    return self._output

  def _setup(self):
    try:
      self._conf = self._model.config
      self._meta = self._model.meta
      self._bizdata = self._model.bizdata

      self._crawler_meta = self._meta[CrawlerName.Field.CRAWLER.value]
      self._crawler_conf = self._conf[CrawlerName.Field.CRAWLER.value]
      self._summary_conf = self._conf[CrawlerName.Field.SUMMARY.value]
    except AttributeError as e:
      # 处理_model的属性缺失（如config/meta/bizdata未定义）
      message = f'[{self.NAME}] Failed to setup - Missing attribute in model'
      raise Exception(message) from e  # 保留原始异常上下文
    
    except KeyError as e:
      # 处理字典键缺失（如_meta或_conf中缺少指定键）
      message = f'[{self.NAME}] Failed to setup - Missing key in config/meta'
      raise Exception(message) from e  # 保留原始异常上下文

  @abstractmethod
  def _invoke(self):
    pass
    
  def _crawl(self,model:Model)->STDOut:
    try:
      bhv = BhvExecutor(model,self._browser)
      stdout:STDOut = bhv.execute()
      if isinstance(stdout.data,dict):
        stdout.data = stdout.data.get(CrawlerName.Field.DATA.value)
      return stdout
    except Exception as e:
      message = f'[{self.NAME}] Failed to crawl - {e}'
      self._logger.error(message)
      return STDOut(500,message)
  
  def _slice(self):
    count = self._summary_conf.get(CrawlerName.Field.COUNT.value)
    rows = self._output.data
    if count and rows and isinstance(rows,list):
      self._output.data = rows[:count]

  def _log(self):
    if self._output.code != 200:
      message = f'[{self.NAME}] Failed to crawl - {self._output.message}'
      self._logger.warning(message)
    else:
      message = f'[{self.NAME}] Managed to crawl'
      self._logger.info(message)