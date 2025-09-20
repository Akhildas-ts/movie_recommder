#!/usr/bin/env python3
"""
Movie Recommender API - Run Script

This script provides convenient commands to run and manage the FastAPI application.
"""

import asyncio
import click
import uvicorn
from app.utils.data_loader import load_sample_data
from app.core.database import init_db


@click.group()
def cli():
    """Movie Recommender API Management CLI"""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.option("--workers", default=1, help="Number of worker processes")
def serve(host, port, reload, workers):
    """Start the FastAPI server"""
    click.echo(f"🚀 Starting Movie Recommender API on {host}:{port}")
    
    if reload:
        click.echo("🔄 Auto-reload enabled for development")
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    else:
        click.echo(f"👥 Running with {workers} worker(s)")
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            workers=workers,
            log_level="info"
        )


@cli.command()
def init_database():
    """Initialize the database (create tables)"""
    click.echo("📊 Initializing database...")
    
    async def _init():
        await init_db()
        click.echo("✅ Database initialized successfully!")
    
    asyncio.run(_init())


@cli.command()
def load_data():
    """Load sample data into the database"""
    click.echo("📥 Loading sample data...")
    
    async def _load():
        await load_sample_data()
        click.echo("✅ Sample data loaded successfully!")
    
    asyncio.run(_load())


@cli.command()
def setup():
    """Complete setup: initialize database and load sample data"""
    click.echo("🛠️ Setting up Movie Recommender API...")
    
    async def _setup():
        click.echo("📊 Initializing database...")
        await init_db()
        click.echo("✅ Database initialized!")
        
        click.echo("📥 Loading sample data...")
        await load_sample_data()
        click.echo("✅ Sample data loaded!")
        
        click.echo("🎉 Setup complete! You can now start the server with 'python run.py serve --reload'")
    
    asyncio.run(_setup())


@cli.command()
@click.option("--coverage", is_flag=True, help="Run with coverage report")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def test(coverage, verbose):
    """Run tests"""
    import subprocess
    import sys
    
    cmd = ["pytest"]
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    if verbose:
        cmd.append("-v")
    
    click.echo(f"🧪 Running tests: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@cli.command()
def docs():
    """Open API documentation in browser"""
    import webbrowser
    
    url = "http://localhost:8000/api/v1/docs"
    click.echo(f"📖 Opening API documentation: {url}")
    webbrowser.open(url)


@cli.command()
def info():
    """Show application information"""
    from app.core.config import settings
    
    click.echo("🎬 Movie Recommender API Information")
    click.echo("=" * 40)
    click.echo(f"Project: {settings.PROJECT_NAME}")
    click.echo(f"Version: {settings.VERSION}")
    click.echo(f"Description: {settings.DESCRIPTION}")
    click.echo(f"API Base: {settings.API_V1_STR}")
    click.echo(f"Database: {settings.DATABASE_URL}")
    click.echo(f"Redis: {settings.REDIS_URL}")
    click.echo("=" * 40)
    
    click.echo("\n📚 Available Endpoints:")
    click.echo("• Health Check: /health")
    click.echo("• API Docs: /api/v1/docs")
    click.echo("• Authentication: /api/v1/auth/*")
    click.echo("• Movies: /api/v1/movies/*")  
    click.echo("• Ratings: /api/v1/ratings/*")
    click.echo("• Recommendations: /api/v1/recommendations/*")


@cli.command()
def check_dependencies():
    """Check if all dependencies are installed"""
    import importlib
    
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
        "asyncpg", "redis", "scikit-learn", "pandas", 
        "numpy", "passlib", "python-jose", "python-multipart"
    ]
    
    click.echo("📦 Checking dependencies...")
    
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace("-", "_"))
            click.echo(f"✅ {package}")
        except ImportError:
            click.echo(f"❌ {package} (missing)")
            missing.append(package)
    
    if missing:
        click.echo(f"\n⚠️ Missing packages: {', '.join(missing)}")
        click.echo("Install with: pip install " + " ".join(missing))
        return 1
    else:
        click.echo("\n🎉 All dependencies are installed!")
        return 0


if __name__ == "__main__":
    cli()