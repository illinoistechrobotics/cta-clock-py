from cta_clock.model import Line, MessageProvider
from rgbmatrix import FrameCanvas, graphics
from datetime import datetime, timedelta


# It's #### #### #state
messages = []
_cur_provider = 0
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


def lower_bar(canvas, small_font, providers):
    global _cur_provider, _cur_msg, _swap_time, _is_static, _msg_width, _msg_time, messages, _msg, last_frame_time, _scroll_start_time
    now = datetime.utcnow()
    if datetime.utcnow() > _swap_time:
        print('[lower_bar]\tSwitching messages')
        # swap messages
        # check to see if we have a message provider (on first run this will more than likely be false)

        # we have a message provider, so load the next message
        _cur_msg += 1
        if not isinstance(providers[_cur_provider], MessageProvider) or _cur_msg >= len(providers[_cur_provider].messages):
            print('[lower_bar]\tSwitching providers (cur_msg = %d; there are %d messages)' % (_cur_msg, len(providers[_cur_provider].messages) if isinstance(providers[_cur_provider], MessageProvider) else 0))
            # switch providers
            _cur_msg = 0
            _cur_provider += 1
            while _cur_provider >= len(providers) or not isinstance(providers[_cur_provider], MessageProvider) or len(providers[_cur_provider].messages) == 0:
                _cur_provider += 1
                if _cur_provider >= len(providers):
                    _cur_provider = 0

        _msg = providers[_cur_provider].messages[_cur_msg].get_message()
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

        print('[lower_bar]\tSwitched to provider %d, message %d: %s' % (_cur_provider, _cur_msg, _msg))

    _td = now - _scroll_start_time

    scroll_progress = _td.total_seconds()

    if _is_static:
        x = (canvas.width - _msg_width) / 2
    else:
        x = canvas.width - (scroll_progress * _scroll_pps)

    #print(scroll_progress, '; x = ', x)

    y = canvas.height - 1

    _msg = providers[_cur_provider].messages[_cur_msg].get_message()

    graphics.DrawText(canvas, small_font, x, y, graphics.Color(255, 255, 255), _msg)


_loading_last_frame_time = datetime.utcnow()
_loading_last_frame = 0
_loading_fps = 10
_loading_frames = ['|', '/', '-', '\\']
def loading_icon(canvas, providers, font):
    global _loading_last_frame_time, _loading_last_frame, _loading_fps, _loading_frames
    requests_pending = False
    for provider in providers:
        if provider.pending_requests > 0:
            requests_pending = True
            break

    if requests_pending:
        if _loading_last_frame_time + timedelta(milliseconds=1000/_loading_fps) < datetime.utcnow():
            # advance to the next frame
            _loading_last_frame += 1
            if _loading_last_frame >= len(_loading_frames):
                _loading_last_frame = 0
            _loading_last_frame_time = datetime.utcnow()

        x = canvas.width - sum([font.CharacterWidth(ord(c)) for c in _loading_frames[_loading_last_frame]])
        y = font.baseline
        graphics.DrawText(canvas, font, x, y, graphics.Color(255, 255, 255), _loading_frames[_loading_last_frame])

