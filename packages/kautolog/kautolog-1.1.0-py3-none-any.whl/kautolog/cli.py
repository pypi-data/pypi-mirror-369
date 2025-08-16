import typer
from typing import Optional
from .installer import install_all, uninstall_all, get_status

app = typer.Typer(add_completion=False, help="Auto-log all terminal sessions on Kali/Linux using script(1).")

@app.command()
def install(
    logdir: Optional[str] = typer.Option(None, help="Log directory (default: ~/terminal-logs)"),
    with_tmux: bool = typer.Option(False, "--with-tmux", help="Append tmux auto-logging to ~/.tmux.conf"),
    with_logrotate: bool = typer.Option(True, "--with-logrotate/--no-logrotate", help="Install user logrotate rule"),
    with_sync: Optional[str] = typer.Option(None, "--with-sync", help="rclone remote (e.g., remote:terminal-logs)"),
    interval: int = typer.Option(10, help="Sync interval in minutes (systemd user timer)"),
):
    """Install kautolog for the current user (both Bash and Zsh rc files)."""
    ok = install_all(
        logdir=logdir,
        enable_tmux=with_tmux,
        enable_logrotate=with_logrotate,
        rclone_remote=with_sync,
        sync_interval_min=interval,
    )
    raise typer.Exit(code=0 if ok else 1)

@app.command()
def uninstall():
    """Uninstall kautolog for the current user."""
    ok = uninstall_all()
    raise typer.Exit(code=0 if ok else 1)

@app.command()
def status():
    """Show install status and recent logs."""
    print(get_status())
