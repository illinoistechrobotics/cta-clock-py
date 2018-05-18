from cta_clock.model import Line
from rgbmatrix import FrameCanvas, graphics
from datetime import datetime, timedelta


# It's #### #### #state
messages = []
_cur_msg = 0
_swap_time = _scroll_start_time = datetime.utcnow()
_scroll_pps = 30


def line_times(canvas, line, directions, small_font, big_font):
    assert(isinstance(canvas, FrameCanvas))
    assert(isinstance(line, Line))
    assert(isinstance(directions, list))

    x = 0
    y = big_font.baseline

    id_fg_color = 255 if \
        line.color.red < 127 or   \
        line.color.green < 127 or \
        line.color.blue < 127     \
        else 0

    identifier_width = sum([big_font.CharacterWidth(ord(c)) for c in line.identifier])
    for x_ in range(0, identifier_width):
        for y_ in range(0, y + 1):
            canvas.SetPixel(x_, y_, line.color.red, line.color.green, line.color.blue)

    x = graphics.DrawText(canvas, big_font, x, y, graphics.Color(id_fg_color, id_fg_color, id_fg_color), line.identifier)

    graphics.DrawText(canvas, big_font, x, y, graphics.Color(255, 255, 255), ' ' + line.name)

    x = 0
    y += big_font.baseline

    if len(directions) >= 1:
        x = graphics.DrawText(canvas, small_font, x, y, graphics.Color(255, 255, 255), "TO ")
        graphics.DrawText(canvas, big_font, x, y, graphics.Color(255, 255, 255), directions[0].destination)

        x = 0
        y += big_font.baseline

    if len(directions) >= 2:
        x = graphics.DrawText(canvas, small_font, x, y, graphics.Color(255, 255, 255), "TO ")
        graphics.DrawText(canvas, big_font, x, y, graphics.Color(255, 255, 255), directions[1].destination)

        x = 0
        y += big_font.baseline


def lower_bar(canvas, small_font):
    global _cur_msg, _swap_time, _is_static, _msg_width, _msg_time, messages, _msg, last_frame_time, _scroll_start_time
    if datetime.utcnow() > _swap_time:
        # swap messages
        if _cur_msg is None or _cur_msg == len(messages) - 1:
            _cur_msg = 0
        else:
            _cur_msg += 1

        # assume a default width for special messages
        if messages[_cur_msg] != 'CLOCK' or messages[_cur_msg] != 'DATE':
            _msg = messages[_cur_msg]
            _msg_width = sum([small_font.CharacterWidth(ord(c)) for c in _msg])

        # determine if we need to scroll
        if _msg_width > canvas.width:
            # we need to scroll the message
            _is_static = False
            _msg_time = ((_msg_width + canvas.width) / _scroll_pps) * 1000
            _scroll_start_time = datetime.utcnow()
        else:
            _is_static = True
            _msg_time = 5000

        # set timer for next swap
        _swap_time = datetime.utcnow() + timedelta(milliseconds=_msg_time)

    now = datetime.utcnow()

    # handle special messages
    if messages[_cur_msg] == 'CLOCK':
        fmt = "%-I:%M %P" if now.second % 2 else "%-I %M %P"
        _msg = datetime.now().strftime(fmt)
        _msg_width = sum([small_font.CharacterWidth(ord(c)) for c in _msg])
    elif messages[_cur_msg] == 'DATE':
        _msg = datetime.now().strftime('%A, %B %-d, %Y')
        _msg_width = sum([small_font.CharacterWidth(ord(c)) for c in _msg])

    _td = now - _scroll_start_time

    scroll_progress = _td.total_seconds()

    if _is_static:
        x = (canvas.width - _msg_width) / 2
    else:
        x = canvas.width - (scroll_progress * _scroll_pps)

    print(scroll_progress, '; x = ', x)

    y = canvas.height

    graphics.DrawText(canvas, small_font, x, y, graphics.Color(255, 255, 255), _msg)