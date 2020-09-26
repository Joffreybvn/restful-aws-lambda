import json
import pytest

from pylambdarest import route


@pytest.fixture
def empty_route():
    @route()
    def test_route():
        return 200

    return test_route


@pytest.fixture
def get_user_route():
    @route()
    def test_route(user_id):
        user = {"id": user_id, "name": "Test User"}
        return 200, user

    return test_route


@pytest.fixture
def schema_validation_route():
    body_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
        "additionalProperties": False,
    }

    query_params_schema = {
        "type": ["object", "null"],
        "properties": {"test": {"type": "string"}},
        "additionalProperties": False,
    }

    @route(body_schema=body_schema, query_params_schema=query_params_schema)
    def test_route():
        return 200

    return test_route


@pytest.fixture
def event_context_as_headers_route():
    @route()
    def test_route(event, context):
        return 200, {}, {"event": event, "context": context}

    return test_route


def test_status_code(empty_route):
    event = {}
    context = {}
    response = empty_route(event, context)
    assert response["statusCode"] == 200


def test_path_params(get_user_route):
    event = {"pathParameters": {"user_id": 123}}
    context = None
    response = get_user_route(event, context)
    assert response["statusCode"] == 200
    assert response["body"] == '{"id": 123, "name": "Test User"}'


def test_invalid_route_args(get_user_route):
    # test that calling the get_user_route
    # without the expected user_id in pathParameters
    # raises a ValueError
    with pytest.raises(ValueError):
        get_user_route({}, {})


def test_event_context(event_context_as_headers_route):
    test_event = {"type": "test_event"}
    test_context = {"type": "test_context"}

    response = event_context_as_headers_route(test_event, test_context)

    expected_headers = {"event": test_event, "context": test_context}

    assert response["headers"] == expected_headers


def test_schema_validation(schema_validation_route):
    context = {}

    event = {"body": json.dumps({"invalid": "schema"})}
    response = schema_validation_route(event, context)
    assert response["statusCode"] == 400

    event = {
        "body": json.dumps({"name": "Test Name"}),
        "queryStringParameters": {"invalidKey": "test"},
    }
    response = schema_validation_route(event, context)
    assert response["statusCode"] == 400

    event = {
        "body": json.dumps({"name": "Test Name"}),
        "queryStringParameters": {"test": "test"},
    }
    response = schema_validation_route(event, context)
    assert response["statusCode"] == 200
