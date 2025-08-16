"""
Console utilities for rich formatting and emoji support.
"""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

console = Console()
error_console = Console(stderr=True)


# Emoji constants
class Emojis:
    # Status
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    PROCESSING = "🔄"

    # Files
    SRT_FILE = "📄"
    ASS_FILE = "🎬"
    FOLDER = "📁"

    # Providers
    OPENAI = "🤖"
    GEMINI = "💎"
    DEEPSEEK = "🧠"

    # Translation modes
    BILINGUAL = "🌐"
    MONOLINGUAL = "📝"

    # Actions
    TRANSLATE = "🔤"
    BATCH = "📦"
    PROGRESS = "📊"
    CLOCK = "⏰"
    ROCKET = "🚀"
    PARTY = "🎉"
    GEAR = "⚙️"
    LIGHTBULB = "💡"
    CHECKMARK = "✔️"
    ARROW_RIGHT = "➡️"
    QUESTION = "❓"

    # Numbers for progress
    NUMBERS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


def get_provider_emoji(provider: str) -> str:
    """Get emoji for AI provider."""
    provider_emojis = {
        "openai": Emojis.OPENAI,
        "gemini": Emojis.GEMINI,
        "deepseek": Emojis.DEEPSEEK,
    }
    return provider_emojis.get(provider.lower(), Emojis.GEAR)


def get_mode_emoji(mode: str) -> str:
    """Get emoji for translation mode."""
    mode_emojis = {
        "bilingual": Emojis.BILINGUAL,
        "monolingual": Emojis.MONOLINGUAL,
    }
    return mode_emojis.get(mode.lower(), Emojis.TRANSLATE)


def print_success(message: str) -> None:
    """Print success message with emoji."""
    console.print(f"{Emojis.SUCCESS} {message}", style="green")


def print_error(message: str) -> None:
    """Print error message with emoji."""
    error_console.print(f"{Emojis.ERROR} {message}", style="red")


def print_warning(message: str) -> None:
    """Print warning message with emoji."""
    console.print(f"{Emojis.WARNING} {message}", style="yellow")


def print_info(message: str) -> None:
    """Print info message with emoji."""
    console.print(f"{Emojis.INFO} {message}", style="blue")


def print_processing(message: str) -> None:
    """Print processing message with emoji."""
    console.print(f"{Emojis.PROCESSING} {message}", style="cyan")


