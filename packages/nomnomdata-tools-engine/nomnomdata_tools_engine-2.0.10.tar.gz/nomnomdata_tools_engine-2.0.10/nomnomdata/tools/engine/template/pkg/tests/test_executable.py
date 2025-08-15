from ..executable import hello_world


def test_hello_world_no_name():
    args = {"repeat": 1}
    api_calls, results = hello_world(**args)
    assert results == (args["repeat"], f"Hello World")


def test_hello_world_with_name():
    args = {"repeat": 3, "name": "Joe"}
    api_calls, results = hello_world(**args)
    assert results == (args["repeat"], f"Hello Joe")


# Nominode API calls are returned along with function results.
# The api_calls variable is used to capture this data.
