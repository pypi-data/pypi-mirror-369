import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.NodeCommand import NodeCommand
from namespace.CommandName import CommandName
from type.output.STDOut import STDOut
from dao.material.MatMutator import MatMutator 

class Sink(NodeCommand):
  
  NAME = CommandName.Material.SINK

  def _setup(self):
    super()._setup()
    if not self._output or self._output.code != 200:
      message = f'[{self.NAME}] Failed to check - {self.OUTPUT} is not ok'
      raise Exception(message)

  def _invoke(self)->STDOut:
    method = self._summary.get('method','insert')
    
    # insert to the db
    if method == 'insert':
      return self._insert()
    elif method == 'update':
      return self._update()
    elif method == 'delete':
      return self._delete()
    else:
      self._logger.warning(f'[{self.NAME}] Skip to upsert - {method} is not supported')
    
  def _insert(self)->STDOut:
    entity:dict = self._summary.get('entity')
    entities:list[dict] = self._output.data
    if entity:
      for item in entities:
        item.update(entity)
    return MatMutator().insert(entities) 
  
  def _update(self)->STDOut:
    output_entity:dict = self._output.data
    entity:dict = self._summary.get('entity',{})
    merged_entity = {**entity,**output_entity}
    conditions:list[dict] = self._summary.get('conditions')
    return MatMutator().update(merged_entity,conditions)

  def _delete(self)->STDOut:
    conditions:list[dict] = self._summary.get('conditions')
    return MatMutator().delete(conditions)

