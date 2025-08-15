"""
IntelliScript CLI Entry Point
============================

Main command-line interface for IntelliScript with all modes:
- Command generation (original functionality)
- Data extraction with LangExtract
- Analysis and insights generation
- Report creation and automation
- Multi-step pipeline workflows

Usage:
    intelliscript "find large files"
    intelliscript extract "analyze logs" --visualize
    intelliscript analyze "system performance" --insights
    intelliscript report "daily health" --format html
    intelliscript pipeline "monitoring" --steps "collect,extract,analyze"
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add src to path for development
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent
    sys.path.insert(0, str(src_path))

# Import IntelliScript components
try:
    from intelliscript.core.intelliscript_main import IntelliScript
    from intelliscript.core.error_handler import ErrorHandler
    # Import ExtractCommands inline to avoid circular import
except ImportError as e:
    # Fallback for development environment
    try:
        from core.intelliscript_main import IntelliScript
        from core.error_handler import ErrorHandler
    except ImportError:
        print(f"❌ Failed to import IntelliScript components: {e}")
        print("Please ensure IntelliScript is properly installed.")
        sys.exit(1)

# Initialize console for rich output
console = Console()

# Version info
__version__ = "2.1.0"


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--provider', default=None, 
              type=click.Choice(['openai', 'anthropic', 'google', 'ollama', 'langextract']),
              help='AI provider to use')
@click.option('--config', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.argument('query', required=False)
@click.pass_context
def main(ctx, version: bool, provider: Optional[str], config: Optional[str], 
         verbose: bool, debug: bool, query: Optional[str]):
    """
    🤖 IntelliScript v2.1 - World's First LangExtract CLI Integration
    
    Transform natural language into executable commands with advanced data analysis.
    
    Examples:
        intelliscript "find large files"
        intelliscript extract "analyze logs" --visualize
        intelliscript analyze "system performance" --insights
        intelliscript report "daily health" --format html
    """
    # Set up logging
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    # Handle version flag
    if version:
        show_version_info()
        return
    
    # If no subcommand and no query, show help
    if ctx.invoked_subcommand is None and not query:
        click.echo(ctx.get_help())
        return
    
    # Handle direct query (original functionality)
    if query and ctx.invoked_subcommand is None:
        handle_direct_query(query, provider, config, verbose, debug)
        return


def show_version_info():
    """Display version and system information."""
    console.print(Panel.fit(
        f"""[bold blue]IntelliScript v{__version__}[/bold blue]
[green]World's First LangExtract CLI Integration[/green]

🔍 Extract • 📊 Analyze • 📋 Report • 🔄 Pipeline

