# llm-tavily

[![PyPI](https://img.shields.io/pypi/v/llm-tavily.svg)](https://pypi.org/project/llm-tavily/)
[![Changelog](https://img.shields.io/github/v/release/ftnext/llm-tavily?include_prereleases&label=changelog)](https://github.com/ftnext/llm-tavily/releases)
[![Tests](https://github.com/ftnext/llm-tavily/actions/workflows/test.yml/badge.svg)](https://github.com/ftnext/llm-tavily/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ftnext/llm-tavily/blob/main/LICENSE)



## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).
```bash
llm install llm-tavily
```
## Usage

**prerequisite**: Tavily API key (Free, No credit card, 1,000 API credits / month)  
https://www.tavily.com/#pricing  
https://blog.tavily.com/getting-started-with-the-tavily-search-api/

```bash
export LLM_TAVILY_KEY=your_api_key_here

llm -m qa-tavily 'Who is Leo Messi?'
```

## Development

To set up this plugin locally, first checkout the code:
```bash
cd llm-tavily
```
Then create a new virtual environment and install the dependencies and test dependencies:
```bash
uv sync --extra test
```
To run the tests:
```bash
uv run pytest
```
