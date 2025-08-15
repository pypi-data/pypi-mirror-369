import json
import requests
import time
import logging

from .config import MAX_RETRIES, GIST_URL

def retry_with_backoff(func, *args, max_retries=MAX_RETRIES, backoff_base=1, **kwargs):
    """Retry a function up to MAX_RETRIES times with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = backoff_base * (2 ** attempt)
            logging.warning(f"Error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)

def fetch_model_list_from_gist(url=GIST_URL):
    """Fetch model list, media support data, and OpenRouter mapping from a Gist URL."""
    try:
        response = requests.get(url, timeout=10) 
        response.raise_for_status()
        data = response.json()
        model_list = []
        support_media_dict = {}
        support_tools_dict = {}
        openrouter_mapping = {}
        for provider, info in data.items():
            if "models" in info:
                prefix_dict = info.get("model_prefix", {})
                support_media = info.get("support_media_inputs", {})
                support_tools = info.get("support_tools", [])
                for model in info["models"]:
                    if prefix_dict:
                        if model in prefix_dict:
                            prefix = prefix_dict[model]
                            full_model = f"{provider}/{prefix}/{model}"
                        else:
                            raise ValueError(
                                f"Model '{model}' for provider '{provider}' does not have a prefix specified in model_prefix."
                            )
                    else:
                        full_model = f"{provider}/{model}"
                    model_list.append(full_model)
                    if model in support_media:
                        support_media_dict[full_model] = support_media[model]
                    else:
                        support_media_dict[full_model] = []
                    support_tools_dict[full_model] = model in support_tools
                # Build OpenRouter mapping
                if "openrouter_identifier" in info:
                    for gist_model, openrouter_id in info["openrouter_identifier"].items():
                        if prefix_dict and gist_model in prefix_dict:
                            prefix = prefix_dict[gist_model]
                            full_gist_model = f"{provider}/{prefix}/{gist_model}"
                        else:
                            full_gist_model = f"{provider}/{gist_model}"
                        openrouter_mapping[openrouter_id] = full_gist_model
        return model_list, support_media_dict, support_tools_dict, openrouter_mapping
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch model list from Gist: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from Gist: {e}")

def is_pdf(url):
    """Check if a URL or data URI points to a PDF."""
    if isinstance(url, str):
        if url.lower().endswith(".pdf"):
            return True
        if url.startswith("data:"):
            return url.split(";")[0][5:] == "application/pdf"
    elif isinstance(url, dict) and "url" in url:
        return is_pdf(url["url"])
    return False

def detect_media_types(messages):
    """Detect presence of PDFs and non-PDF images in messages."""
    has_pdf = has_image = False
    for msg in messages:
        if isinstance(msg, dict) and isinstance(msg.get("content"), list):
            for item in msg["content"]:
                if item.get("type") == "image_url":
                    url = item.get("image_url")
                    if is_pdf(url):
                        has_pdf = True
                    else:
                        has_image = True
                if has_pdf and has_image:
                    return has_pdf, has_image
    return has_pdf, has_image