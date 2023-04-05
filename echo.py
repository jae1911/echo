from typing import Optional
from time import time
from html import escape

from mautrix.types import TextMessageEventContent, MessageType, Format, RelatesTo, RelationType

from maubot import Plugin, MessageEvent
from maubot.handlers import command


class EchoBot(Plugin):
    @staticmethod
    def plural(num: float, unit: str, decimals: Optional[int] = None) -> str:
        num = round(num, decimals)
        if num == 1:
            return f"{num} {unit}"
        else:
            return f"{num} {unit}s"

    @classmethod
    def prettify_diff(cls, diff: int) -> str:
        if abs(diff) < 10 * 1_000:
            return f"{diff} ms"
        elif abs(diff) < 60 * 1_000:
            return cls.plural(diff / 1_000, 'second', decimals=1)
        minutes, seconds = divmod(diff / 1_000, 60)
        if abs(minutes) < 60:
            return f"{cls.plural(minutes, 'minute')} and {cls.plural(seconds, 'second')}"
        hours, minutes = divmod(minutes, 60)
        if abs(hours) < 24:
            return (f"{cls.plural(hours, 'hour')}, {cls.plural(minutes, 'minute')}"
                    f" and {cls.plural(seconds, 'second')}")
        days, hours = divmod(hours, 24)
        return (f"{cls.plural(days, 'day')}, {cls.plural(hours, 'hour')}, "
                f"{cls.plural(minutes, 'minute')} and {cls.plural(seconds, 'second')}")

    @command.new("beep", help="Beep")
    @command.argument("message", pass_raw=True, required=False)
    async def ping_handler(self, evt: MessageEvent, message: str = "") -> None:
        diff = int(time() * 1000) - evt.timestamp
        pretty_diff = self.prettify_diff(diff)
        text_message = f'"{message[:20]}" took' if message else "took"
        html_message = f'"{escape(message[:20])}" took' if message else "took"
        content = TextMessageEventContent(
            msgtype=MessageType.NOTICE, format=Format.HTML,
            body=f"{evt.sender}: Boop! (beep {text_message} {pretty_diff} to arrive)",
            formatted_body=f"<a href='https://matrix.to/#/{evt.sender}'>{evt.sender}</a>: Boop! "
            f"(<a href='https://matrix.to/#/{evt.room_id}/{evt.event_id}'>beep</a> {html_message} "
            f"{pretty_diff} to arrive)",
            relates_to=RelatesTo(
                rel_type=RelationType("xyz.maubot.pong"),
                event_id=evt.event_id,
            ))
        pong_from = evt.sender.split(":", 1)[1]
        content.relates_to["from"] = pong_from
        content.relates_to["ms"] = diff
        content["pong"] = {
            "ms": diff,
            "from": pong_from,
            "ping": evt.event_id,
        }
        await evt.respond(content)

    @command.new("echo", help="Repeat a message")
    @command.argument("message", pass_raw=True)
    async def echo_handler(self, evt: MessageEvent, message: str) -> None:
        await evt.respond(message)
