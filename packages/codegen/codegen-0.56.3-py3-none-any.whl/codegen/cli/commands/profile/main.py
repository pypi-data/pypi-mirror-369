import rich
from rich import box
from rich.panel import Panel

from codegen.cli.auth.decorators import requires_auth
from codegen.cli.auth.session import CodegenSession

# from codegen.cli.workspace.decorators import requires_init  # Removed to simplify CLI


def requires_init(func):
    """Simple stub decorator that does nothing."""
    return func


@requires_auth
@requires_init
def profile(session: CodegenSession):
    """Display information about the currently authenticated user."""
    repo_config = session.config.repository
    rich.print(
        Panel(
            f"[cyan]Name:[/cyan]  {repo_config.user_name}\n[cyan]Email:[/cyan] {repo_config.user_email}\n[cyan]Repo:[/cyan]  {repo_config.name}",
            title="🔑 [bold]Current Profile[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
