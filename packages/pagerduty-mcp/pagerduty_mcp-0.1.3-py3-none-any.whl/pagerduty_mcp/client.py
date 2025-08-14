import logging
import os
from contextvars import ContextVar
from functools import lru_cache
from importlib import metadata

import pagerduty
from dotenv import load_dotenv
from pydantic import BaseModel

from pagerduty_mcp import DIST_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("PAGERDUTY_USER_API_KEY")
API_HOST = os.getenv("PAGERDUTY_API_HOST", "https://api.pagerduty.com")


class PagerdutyMCPClient(pagerduty.RestApiV2Client):
    @property
    def user_agent(self) -> str:
        return f"{DIST_NAME}/{metadata.version(DIST_NAME)} {super().user_agent}"


class ClientConfig(BaseModel):
    api_key: str
    api_host: str = "https://api.pagerduty.com"


pd_client_config: ContextVar[ClientConfig | None] = ContextVar("pd_client_client", default=None)


@lru_cache(maxsize=1)
def _get_cached_client(api_key: str, api_host: str) -> pagerduty.RestApiV2Client:
    """Get a cached PagerDuty client."""
    return create_pd_client(api_key, api_host)


def create_pd_client(api_key: str, api_host: str | None = None) -> pagerduty.RestApiV2Client:
    """Get the PagerDuty client."""
    pd_client = PagerdutyMCPClient(api_key)
    if api_host:
        pd_client.url = api_host

    return pd_client


def get_client() -> pagerduty.RestApiV2Client:
    """Get the PagerDuty client, using cached configuration if available.

    This function will check if client config information is stored in a context var.
    If it is, that means the package is being used in a remote MCP server context, and
    we need to update the client credentials for each request, since remote MCP servers
    need to support multi tenancy.
    """
    client = _get_cached_client(API_KEY, API_HOST)
    client_config = pd_client_config.get()
    if client_config is None:
        logger.info("Using default PagerDuty client configuration")
        return client
    client.api_key = client_config.api_key
    client.url = client_config.api_host

    return client
