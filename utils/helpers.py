def deep_copy(obj):
    import json
    return json.loads(json.dumps(obj))
