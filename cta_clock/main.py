#!/usr/bin/python3
# ITR's CTA clock

from datetime import datetime, timedelta
from rgbmatrix import RGBMatrix, graphics
from cta_clock import render, util
from cta_clock.config import load_config, gen_options, create_providers
from cta_clock.model import update_providers, RouteProvider
from sys import stdin, exc_info
from select import select

import subprocess

matrix = canvas = None
data_locks = 0


def main():
    global matrix, canvas
    cfg = load_config()
    options = gen_options(cfg)

    # Prepare matrix & fonts

    small_font = graphics.Font()
    small_font.LoadFont(cfg['display']['small_font'])

    large_font = graphics.Font()
    large_font.LoadFont(cfg['display']['large_font'])

    default_text_color = graphics.Color(255, 255, 255)

    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()

    last_slide = datetime.utcnow()
    cur_provider = cur_line = cur_dir = 0
    render.last_frame_time = datetime.utcnow()

    # Wait for network
    print('[main]\tWaiting for network...')
    while not util.is_connected():
        pass
    print('[main]\tConnected.')

    print('[main]\tRegistering providers...')
    providers = create_providers(cfg)

    print('[main]\tReady.')

    # set up route provider
    # loop through the providers until we get a RouteProvider
    while not isinstance(providers[cur_provider], RouteProvider):
        cur_provider += 1
        if cur_provider >= len(cur_provider):
            cur_provider = 0

    while True:
        # Process input
        # If stdin has data:
        if select([stdin], [], [], 0) == ([stdin], [], []):
            char = stdin.read(1)

            if char == 'i':
                ip_start_time = datetime.now()
                ip_len = timedelta(seconds=10)
                ips = util.get_ips()

                with open('/proc/meminfo') as f:
                    meminfo = dict(map(str.strip, line.split(':', 1)) for line in f)

                try:
                    version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
                except subprocess.CalledProcessError:
                    version = None

                while ip_start_time + ip_len > datetime.now():
                    canvas.Clear()
                    y = large_font.baseline
                    for ip in ips[:2]:
                        if ip != '127.0.0.1':
                            graphics.DrawText(canvas, large_font, 0, y, graphics.Color(255, 255, 255), ip)
                            y += large_font.baseline

                    x = 0
                    y = canvas.height
                    graphics.DrawText(canvas, small_font, x, y, graphics.Color(255, 255, 255), '%s/%s free' % (meminfo['MemAvailable'], meminfo['MemTotal']))

                    if version:
                        y -= small_font.baseline
                        graphics.DrawText(canvas, small_font, x, y, graphics.Color(255, 255, 255), 'Version ' + version)

                    canvas = matrix.SwapOnVSync(canvas)

                continue

        if datetime.utcnow() - last_slide > timedelta(milliseconds=cfg['slideshow']['slide_time']):
            print('[main]\tSwitching slides')
            # if there are more directions, display those
            if len(providers[cur_provider].lines[cur_line].directions) > 2 * (cur_dir + 1):
                cur_dir += 1
            else:
                # advance to the next line
                cur_dir = 0

                if cur_line == len(providers[cur_provider].lines) - 1:
                    # advance to the next provider
                    cur_line = 0
                    print('Swapping providers')
                    cur_provider += 1
                    while not isinstance(providers[cur_provider], RouteProvider):
                        print('Skipping %d, its not a RouteProvider' % (cur_provider))
                        cur_provider += 1
                        if cur_provider >= len(providers):
                            cur_provider = 0
                else:
                    cur_line += 1

            last_slide = datetime.utcnow()
            print('[main]\tSwitched to provider %d, line %d, directions %d - %d' % (cur_provider, cur_line, cur_dir, cur_dir + 1))

        canvas.Clear()

        l = providers[cur_provider].lines[cur_line]
        d = l.directions[cur_dir * 2:(cur_dir + 1) * 2]

        render.line_times(canvas, l, d, small_font, large_font)
        render.lower_bar(canvas, small_font, providers)
        render.loading_icon(canvas, providers, large_font)
        render.last_frame_time = datetime.utcnow()

        canvas = matrix.SwapOnVSync(canvas)

        update_providers(providers)

if __name__ == '__main__':
    # fault tolerance... heh
    while True:
        try:
            main()
        except:
            print(exc_info())
