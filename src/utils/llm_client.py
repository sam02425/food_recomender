# src/utils/llm_client.py
import os
import requests
import json
import logging

logger = logging.getLogger("llm_client")

# LLM API configuration
# Replace with your actual API provider details
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_API_URL = os.environ.get("LLM_API_URL", "https://api.openai.com/v1/chat/completions")

def get_llm_response(prompt, model="gpt-3.5-turbo", max_tokens=150):
    """
    Get a response from the LLM API.

    Args:
        prompt: The prompt to send to the LLM
        model: The model to use
        max_tokens: Maximum number of tokens to generate

    Returns:
        Generated text response or None if failed
    """
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        response = requests.post(
            LLM_API_URL,
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            logger.error(f"LLM API error: {response.status_code}, {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error calling LLM API: {e}")
        return None