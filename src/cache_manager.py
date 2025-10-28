import base64
import json
from pathlib import Path


class CacheManager:

    def __init__(self):
        self.cache_file = Path.home() / '.movie_wall_cache.json'

    def get_cache(self):
        try:
            with open(self.cache_file, 'r', encoding="utf-8") as f:
                cache_str = self.b64decode(f.read())
                return json.loads(cache_str)
        except Exception as e:
            print(e)
            return []

    def set_cache(self, cache):
        with open(self.cache_file, 'w', encoding="utf-8") as f:
            cache_str = json.dumps(cache)
            f.write(self.b64encode(cache_str))

    def b64encode(self, data):
        data = base64.b64encode(data.encode("utf-8"))
        print(data)
        return data.decode()

    def b64decode(self, encoded_string):
        data = base64.b64decode(encoded_string).decode("utf-8")
        print(data)
        return data
