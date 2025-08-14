"""
Helpers for interactive prompts
"""


class PromptAlarmInterrupt(Exception):
    "Exception for user-prompt timeouts"


def handle_alarm(signum, frame):
    """
    called when read times out
    """
    raise PromptAlarmInterrupt


def confirm_with_timeout(msg='', timeout=None, default=True):
    """
    Runs rich.Confirm.ask with a timeout

    References:
        .. [SO1335507] https://stackoverflow.com/questions/1335507/keyboard-input-with-timeout
        .. [SO22916783] https://stackoverflow.com/questions/22916783/reset-python-sigint-to-default-signal-handler
    """
    import signal
    import rich
    from rich import prompt
    if timeout is not None:
        signal.alarm(timeout)
        original_sigalarm_handler = signal.getsignal(signal.SIGALRM)
        rich.print(f'The following prompt will default to {default!r} in {timeout} seconds...')
        signal.signal(signal.SIGALRM, handle_alarm)
    try:
        ans = prompt.Confirm.ask(msg)
        if timeout is not None:
            # Disarm the alarm as soon as possible after getting the answer.
            signal.alarm(0)
        return ans
    except PromptAlarmInterrupt:
        print('\n')
        rich.print('... prompt time out')
        return default
    finally:
        if timeout is not None:
            signal.signal(signal.SIGALRM, original_sigalarm_handler)
