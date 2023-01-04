import json

from django.utils.encoding import force_str
from django.utils.functional import Promise


class LazyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_str(o)
        return super().default(o=o)
