import asyncio

from ndefender_backend_aggregator.commands import (
    CommandHandler,
    CommandRequest,
    CommandResult,
    CommandRouter,
)


class StubHandler(CommandHandler):
    def can_handle(self, command: str) -> bool:
        return command == "scan/start"

    async def handle(self, request: CommandRequest) -> CommandResult:
        return CommandResult(
            command=request.command,
            command_id="stub-id",
            accepted=True,
            detail=None,
            timestamp_ms=1,
        )


def test_router_dispatches_to_handler():
    router = CommandRouter([StubHandler()])

    async def run() -> None:
        result = await router.dispatch(CommandRequest(command="scan/start"))
        assert result.accepted is True
        assert result.command_id == "stub-id"

    asyncio.run(run())


def test_router_handles_unknown_command():
    router = CommandRouter([])

    async def run() -> None:
        result = await router.dispatch(CommandRequest(command="unknown"))
        assert result.accepted is False

    asyncio.run(run())
