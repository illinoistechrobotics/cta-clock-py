import os
import json
from rgbmatrix import RGBMatrixOptions
from cta_clock.model import Provider, Line, Direction


def load_config():
    filepath = '/etc/transit-clock/config.json' if os.path.isfile('/etc/transit-clock/config.json') else 'config.json'

    if not os.path.isfile(filepath):
        cfg = init_config('config.json')
    else:
        with open(filepath, 'r') as f:
            cfg = json.load(f)
    return cfg


def init_config(path):
    cfg = {
        'display': {
            'chain': 2,
            'rows': 32,
            'cols': 64,
            'brightness': 30,
            'hardware_mapping': 'adafruit-hat',
            'debug': {
                'show_refresh_rate': False
            },
            'small_font': 'fonts/4x6.bdf',
            'large_font': 'fonts/cI6x12.bdf'
        },
        'providers': [
            {
                'provider': 'cta_clock.providers.cta_rail',
                'endpoint': 'http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx',
                'key': 'MY_CTA_TRAIN_API_KEY',
                'lines': [
                    {
                        'name': 'Red Line',
                        'color': (255, 0, 0),
                        'map_id': 40190,
                        'directions': ['Howard', '95th/Dan Ryan']
                    },
                    {
                        'name': 'Green Line',
                        'color': (0, 255, 0),
                        'map_id': 41120,
                        'directions': ['Harlem/Lake', '63rd/Cottage Grove', '63rd/Ashland']
                    }
                ]
            }, {
                'provider': 'cta_clock.providers.static_messages',
                'messages': [
                    'Hello, world!'
                ]
            }, {
                'provider': 'cta_clock.providers.clock'
            }
        ]
    }

    with open(path, 'w') as f:
        json.dump(cfg, f, indent=True)

    return cfg


def gen_options(cfg):
    options = RGBMatrixOptions()

    options.chain_length = int(cfg['display']['chain'])
    options.rows = int(cfg['display']['rows'])
    options.cols = int(cfg['display']['cols'])
    options.brightness = float(cfg['display']['brightness'])
    options.hardware_mapping = cfg['display']['hardware_mapping']

    options.show_refresh_rate = int(cfg['display']['debug']['show_refresh_rate'])

    return options


def create_providers(cfg):
    import importlib
    providers = []

    for p in cfg['providers']:
        module = importlib.import_module(p['provider'])
        providers.append(module.init(p))

    return providers
