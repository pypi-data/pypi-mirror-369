from typing import Union, Optional

from eth_account.signers.local import LocalAccount
from eth_typing import URI
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3._utils.module import attach_modules

from .flashbots import Flashbots
from .middleware import FlashbotsMiddlewareBuilder
from .provider import FlashbotProvider

DEFAULT_FLASHBOTS_RELAY = "https://relay.flashbots.net"


def flashbot(
    w3: Web3,
    signature_account: LocalAccount,
    endpoint_uri: Optional[Union[URI, str]] = None,
):
    """
    Injects the flashbots module and middleware to w3.
    """

    flashbots_provider = FlashbotProvider(signature_account, endpoint_uri)

    # goerli connection requires extra PoA middleware
    if endpoint_uri is not None and "goerli" in endpoint_uri:
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    flash_middleware = FlashbotsMiddlewareBuilder.build(flashbots_provider)
    w3.middleware_onion.add(flash_middleware)

    # attach modules to add the new namespace commands
    attach_modules(w3, {"flashbots": (Flashbots,)})
