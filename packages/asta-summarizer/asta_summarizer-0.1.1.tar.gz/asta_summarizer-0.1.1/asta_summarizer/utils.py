import re


def remove_think_tags(text: str) -> str:
    """Remove thinking tags from the generated text. Weird quirk from Qwen model"""
    if not text:
        return ""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
