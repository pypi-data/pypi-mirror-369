from tencentcloud.tiangong.v20230901 import models
import ujson

def compute_forward(client, model, messages, param):
  params = {
    'Model': model,
    'Messages': messages,
    **param,
  }
  req = models.ChatCompletionsRequest()
  req.from_json_string(ujson.dumps(params))
  return client.ChatCompletions(req).to_json_string()