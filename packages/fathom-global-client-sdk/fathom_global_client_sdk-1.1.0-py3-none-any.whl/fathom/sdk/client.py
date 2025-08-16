"""The Fathom API client for querying flood and related data."""

import datetime
import json
import logging
from collections.abc import MutableMapping
from typing import Any

import grpc
from google.protobuf import any_pb2, symbol_database
from google.rpc import error_details_pb2  # type: ignore[attr-defined]
from grpc_status import rpc_status

from fathom.api.v2 import fathom_pb2, fathom_pb2_grpc

from .exceptions import (
    AuthenticationError,
    FathomException,
    InvalidCredentialsError,
)

# Do a 'blank import' style thing, we just want this to be imported to register the protobuf types in the global
# registry.
_ = error_details_pb2

FATHOM_GRPC_CHANNEL_MSG_SIZE = 10 * 1024 * 1024  # default 10MB


log = logging.getLogger(__name__)


def _default_channel_opts() -> list[tuple[str, str]]:
    """Default options for all connections"""
    service_default_config = {
        "methodConfig": [
            {
                # Empty name field means this applies to all RPCs
                "name": [{}],
                "retryPolicy": {
                    "maxAttempts": 5,
                    "initialBackoff": "0.1s",
                    "maxBackoff": "5s",
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": ["UNAVAILABLE"],
                },
            }
        ]
    }

    return [
        ("grpc.service_config", json.dumps(service_default_config)),
    ]


class _GRPCDetailsInterceptor(grpc.UnaryUnaryClientInterceptor):
    """Logs any gRPC metadata at the 'info' level."""

    def intercept_unary_unary(
        self,
        continuation,
        client_call_details,
        request,
    ):
        response = continuation(client_call_details, request)
        status = rpc_status.from_call(response)
        if status:
            for detail in status.details:
                # Decode 'any' message
                anypb = any_pb2.Any()
                anypb.CopyFrom(detail)

                # Get the actual type
                sym_db = symbol_database.Default()
                msg_type = sym_db.GetSymbol(anypb.TypeName())

                # Decode and print it
                msg = msg_type()
                msg.ParseFromString(anypb.value)

                log.info(msg)

        return response


class BaseClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_address: str = "api.fathom.global",
        msg_channel_size: int = FATHOM_GRPC_CHANNEL_MSG_SIZE,
        *,
        grpc_interceptors: list[grpc.UnaryUnaryClientInterceptor] | None = None,
    ) -> None:
        """Constructs a new Client, connected to a remote server. Should not be used directly - use the V1 or V2
        specific clients instead.

        Args:
            api_address: Address of the Fathom API server.
            client_id: Client ID to identify a registered client on the
                    authorization server.
            client_secret: Client Secret used with client_id to get an
                    access token.
            msg_channel_size: gRPC message channel size, it is 10MB by
                default but if you will be dealing with data size larger than
                the default, you can configure the size.
            grpc_interceptors: An optional list of grpc interceptors to add
                to the grpc channel, for logging or other purposes.

        """
        log.info(f"fathom.Client: connecting to {api_address}")

        if not client_id:
            raise InvalidCredentialsError("Client ID can not be empty")
        if not client_secret:
            raise InvalidCredentialsError("Client secret can not be empty")
        if not api_address:
            raise FathomException("API Address can not be empty")

        self._api_addr = api_address
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_conn = None
        self._message_size = msg_channel_size

        # expired at creation.
        self._token_expiry = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=-0.5
        )
        self._channel: grpc.Channel | None = None
        self._client_interceptors = [_GRPCDetailsInterceptor()]
        self._client_interceptors.extend(grpc_interceptors or [])

        self._stub_cache: MutableMapping[Any, Any] = {}

        # Check auth and initialise the channel
        _, _ = self._get_channel()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if channel := getattr(self, "_channel", None):
            channel.close()
            log.info("fathom.Client: closed gRPC channel")
            del self._channel

    def _get_channel(self) -> tuple[grpc.Channel, bool]:
        """Checks that the api credentials are still valid using an
        expiration time, creates a new grpc channel or use the previously
        created grpc channel depending on the condition.
        """
        channel_opt = [
            ("grpc.max_send_message_length", self._message_size),
            ("grpc.max_receive_message_length", self._message_size),
            *_default_channel_opts(),
        ]

        new = False

        if self._token_expiry <= datetime.datetime.utcnow() or self._channel is None:
            call_creds = grpc.access_token_call_credentials(self._api_access_token())
            creds = grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(), call_creds
            )
            self._channel = grpc.secure_channel(
                self._api_addr, creds, options=channel_opt
            )
            if self._client_interceptors:
                self._channel = grpc.intercept_channel(
                    self._channel, *self._client_interceptors
                )
            new = True

        return self._channel, new

    def _get_stub(self, stub_type):
        """Gets a new stub for the given type from a new or cached channel"""
        channel, new = self._get_channel()

        if new or stub_type not in self._stub_cache:
            # Always create a new one if we had to create a new channel
            stub = stub_type(self._channel)
            self._stub_cache[stub_type] = stub

        return self._stub_cache[stub_type]

    def _api_access_token(self) -> str:
        """Returns an access token to authenticate with the Fathom API."""
        try:
            request = fathom_pb2.CreateAccessTokenRequest(
                client_id=self._client_id, client_secret=self._client_secret
            )
            channel_opt = [*_default_channel_opts()]
            channel = grpc.secure_channel(
                self._api_addr, grpc.ssl_channel_credentials(), options=channel_opt
            )
            stub = fathom_pb2_grpc.FathomServiceStub(channel)
            response = stub.CreateAccessToken(request)
            channel.close()
            self._token_expiry = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=response.expire_secs
            )
            return response.access_token
        except Exception as err:
            raise AuthenticationError(
                "Could not obtain access token from auth server"
            ) from err
