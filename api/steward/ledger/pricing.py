"""Token prices, $ per 1M input / output tokens (docs/04 T2.4)."""

PRICES: dict[str, tuple[float, float]] = {
    "nvidia/Nemotron-3_5-Lightning": (0.06, 0.24),
    "nvidia/nemotron-3-super-120b-a12b": (0.30, 0.90),
    "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B": (0.06, 0.24),
}

DISPLAY_NAMES: dict[str, str] = {
    "nvidia/Nemotron-3_5-Lightning": "Nemotron 3.5 Lightning",
    "nvidia/nemotron-3-super-120b-a12b": "Nemotron 3 Super",
    "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B": "Nemotron 3 Nano 30B",
}


def cost_usd(model: str | None, prompt_tokens: int, completion_tokens: int) -> float:
    price_in, price_out = PRICES.get(model or "", (0.0, 0.0))
    return round(prompt_tokens / 1e6 * price_in + completion_tokens / 1e6 * price_out, 8)


def display_name(model: str | None) -> str:
    return DISPLAY_NAMES.get(model or "", model or "Unknown model")
