import re

from scim2_models import Error
from scim2_models import User

from scim2_tester.checkers import random_url
from scim2_tester.utils import Status


def test_random_url(httpserver, testing_context):
    """Test reaching a random URL that returns a SCIM 404 error."""
    httpserver.expect_request(re.compile(r".*")).respond_with_json(
        Error(status=404, detail="Endpoint Not Found").model_dump(),
        status=404,
        content_type="application/scim+json",
    )

    result = random_url(testing_context)

    assert result[0].status == Status.SUCCESS
    assert "correctly returned a 404 error" in result[0].reason


def test_random_url_valid_object(httpserver, testing_context):
    """Test reaching a random URL that returns a SCIM object."""
    httpserver.expect_request(re.compile(r".*")).respond_with_json(
        User(
            id="2819c223-7f76-453a-919d-413861904646", user_name="bjensen@example.com"
        ).model_dump(),
        status=404,
        content_type="application/scim+json",
    )

    result = random_url(testing_context)

    assert result[0].status == Status.ERROR
    assert "did not return an Error object" in result[0].reason


def test_random_url_not_404(httpserver, testing_context):
    """Test reaching a random URL that returns a non-404 status code."""
    httpserver.expect_request(re.compile(r".*")).respond_with_json(
        Error(status=200, detail="Endpoint Not Found").model_dump(),
        status=200,
        content_type="application/scim+json",
    )

    result = random_url(testing_context)

    assert result[0].status == Status.ERROR
    assert "did return an object, but the status code is 200" in result[0].reason
