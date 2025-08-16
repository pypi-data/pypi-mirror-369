import logging
from typing import Optional

from sirabus import IRouteCommands, SqsConfig
from sirabus.hierarchical_topicmap import HierarchicalTopicMap
from sirabus.message_pump import MessagePump
from sirabus.publisher.amqp_command_router import AmqpCommandRouter


def create_amqp_router(
    amqp_url: str,
    topic_map: HierarchicalTopicMap,
    logger: Optional[logging.Logger] = None,
) -> IRouteCommands:
    from sirabus.publisher.pydantic_serialization import create_command

    from sirabus.publisher.pydantic_serialization import read_command_response

    return AmqpCommandRouter(
        amqp_url=amqp_url,
        topic_map=topic_map,
        logger=logger,
        message_writer=create_command,
        response_reader=read_command_response,
    )


def create_sqs_router(
    config: SqsConfig,
    topic_map: HierarchicalTopicMap,
    logger: Optional[logging.Logger] = None,
) -> IRouteCommands:
    from sirabus.publisher.pydantic_serialization import create_command
    from sirabus.publisher.pydantic_serialization import read_command_response
    from sirabus.publisher.sqs_command_router import SqsCommandRouter

    return SqsCommandRouter(
        config=config,
        topic_map=topic_map,
        logger=logger,
        message_writer=create_command,
        response_reader=read_command_response,
    )


def create_inmemory_router(
    message_pump: MessagePump,
    topic_map: HierarchicalTopicMap,
    logger: Optional[logging.Logger] = None,
) -> IRouteCommands:
    from sirabus.publisher.pydantic_serialization import (
        create_command,
        read_command_response,
    )
    from sirabus.publisher.inmemory_command_router import InMemoryCommandRouter

    return InMemoryCommandRouter(
        message_pump=message_pump,
        topic_map=topic_map,
        logger=logger,
        command_writer=create_command,
        response_reader=read_command_response,
    )
