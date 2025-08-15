from __future__ import annotations

from typing import Optional, Union

from autonomi_client import Client, DataAddress

from .._client_manager import async_client_manager
from ..errors import InvalidAddressError
from .. import network as network_mod


def _address_from_hex_maybe(address: Union[str, DataAddress]) -> DataAddress:
    if isinstance(address, DataAddress):
        return address
    if isinstance(address, str):
        hex_str = address.lower()
        if hex_str.startswith("0x"):
            hex_str = hex_str[2:]
        if len(hex_str) != 64:
            raise InvalidAddressError(
                "Data map address must be 64 hex chars (with or without 0x prefix)."
            )
        try:
            return DataAddress.from_hex(hex_str)
        except Exception as exc:  # pragma: no cover - relies on upstream validation
            raise InvalidAddressError("Invalid data address hex string.") from exc
    raise InvalidAddressError("Unsupported address type.")


async def get(
    address: Union[str, DataAddress],
    *,
    network: network_mod._Network = network_mod.mainnet,
    client: Optional[Client] = None,
) -> bytes:
    """Fetch immutable public data by data map address.

    Args:
        address: 64-hex data map address (string) or `DataAddress`.
        network: network selector (`network.mainnet` or `network.alpha`). Defaults to mainnet.
        client: optional pre-initialized `autonomi_client.Client`.

    Returns:
        Raw bytes of the immutable data.
    """

    data_address = _address_from_hex_maybe(address)

    use_client: Client
    if client is not None:
        use_client = client
    else:
        use_client = await async_client_manager.get_client(alpha=(network is network_mod.alpha))

    return await use_client.data_get_public(data_address)


