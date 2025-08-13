def compute_forward(client, model, messages, param):
  payload = {
    'model': model,
    'messages': messages,
    **param,
  }
  return client.post(url='/chat/completions', json=payload).json()

