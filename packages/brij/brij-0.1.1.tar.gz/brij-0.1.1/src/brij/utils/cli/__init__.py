import importlib.util as imputil
import inspect
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing_extensions import Annotated

from brij.utils.server.base import BaseServer

console = Console()
app = typer.Typer(help="Brij CLI for servers with ZMQ")


def load_module(file_path: Path):
    spec = imputil.spec_from_file_location(file_path.stem, str(file_path))
    mod = imputil.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(mod)  # type: ignore
    return mod


def find_server_class(module) -> type[BaseServer]:
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BaseServer) and obj is not BaseServer:
            return obj
    raise ValueError("[red]❌ No subclass of BaseServer found in the module.[/red]")


@app.command("hello", help="Greets the user")
def hello():
    console.log(
        Panel.fit(
            Text("Welcome to [bold green]Brij[/bold green] 🚀", justify="center"),
            title="👋 Hello",
            border_style="green",
        )
    )


@app.command(name="serve", help="Start a brij server")
def serve(
    server_file: Annotated[
        Path, typer.Argument(help="Path to the server implementation file")
    ],
    port: Annotated[
        int, typer.Option("--port", "-p", help="Port to bind the server to")
    ] = 5555,
):
    """
    Serve a ZMQ server from a given Python file.
    """
    console.log(f":mag: [cyan]Loading server from[/cyan] {server_file}...")
    module = load_module(server_file)
    console.log("[green]Module imported successfully.[/green]")

    server_class = find_server_class(module)
    server_instance = server_class(port=port)
    console.log(f"[cyan]Found server class[/cyan] {server_class.__name__}")

    try:
        console.log(
            f":rocket: [bold cyan]Starting[/] {server_class.__name__} on port [bold yellow]{port}[/bold yellow]"
        )
        with console.status(
            "[bold green]Server is running[/] [dim][Press Ctrl+C to exit][/]",
            spinner="dots8",
        ):
            server_instance.run()
    except KeyboardInterrupt:
        console.log(":stop_sign: [red]Shutting down server...[/red]")
        server_instance.close()
