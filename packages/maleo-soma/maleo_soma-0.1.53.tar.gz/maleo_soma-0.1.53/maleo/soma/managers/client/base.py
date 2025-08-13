import httpx
from contextlib import asynccontextmanager
from pydantic import BaseModel, ConfigDict, Field
from typing import AsyncGenerator, Generator, Optional
from maleo.soma.enums.cache import CacheLayer, CacheOrigin
from maleo.soma.enums.environment import Environment
from maleo.soma.enums.operation import OperationLayer, OperationOrigin, OperationTarget
from maleo.soma.schemas.operation.context import OperationOriginSchema
from maleo.soma.schemas.service import ServiceContext
from maleo.soma.utils.logging import ClientLogger, SimpleConfig


#     @property
#     def client(self) -> httpx.AsyncClient:
#         return self._client

#     @property
#     def url(self) -> str:
#         return self._url

#     async def dispose(self) -> None:
#         await self._client.aclose()


# class ClientControllerManagers(BaseModel):
#     model_config = ConfigDict(arbitrary_types_allowed=True)

#     http: ClientHTTPControllerManager = Field(..., description="HTTP Client Controller")


# class ClientHTTPController:
#     _OPERATION_LAYER_TYPE = OperationLayer.SERVICE
#     _OPERATION_TARGET_TYPE = OperationTarget.INTERNAL
#     _CACHE_ORIGIN = CacheOrigin.CLIENT
#     _CACHE_LAYER = CacheLayer.CONTROLLER

#     def __init__(self, manager: ClientHTTPControllerManager):
#         self._manager = manager

#     @property
#     def manager(self) -> ClientHTTPControllerManager:
#         return self._manager


# class ClientServiceControllers(BaseModel):
#     model_config = ConfigDict(arbitrary_types_allowed=True)

#     http: ClientHTTPController = Field(..., description="HTTP Client Controller")


# class ClientControllers(BaseModel):
#     model_config = ConfigDict(arbitrary_types_allowed=True)
#     # * Reuse this class while also adding all controllers of the client


class ClientService:
    _OPERATION_LAYER_TYPE = OperationLayer.SERVICE
    _OPERATION_TARGET_TYPE = OperationTarget.INTERNAL
    _CACHE_ORIGIN = CacheOrigin.CLIENT
    _CACHE_LAYER = CacheLayer.SERVICE

    def __init__(
        self,
        service_context: ServiceContext,
        operation_origin: OperationOriginSchema,
        logger: ClientLogger,
    ):
        self._service_context = service_context
        self._operation_origin = operation_origin
        self._logger = logger

    # @property
    # def controllers(self) -> ClientServiceControllers:
    #     raise NotImplementedError()

    # @property
    # def logger(self) -> ClientLogger:
    #     return self._logger


# class ClientServices(BaseModel):
#     model_config = ConfigDict(arbitrary_types_allowed=True)
#     # * Reuse this class while also adding all the services of the client


class ClientManager:
    _OPERATION_ORIGIN_TYPE = OperationOrigin.CLIENT
    _CACHE_ORIGIN = CacheOrigin.CLIENT

    def __init__(
        self,
        key: str,
        name: str,
        log_config: SimpleConfig,
        service_context: Optional[ServiceContext] = None,
    ) -> None:
        self._key = key
        self._name = name
        self._log_config = log_config

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

        self._operation_origin = OperationOriginSchema(
            type=self._OPERATION_ORIGIN_TYPE,
            details={"identifier": {"key": self._key, "name": self._name}},
        )

        self._logger = ClientLogger(
            client_key=self._key,
            environment=self._service_context.environment,
            service_key=self._service_context.key,
            **self._log_config.model_dump(),
        )

    @property
    def key(self) -> str:
        return self._key

    @property
    def name(self) -> str:
        return self._name

    @property
    def service_context(self) -> ServiceContext:
        return self._service_context

    @property
    def environment(self) -> Environment:
        raise NotImplementedError()

    @property
    def logger(self) -> ClientLogger:
        return self._logger

    # def _initialize_services(self) -> None:
    #     # * Initialize services
    #     #! This initialied an empty services. Extend this function in the actual class to initialize all services.
    #     self._services = ClientServices()

    # @property
    # def services(self) -> ClientServices:
    #     return self._services

    @property
    def credentials(self):
        raise NotImplementedError()

    @property
    def client(self):
        raise NotImplementedError()
