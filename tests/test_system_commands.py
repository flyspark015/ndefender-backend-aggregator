import asyncio

from ndefender_backend_aggregator.commands.contracts import CommandRequest
from ndefender_backend_aggregator.commands.system_commands import SystemCommandHandler
from ndefender_backend_aggregator.config import get_config


def test_system_command_requires_confirm():
    handler = SystemCommandHandler(get_config())

    async def run() -> None:
        result = await handler.handle(CommandRequest(command="system/reboot", confirm=False))
        assert result.accepted is False

    asyncio.run(run())


def test_system_command_unsafe_disabled():
    config = get_config()
    config.safety.allow_unsafe_operations = False
    handler = SystemCommandHandler(config)

    async def run() -> None:
        result = await handler.handle(CommandRequest(command="system/shutdown", confirm=True))
        assert result.accepted is False

    asyncio.run(run())
