import logging
from nats.aio.client import Client as NATS
from nats.js.client import JetStreamContext

from typing import Any, Dict

LOGGER = logging.getLogger(__name__)


async def make_nats_client(
    nats_config: Dict[str, Any],
) -> tuple[NATS, JetStreamContext]:
    nc = NATS()

    async def error_cb(e):
        LOGGER.error("Error:", e)

    async def disconnected_cb():
        LOGGER.warning("Got disconnected!")

    async def reconnected_cb():
        if nc.connected_url:
            LOGGER.info("Got reconnected to {url}".format(url=nc.connected_url.netloc))

    try:
        await nc.connect(
            servers=nats_config["servers"],
            disconnected_cb=disconnected_cb,
            error_cb=error_cb,
            reconnected_cb=reconnected_cb,
            **nats_config["options"],
        )

        if nc.connected_url:
            LOGGER.info("Connected to NATS at %s" % nc.connected_url.netloc)
        else:
            LOGGER.error("Connected to NATS but URL information not available")

        js = nc.jetstream()

        return nc, js
    except Exception as e:
        LOGGER.error(f"Failed to connect to NATS: {e}")
        raise
