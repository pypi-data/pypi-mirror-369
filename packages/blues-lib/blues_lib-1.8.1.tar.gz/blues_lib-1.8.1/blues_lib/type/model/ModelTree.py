import sys,os,re
from typing import Any
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.model.Model import Model

class ModelTree:
  @classmethod
  def create(cls, tree: Any):
    return cls._process(tree)

  @classmethod
  def _process_dict(cls, data: dict):
    """Process dictionary data"""
    result = {}
    for key, value in data.items():
      result[key] = cls._process(value)  # Recursively process values through _process
    return result

  @classmethod
  def _process_list(cls, data: list):
    """Process list data"""
    return [cls._process(item) for item in data]  # Recursively process items through _process

  @classmethod
  def _process(cls, value:Any):
    """Central processing method that handles all value types"""
    # Check for __model__ pattern first (highest priority)
    if isinstance(value, list) and len(value) >= 2 and value[0] == '__model__':
      meta = value[1]
      bizdata = value[2] if len(value) > 2 else {} # must be a dict, or can't be set mapping
      return Model(meta, bizdata)
    
    # Handle dict processing
    elif isinstance(value, dict):
      return cls._process_dict(value)
    
    # Handle list processing
    elif isinstance(value, list):
      return cls._process_list(value)
    
    # Return all other types as-is
    else:
      return value