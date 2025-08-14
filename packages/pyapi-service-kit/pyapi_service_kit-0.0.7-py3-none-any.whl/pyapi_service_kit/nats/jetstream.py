import logging
from typing import Any, Mapping

from nats.js.client import JetStreamContext


LOGGER = logging.getLogger(__name__)


async def try_delete_stream(js: JetStreamContext, stream_name: str):
    try:
        await js.delete_stream(stream_name)
        return True
    except Exception:
        return False


async def create_jetstream_streams(js: JetStreamContext, config: Mapping[str, Any]):
    for stream_name, stream_config in config.items():
        try:
            if stream_config.get("recreate_if_exists", False):
                await try_delete_stream(js, stream_name)

            await js.add_stream(name=stream_name, **stream_config["options"])
            LOGGER.info(f"JetStream stream {stream_name} created")
        except Exception as e:
            LOGGER.error(f"Error creating JetStream stream {stream_name}: {e}")
            raise
