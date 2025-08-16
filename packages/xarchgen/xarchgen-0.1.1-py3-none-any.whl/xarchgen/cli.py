#!/usr/bin/env python3
"""
CLI interface for xarchgen package
"""

import click
import sys
import os
import zipfile
import io
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from .database import DatabaseSchemaReader
from .generators import create_generator
from .utils import extract_tables_by_schema

console = Console()

@click.group()
@click.version_option(version="0.1.0", prog_name="xarchgen")
def cli():
    """xarchgen - Generate Clean Architecture backend applications from PostgreSQL schemas"""
    pass

@cli.command()
@click.argument('framework', type=click.Choice(['fastapi', 'dotnet'], case_sensitive=False))
@click.option('--database', '-d', required=True, help='PostgreSQL connection string')
@click.option('--output', '-o', default='./generated-app', help='Output directory for generated code')
@click.option('--name', '-n', default='GeneratedApp', help='Application/Solution name')
@click.option('--group-by', '-g', type=click.Choice(['schema', 'prefix', 'none']), default='schema',
              help='Table grouping strategy: schema (by database schema), prefix (by table prefix), none (all in General)')
@click.option('--zip', '-z', is_flag=True, help='Generate a ZIP file instead of directory')
@click.option('--tables', '-t', multiple=True, help='Specific tables to include (default: all)')
@click.option('--exclude', '-e', multiple=True, help='Tables to exclude')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def create(framework, database, output, name, group_by, zip, tables, exclude, verbose):
    """
    Create a new backend application from PostgreSQL database schema.
    
    Examples:
    
        xarchgen create fastapi --database "postgresql://user:pass@localhost/db"
        
        xarchgen create dotnet -d "postgresql://..." -n MyApp -o ./my-app
        
        xarchgen create fastapi -d "postgresql://..." --group-by prefix --zip
    """
    
    # Display header
    console.print(Panel.fit(
        f"[bold cyan]xarchgen[/bold cyan] - Generating {framework.upper()} Application",
        border_style="cyan"
    ))
    
    try:
        # Connect to database
        with console.status("[bold green]Connecting to database...") as status:
            reader = DatabaseSchemaReader(database)
            schema = reader.read_schema()
            
        console.print(f"✅ Connected successfully! Found [bold]{len(schema['tables'])}[/bold] tables")
        
        # Filter tables if specified
        if tables:
            schema['tables'] = [t for t in schema['tables'] if t['name'] in tables]
            console.print(f"📋 Filtered to {len(schema['tables'])} specified tables")
        
        # Exclude tables if specified
        if exclude:
            schema['tables'] = [t for t in schema['tables'] if t['name'] not in exclude]
            console.print(f"🚫 Excluded tables, {len(schema['tables'])} remaining")
        
        # Group tables based on strategy
        table_groups = group_tables(schema['tables'], group_by, verbose)
        
        # Display groups
        if verbose:
            display_table_groups(table_groups)
        
        # Generate application
        console.print(f"\n🔨 Generating {framework.upper()} application...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            
            task = progress.add_task("[cyan]Generating code...", total=100)
            
            def progress_callback(percent, message):
                progress.update(task, completed=percent, description=f"[cyan]{message}")
            
            generator = create_generator(framework)
            files = generator.generate_application(
                schema,
                connection_string=database,
                table_groups=table_groups,
                solution_name=name,
                progress_callback=progress_callback if verbose else None
            )
            
            progress.update(task, completed=100, description="[green]Generation complete!")
        
        # Save files
        if zip:
            # Create ZIP file
            zip_path = Path(output).with_suffix('.zip')
            save_as_zip(files, zip_path)
            console.print(f"\n✨ [bold green]Success![/bold green] Generated ZIP file: [cyan]{zip_path}[/cyan]")
        else:
            # Save to directory
            save_to_directory(files, output)
            console.print(f"\n✨ [bold green]Success![/bold green] Generated application in: [cyan]{output}[/cyan]")
        
        # Display next steps
        display_next_steps(framework, output, zip)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        if verbose:
            console.print_exception()
        sys.exit(1)

@cli.command()
@click.option('--database', '-d', required=True, help='PostgreSQL connection string')
def inspect(database):
    """
    Inspect database schema and display table information.
    
    Example:
        xarchgen inspect --database "postgresql://user:pass@localhost/db"
    """
    console.print(Panel.fit(
        "[bold cyan]Database Schema Inspector[/bold cyan]",
        border_style="cyan"
    ))
    
    try:
        with console.status("[bold green]Connecting to database...") as status:
            reader = DatabaseSchemaReader(database)
            schema = reader.read_schema()
        
        console.print(f"✅ Connected successfully!\n")
        
        # Display summary
        table = Table(title="Database Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Count", justify="right")
        
        table.add_row("Tables", str(len(schema['tables'])))
        total_columns = sum(len(t['columns']) for t in schema['tables'])
        table.add_row("Total Columns", str(total_columns))
        
        # Count tables by schema
        schemas = {}
        for t in schema['tables']:
            schema_name = t.get('schema', 'public')
            schemas[schema_name] = schemas.get(schema_name, 0) + 1
        
        for schema_name, count in schemas.items():
            table.add_row(f"Schema: {schema_name}", str(count))
        
        console.print(table)
        console.print()
        
        # Display tables
        table = Table(title="Tables", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Schema", style="cyan")
        table.add_column("Table Name", style="green")
        table.add_column("Columns", justify="right")
        table.add_column("Primary Key", style="yellow")
        
        for idx, t in enumerate(schema['tables'], 1):
            pk = next((col['name'] for col in t['columns'] if col.get('is_primary_key')), 'none')
            table.add_row(
                str(idx),
                t.get('schema', 'public'),
                t['name'],
                str(len(t['columns'])),
                pk
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

def group_tables(tables, strategy='schema', verbose=False):
    """Group tables based on the specified strategy"""
    
    if strategy == 'none':
        # All tables in General group
        return {'General': [t['name'] for t in tables]}
    
    elif strategy == 'schema':
        # Group by database schema
        groups = {}
        for table in tables:
            schema = table.get('schema', 'public')
            group_name = schema.replace('_', '').title() if schema != 'public' else 'General'
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(table['name'])
        return groups
    
    elif strategy == 'prefix':
        # Group by common prefixes
        groups = {}
        prefixes = {}
        
        # Find common prefixes (at least 2 tables with same prefix)
        for table in tables:
            parts = table['name'].split('_')
            if len(parts) > 1:
                prefix = parts[0]
                if prefix not in prefixes:
                    prefixes[prefix] = []
                prefixes[prefix].append(table['name'])
        
        # Create groups from prefixes with multiple tables
        for prefix, table_list in prefixes.items():
            if len(table_list) > 1:
                group_name = prefix.title()
                groups[group_name] = table_list
        
        # Put remaining tables in General
        grouped_tables = set()
        for table_list in groups.values():
            grouped_tables.update(table_list)
        
        ungrouped = [t['name'] for t in tables if t['name'] not in grouped_tables]
        if ungrouped:
            groups['General'] = ungrouped
        
        return groups if groups else {'General': [t['name'] for t in tables]}
    
    return {'General': [t['name'] for t in tables]}

def display_table_groups(groups):
    """Display table groups in a nice format"""
    table = Table(title="Table Groups", show_header=True, header_style="bold magenta")
    table.add_column("Group", style="cyan", no_wrap=True)
    table.add_column("Tables", style="green")
    table.add_column("Count", justify="right")
    
    for group, tables in groups.items():
        table_list = ", ".join(tables[:3])
        if len(tables) > 3:
            table_list += f" ... (+{len(tables)-3} more)"
        table.add_row(group, table_list, str(len(tables)))
    
    console.print(table)

def save_to_directory(files: Dict[str, str], output_dir: str):
    """Save generated files to directory"""
    base_path = Path(output_dir)
    for filepath, content in files.items():
        full_path = base_path / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

def save_as_zip(files: Dict[str, str], zip_path: Path):
    """Save generated files as ZIP"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filepath, content in files.items():
            zip_file.writestr(filepath, content)
    
    zip_path.write_bytes(zip_buffer.getvalue())

def display_next_steps(framework: str, output: str, is_zip: bool):
    """Display next steps after generation"""
    
    if framework.lower() == 'fastapi':
        steps = [
            "Extract the ZIP file" if is_zip else f"Navigate to {output}",
            "Copy `.env.example` to `.env` and configure database connection",
            "Run `uv sync` or `pip install -r requirements.txt`",
            "Run `uv run alembic upgrade head` for database migrations",
            "Run `uv run uvicorn src.api.main:app --reload` to start the server"
        ]
    else:  # dotnet
        steps = [
            "Extract the ZIP file" if is_zip else f"Navigate to {output}",
            "Update `appsettings.json` with your connection string",
            "Run `dotnet restore` to restore dependencies",
            "Run `dotnet build` to build the solution",
            "Run `dotnet run --project src/WebApi` to start the server"
        ]
    
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    for i, step in enumerate(steps, 1):
        console.print(f"  {i}. {step}")
    
    console.print(f"\n📚 API documentation will be available at:")
    if framework.lower() == 'fastapi':
        console.print(f"   http://localhost:8000/docs")
    else:
        console.print(f"   https://localhost:5001/swagger")

def main():
    """Main entry point for the CLI"""
    cli()

if __name__ == '__main__':
    main()