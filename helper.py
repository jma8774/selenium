def try_get_json_value(json, key):
  parts = key.split(".")
  for part in parts:
    json = json.get(part)
    if json is None:
      return None
  return json

