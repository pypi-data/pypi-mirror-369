from __future__ import annotations

import importlib
import os
import pkgutil
from importlib import resources

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE, MCPServerStdio
from pydantic_ai.models.openai import OpenAIModel, OpenAIResponsesModel
from pydantic_ai.providers.azure import AzureProvider

import rune.tools as _pkg
from rune.agent.rich_wrappers import rich_tool
from rune.core.model_settings import build_settings
from rune.tools.registry import REGISTRY

DEFAULT_MODEL = "google-vertex:gemini-2.5-pro"


def _load_system_prompt() -> str:
    # Reads ai_chat/core/prompts/system_prompt.md at runtime
    return resources.files("rune.core.prompts").joinpath("system_prompt.md").read_text()


def _import_all_tools():
    """Ensure every module under ai_chat.tools is imported once."""
    for mod in pkgutil.walk_packages(_pkg.__path__, _pkg.__name__ + "."):
        importlib.import_module(mod.name)


def _build_mcp_servers(mcp_url: str | None, mcp_stdio: bool) -> list:
    mcp_servers = []
    if mcp_url:
        mcp_servers.append(MCPServerSSE(url=mcp_url))
    if mcp_stdio:
        mcp_servers.append(
            MCPServerStdio(
                "deno",
                args=[
                    "run",
                    "-N",
                    "-R=node_modules",
                    "-W=node_modules",
                    "--node-modules-dir=auto",
                    "jsr:@pydantic/mcp-run-python",
                    "stdio",
                ],
            )
        )
    return mcp_servers


def build_agent(
    *,
    model_name: str | None = None,
    model_overrides: dict | None = None,
    mcp_url: str | None = None,
    mcp_stdio: bool = False,
    deps_type: type | None = None,
) -> Agent:
    model_name = model_name or DEFAULT_MODEL
    settings = build_settings(model_name, model_overrides)
    model: str | OpenAIModel | OpenAIResponsesModel

    if model_name.startswith("azure:"):
        deployment = model_name.split(":", 1)[1]
        try:
            provider = AzureProvider(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            )
            model = OpenAIModel(
                model_name=deployment, provider=provider
            )
        except KeyError as e:
            raise ValueError(
                f"Missing Azure environment variable: {e}. Please set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_API_VERSION."
            ) from e
    elif model_name.startswith("openai:"):
        model = OpenAIModel(model_name=model_name)
    else:
        model = model_name

    agent = Agent(
        system_prompt=_load_system_prompt(),
        model=model,
        model_settings=settings,
        mcp_servers=_build_mcp_servers(mcp_url, mcp_stdio),
        retries=10,
        deps_type=deps_type,
    )

    _import_all_tools()

    for spec in REGISTRY:
        if spec.needs_ctx:
            agent.tool(rich_tool(spec.fn))  # expects RunContext
        else:
            agent.tool_plain(rich_tool(spec.fn))  # plain callable

    return agent
