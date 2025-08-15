# truto_sdk/pagination_result.py

class PaginationResult:
    def __init__(self, api_client, endpoint, query_params):
        self.api_client = api_client
        self.endpoint = endpoint
        self.query_params = query_params
        self.next_cursor = None
        self.items = []
        self.initial_fetch_done = False  # To check if we fetched the first page

    def __aiter__(self):
        return self

    async def __anext__(self):
        # If the first fetch is not done, do it now
        if not self.initial_fetch_done:
            await self._fetch_next_page()
            self.initial_fetch_done = True

        # If no items are left in the current page and there's a next_cursor, fetch the next page
        if not self.items and self.next_cursor:
            await self._fetch_next_page()

        # If there are no items and no next_cursor, stop iteration
        if not self.items:
            raise StopAsyncIteration

        # Pop and return the first item from the items list
        return self.items.pop(0)

    async def _fetch_next_page(self):
        # If there's a next cursor, include it in the query parameters
        if self.next_cursor:
            self.query_params['next_cursor'] = self.next_cursor

        # Fetch the next page asynchronously
        response = await self.api_client._get(self.endpoint, params=self.query_params)

        # Get the result (list of items) from the response
        self.items = response.get('result', [])

        # Update the next cursor for pagination
        self.next_cursor = response.get('next_cursor')

        # If the first API call returns an empty result and no next_cursor, break early
        if not self.items and not self.next_cursor:
            self.items = []  # Ensure no more items will be processed

    async def to_array(self):
        """Fetch all results and return them as a list."""
        all_items = []
        async for item in self:
            all_items.append(item)
        return all_items

    async def next_page(self):
        """Fetch the next page and return the items."""
        await self._fetch_next_page()
        return self.items
