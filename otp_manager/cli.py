import json
import os
from datetime import datetime
from pathlib import Path

import click
import pyotp
from rich.console import Console
from rich.table import Table

from .crypto import decrypt_data, encrypt_data
from .storage import DATA_DIR, clear_all_secrets, load_secrets, save_secrets

console = Console()
ERR_CONSOLE = Console(stderr=True)


@click.group()
def main():
    """Manage OTP secrets in secure way"""
    pass


# 在cli.py顶部添加
HISTORY_FILE = DATA_DIR / "history.log"


@main.command()
@click.argument("name")
@click.option("--show", is_flag=True, help="Display QR code")
def uri(name: str, show: bool):
    """Generate TOTP URI (for QR codes)"""
    secret = decrypt_data(
        load_secrets()[name], click.prompt("Password", hide_input=True)
    )
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name, issuer_name="MyOTP")
    if show:
        import qrcode

        qr = qrcode.QRCode()
        qr.add_data(uri)
        qr.print_ascii(tty=True)
    else:
        console.print(f"[blue]{uri}[/blue]")


def log_history(name: str):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} {name}\n")


def copy_to_clipboard(text: str):
    """Cross-platform clipboard copy"""
    try:
        import pyperclip
        pyperclip.copy(text)
        console.print("[dim]Copied to clipboard![/dim]")
    except ImportError:
        console.print(
            "[yellow]Install 'pyperclip' for auto-copy: pip install pyperclip[/yellow]"
        )


@main.command()
@click.argument("export_file", type=click.Path(exists=False))
def export_json(export_file: str):
    """Export all secrets to encrypted file"""
    encrypted = encrypt_data(json.dumps(load_secrets()), "export_password")
    Path(export_file).write_text(encrypted)
    console.print(f"[green]✓ Exported to {export_file}[/green]")


@main.command()
@click.argument("import_file", type=click.Path(exists=True))
def import_json(import_file: str):
    """Import secrets from encrypted file"""
    try:
        data = json.loads(
            decrypt_data(Path(import_file).read_text(), "export_password")
        )
        save_secrets(data)
        console.print("[green]✓ Import successful[/green]")
    except Exception as e:
        ERR_CONSOLE.print(f"[red]Import failed: {str(e)}[/red]")


@main.command()
def recent():
    """Show recently used OTPs"""
    if HISTORY_FILE.exists():
        console.print("[bold]Recent usage:[/bold]")
        os.system(f"tail -n 5 {HISTORY_FILE}")


@main.command()
@click.argument("name")
@click.argument("secret")
@click.password_option()
def add(name: str, secret: str, password: str):
    """Add new OTP secret"""
    secrets = load_secrets()
    secrets[name] = encrypt_data(secret, password)
    save_secrets(secrets)
    console.print(f"[green]✓ Added secret '{name}'[/green]")


@main.command()
@click.argument("name")
@click.option("--copy", is_flag=True, help="Copy OTP to clipboard")
@click.password_option()
def generate(name: str, password: str, copy: bool):
    """Generate OTP code"""
    secrets = load_secrets()
    if name not in secrets:
        ERR_CONSOLE.print(f"[red]Error: Secret '{name}' not found[/red]")
        return

    try:
        secret = decrypt_data(secrets[name], password)
        totp = pyotp.TOTP(secret)
        veri_code = totp.now()
        if copy:
            copy_to_clipboard(veri_code)
        else:
            console.print(f"[bold]{veri_code}[/bold]")

    except Exception as e:
        ERR_CONSOLE.print(f"[red]Decryption failed: {str(e)}[/red]")


@main.command()
def list():
    """List all stored secret names"""
    secrets = load_secrets()
    table = Table(title="Stored Secrets")
    table.add_column("Name", style="cyan")
    for name in secrets.keys():
        table.add_row(name)
    console.print(table)


@main.command()
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def reset(confirm: bool):
    """Remove ALL stored secrets (secure delete)"""
    if not confirm:
        click.confirm("This will PERMANENTLY delete all secrets. Continue?", abort=True)
    clear_all_secrets()
    console.print("[red]⚠ All secrets have been securely deleted[/red]")


@main.command()
@click.argument("name")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def remove(name: str, confirm: bool):
    """Remove a stored OTP secret"""
    secrets = load_secrets()

    if name not in secrets:
        ERR_CONSOLE.print(f"[red]Error: Secret '{name}' not found[/red]")
        return

    if not confirm:
        click.confirm(f"Really delete secret '{name}'?", abort=True)

    del secrets[name]
    save_secrets(secrets)
    console.print(f"[green]✓ Removed secret '{name}'[/green]")


if __name__ == "__main__":
    main()
