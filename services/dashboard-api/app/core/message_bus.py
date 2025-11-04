from dataclasses import dataclass
import logging
from typing import Dict, Generic, Type, TypeVar


logger = logging.getLogger(__name__)


@dataclass
class Query:
    pass


@dataclass
class Command:
    pass


# TCommand = TypeVar("TCommand", bound=Command)
TCommand = TypeVar("TCommand", bound=Command)
TQuery = TypeVar("TQuery", bound=Query)
TResult = TypeVar("TResult")


class CommandHandler(Generic[TCommand, TResult]):
    """Base class for command handlers"""

    async def handle(self, command: TCommand) -> TResult:
        raise NotImplementedError


class QueryHandler(Generic[TQuery, TResult]):
    """Base class for query handlers"""

    async def handle(self, query: TQuery) -> TResult:
        raise NotImplementedError


class MessageBus:
    """
    Message Bus for dispatching commands and queries
    Implements the Mediator pattern for CQRS
    """

    def __init__(self) -> None:
        self._query_handlers: Dict[Type[Query], QueryHandler] = {}
        self._command_handlers: Dict[Type[Command], CommandHandler] = {}

    def register_command_handler(
        self, command_type: Type[TCommand], handler: CommandHandler[TCommand, TResult]
    ):
        """Register a command handler"""
        self._command_handlers[command_type] = handler
        logger.info(f"Registered command handler for {command_type.__name__}")

    def register_query_handler(
        self, query_type: Type[TQuery], handler: QueryHandler[TQuery, TResult]
    ):
        """Register a query handler"""
        self._query_handlers[query_type] = handler
        logger.info(f"Registered query handler for {query_type.__name__}")

    async def execute_command(self, command: TCommand, **dependencies) -> TResult:
        """
        Execute a command by dispatching to its handler

        Args:
            command: Command to execute
            **dependencies: Dependencies to pass to handler (e.g., db=session)
        """
        command_type = type(command)
        handler = self._command_handlers.get(command_type)

        if not handler:
            raise ValueError(
                f"No handler registered for command {command_type.__name__}"
            )

        logger.info(f"Executing command: {command_type.__name__}")
        return await handler.handle(command, **dependencies)

    async def execute_query(self, query: TQuery, **dependencies) -> TResult:
        """
        Execute a query by dispatching to its handler

        Args:
            query: Query to execute
            **dependencies: Dependencies to pass to handler (e.g., db=session for history queries)
        """
        query_type = type(query)
        handler = self._query_handlers.get(query_type)

        if not handler:
            raise ValueError(f"No handler registered for query {query_type.__name__}")

        logger.debug(f"Executing query: {query_type.__name__}")
        return await handler.handle(query, **dependencies)


# Global message bus instance
message_bus = MessageBus()


def get_message_bus() -> MessageBus:
    """Dependency injection for message bus"""
    return message_bus
