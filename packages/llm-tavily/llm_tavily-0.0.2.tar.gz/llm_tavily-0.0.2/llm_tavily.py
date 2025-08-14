import asyncio
from typing import Literal

import llm
from tavily import AsyncTavilyClient


class TavilyQnASearch(llm.KeyModel):
    model_id = "qa-tavily"
    needs_key = "tavily"
    key_env_var = "LLM_TAVILY_KEY"

    class Options(llm.Options):
        search_depth: Literal["advanced", "basic"] = "advanced"

    def execute(self, prompt, stream, response, conversation, key):
        tavily_client = AsyncTavilyClient(api_key=key)
        answer = asyncio.run(
            tavily_client.qna_search(prompt.prompt, prompt.options.search_depth)
        )
        return answer


@llm.hookimpl
def register_models(register):
    register(TavilyQnASearch())
