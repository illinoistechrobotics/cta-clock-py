from cta_clock.model import Line
from rgbmatrix import FrameCanvas, graphics
from datetime import datetime, timedelta


# It's #### #### #state
messages = []
_cur_msg = 0
_swap_time = _scroll_start_time = datetime.utcnow()
_scroll_pps = 60


def line_times(canvas, line, directions, small_font, big_font):
    assert(isinstance(canvas, FrameCanvas))
    assert(isinstance(line, Line))
    assert(isinstance(directions, list))

    x = 0
    y = big_font.baseline

    # many thanks https://stackoverflow.com/questions/1855884/
    perceptive_luminance = 1 - (0.299 * line.color.red + 0.587 * line.color.blue + 0.114 * line.color.blue) / 255
    id_fg_color = 0 if perceptive_luminance < 0.5 else 255

    identifier_width = sum([big_font.CharacterWidth(ord(c)) for c in line.identifier])
    for x_ in range(0, identifier_width + 1):
        for y_ in range(0, y + 1):
            canvas.SetPixel(x_, y_, line.color.red, line.color.green, line.color.blue)

    x = graphics.DrawText(canvas, big_font, x + 1, y, graphics.Color(id_fg_color, id_fg_color, id_fg_color), line.identifier)

    graphics.DrawText(canvas, big_font, x, y, graphics.Color(255, 255, 255), ' ' + line.name)

    x = 0
    y += big_font.baseline

    if len(directions) == 0:
        msg = 'NO SCHEDULED SERVICES'
        msg_len = sum([big_font.CharacterWidth(ord(c)) for c in msg])
        x = (canvas.width - msg_len) / 2
        y = (canvas.height + big_font.baseline) / 2
        graphics.DrawText(canvas, small_font, x, y, graphics.Color(255, 255, 255), msg)
    else:
        for dir in directions:
            x = graphics.DrawText(canvas, small_font, x, y, graphics.Color(255, 255, 255), "TO ")

            graphics.DrawText(canvas, big_font, x, y, graphics.Color(255, 255, 255), dir.destination)

            next_arrival = dir.next_arrival()
            if next_arrival is None:
                next_arrival_str = ''
            elif next_arrival.is_delayed:
                next_arrival_str = 'Delay'
            elif next_arrival.is_approaching or next_arrival.minutes() <= 1:
                next_arrival_str = 'Due'
            elif next_arrival.is_scheduled:
                next_arrival_str = '* ' + str(next_arrival.minutes())
            elif next_arrival.is_fault:
                next_arrival_str = '? ' + str(next_arrival.minutes())
            else:
                next_arrival_str = str(next_arrival.minutes())

            time_len = sum([big_font.CharacterWidth(ord(c)) for c in next_arrival_str])
            x = canvas.width - time_len
            for x_ in range(x - 1, canvas.width):
                for y_ in range(y - big_font.baseline, y + 1):
                    canvas.SetPixel(x_, y_, 0, 0, 0)
            graphics.DrawText(canvas, big_font, x, y, graphics.Color(255, 255, 255), next_arrival_str)

            x = 0
            y += big_font.baseline


def lower_bar(canvas, small_font):
    global _cur_msg, _swap_time, _is_static, _msg_width, _msg_time, messages, _msg, last_frame_time, _scroll_start_time
    now = datetime.utcnow()
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

        # handle special messages
        if messages[_cur_msg] == 'CLOCK':
            fmt = "%-I:%M %p" if now.second % 2 else "%-I %M %p"
            _msg = datetime.now().strftime(fmt)
            _msg_width = sum([small_font.CharacterWidth(ord(c)) for c in _msg])
        elif messages[_cur_msg] == 'DATE':
            _msg = datetime.now().strftime('%A, %B %-d, %Y')
            _msg_width = sum([small_font.CharacterWidth(ord(c)) for c in _msg])

        # determine if we need to scroll
        if _msg_width > canvas.width:
            # we need to scroll the message
            _is_static = False
            _msg_time = ((_msg_width + canvas.width) / _scroll_pps) * 1000
            _scroll_start_time = now
        else:
            _is_static = True
            _msg_time = 5000

        # set timer for next swap
        _swap_time = now + timedelta(milliseconds=_msg_time)

    _td = now - _scroll_start_time

    scroll_progress = _td.total_seconds()

    if _is_static:
        x = (canvas.width - _msg_width) / 2
    else:
        x = canvas.width - (scroll_progress * _scroll_pps)

    #print(scroll_progress, '; x = ', x)

    y = canvas.height - 1

    if messages[_cur_msg] == 'CLOCK':
        fmt = "%-I:%M %p" if now.second % 2 else "%-I %M %p"
        _msg = datetime.now().strftime(fmt)

    graphics.DrawText(canvas, small_font, x, y, graphics.Color(255, 255, 255), _msg)