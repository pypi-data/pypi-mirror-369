import base64
import requests
import os
from urllib.parse import urlparse
from typing import List, Dict, Any
from openai import OpenAI
from .config import DEFAULT_TIMEOUT

def openai_completion_with_pdf(model: str, messages: List[Dict[str, Any]], stream: bool = False, timeout: float = DEFAULT_TIMEOUT, **kwargs):
    client = OpenAI()
    inputs = []

    for msg in messages:
        content = []
        for item in msg.get("content", []):
            if item.get("type") == "text":
                content.append({"type": "input_text", "text": item.get("text", "")})
            elif item.get("type") == "image_url":
                url = item["image_url"]["url"] if isinstance(item["image_url"], dict) else item["image_url"]
                if url.startswith("data:application/pdf;base64,"):
                    base64_data = url.split(",", 1)[1]
                else:
                    try:
                        file_data = requests.get(url, timeout=timeout).content
                        base64_data = base64.b64encode(file_data).decode()
                    except Exception:
                        raise RuntimeError(f"Failed to download PDF: {url}")

                filename = os.path.basename(urlparse(url).path) or "document.pdf"
                content.append({
                    "type": "input_file",
                    "filename": filename,
                    "file_data": f"data:application/pdf;base64,{base64_data}"
                })

        inputs.append({"role": "user", "content": content})

    return client.responses.create(model=model, input=inputs, stream=stream, timeout=timeout, **kwargs)
