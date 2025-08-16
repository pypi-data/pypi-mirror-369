"""
SEDQL CLI - Simple command-line interface
"""

import click
from pathlib import Path
from .client import SEDClient


@click.group()
@click.version_option(version="1.0.0")
def main():
    """SEDQL - Python SDK for SED (Semantic Entities Designs)"""
    pass


@main.command()
@click.option('--db-url', help='Database connection string')
@click.option('--config', default=str(Path.cwd() / 'sed.config.json'), help='Config file path')
@click.option('--force', is_flag=True, help='Force overwrite existing config')
def init(db_url, config, force):
    """Initialize SED with database connection"""
    try:
        client = SEDClient(db_url=db_url, config_path=config)
        result = client.init(force=force)
        click.echo(f"Initialization result: {result}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.option('--config', default=str(Path.cwd() / 'sed.config.json'), help='Config file path')
@click.option('--output', help='Output file path')
def build(config, output):
    """Build or rebuild semantic layer"""
    try:
        client = SEDClient(config_path=config)
        result = client.build(output_file=output)
        click.echo(f"Build result: {result}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.argument('query')
@click.option('--config', default=str(Path.cwd() / 'sed.config.json'), help='Config file path')
@click.option('--verbose', is_flag=True, help='Show detailed query translation')
def query(query, config, verbose):
    """Query database using natural language"""
    try:
        client = SEDClient(config_path=config)
        result = client.query(query, verbose=verbose)
        click.echo(f"Query result: {result}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@main.command()
@click.argument('query')
@click.option('--ai', is_flag=True, help='Use AI to enhance query results')
@click.option('--ai-model', default='gpt-4', help='AI model to use')
@click.option('--config', default=str(Path.cwd() / 'sed.config.json'), help='Config file path')
@click.option('--verbose', is_flag=True, help='Show detailed output')
def query_ai(query, ai, ai_model, config, verbose):
    """Query database using AI-enhanced natural language"""
    try:
        client = SEDClient(config_path=config)
        
        if ai:
            # For CLI usage, we'll provide a simple AI enhancement
            # Users should use the Python SDK for full AI integration
            click.echo("AI enhancement requires Python SDK usage with your AI client.")
            click.echo("Example:")
            click.echo("  from sedql import SEDClient")
            click.echo("  import openai")
            click.echo("  client = SEDClient()")
            click.echo("  openai_client = openai.OpenAI(api_key='your-key')")
            click.echo("  result = client.query_with_ai({")
            click.echo("      'natural_language': 'your query',")
            click.echo("      'ai_client': openai_client,")
            click.echo("      'ai_model': 'gpt-4'")
            click.echo("  })")
            
            # Still run the basic query
            result = client.query(query, verbose=verbose)
        else:
            result = client.query(query, verbose=verbose)
            
        click.echo(f"Result: {result}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.option('--config', default=str(Path.cwd() / 'sed.config.json'), help='Config file path')
def status(config):
    """Get current SED status"""
    try:
        client = SEDClient(config_path=config)
        result = client.get_status()
        click.echo(f"Status: {result}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    main()
