"""
This module provides a client for the IronaAI API.
"""

import os
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union, Type
import litellm
import json
import requests
import random
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool

from .openai_pdf_handler import openai_completion_with_pdf
from .config import DEFAULT_MODEL, DEFAULT_API_URL, MODEL_SELECT_ENDPOINT, DEFAULT_TIMEOUT
from .utils import fetch_model_list_from_gist, detect_media_types, retry_with_backoff

# Load environment variables from .env file
load_dotenv()

class IronaAI:
    def __init__(self, api_key: Optional[str] = None, model_list: Optional[List[str]] = None, reliability: Optional[Dict[str, Any]] = None):
        self.api_key = api_key or os.getenv("IRONAAI_API_KEY")
        model_list_from_gist, support_media_dict_from_gist, support_tools_dict_from_gist, openrouter_mapping = fetch_model_list_from_gist()
        if model_list is None:
            self.model_list = model_list_from_gist
            self.support_media_dict = support_media_dict_from_gist
            self.support_tools_dict = support_tools_dict_from_gist
        else:
            self.model_list = model_list
            self.support_media_dict = {model: support_media_dict_from_gist.get(model, []) for model in model_list}
            self.support_tools_dict = {model: support_tools_dict_from_gist.get(model, False) for model in model_list}
            # Set defaults for known models
            self.support_media_dict["openai/gpt-4o-mini"] = ["image", "pdf"]
            self.support_media_dict["anthropic/claude-3-5-haiku-20241022"] = ["image", "pdf"]
            self.support_tools_dict["openai/gpt-4o-mini"] = True
            self.support_tools_dict["anthropic/claude-3-5-haiku-20241022"] = True
        self.openrouter_mapping = openrouter_mapping
        self.default_model = DEFAULT_MODEL
        self.iai_api_url = DEFAULT_API_URL
        self.default_fallback_models = ["openai/gpt-4o-mini", "anthropic/claude-3-5-haiku-20241022"]
        self.reliability = reliability or {}

    def _model_select(
        self,
        messages: List[Dict[str, Any]],
        model_list: Optional[List[str]] = None,
        max_model_depth: int = None,
        hash_content: bool = False,
        tradeoff: Optional[str] = None,  # latency, cost, accuracy
        preference_id: Optional[str] = None,
        previous_session: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> str:
        url = MODEL_SELECT_ENDPOINT
        
        active_api_key = api_key or self.api_key
        if not active_api_key:
            raise ValueError("API key is required for model selection")
        active_model_list = model_list if model_list is not None else self.model_list

        model_mapping = {}
        llm_providers = []
        
        for full_model in active_model_list:
            parts = full_model.split("/")
            provider = parts[0]
            if len(parts) == 2:
                model_name = parts[1]
            elif len(parts) == 3:
                model_name = parts[2]
            else:
                raise ValueError(f"Invalid model format: {full_model}")
            llm_providers.append({"provider": provider, "model": model_name})
            model_mapping[(provider, model_name)] = full_model
        
        payload = {
            "messages": messages,
            "llm_providers": llm_providers,
            "max_model_depth": max_model_depth or len(active_model_list),
            "hash_content": hash_content,
        }
        if tradeoff:
            payload["tradeoff"] = tradeoff
        if preference_id:
            payload["preference_id"] = preference_id
        if previous_session:
            payload["previous_session"] = previous_session

        headers = {"Authorization": f"Bearer {active_api_key}"}
        response = requests.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            raise ValueError(f"Model selection failed: {data['error']}")
        
        selected_provider = data["providers"][0]["provider"]
        selected_model_name = data["providers"][0]["model"]
        
        try:
            best_model = model_mapping[(selected_provider, selected_model_name)]
        except KeyError:
            raise ValueError(f"Selected model {selected_provider}/{selected_model_name} not found in model list.")
        return best_model

    def _get_litellm_params(self, selected_model: str) -> str:
        special_provider_map = {
            "togetherai": {"litellm_provider": "together_ai", "model_extract": lambda parts: "/".join(parts[1:])},
            "google": {"litellm_provider": "gemini", "model_extract": lambda parts: parts[-1]},
            "replicate": {"litellm_provider": "replicate", "model_extract": lambda parts: "/".join(parts[1:])},
            "openai": {"litellm_provider": "openai", "model_extract": lambda parts: "/".join(parts[1:])},
            "anthropic": {"litellm_provider": "anthropic", "model_extract": lambda parts: "/".join(parts[1:])},
            "cohere": {"litellm_provider": "cohere", "model_extract": lambda parts: "/".join(parts[1:])},
            "mistral": {"litellm_provider": "mistral", "model_extract": lambda parts: "/".join(parts[1:])},
            "perplexity": {"litellm_provider": "perplexity", "model_extract": lambda parts: "/".join(parts[1:])},
            "openrouter": {"litellm_provider": "openrouter", "model_extract": lambda parts: "/".join(parts[1:])},
        }
        parts = selected_model.split("/")
        provider = parts[0]
        if provider in special_provider_map:
            litellm_provider = special_provider_map[provider]["litellm_provider"]
            model_name = special_provider_map[provider]["model_extract"](parts)
        else:
            litellm_provider = provider
            model_name = "/".join(parts[1:])
        full_model_string = f"{litellm_provider}/{model_name}"
        return full_model_string

    def _model_supports_features(self, model: str, required_media: set, tools: bool) -> bool:
        """Check if the model supports the required media types and tools."""
        if model.startswith("openrouter/"):
            openrouter_id = "/".join(model.split("/")[1:])
            gist_model = self.openrouter_mapping.get(openrouter_id)
            if gist_model is None:
                return False
        else:
            gist_model = model
        return all(media in self.support_media_dict.get(gist_model, []) for media in required_media) and (not tools or self.support_tools_dict.get(gist_model, False))

    def _try_model(self, model: str, messages: List[Dict], has_pdf: bool, stream: bool, tools: Optional[List], 
                tool_choice: str, response_format: Optional[Union[Dict, Type[BaseModel]]], 
                max_retries: int, timeout: float, backoff_base: float, model_messages: List[Dict], **kwargs):
        """Attempt to complete the request with the given model and settings."""
        request_messages = messages + model_messages
        if model.startswith("openai/") and has_pdf:
            model_name = model.split("/", 1)[1]
            try:
                response = retry_with_backoff(
                    openai_completion_with_pdf,
                    max_retries=max_retries,
                    backoff_base=backoff_base,
                    model=model_name,
                    messages=request_messages,
                    stream=stream,
                    timeout=timeout,
                    **kwargs
                )
                return response
            except Exception as e:
                raise
        else:
            full_model_string = self._get_litellm_params(model)
            provider = full_model_string.split("/")[0]
            model_name = "/".join(full_model_string.split("/")[1:])
            supported_params = litellm.get_supported_openai_params(model=model_name, custom_llm_provider=provider)
            completion_kwargs = {
                "model": full_model_string,
                "messages": request_messages,
                "stream": stream,
                "timeout": timeout,
                **kwargs,
            }
            if tools:
                completion_kwargs["tools"] = tools
                completion_kwargs["tool_choice"] = tool_choice
            if response_format:
                if isinstance(response_format, dict):
                    if "type" not in response_format or not isinstance(response_format["type"], str):
                        raise ValueError("response_format must have a 'type' key with a string value.")
                    if response_format["type"] == "json_object":
                        if "response_format" not in supported_params:
                            raise ValueError(f"Model {model} does not support JSON output (json_object).")
                        completion_kwargs["response_format"] = response_format
                    else:
                        raise ValueError(f"Unsupported response_format type: {response_format['type']}")
                elif isinstance(response_format, type) and issubclass(response_format, BaseModel):
                    if not litellm.supports_response_schema(model=model_name, custom_llm_provider=provider):
                        litellm.enable_json_schema_validation = True
                    else:
                        completion_kwargs["response_format"] = response_format
                else:
                    raise ValueError("response_format must be a dict or a Pydantic model class.")
            api_key_env_map = {
                "together_ai": "TOGETHER_API_KEY",
                "gemini": "GOOGLE_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "replicate": "REPLICATE_API_KEY",
                "cohere": "COHERE_API_KEY",
                "mistral": "MISTRAL_API_KEY",
                "perplexity": "PERPLEXITY_API_KEY",
                "openrouter": "OPENROUTER_API_KEY",
            }
            if provider not in api_key_env_map:
                raise ValueError(f"Provider '{provider}' not supported.")
            api_key = os.getenv(api_key_env_map[provider])
            if not api_key:
                raise ValueError(f"Environment variable '{api_key_env_map[provider]}' not found")
            completion_kwargs["api_key"] = api_key
            try:
                response = retry_with_backoff(
                    litellm.completion,
                    max_retries=max_retries,
                    backoff_base=backoff_base,
                    **completion_kwargs
                )
                return response
            except Exception as e:
                raise

    @property
    def completions(self):
        class Completions:
            def __init__(self, parent):
                self.parent = parent

            def create(self, *args, **kwargs):
                return self.parent.completion(*args, **kwargs)

        return Completions(self)
    
    def completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        model_list: Optional[List[str]] = None,
        max_model_depth: Optional[int] = None,
        hash_content: bool = False,
        tradeoff: Optional[str] = None,
        preference_id: Optional[str] = None,
        previous_session: Optional[str] = None,
        stream: bool = False,
        tools: Optional[List[Union[Dict, Callable, BaseTool]]] = None,
        tool_choice: Optional[str] = "auto",
        response_format: Optional[Union[Dict[str, Any], Type[BaseModel]]] = None,
        fallback_models: Optional[List[str]] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        :param messages: List of message dictionaries with role and content.
        :param model: Optional model specification.
        :param max_model_depth: Maximum depth for model selection.
        :param hash_content: Whether to hash message content (default: False).
        :param tradeoff: Tradeoff between latency, cost, accuracy.
        :param preference_id: Identifier for preferences.
        :param previous_session: ID of a previous session.
        :param stream: Whether to stream the response (default: False).
        :param tools: List of tool dictionaries for function calling.
        :param tool_choice: How the model should use tools (default: "auto").
        :param response_format: Desired response format (dict or Pydantic model).
        :param fallback_models: List of fallback models to use if the primary model fails.
        :param api_key: API key for model selection.
        :param kwargs: Additional arguments for litellm.completion.
        :return: Response object from litellm.completion.
        """
        if tools and response_format:
            raise ValueError("Cannot use both 'tools' and 'response_format' simultaneously.")

        def message_to_dict(message):
            if isinstance(message, dict):
                return message
            msg_dict = {
                "role": message.role,
                "content": message.content if message.content is not None else "",
            }
            if getattr(message, "tool_calls", None):
                msg_dict["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "function": {
                            "name": tool_call.function.name,
                            "type": tool_call.type,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in message.tool_calls
                ]
            return msg_dict

        serializable_messages = [message_to_dict(msg) for msg in messages]
        has_pdf, has_image = detect_media_types(messages)
        required_media = set()
        if has_image:
            required_media.add("image")
        if has_pdf:
            required_media.add("pdf")

        if "failover_chain" in self.reliability and "weights" in self.reliability:
            raise ValueError("Cannot specify both 'failover_chain' and 'weights' in reliability config.")

        # Ordered Failover Logic
        if "failover_chain" in self.reliability:
            if not self.reliability["failover_chain"]:
                raise ValueError("The 'failover_chain' in reliability config cannot be empty.")
            for chain_item in self.reliability["failover_chain"]:
                selected_model = chain_item["model"]
                if not self._model_supports_features(selected_model, required_media, tools):
                    continue
                max_retries = chain_item.get("max_retries", 1)
                timeout = chain_item.get("timeout", 30)
                backoff_base = chain_item.get("backoff", 1)
                model_messages = chain_item.get("messages", [])
                try:
                    response = self._try_model(
                        model=selected_model,
                        messages=messages,
                        has_pdf=has_pdf,
                        stream=stream,
                        tools=tools,
                        tool_choice=tool_choice,
                        response_format=response_format,
                        max_retries=max_retries,
                        timeout=timeout,
                        backoff_base=backoff_base,
                        model_messages=model_messages,
                        **kwargs
                    )
                    return response
                except Exception as e:
                    print(f"Model {selected_model} failed: {e}")
                    continue
            raise ValueError("All models in the failover chain failed to provide a response.")

        # Weighted Load Balancing Logic
        elif "weights" in self.reliability:
            candidate_models = [
                m for m in self.reliability["weights"].keys()
                if self._model_supports_features(m, required_media, tools)
            ]
            if not candidate_models:
                raise ValueError("No models available that support the required features.")
            while candidate_models:
                selected_model = random.choices(candidate_models, weights=[self.reliability["weights"][m] for m in candidate_models], k=1)[0]
                max_retries = self.reliability.get("max_retries", {}).get(selected_model, 1)
                timeout = self.reliability.get("timeout", {}).get(selected_model, 30)
                backoff_base = self.reliability.get("backoff", {}).get(selected_model, 1)
                model_messages = self.reliability.get("model_messages", {}).get(selected_model, [])
                try:
                    response = self._try_model(
                        model=selected_model,
                        messages=messages,
                        has_pdf=has_pdf,
                        stream=stream,
                        tools=tools,
                        tool_choice=tool_choice,
                        response_format=response_format,
                        max_retries=max_retries,
                        timeout=timeout,
                        backoff_base=backoff_base,
                        model_messages=model_messages,
                        **kwargs
                    )
                    return response
                except Exception as e:
                    print(f"Model {selected_model} failed: {e}")
                    candidate_models.remove(selected_model)
                    continue
            raise ValueError("All models failed after retries.")

        # Default Logic
        else:
            if model is not None:
                selected_model = model
            elif model_list is not None and len(model_list) == 1:
                selected_model = model_list[0]
            else:
                active_model_list = model_list if model_list is not None else self.model_list
                filtered_model_list = [
                    m for m in active_model_list
                    if self._model_supports_features(m, required_media, tools)
                ]
                try:
                    selected_model = self._model_select(
                        serializable_messages,
                        model_list=filtered_model_list,
                        max_model_depth=max_model_depth,
                        hash_content=hash_content,
                        tradeoff=tradeoff,
                        preference_id=preference_id,
                        previous_session=previous_session,
                        api_key=api_key,
                    )
                except Exception as e:
                    print(f"Model selection failed: {e}. Using fallback models.")
                    selected_model = None

            if selected_model is not None:
                if not self._model_supports_features(selected_model, required_media, tools):
                    print(f"Selected model {selected_model} does not support the required features or tools. Using fallback models.")
                    selected_model = None

            if selected_model is None:
                fallback_models_list = fallback_models or self.default_fallback_models
                models_to_try = [
                    m for m in fallback_models_list
                    if self._model_supports_features(m, required_media, tools)
                ]
            else:
                models_to_try = [selected_model]

            exceptions = []
            for try_model in models_to_try:
                try:
                    response = self._try_model(
                        model=try_model,
                        messages=messages,
                        has_pdf=has_pdf,
                        stream=stream,
                        tools=tools,
                        tool_choice=tool_choice,
                        response_format=response_format,
                        max_retries=1,
                        timeout=30,
                        backoff_base=1,
                        model_messages=[],
                        **kwargs
                    )
                    return response
                except Exception as e:
                    print(f"Completion with model {try_model} failed: {e}")
                    exceptions.append(e)
                    continue
            if exceptions:
                raise exceptions[-1]
            raise ValueError("All attempted models failed.")

    def stream_completion(self, *args, **kwargs):
        kwargs["stream"] = True
        return self.completion(*args, **kwargs)

    def function_call(
        self, messages: List[Dict[str, str]], tools: List[Dict], tool_choice: str = "auto", **kwargs
    ):
        return self.completion(messages=messages, tools=tools, tool_choice=tool_choice, **kwargs)

    def _standardize_tool(self, tool: Union[Dict[str, Any], Callable, BaseTool]) -> Dict[str, Any]:
        if isinstance(tool, dict):
            if "type" in tool:
                return tool
            else:
                return {"type": "function", "function": tool}
        elif isinstance(tool, BaseTool):
            converted = convert_to_openai_tool(tool)
            if not isinstance(converted, dict) or "type" not in converted or converted["type"] != "function" or "function" not in converted:
                raise ValueError(f"Invalid tool conversion for {tool}: {converted}")
            return converted
        elif callable(tool):
            function_dict = litellm.utils.function_to_dict(tool)
            if "name" not in function_dict or "parameters" not in function_dict:
                raise ValueError(f"Invalid function dictionary for {tool.__name__}: {function_dict}")
            return {"type": "function", "function": function_dict}
        else:
            raise ValueError(f"Unsupported tool type: {type(tool)}")

    def bind_tools(self, tools: List[Union[Dict[str, Any], Callable, BaseTool]]):
        tools_list = [self._standardize_tool(tool) for tool in tools]
        return lambda messages, **kwargs: self.completion(messages=messages, tools=tools_list, **kwargs)

    def supports_function_calling(self, model: str) -> bool:
        return litellm.supports_function_calling(model=model)

    def supports_json_mode(self, model: str) -> bool:
        provider, model_name = model.split("/", 1)
        params = litellm.get_supported_openai_params(model=model_name, custom_llm_provider=provider)
        return "response_format" in params
    
    def supports_vision(self, model: str) -> bool:
        provider, model_name = model.split("/", 1)
        return litellm.supports_vision(model=model_name, custom_llm_provider=provider)
    
    def supports_pdf_input(self, model: str) -> bool:
        provider, model_name = model.split("/", 1)
        return litellm.utils.supports_pdf_input(model=model_name, custom_llm_provider=provider)