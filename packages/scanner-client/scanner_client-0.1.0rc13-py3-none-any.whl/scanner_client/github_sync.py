import uuid

from .http_err import get_body_and_handle_err
from .raw_api.api.github_repo_sync_source import sync_github_repositories
from .raw_api.client import AuthenticatedClient
from .raw_api.models import (
    SyncGithubReposRequestData,
    SyncGithubReposResponseData,
)


class GithubSync():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    def sync_repositories(
        self,
        tenant_id: str
    ) -> SyncGithubReposResponseData:
        req_body = SyncGithubReposRequestData(
            tenant_id=uuid.UUID(tenant_id),
        )

        resp = sync_github_repositories.sync_detailed(
            client=self._client,
            body=req_body)

        return get_body_and_handle_err(resp)


class AsyncGithubSync():
    _client: AuthenticatedClient

    def __init__(self, client: AuthenticatedClient) -> None:
        self._client = client

    async def sync_repositories(
        self,
        tenant_id: str
    ) -> SyncGithubReposResponseData:
        req_body = SyncGithubReposRequestData(
            tenant_id=uuid.UUID(tenant_id),
        )

        resp = await sync_github_repositories.asyncio_detailed(
            client=self._client,
            body=req_body)

        return get_body_and_handle_err(resp)
