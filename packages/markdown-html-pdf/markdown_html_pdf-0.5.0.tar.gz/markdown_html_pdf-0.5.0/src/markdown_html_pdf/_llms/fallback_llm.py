import time
from typing import List, Optional, Union

from .fireworks import FireworksLLMs, call_fireworks_llm
from .groq import GroqLLMs, call_groq_llm

fallback_chain = [
    {"provider": "groq", "model": GroqLLMs.llama_4_maverick_17b_128e_instruct, "name": "Groq Llama4 Maverick"},
    {"provider": "groq", "model": GroqLLMs.llama_4_scout_17b_16e_instruct, "name": "Groq Llama4 Scout"},
    {"provider": "fireworks", "model": FireworksLLMs.llama4_maverick_instruct_basic, "name": "Fireworks Llama4 Maverick"},
]


def call_llm_with_fallback(
    prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    top_p: float = 1,
    stop: str = None,
    images: Optional[List[Union[str, bytes]]] = None,
    retry_delay: float = 1.0,
) -> str:
    """
    Call LLM with automatic fallback between different providers and models.

    Fallback order:
    1. Groq -> Llama4 Scout
    2. Groq -> Llama4 Maverick
    3. Fireworks -> Llama4 Scout
    4. Fireworks -> Llama4 Maverick

    Args:
        prompt: The text prompt
        temperature: Controls randomness
        max_tokens: Maximum tokens to generate
        top_p: Controls diversity via nucleus sampling
        stop: Stop sequence
        images: Optional list of images (URLs, file paths, or base64 encoded data)
        retry_delay: Delay between retries in seconds

    Returns:
        The generated response text

    Raises:
        Exception: If all providers/models fail
    """

    last_error = None

    for i, fallback in enumerate(fallback_chain):
        provider = fallback["provider"]
        model = fallback["model"]
        name = fallback["name"]

        try:
            print(f"🔄 Trying {name}...")

            if provider == "groq":
                result = call_groq_llm(
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    stop=stop,
                    images=images,
                )
            elif provider == "fireworks":
                result = call_fireworks_llm(
                    model=model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    stop=stop,
                    images=images,
                )
            else:
                raise ValueError(f"Unknown provider: {provider}")

            print(f"✅ Success with {name}")
            return result

        except Exception as e:
            error_msg = str(e)
            last_error = e

            # Check if it's a rate limit error (429)
            is_rate_limit = (
                "429" in error_msg
                or "Too Many Requests" in error_msg
                or "rate limit" in error_msg.lower()
                or "quota exceeded" in error_msg.lower()
            )

            if is_rate_limit:
                print(f"⚠️  Rate limit hit for {name}, trying next provider...")
                if i < len(fallback_chain) - 1:
                    print(f"⏳ Waiting {retry_delay} seconds before next attempt...")
                    time.sleep(retry_delay)
            else:
                print(f"❌ Error with {name}: {error_msg}")
                if i < len(fallback_chain) - 1:
                    print(f"⏳ Waiting {retry_delay} seconds before next attempt...")
                    time.sleep(retry_delay)

    # If we get here, all providers failed
    error_summary = f"All LLM providers failed. Last error: {last_error}"
    print(f"💥 {error_summary}")
    raise Exception(error_summary)


def call_llm_with_fallback_robust(
    prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 1024,
    top_p: float = 1,
    stop: str = None,
    images: Optional[List[Union[str, bytes]]] = None,
    retry_delay: float = 1.0,
    max_retries_per_provider: int = 2,
) -> str:
    """
    Enhanced version of call_llm_with_fallback with additional retry logic per provider.

    Args:
        prompt: The text prompt
        temperature: Controls randomness
        max_tokens: Maximum tokens to generate
        top_p: Controls diversity via nucleus sampling
        stop: Stop sequence
        images: Optional list of images (URLs, file paths, or base64 encoded data)
        retry_delay: Delay between retries in seconds
        max_retries_per_provider: Maximum retries per provider before moving to next

    Returns:
        The generated response text

    Raises:
        Exception: If all providers/models fail
    """

    last_error = None

    for i, fallback in enumerate(fallback_chain):
        provider = fallback["provider"]
        model = fallback["model"]
        name = fallback["name"]

        # Try each provider multiple times before moving to next
        for retry in range(max_retries_per_provider):
            try:
                if retry > 0:
                    print(f"🔄 Retrying {name} (attempt {retry + 1}/{max_retries_per_provider})...")
                else:
                    print(f"🔄 Trying {name}...")

                if provider == "groq":
                    result = call_groq_llm(
                        model=model,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        stop=stop,
                        images=images,
                    )
                elif provider == "fireworks":
                    result = call_fireworks_llm(
                        model=model,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        stop=stop,
                        images=images,
                    )
                else:
                    raise ValueError(f"Unknown provider: {provider}")

                print(f"✅ Success with {name}")
                return result

            except Exception as e:
                error_msg = str(e)
                last_error = e

                # Check if it's a rate limit error (429)
                is_rate_limit = (
                    "429" in error_msg
                    or "Too Many Requests" in error_msg
                    or "rate limit" in error_msg.lower()
                    or "quota exceeded" in error_msg.lower()
                )

                if is_rate_limit:
                    print(f"⚠️  Rate limit hit for {name}")
                    if retry < max_retries_per_provider - 1:
                        print(f"⏳ Waiting {retry_delay * (retry + 1)} seconds before retry...")
                        time.sleep(retry_delay * (retry + 1))  # Exponential backoff
                    else:
                        print("🔄 Moving to next provider...")
                else:
                    print(f"❌ Error with {name}: {error_msg}")
                    if retry < max_retries_per_provider - 1:
                        print(f"⏳ Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                    else:
                        print("🔄 Moving to next provider...")

        # If we get here, this provider failed all retries
        if i < len(fallback_chain) - 1:
            print(f"⏳ Waiting {retry_delay} seconds before next provider...")
            time.sleep(retry_delay)

    # If we get here, all providers failed
    error_summary = f"All LLM providers failed after {max_retries_per_provider} retries each. Last error: {last_error}"
    print(f"💥 {error_summary}")
    raise Exception(error_summary)
