from jipso.Conversation import Conversation
from jipso.Compute import Compute, exe
from dotenv import load_dotenv
import os, re



class Room(Conversation):
  def __init__(self, content, param={}, j=None, default={}):
    super().__init__(content)
    if j is not None: self.j = j
    self.param = param

    load_dotenv()
    if 'chatgpt' not in default:
      default['chatgpt'] = os.getenv('DEFAULT_CHATGPT', 'gpt-3.5-turbo')
    if 'claude' not in default:
      default['claude'] = os.getenv('DEFAULT_CLAUDE', 'claude-3-5-haiku-20241022')
    if 'gemini' not in default:
      default['gemini'] = os.getenv('DEFAULT_GEMINI', 'model/gemini-1.5-flash')
    if 'xai' not in default:
      default['xai'] = os.getenv('DEFAULT_XAI', 'grok-3-mini-fast')
    if 'qwen' not in default:
      default['qwen'] = os.getenv('DEFAULT_QWEN', 'qwen-turbo')
    self.default = default


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
    }
    for m in self.content:
      res['content'].append(m.dict())
    for h in ['platform', 'j', 'param']:
      if hasattr(self, h):
        res[h] = getattr(self, h)
    return res
  

  def ask(self, p=None, s=None, i=None, j=None, param={}):
    self.prev = self.__copy__()
    self.prev_param = {'p': p, 's': s, 'i': i, 'j': j}
    if not param: param = self.param
    if j is None and hasattr(self, 'j') and self.j is not None: j = self.j
    i = self if i is None else Conversation(i) + self
    c = Compute(j=j, i=i, p=p, s=s, param=param)
    o = exe(c)
    if s is not None: self += s
    if p is not None: self += p
    self += o

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
          j = self.default[j]
          self.ask(p=p, s=s, i=i, j=j, param=param)

  
  def retry(self):
    prev_param = self.prev_param
    self = self.prev
    self.chat(**prev_param)