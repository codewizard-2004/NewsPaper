from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()


class TokenCountingCallback(BaseCallbackHandler):
    """Collects token usage from LLM calls for reporting."""

    def __init__(self):
        self.calls: List[Dict[str, Any]] = []

    def on_llm_end(self, response, **kwargs) -> None:
        try:
            prompt_tokens = 0
            completion_tokens = 0

            # Check LLMResult.llm_output (Ollama via ChatOllama)
            llm_output = getattr(response, "llm_output", None) or {}
            if isinstance(llm_output, dict):
                prompt_tokens = llm_output.get("prompt_eval_count", 0) or llm_output.get("prompt_tokens", 0)
                completion_tokens = llm_output.get("eval_count", 0) or llm_output.get("completion_tokens", 0)

            # Check per-generation info
            if not prompt_tokens and not completion_tokens:
                generations = getattr(response, "generations", [])
                if generations and generations[0]:
                    gen_info = generations[0][0].generation_info or {}
                    prompt_tokens = gen_info.get("prompt_eval_count", 0) or gen_info.get("prompt_tokens", 0)
                    completion_tokens = gen_info.get("eval_count", 0) or gen_info.get("completion_tokens", 0)

            if prompt_tokens or completion_tokens:
                self.calls.append({
                    "prompt_tokens": prompt_tokens or 0,
                    "completion_tokens": completion_tokens or 0,
                    "total_tokens": (prompt_tokens or 0) + (completion_tokens or 0),
                })
        except Exception:
            pass


def print_token_summary(callbacks: List[TokenCountingCallback], label: str = "Pipeline") -> None:
    """Aggregate and display token usage from one or more callbacks."""
    total_prompt = 0
    total_completion = 0
    total_all = 0
    call_count = 0
    for cb in callbacks:
        for c in cb.calls:
            total_prompt += c["prompt_tokens"]
            total_completion += c["completion_tokens"]
            total_all += c["total_tokens"]
            call_count += 1

    if call_count == 0:
        return

    table = Table(
        title=f"🔢 Token Consumption — {label}",
        box=box.ROUNDED,
        border_style="cyan",
    )
    table.add_column("Metric", style="bold")
    table.add_column("Count", justify="right")
    table.add_row("LLM Calls", str(call_count))
    table.add_row("Prompt Tokens", f"{total_prompt:,}")
    table.add_row("Completion Tokens", f"{total_completion:,}")
    table.add_row("Total Tokens", f"{total_all:,}")
    console.print()
    console.print(Panel(table, border_style="cyan", title="📊 Token Usage"))
