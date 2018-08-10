import json

from django.utils.encoding import force_text
from django.utils.functional import Promise


class LazyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Promise):
            return force_text(o)
        return super().default(o=o)