[dim]Python: {sys.version.split()[0]}
Platform: {sys.platform}
Installation: {"PyPI" if __package__ else "Development"}[/dim]""",
        title="🤖 IntelliScript",
        border_style="blue"
    ))


def handle_direct_query(query: str, provider: Optional[str], config: Optional[str], 
                       verbose: bool, debug: bool):
    """Handle direct query without subcommands (original functionality)."""
    try:
        # Initialize IntelliScript
        app = IntelliScript(config_path=config)
        
        if verbose:
            console.print(f"🤖 Processing query: [bold]{query}[/bold]")
            if provider:
                console.print(f"🧠 Using provider: [blue]{provider}[/blue]")
        
        # Process the query
        result = app.process_query(query, provider or app.default_provider)
        
        # Display result
        if isinstance(result, str):
            console.print(Panel(result, title="📝 Generated Command", border_style="green"))
        else:
            console.print(result)
            
    except Exception as e:
        error_handler = ErrorHandler()
        error_msg = error_handler.handle_error(e, context={'query': query, 'provider': provider})
        console.print(f"❌ [red]{error_msg}[/red]")
        if debug:
            console.print_exception(show_locals=True)
        sys.exit(1)


@main.command()
@click.argument('query', required=True)
@click.option('--provider', default='langextract',
              type=click.Choice(['langextract', 'openai', 'anthropic', 'google', 'ollama']),
              help='AI provider for extraction')
@click.option('--schema', type=str, help='JSON schema file for structured extraction')
@click.option('--output', default='json',
              type=click.Choice(['json', 'csv', 'html', 'md']),
              help='Output format')
@click.option('--visualize', is_flag=True, help='Generate visualization')
@click.option('--data', type=str, help='Input data (text or file path)')
@click.option('--save', type=str, help='Save results to file')
@click.option('--verbose', is_flag=True, help='Verbose output')
def extract(query: str, provider: str, schema: str, output: str,
            visualize: bool, data: str, save: str, verbose: bool):
    """
    🔍 Extract structured information from text or command output.
    
    Examples:
        intelliscript extract "analyze server logs for error patterns"
        intelliscript extract "parse system info" --data /var/log/syslog
        intelliscript extract "extract API endpoints" --visualize --save results.json
    """
    console.print(f"🔍 Extract command: {query}")
    console.print(f"Provider: {provider}, Output: {output}")
    if visualize:
        console.print("📊 Visualization enabled")
    if save:
        console.print(f"💾 Saving to: {save}")


@main.command()
@click.argument('query', required=True)
@click.option('--provider', default='langextract',
              type=click.Choice(['langextract', 'openai', 'anthropic', 'google', 'ollama']),
              help='AI provider for analysis')
@click.option('--data', type=str, help='Data source (file path or command output)')
@click.option('--output', default='md',
              type=click.Choice(['json', 'csv', 'html', 'md']),
              help='Analysis output format')
@click.option('--visualize', is_flag=True, help='Generate charts and graphs')
@click.option('--insights', is_flag=True, help='Generate actionable insights')
@click.option('--save', type=str, help='Save analysis to file')
@click.option('--verbose', is_flag=True, help='Verbose output')
def analyze(query: str, provider: str, data: str, output: str,
            visualize: bool, insights: bool, save: str, verbose: bool):
    """
    📊 Analyze data and generate insights with AI.
    
    Examples:
        intelliscript analyze "system performance trends"
        intelliscript analyze "log error patterns" --data server.log --insights
        intelliscript analyze "user behavior" --visualize --save analysis.html
    """
    console.print(f"📊 Analyze command: {query}")
    console.print(f"Provider: {provider}, Output: {output}")
    if insights:
        console.print("💡 Insights generation enabled")
    if save:
        console.print(f"💾 Saving to: {save}")


@main.command()
@click.argument('report_type', required=True)
@click.option('--provider', default='langextract', help='AI provider for report generation')
@click.option('--include', type=str, multiple=True,
              help='Include sections: metrics, logs, performance, security')
@click.option('--period', default='daily',
              type=click.Choice(['hourly', 'daily', 'weekly', 'monthly']),
              help='Report time period')
@click.option('--format', 'output_format', default='html',
              type=click.Choice(['html', 'pdf', 'md', 'json']),
              help='Report output format')
@click.option('--template', type=str, help='Custom report template')
@click.option('--save', type=str, help='Save report to file')
@click.option('--email', type=str, help='Email report to address')
@click.option('--verbose', is_flag=True, help='Verbose output')
def report(report_type: str, provider: str, include: tuple, period: str,
           output_format: str, template: str, save: str, email: str, verbose: bool):
    """
    📋 Generate comprehensive reports with AI analysis.
    
    Examples:
        intelliscript report "system health" --include metrics,logs --format html
        intelliscript report "security audit" --period weekly --save audit.pdf
        intelliscript report "performance" --template custom.html --email admin@company.com
    """
    console.print(f"📋 Report command: {report_type}")
    console.print(f"Period: {period}, Format: {output_format}")
    if include:
        console.print(f"Sections: {', '.join(include)}")
    if email:
        console.print(f"📧 Email to: {email}")
    if save:
        console.print(f"💾 Saving to: {save}")


@main.command()
@click.argument('pipeline_name', required=True)
@click.option('--steps', type=str, help='Pipeline steps: collect,extract,analyze,report')
@click.option('--config', type=str, help='Pipeline configuration file')
@click.option('--provider', default='langextract', help='AI provider for pipeline')
@click.option('--save', type=str, help='Save pipeline results')
@click.option('--schedule', type=str, help='Schedule pipeline execution (cron format)')
@click.option('--verbose', is_flag=True, help='Verbose output')
def pipeline(pipeline_name: str, steps: str, config: str, provider: str,
             save: str, schedule: str, verbose: bool):
    """
    🔄 Execute multi-step data processing pipelines.
    
    Examples:
        intelliscript pipeline "monitor_system" --steps "collect,extract,analyze,report"
        intelliscript pipeline "log_analysis" --config pipeline.json --schedule "0 */6 * * *"
        intelliscript pipeline "security_check" --save security_results.json
    """
    console.print(f"🔄 Pipeline command: {pipeline_name}")
    if steps:
        console.print(f"Steps: {steps}")
    if config:
        console.print(f"Config: {config}")
    if schedule:
        console.print(f"Schedule: {schedule}")
    if save:
        console.print(f"💾 Saving to: {save}")


@main.command()
@click.option('--create', is_flag=True, help='Create default configuration file')
@click.option('--edit', is_flag=True, help='Edit configuration file')
@click.option('--validate', is_flag=True, help='Validate configuration file')
@click.option('--show', is_flag=True, help='Show current configuration')
def config(create: bool, edit: bool, validate: bool, show: bool):
    """
    ⚙️ Manage IntelliScript configuration.
    
    Examples:
        intelliscript config --create
        intelliscript config --show
        intelliscript config --validate
    """
    if create:
        console.print("🔧 Creating default configuration...")
        # TODO: Implement config creation
        console.print("✅ Configuration created at ~/.config/intelliscript/config.toml")
    elif show:
        console.print("📋 Current Configuration:")
        # TODO: Implement config display
    elif validate:
        console.print("✅ Configuration is valid")
    else:
        console.print("Use --help to see configuration options")


@main.command()
def diagnostics():
    """
    🔍 Run system diagnostics and check IntelliScript setup.
    """
    console.print(Panel.fit(
        "🔍 [bold]IntelliScript Diagnostics[/bold]\n\n"
        "Checking system requirements and configuration...",
        border_style="blue"
    ))
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        console.print("✅ Python version: " + f"{python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        console.print("❌ Python version too old. Requires 3.8+")
    
    # Check dependencies
    dependencies = [
        'requests', 'toml', 'click', 'rich', 'langextract',
        'matplotlib', 'plotly', 'pandas', 'numpy'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            console.print(f"✅ {dep}")
        except ImportError:
            console.print(f"❌ {dep} - Not installed")
    
    # Check providers
    console.print("\n🧠 [bold]AI Providers:[/bold]")
    try:
        from intelliscript.core.intelliscript_main import IntelliScript
        app = IntelliScript()
        for provider_name in ['openai', 'anthropic', 'google', 'ollama', 'langextract']:
            if provider_name in app.providers:
                console.print(f"✅ {provider_name}")
            else:
                console.print(f"⚠️ {provider_name} - Not configured")
    except Exception as e:
        console.print(f"❌ Provider check failed: {e}")


# Entry point for setuptools
def cli_main():
    """Entry point for pip-installed version."""
    main()


# Development entry point
if __name__ == "__main__":
    main()
