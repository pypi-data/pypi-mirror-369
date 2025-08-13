import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.SQLSTDOut import SQLSTDOut
from dao.sql.TableQuerier import TableQuerier

class MatQuerier(TableQuerier):

  _TABLE = 'ap_mat'

  def __init__(self) -> None:
    super().__init__(self._TABLE)

  def exist(self,mat_id:str)->bool:
    fields = ['mat_id']
    conditions = [
      {
        'field':'mat_id',
        'comparator':'=',
        'value':mat_id,
      },
    ]
    stdout:SQLSTDOut = self.get(fields,conditions)
    return stdout.count>0

  def random(self,query:dict=None,size:int=1)->SQLSTDOut:
    '''
    @description: Get a random row
    @param {dict} query : the query dict,like:
      {
        'mat_chan':'article',
        'mat_stat':'available',
      }
    @param {int} size : the size of the random rows
    @returns {SQLSTDOut}
    '''
    # get all fields
    fields = '*' 
    conditions = [
      {
        'field':'mat_stat',
        'comparator':'=',
        'value':query.get('mat_stat','available')
      },
      {
        'field':'mat_paras',
        'comparator':'!=',
        'value':'',
      },
    ]
    
    if query.get('mat_chan'):
      conditions.append({
        'field':'mat_chan',
        'comparator':'=',
        'value':query.get('mat_chan')
      })

    # get the latest
    orders = [{
      'field':'rand()',
      'sort':''
    }]
    # get one row
    pagination = {
      'no':1,
      'size':size
    }
    return self.get(fields,conditions,orders,pagination)

  def latest(self,query:dict=None,size:int=1)->SQLSTDOut:
    '''
    @description: Get the latest rows
    @param {dict} query : the query dict,like:
      {
        'mat_chan':'article',
        'mat_stat':'available',
      }
    @param {int} size : the size of the latest rows
    @returns {SQLSTDOut}
    '''
    # get all fields
    fields = None 
    # only get the available row
    conditions = [{
      'field':'mat_stat',
      'comparator':'=',
      'value':query.get('mat_stat','available')
    }]
    
    if query.get('mat_chan'):
      conditions.append({
        'field':'mat_chan',
        'comparator':'=',
        'value':query.get('mat_chan')
      })
      
    # get the latest
    orders = [{
      'field':'mat_ctime',
      'sort':'desc'
    }]
    # get one row
    pagination = {
      'no':1,
      'size':size
    }
    return self.get(fields,conditions,orders,pagination)
