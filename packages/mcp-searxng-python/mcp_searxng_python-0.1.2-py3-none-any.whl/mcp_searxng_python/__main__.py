import asyncio
import typer

from . import __version__
from .server import run_sse, run_stdio, run_streamable_http

def version_callback(value: bool):
    if value:
        typer.echo(f"mcp-searxng-python version {__version__}")
        raise typer.Exit()

app = typer.Typer(
    help=f"SearXNG MCP Server (v{__version__})",
    add_completion=False
)

@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    )
):
    """SearXNG MCP Server - Web search and URL reading with proxy support"""
    pass

@app.command()
def sse():
    """Start SearXNG MCP Server in SSE mode"""
    print(f"SearXNG MCP Server v{__version__} - SSE mode")
    print("=" * 40)
    print("Press Ctrl+C to exit")
    try:
        asyncio.run(run_sse())
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Service stopped.")

@app.command()
def streamable_http():
    """Start SearXNG MCP Server in streamable HTTP mode"""
    print(f"SearXNG MCP Server v{__version__} - Streamable HTTP mode")
    print("=" * 50)
    print("Press Ctrl+C to exit")
    try:
        asyncio.run(run_streamable_http())
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Service stopped.")

@app.command()
def stdio():
    """Start SearXNG MCP Server in stdio mode"""
    print(f"SearXNG MCP Server v{__version__} - Stdio mode")
    print("=" * 40)
    print("Press Ctrl+C to exit")
    try:
        run_stdio()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Service stopped.")

if __name__ == "__main__":
    app()
