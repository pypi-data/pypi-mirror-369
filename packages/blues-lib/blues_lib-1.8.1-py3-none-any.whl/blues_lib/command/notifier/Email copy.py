import sys,os,re
from typing import List

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.output.STDOut import STDOut
from util.BluesMailer import BluesMailer  
from command.NodeCommand import NodeCommand
from util.BluesFiler import BluesFiler
from namespace.CommandName import CommandName

class Email(NodeCommand):

  NAME = CommandName.Notifier.EMAIL

  def _invoke(self)->STDOut:
    payload = self.get_payload()
    mailer = BluesMailer.get_instance()
    return mailer.send(payload)
      
  def get_payload(self)->dict:
    entities = None
    if self._output and self._output.code==200:
      entities = self._output.data

    title = self._get_subject(entities)
    content = self._get_content(title,entities)
    subject = BluesMailer.get_title_with_time(title)
    return {
      'subject':subject,
      'content':content,
      'images':None,
      'addressee':['langcai10@dingtalk.com'], # send to multi addressee
      'addressee_name':'BluesLiu',
    }

  def _get_subject(self,entities:List[dict])->str:
    subject = ''
    if entities:
      count = len(entities)
      subject = f'Managed to crawl and persist {count} entities'
    else:
      subject = 'Failed to crawl and persist entities'
    return subject

  def _get_content(self,title:str,entities:List[dict])->str:
    para = self._get_para(entities)
    urls = self._get_urls()
    detail = self._get_log()
    return BluesMailer.get_html_body(title,para,urls,detail)
  
  def _get_urls(self):
    href = self._logger.file
    text = f'Local log file: {href}'
    return [
      {
        'href':href,
        'text':text,
      }
    ]
    
  def _get_log(self):
    file = self._logger.file
    separator = self._logger.separator
    content = BluesFiler.read(file)
    if content:
      # retain the latest one
      items = content.split(separator)
      non_empty_items = [item.strip() for item in items if item.strip()]
      content = non_empty_items[-1] if non_empty_items else content
      
      # break line
      content = content.replace('\n','<br/>')
      # dash line
      pattern = r'[-=]{10,}'
      content = re.sub(pattern, '----------', content)
    return content
  
  def _get_para(self,entities:List[dict])->str:
    para = ''
    if not entities:
      return 'Failed to crawl entities'

    para = f'There are {len(entities)} entities:<br/>'

    for idx,entity in enumerate(entities):
      para+=f"{idx+1}. {entity['material_title']}</br>"
    return para