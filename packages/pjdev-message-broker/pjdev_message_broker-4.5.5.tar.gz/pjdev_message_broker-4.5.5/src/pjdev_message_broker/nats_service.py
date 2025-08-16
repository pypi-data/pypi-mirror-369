import asyncio
from ssl import SSLContext
from typing import Any, Awaitable, Callable, List, Optional, Type, TypeVar

import nats
from nats.aio.client import Client, Subscription
from nats.aio.msg import Msg
from nats.errors import TimeoutError
from nats.js import JetStreamContext
from nats.js.api import RetentionPolicy, Header, StreamConfig, ConsumerConfig, AckPolicy
from pydantic import BaseModel
from loguru import logger


from pjdev_message_broker.models import (
    ErrorMessage,
    Message,
    MessageBaseModel,
    MessageResponse,
)

T = TypeVar("T", bound=MessageBaseModel)

nc: Optional[Client] = None
js: Optional[JetStreamContext] = None
subscriptions: List[Subscription] = []


class NatsInitializationError(Exception):
    def __init__(self):
        super().__init__("Failed to initialize nats client")

async def init(servers: List[str], tls: Optional[SSLContext] = None, use_js: bool = False) -> None:

    global nc
    logger.info(f"Attempting to connect to nats server: {','.join(servers)}")
    nc = await nats.connect(servers, tls=tls)
    logger.success(f"Connected to nats server: {','.join(servers)}")

    if use_js:
        global js
        js = nc.jetstream()


async def add_work_stream(name: str, subjects: List[str]) -> None:
    """
    Add a work queue stream

    see https://docs.nats.io/nats-concepts/jetstream/streams#retentionpolicy for more info
    """
    if not js:
        raise NatsInitializationError()

    stream_config = StreamConfig(name=name, subjects=subjects, retention=RetentionPolicy.WORK_QUEUE)
    await js.add_stream(config=stream_config)



async def send_request(
    subject: str, payload: T, out_type: Type[BaseModel]
) -> MessageResponse:
    if not nc:
        raise NatsInitializationError()
    try:
        response = await nc.request(subject, payload.to_bytes(), timeout=10)
        return MessageResponse[out_type].model_validate_json(response.data.decode())
    except TimeoutError as e:
        logger.error("timed out waiting for reply")
        raise e

    except Exception as e:
        raise e


async def publish(subject: str, payload: T) -> MessageResponse[Message]:
    if not nc:
        raise NatsInitializationError()
    message = Message(value=True)
    try:
        await nc.publish(subject=subject, payload=payload.to_bytes())
        return MessageResponse(body=message)
    except Exception as e:
        message.value = False
        return MessageResponse(error=ErrorMessage.from_exception(e))


async def js_publish(subject: str, payload: T, msg_id: Optional[str] = None) -> MessageResponse[Message]:
    if not js:
        raise NatsInitializationError()
    message = Message(value=-1)
    try:
        headers = None
        if msg_id:
            headers = {Header.MSG_ID: msg_id}
        pub_ack = await js.publish(subject=subject, payload=payload.to_bytes(), headers=headers)
        message.value = pub_ack.seq
        logger.info(f"published message with sequence: {pub_ack.seq}")
        return MessageResponse(body=message)
    except Exception as e:
        return MessageResponse(error=ErrorMessage.from_exception(e))


async def cleanup() -> None:
    await nc.drain()


async def subscribe(
    subject: str,
    queue: str,
    cb: Callable[[T], Awaitable[MessageResponse]],
    parsing_cb: Callable[[bytes], T],
) -> None:
    if nc is None:
        raise NatsInitializationError()
    sub = await nc.subscribe(
        subject=subject, queue=queue, cb=__cb_request_wrapper_async(cb, parsing_cb)
    )
    subscriptions.append(sub)


async def js_subscribe(
    subject: str,
    durable_name: str,
    cb: Callable[[T], Awaitable[None]],
    parsing_cb: Callable[[bytes], T],
) -> None:
    if js is None:
        raise NatsInitializationError()
    consumer_config = ConsumerConfig(
        max_deliver=3,
        max_ack_pending=100,
        ack_policy=AckPolicy.EXPLICIT,
        ack_wait=1 * 3600,  # 1 hour
        num_replicas=1,
        idle_heartbeat=0.5,
        flow_control=True,
    )
    sub = await js.subscribe(
        subject=subject,
        durable=durable_name,
        config=consumer_config,
        manual_ack=True,
        cb=__cb_ack_wrapper_async(cb, parsing_cb)
    )
    subscriptions.append(sub)


async def listen(
    subject: str, cb: Callable[[T], None], parsing_cb: Callable[[bytes], T]
) -> None:
    if nc:
        sub = await nc.subscribe(subject=subject, cb=__cb_wrapper(cb, parsing_cb))

        subscriptions.append(sub)


async def listen_async(
    subject: str, cb: Callable[[T], Awaitable[None]], parsing_cb: Callable[[bytes], T]
) -> None:
    if nc:
        sub = await nc.subscribe(subject=subject, cb=__cb_wrapper_async(cb, parsing_cb))

        subscriptions.append(sub)


def __cb_request_wrapper_async(
    cb: Callable[[T], Awaitable[MessageResponse]], parsing_cb: Callable[[bytes], T]
) -> Callable[[Msg], Any]:
    async def callback(msg: Msg) -> Any:
        payload = parsing_cb(msg.data)
        result = await cb(payload)

        reply_payload = result.to_bytes()

        await nc.publish(msg.reply, reply_payload)

    return callback

def __cb_ack_wrapper_async(
    cb: Callable[[T], Awaitable[None]], parsing_cb: Callable[[bytes], T]
) -> Callable[[Msg], Any]:
    async def callback(msg: Msg) -> Any:
        payload = parsing_cb(msg.data)

        try:
            await cb(payload)
            await msg.ack()
            logger.success(f"message success acknowledged for sequence: {msg.metadata.sequence}")
        except Exception as e:
            logger.error("failed to process message")
            logger.error(e)
            await msg.nak()
            logger.error(f"message failure acknowledged for sequence: {msg.metadata.sequence}")

    return callback


def __cb_wrapper(
    cb: Callable[[T], None], parsing_cb: Callable[[bytes], T]
) -> Callable[[Msg], Awaitable[None]]:
    async def callback(msg: Msg) -> None:
        return cb(parsing_cb(msg.data))

    return callback


def __cb_wrapper_async(
    cb: Callable[[T], Awaitable[None]], parsing_cb: Callable[[bytes], T]
) -> Callable[[Msg], Awaitable[None]]:
    async def callback(msg: Msg) -> None:
        return await cb(parsing_cb(msg.data))

    return callback


if __name__ == "__main__":
    class DemoPayload(MessageBaseModel):
        msg: str

    async def demo_cb(payload: DemoPayload) -> bool:
        logger.info(f"Here's the payload: {payload.msg}")
        return True

    async def handle_request(subject: str, b: T) -> None:
        try:
            await send_request(subject, b)
        except Exception:
            pass
        finally:
            logger.info("finished request")

    async def main() -> None:
        await init([])

        subject = "demo.test"
        blocks = [DemoPayload(msg=f"Message {ndx}") for ndx in range(0, 100)]
        await subscribe(
            subject, "DEMO_Q1", demo_cb, lambda d: DemoPayload.model_validate_json(d)
        )
        tasks = [asyncio.create_task(handle_request(subject, b)) for b in blocks]
        try:
            await asyncio.gather(*tasks)
        finally:
            await cleanup()

    asyncio.run(main())
