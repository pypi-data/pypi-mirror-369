import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from command.hook.processor.post.AbsPostProc import AbsPostProc
from ai.formatter.Extractor import Extractor

class AIAnswerToMat(AbsPostProc):
  
  ANSWER_KEY = 'answer'
  
  def execute(self)->None:
    '''
    @description: Convert the AI answer to mat dict
    @return: None
    '''
    answer = self._output.data.get(self.ANSWER_KEY)
    if not answer:
      raise Exception(f'{self.__class__.__name__} - No answer found')
    
    self._output.data = Extractor().execute(answer)
    
    
    
     
