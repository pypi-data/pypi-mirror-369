from jipso.Conversation import Conversation
from jipso.Compute import Compute, exe
from jipso.utils import default_model, mongo_save
import re


class Room(Conversation):
  def __init__(self, content=None, param={}, j=None, default={}):
    super().__init__(content)
    if j is not None: self.j = j
    self.param = param
    if default:
      for k,v in default_model.items():
        if k not in default:
          default[k] = v
      self.default = default
    else:
      self.default = default_model
    mongo_save(self, 'Room')


  def __copy__(self):
    item = Room(content=self.content)
    for k,v in self.dict().items():
      if k not in ['id', 'content']:
        setattr(item, k, v)
    return item

  def dict(self):
    res = {
      'id': self.id,
      'content': [],
      'param': self.param,
      'default': self.default,
    }
    for m in self.content:
      res['content'].append(m.dict())
    for h in ['platform', 'j']:
      if hasattr(self, h):
        res[h] = getattr(self, h)
    return res
  

  def ask(self, p=None, s=None, i=None, j=None, param={}):
    if not param: param = self.param
    if j is None and hasattr(self, 'j') and self.j is not None:
      j = self.j
    j = self.default.get(j, j)
    p = Conversation(p)
    s = Conversation(s)
    self += Conversation(i)
    c = Compute(j=j, i=self.content, p=p, s=s, param=param)
    o = exe(c)
    if s is not None: self += s
    if p is not None: self += p
    self += o
    mongo_save(self, 'Room')

  def chat(self, p=None, s=None, i=None, j=None, param={}):
    if p is not None:
      p = Conversation(p)
      call = []
      for mess in p:
        if '@@' in mess:
          call.extend(set(re.findall(r'@@(\w+)', mess.content)))
      call = set(call)
      if len(call) > 0:
        for j in call:
          self.ask(p=p, s=s, i=i, j=j, param=param)
    else:
      self += Conversation(i)
      self += Conversation(s)
      self += Conversation(p)
    mongo_save(self, 'Room')

  def rollback(self, index):
    index = self.find(index)[0]
    item = self.__copy__()
    item.content = item.content[:index+1]
    return item
