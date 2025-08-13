from rich.console import Console
from rich.pretty import Pretty

from janito.config import config
from janito.cli.config import CONFIG_OPTIONS


def resolve_effective_model(provider_name):
    # Try provider-specific model, then global model, then provider default
    provider_cfg = config.get_provider_config(provider_name)
    model = provider_cfg.get("model") if provider_cfg else None
    if not model:
        model = config.get("model")
    if not model:
        try:
            from janito.provider_registry import ProviderRegistry

            provider_class = ProviderRegistry().get_provider(provider_name)
            model = getattr(provider_class, "DEFAULT_MODEL", None)
        except Exception:
            model = None
    return model


def handle_show_config(args):
    console = Console()
    provider = config.get("provider")
    model = config.get("model")
    # Show all providers with their effective model
    from janito.provider_registry import ProviderRegistry

    provider_names = []
    try:
        provider_names = ProviderRegistry()._get_provider_names()
    except Exception:
        pass
    from janito.provider_config import get_config_path

    config_path = get_config_path()
    console.print("[bold green]Current configuration:[/bold green]")
    console.print(f"[bold yellow]Config file:[/bold yellow] {config_path}")
    console.print(f"[bold yellow]Current provider:[/bold yellow] {provider!r}\n")
    if model is not None:
        console.print(f"[bold yellow]Global model:[/bold yellow] {model!r}\n")

    # Show disabled tools
    from janito.tools.disabled_tools import load_disabled_tools_from_config

    disabled_tools = load_disabled_tools_from_config()
    if disabled_tools:
        console.print(
            f"\n[bold red]Disabled tools:[/bold red] {', '.join(sorted(disabled_tools))}"
        )
    else:
        console.print("\n[bold green]No tools are disabled[/bold green]")
    return
