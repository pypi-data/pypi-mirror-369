import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from namespace.CommandName import CommandName
from command.NodeCommand import NodeCommand
from dao.material.MatQuerier import MatQuerier
from type.output.STDOut import STDOut

class Querier(NodeCommand):

  NAME = CommandName.Material.QUERIER
  TYPE = CommandName.Type.SETTER

  def _invoke(self)->STDOut:
    querier = MatQuerier()
    count = self._summary.get('count',1)
    mat_chan = self._summary.get('mat_chan','article')
    query = {
      'mat_chan':mat_chan,
      'mat_stat':'available',
    }
    return querier.random(query,count)

    