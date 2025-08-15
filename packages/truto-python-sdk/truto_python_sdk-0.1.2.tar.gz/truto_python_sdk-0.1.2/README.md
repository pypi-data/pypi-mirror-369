# truto-python-sdk
Python3 SDK for the Truto API. The SDK mirrors the Truto REST API endpoints which are documented in the Truto Postman Collection.

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/25523816-b3550004-776b-4372-be86-562791b192ce?action=collection%2Ffork&collection-url=entityId%3D25523816-b3550004-776b-4372-be86-562791b192ce%26entityType%3Dcollection%26workspaceId%3D7cc4fe33-eb97-4dc7-98b5-2a7ff2e94e67)

## Installation
```bash
pip install truto-python-sdk
```

## Usage

```python
import asyncio
from truto_python_sdk import TrutoApi

# Initialize the SDK with your token
truto_api = TrutoApi(token="<your_api_token>")

async def main():
    async for ticket in truto_api.unified_api.list("ticketing", "tickets", {
        "integrated_account_id": "c54bc595-486e-4bbb-8c17-20810fa4a86c"
    }):
        print(await truto_api.proxy_api.get("ticketing-tickets", ticket["id"], {
            "integrated_account_id": "c54bc595-486e-4bbb-8c17-20810fa4a86c"
        }))

# Run the async function
asyncio.run(main())
```

## List calls and pagination

The SDK uses async generators to handle list calls. This allows you to iterate over the results of a list call without having to worry about pagination. The SDK will automatically fetch the next page of results when needed.

```python
async for ticket in truto_api.unified_api.list("ticketing", "tickets", {
    "integrated_account_id": "c54bc595-486e-4bbb-8c17-20810fa4a86c"
}):
    print(ticket)
```

You can also call `to_array()`, which will auto-paginate all the resources and return them as a list.

```python
tickets = await truto_api.unified_api.list("ticketing", "tickets", {
    "integrated_account_id": "c54bc595-486e-4bbb-8c17-20810fa4a86c"
}).to_array()
```

Getting each page of results manually is also possible.

```python
page = await truto_api.unified_api.list("ticketing", "tickets", {
    "integrated_account_id": "c54bc595-486e-4bbb-8c17-20810fa4a86c"
}).next_page()
```

## Contributing
We welcome contributions to improve `truto-python-sdk`. Please submit issues or pull requests on the GitHub repository.

## License
MIT