def create_progress_bar() -> Progress:
    """Create a rich progress bar for batch processing."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="green"),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def is_success_status(status: str) -> bool:
    """Check if status represents a successful outcome."""
    success_terms = {
        "success",
        "successful",
        "complete",
        "completed",
        "done",
        "finished",
        "ok",
        "ready",
        "good",
        "passed",
    }
    status_lower = status.lower()
    return any(term in status_lower for term in success_terms)


def _add_fallback_info(summary_text, fallback_usage: list[dict]) -> None:
    """Add fallback information to summary text."""
    # Group by provider
    provider_stats = {}
    for usage in fallback_usage:
        provider = usage["provider"]
        if provider not in provider_stats:
            provider_stats[provider] = {"count": 0, "ranges": []}
        provider_stats[provider]["count"] += usage["count"]
        provider_stats[provider]["ranges"].append(
            f"{usage['line_start']}-{usage['line_end']}"
        )

    # Display fallback info for each provider
    for provider, stats in provider_stats.items():
        summary_text.append("🔄 Fallback: ", style="bold")

        if len(stats["ranges"]) <= 3:
            # Show ranges if there are few incidents
            ranges_str = ", ".join(stats["ranges"])
            summary_text.append(f"{provider} ({stats['count']} lines: {ranges_str})\n")
        else:
            # Show count only for many incidents
            summary_text.append(
                f"{provider} ({stats['count']} lines, {len(stats['ranges'])} batches)\n"
            )


def create_summary_panel(
    status: str,
    output_file: str,
    mode: str,
    template: str,
    provider: str,
    translated_count: int,
    total_count: int,
    fallback_usage: list[dict] | None = None,
) -> Panel:
    """Create a summary panel with emojis."""
    status_emoji = Emojis.SUCCESS if is_success_status(status) else Emojis.ERROR
    provider_emoji = get_provider_emoji(provider)
    mode_emoji = get_mode_emoji(mode)

    summary_text = Text()
    summary_text.append(f"{status_emoji} Status: ", style="bold")
    summary_text.append(
        f"{status}\n", style="green" if is_success_status(status) else "red"
    )

    summary_text.append(f"{Emojis.ASS_FILE} Output: ", style="bold")
    summary_text.append(f"{output_file}\n", style="blue")

    summary_text.append(f"{mode_emoji} Mode: ", style="bold")
    summary_text.append(f"{mode}\n")

    summary_text.append(f"{Emojis.GEAR} Template: ", style="bold")
    summary_text.append(f"{template}\n")

    summary_text.append(f"{provider_emoji} Provider: ", style="bold")
    summary_text.append(f"{provider}\n")

    # Add fallback information if any fallbacks were used
    if fallback_usage:
        _add_fallback_info(summary_text, fallback_usage)

    summary_text.append(f"{Emojis.PROGRESS} Progress: ", style="bold")
    summary_text.append(f"{translated_count}/{total_count} lines")

    return Panel(
        summary_text,
        title=f"{Emojis.PARTY} Conversion Summary",
        border_style="green" if is_success_status(status) else "red",
        box=box.ROUNDED,
    )


def create_provider_table() -> Table:
    """Create a table showing available providers."""
    table = Table(title=f"{Emojis.GEAR} Available AI Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Emoji", justify="center")
    table.add_column("Models", style="magenta")

    table.add_row("OpenAI", Emojis.OPENAI, "Latest GPT models")
    table.add_row("Gemini", Emojis.GEMINI, "Latest Gemini models")
    table.add_row("DeepSeek", Emojis.DEEPSEEK, "Latest DeepSeek models")

    return table


def print_welcome_banner() -> None:
    """Print welcome banner with emojis."""
    banner = Panel(
        Text(
            f"{Emojis.TRANSLATE} AI Subtitle Translator {Emojis.ROCKET}\n"
            f"Advanced SRT to ASS conversion with AI translation",
            justify="center",
        ),
        title=f"{Emojis.PARTY} Welcome",
        border_style="cyan",
        box=box.DOUBLE,
    )
    console.print(banner)


def print_file_info(input_file: str, output_file: str) -> None:
    """Print file information with emojis."""
    console.print(f"{Emojis.SRT_FILE} Input:  [blue]{input_file}[/blue]")
    console.print(f"{Emojis.ASS_FILE} Output: [green]{output_file}[/green]")


def print_config_info(provider: str, mode: str, template: str, batch_size: int) -> None:
    """Print configuration information with emojis."""
    provider_emoji = get_provider_emoji(provider)
    mode_emoji = get_mode_emoji(mode)

    console.print(f"{provider_emoji} Provider: [cyan]{provider}[/cyan]")
    console.print(f"{mode_emoji} Mode: [magenta]{mode}[/magenta]")
    console.print(f"{Emojis.GEAR} Template: [yellow]{template}[/yellow]")
    console.print(f"{Emojis.BATCH} Batch Size: [white]{batch_size}[/white]")


def print_resume_info(completed_count: int) -> None:
    """Print resume information with emojis."""
    console.print(
        f"{Emojis.CHECKMARK} Resuming translation. "
        f"Found [green]{completed_count}[/green] completed lines."
    )


def print_batch_info(start_idx: int, end_idx: int, current: int, total: int) -> None:
    """Print batch processing information with emojis."""
    console.print(
        f"{Emojis.BATCH} Processing batch: lines {start_idx} to {end_idx} "
        f"({current}/{total} batches)"
    )


def print_completion_celebration(translated_count: int, total_count: int) -> None:
    """Print completion celebration with emojis."""
    if translated_count == total_count:
        console.print(
            f"{Emojis.PARTY} All done! Successfully translated "
            f"[green]{translated_count}[/green] lines! {Emojis.ROCKET}",
            style="bold green",
        )
    else:
        console.print(
            f"{Emojis.CHECKMARK} Completed! Translated "
            f"[yellow]{translated_count}[/yellow] out of "
            f"[white]{total_count}[/white] lines.",
            style="bold yellow",
        )


def print_helpful_tip(tip: str) -> None:
    """Print helpful tip with emoji."""
    console.print(f"{Emojis.LIGHTBULB} Tip: {tip}", style="dim")


def print_error_with_help(error: str, help_text: str) -> None:
    """Print error with helpful guidance."""
    error_console.print(f"{Emojis.ERROR} Error: {error}", style="red")
    error_console.print(f"{Emojis.ARROW_RIGHT} {help_text}", style="dim")
