from typing import Callable, Any
from web3.middleware import Web3Middleware
from web3.types import RPCEndpoint, RPCResponse
from .provider import FlashbotProvider

FLASHBOTS_METHODS = [
    "eth_sendBundle",
    "eth_callBundle",
    "eth_cancelBundle",
    "eth_sendPrivateTransaction",
    "eth_cancelPrivateTransaction",
    "flashbots_getBundleStats",
    "flashbots_getUserStats",
    "flashbots_getBundleStatsV2",
    "flashbots_getUserStatsV2",
]


class FlashbotsMiddlewareBuilder:
    """Builder for a Flashbots middleware.

    Usage:
    >>> w3.middleware_onion.add(FlashbotsMiddlewareBuilder.build(provider))
    """

    @classmethod
    def build(cls, flashbots_provider: FlashbotProvider):
        """Return a middleware class bound to the given Flashbots provider."""

        class FlashbotsMiddleware(Web3Middleware):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._flashbots_provider = flashbots_provider

            def wrap_make_request(
                self, make_request: Callable[[RPCEndpoint, Any], RPCResponse]
            ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
                def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
                    if method not in FLASHBOTS_METHODS:
                        return make_request(method, params)

                    # otherwise intercept it and POST it
                    return self._flashbots_provider.make_request(method, params)

                return middleware

        return FlashbotsMiddleware
