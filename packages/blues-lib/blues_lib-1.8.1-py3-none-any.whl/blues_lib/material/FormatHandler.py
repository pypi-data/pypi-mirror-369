import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from dao.material.MatMutator import MatMutator 

class FormatHandler(AllMatchHandler):
  
  def _setup(self):
    entities = self._request.get('entities')
    if not entities:
      message = f'[{self.__class__.__name__}] Received an empty entity'
      raise Exception(message)

    model = self._request.get('model')
    if not model:
      message = f'[{self.__class__.__name__}] Received an empty model'
      raise Exception(message)

  def _log(self,stdout:STDOut):
    if stdout.code==200:
      message = f'[{self.__class__.__name__}] Managed to retain {len(stdout.data)} entities'
      self._logger.info(message)
    else:
      message = f'[{self.__class__.__name__}] Failed to retain any valid entities - {stdout.message}'
      self._logger.error(message)

  def _mark(self,entity:dict)->STDOut:
    '''
    Mark the invalid entity in the DB, avoid to duplicately crawl
    '''
    entity['mat_stat'] = "invalid"
    return MatMutator().insert([entity]) 