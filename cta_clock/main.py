#!/usr/bin/python3
# ITR's CTA clock

from datetime import datetime, timedelta
from rgbmatrix import RGBMatrix, graphics
from cta_clock import render
from cta_clock.config import load_config, gen_options, create_providers
from cta_clock.model import update_providers

matrix = None

def main():
    global matrix
    cfg = load_config()
    options = gen_options(cfg)
    providers = create_providers(cfg)
    render.messages = cfg['lower_bar']['messages']

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

    while True:
        if datetime.utcnow() - last_slide > timedelta(milliseconds=cfg['slideshow']['slide_time']):
            # choose the next slide to display
            # if there are more directions, display those
            if len(providers[cur_provider].lines[cur_line].directions) > 2 * (cur_dir + 1):
                cur_dir += 1
            else:
                # advance to the next line
                cur_dir = 0

                if cur_line == len(providers[cur_provider].lines) - 1:
                    # advance to the next provider
                    cur_line = 0

                    if cur_provider == len(providers) - 1:
                        cur_provider = 0
                    else:
                        cur_provider += 1
                else:
                    cur_line += 1

            last_slide = datetime.utcnow()

        canvas.Clear()

        l = providers[cur_provider].lines[cur_line]
        d = l.directions[cur_dir * 2:(cur_dir + 1) * 2]

        render.line_times(canvas, l, d, small_font, large_font)
        render.lower_bar(canvas, small_font)
        render.last_frame_time = datetime.utcnow()

        canvas = matrix.SwapOnVSync(canvas)

        update_providers(providers)

if __name__ == '__main__':
    main()
