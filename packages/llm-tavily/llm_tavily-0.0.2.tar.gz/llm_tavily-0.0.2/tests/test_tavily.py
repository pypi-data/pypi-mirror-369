from unittest.mock import MagicMock

import httpx
import respx
from llm.plugins import load_plugins, pm

from llm_tavily import TavilyQnASearch


def test_plugin_is_installed():
    load_plugins()

    names = [mod.__name__ for mod in pm.get_plugins()]
    assert "llm_tavily" in names


@respx.mock(assert_all_called=True, assert_all_mocked=True)
def test_execute(respx_mock):
    respx_mock.post(
        "https://api.tavily.com/search",
        headers__contains={"Authorization": "Bearer tvly-test-key"},
        json__query="Who is Leo Messi?",
        json__search_depth="advanced",
        json__include_answer=True,
    ).mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "answer": "Lionel Messi is ...",
            },
        )
    )

    sut = TavilyQnASearch()
    prompt = MagicMock()
    prompt.prompt = "Who is Leo Messi?"
    prompt.options.search_depth = "advanced"

    actual = sut.execute(
        prompt,
        stream=False,
        response=MagicMock(),
        conversation=MagicMock(),
        key="tvly-test-key",
    )

    assert actual == "Lionel Messi is ..."


@respx.mock(assert_all_called=True, assert_all_mocked=True)
def test_execute_basic_depth(respx_mock):
    respx_mock.post(
        "https://api.tavily.com/search",
        headers__contains={"Authorization": "Bearer tvly-test-key"},
        json__query="Who is Leo Messi?",
        json__search_depth="basic",
        json__include_answer=True,
    ).mock(
        return_value=httpx.Response(
            status_code=200,
            json={
                "answer": "This is a basic answer",
            },
        )
    )

    sut = TavilyQnASearch()
    prompt = MagicMock()
    prompt.prompt = "Who is Leo Messi?"
    prompt.options.search_depth = "basic"

    actual = sut.execute(
        prompt,
        stream=False,
        response=MagicMock(),
        conversation=MagicMock(),
        key="tvly-test-key",
    )

    assert actual == "This is a basic answer"
