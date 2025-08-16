import asyncio
from magique.client import connect_to_server, ServiceProxy, MagiqueError, ServerProxy

from .constant import SERVER_URLS
from .log import logger


async def connect_remote(
        service_name_or_id: str,
        server_url: str | list[str] | None = None,
        server_timeout: float = 10.0,
        service_timeout: float = 10.0,
        time_delta: float = 0.5,
        ) -> ServiceProxy:
    if server_url is None:
        server_urls = SERVER_URLS
    elif isinstance(server_url, str):
        server_urls = [server_url]
    else:
        server_urls = server_url

    async def _get_server() -> ServerProxy:
        while True:
            try:
                server = await connect_to_server(server_urls)
                return server
            except Exception:
                await asyncio.sleep(time_delta)


    async def _get_service(server: ServerProxy) -> ServiceProxy:
        while True:
            try:
                service = await server.get_service(service_name_or_id)
                return service
            except MagiqueError:
                await asyncio.sleep(time_delta)
    
    try:
        server = await asyncio.wait_for(_get_server(), server_timeout)
    except asyncio.TimeoutError:
        error_msg = f"Failed to connect to servers: {server_urls}"
        logger.debug(error_msg)
        raise MagiqueError(error_msg)
    try:
        service = await asyncio.wait_for(_get_service(server), service_timeout)
        logger.debug(f"Service {service_name_or_id} is available on servers")
        return service
    except asyncio.TimeoutError:
        error_msg = f"Failed to get service {service_name_or_id} on servers: {server_urls}"
        logger.debug(error_msg)
        raise MagiqueError(error_msg)
