# dweb

![dweb ants tron](assets/illustrations/dweb_ants.svg)

> dweb → use the Autonomi network as a global datalake where you can just throw in data and retrieve it from anywhere.


Wrapper around `autonomi-client` to simplify fetching immutable public data with async and sync APIs.

- Async: `dweb.aio`
- Sync: `dweb`
- Networks: `from dweb import network` → `network.mainnet` (default) or `network.alpha`

## Install

```bash
poetry install --with test,notebooks
```

## Usage

### Sync
```python
from dweb import autonomi, network
content = autonomi.get("a7d2fdbb975efaea25b7ebe3d38be4a0b82c1d71e9b89ac4f37bc9f8677826e0", network=network.alpha)
with open("dogfile.jpg", "wb") as f:
    f.write(content)
```

### Async
```python
import asyncio
from dweb.aio import autonomi
from dweb import network

async def main():
    data = await autonomi.get("a7d2fdbb975efaea25b7ebe3d38be4a0b82c1d71e9b89ac4f37bc9f8677826e0", network=network.mainnet)
    print(len(data))

asyncio.run(main())
```

## Tests (Alpha network)

- Provide `.env` with `AUTONOMI_TEST_ADDRESS`.
- Run unit tests: `poetry run pytest -m "not alpha"`
- Run alpha tests: `poetry run pytest -m alpha`

Reference: `https://pypi.org/project/autonomi-client/`

## What is dweb (decentralized web)?

"dweb" is a small, ergonomic wrapper that lets your application interact with the decentralized Autonomi network as if it were a single, global data service. You can read from and (soon) write to globally addressable immutable data without running servers, without coordinating networks between participants, and without account-bound storage quotas or subscriptions. Producers and consumers of data do not need to be in the same local network or share infrastructure.

Key ideas:

- Global addressing via deterministic content/data map addresses
- Public, immutable data fetch with a single call (sync or async)
- No app servers to manage for reads; the network serves the data
- Writers and readers can be completely decoupled in time and space

## How it works (high level)

```mermaid
flowchart LR
    A[Your App] -- sync/async --> B[dweb wrapper]
    B -- uses --> C[autonomi-client]
    C -- connects --> D{Autonomi Network}
    D -- mainnet/alpha --> E[(Immutable Data)]

    subgraph Notes
    N1[Data is addressed by its data map address (64-hex)]
    N2[Readers do not need to know writers or share infra]
    N3[No app server required for public reads]
    end
    B -. future .-> F[[Convenience writes]]
    F -. put helpers .-> D
```

With `dweb`, fetching public content by its data map address is one call. Think of it as pulling a blob from a global, decentralized datastore.

## Concept: storing and retrieving data

- Reading (available today): Provide a 64-hex data map address and the network (default mainnet). You receive raw bytes of the immutable object.
- Writing (planned convenience): The wrapper will expose simple helpers to publish immutable data via the underlying `autonomi-client` so your app can store content without handling low-level details.

Properties:

- Decentralized: No single server you own or operate for public reads
- Global: Any participant can read the same address anywhere
- Durable: Immutable data is content-addressed; readers get the exact bytes referenced

> Note: Actual network policies and costs are determined by the Autonomi network and client library. The wrapper does not impose subscription fees or quotas itself.

## Notebook display example

```python
from IPython.display import Image, display
from dweb import autonomi, network

addr = "a7d2fdbb975efaea25b7ebe3d38be4a0b82c1d71e9b89ac4f37bc9f8677826e0"
content = autonomi.get(addr, network=network.alpha)
display(Image(data=content))
```
