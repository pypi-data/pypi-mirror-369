import pytest
from httpx import Client
from scim2_client import SCIMClientError
from scim2_client.engines.httpx import SyncSCIMClient
from scim2_models import Group
from scim2_models import User

from scim2_tester.checker import check_server


def test_raise_exceptions():
    """Test that exceptions are raised instead of stored in a Result object when 'raise_exceptions' is True."""
    client = Client(base_url="https://invalid.test")
    scim = SyncSCIMClient(client, resource_models=(User, Group))
    with pytest.raises(SCIMClientError):
        check_server(scim, raise_exceptions=True)
