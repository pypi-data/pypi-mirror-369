from typing import TypedDict

class LinkTokenCreateBody(TypedDict, total=False):
    tenant_id: str # When connecting a new integrated account, this is required.
    integrated_account_id: str # When reconnecting an existing integrated account, this is required.
    redirect_uri: str # The URL to redirect to after the user has completed the connect flow. Useful if you are authenticating via a Desktop app
    context: dict # A dictionary of key-value pairs that will be stored in the integrated account's context attribute.
    persist_previous_context: bool # If true, the context attribute of the integrated account will be retained when reconnecting the account. If false, the context attribute will be reset.
    environment_unified_model_id: str # Only works if the integration you want to connect follows OAuth 2.0. This option sets the scopes to ask for depending on the Unified API you want to use.

class LinkToken:
    def __init__(self, api_client):
        self.api_client = api_client

    def create(self, link_token_data: LinkTokenCreateBody):
        """Create a new link_token."""
        return self.api_client._post("link-token", data=link_token_data)