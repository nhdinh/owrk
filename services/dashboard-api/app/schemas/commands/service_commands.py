from dataclasses import dataclass
from app.core.message_bus import Command


@dataclass
class RegisterServiceCommand(Command):
    pass
