import logging

from rich.logging import RichHandler


class CapturingRichHandler(RichHandler):
    def __init__(self, console, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = console

    def emit(self, record):
        message = self.format(record)
        message_renderable = self.render_message(record, message)
        rendered = self.render(
            record=record,
            traceback=None,
            message_renderable=message_renderable,
        )
        self.console.print(rendered)
