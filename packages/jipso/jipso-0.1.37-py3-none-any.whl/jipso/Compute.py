from jipso.utils import sql_create, mongo_save
from jipso.Status import Status
from jipso.Output import Output
from jipso.utils import get_platform, get_str, mongo_save
from jipso.Client import Client
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base
from uuid import uuid4
from jipso.Conversation import Conversation
import os

Base = declarative_base()

class ComputeSQL(Base):
  __tablename__ = 'compute'
  id = Column(String(32), primary_key=True)
  j = Column(String(255), nullable=True)
  i = Column(String(32), nullable=True)
  p = Column(String(32), nullable=True)
  s = Column(String(32), nullable=True)
  o = Column(String(32), nullable=True)
  status = Column(String(32), nullable=True)

  def __init__(self, id=None):
    self.id = id if id is not None else uuid4().hex

  def __str__(self) -> str:
    return self.id
  
  def __repr__(self) -> str:
    return f'ComputeSQL({self.id})'



class Compute:
  """Orchestrates complete JIPSO evaluations and workflows.
  
  The Compute class represents a complete J(I,P,S)=O evaluation unit as a
  five-dimensional vector enabling systematic AI orchestration. Provides
  forward and reverse computational capabilities for comprehensive workflow
  management and optimization.
  
  Supports batch processing, pipeline chaining, and meta-computational
  recursion for complex multi-agent coordination. Enables serialization
  for distributed computing and workflow persistence across sessions
  and platforms.
  """
  def __init__(self, j=None, i=None, p=None, s=None, o=None, param={}):
    i = Conversation(i)
    p = Conversation(p)
    s = Conversation(s)
    o = Conversation(o)
    if i: self.i = i
    if p: self.p = p
    if s: self.s = s
    if o: self.o = o
    if j is None:
      from jipso.utils import default_model
      from dotenv import load_dotenv
      from os import getenv
      load_dotenv()
      if getenv('OPENAI_API_KEY') is not None:
        j = default_model['chatgpt']
      elif getenv('ANTHROPIC_API_KEY') is not None:
        j = default_model['claude']
      elif getenv('GEMINI_API_KEY') is not None:
        j = default_model['gemini']
      elif getenv('XAI_API_KEY') is not None:
        j = default_model['xai']
      elif getenv('QWEN_API_KEY') is not None:
        j = default_model['qwen']
    self.j = j
    self.param = param



def _exe(model, messages, param):
  platform = get_platform(model)
  client = Client(platform)()
  messages = messages.render(platform=platform)

  if platform in {'Openai', 'Alibabacloud', 'Byteplus'}:
    from jipso.vendor.Openai import compute_forward
    res = compute_forward(client=client, model=model, messages=messages, param=param)

  elif platform == 'Anthropic':
    from jipso.vendor.Anthropic import compute_forward
    if 'max_token' not in param:
      param['max_tokens'] = 512
    res = compute_forward(client=client, model=model, messages=messages, param=param)

  elif platform == 'Gemini':
    from jipso.vendor.Gemini import compute_forward
    res = compute_forward(client=client, model=model, messages=messages, param=param)
  
  elif platform == 'Xai':
    from jipso.vendor.Xai import compute_forward
    res = compute_forward(client=client, model=model, messages=messages, param=param)

  elif platform == 'Sberbank':
    from jipso.vendor.Sberbank import compute_forward
    res = compute_forward(client=client, model=model, messages=messages, param=param)

  elif platform == 'Tencentcloud':
    from jipso.vendor.Tencentcloud import compute_forward
    res = compute_forward(client=client, model=model, messages=messages, param=param)

  status = Status(response=res)
  output = Output(status.content())
  return output, status


def exe_sql(c):
  exe(c)
  c_sql = ComputeSQL()
  for e in ['i', 'p', 's', 'status']:
    if hasattr(c, e) and getattr(c, e) is not None:
      setattr(c_sql, e, getattr(c, e).id)
      mongo_save(item=getattr(c, e), collection='Conservation')
  c_sql.j = c.j
  c_sql.id = sql_create(item=c_sql, table=ComputeSQL)
  return c.o


def exe(c):
  messages = []
  for e in ['i', 'p', 's']:
    if hasattr(c, e) and getattr(c, e) is not None:
      element = getattr(c, e)
      for mess in element:
        mess.content = get_str(mess.content)
      messages.extend(element)
  messages = Conversation(messages)
  c.o, c.status = _exe(model=c.j, messages=messages, param=c.param)
  return c.o
