import os
import json

API_KEYS = os.getenv('VISUAL_CROSSING_API_KEY')
API_KEY_LIST = json.loads(API_KEYS)

API_KEY_GENERATOR = (key
                     for key
                     in API_KEY_LIST)
