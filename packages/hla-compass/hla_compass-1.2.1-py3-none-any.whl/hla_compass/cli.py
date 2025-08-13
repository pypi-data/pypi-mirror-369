"""
HLA-Compass CLI for module development
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.panel import Panel

from . import __version__
from .testing import ModuleTester
from .auth import Auth
from .config import Config

console = Console()

ALITHEA_BANNER = """
        [bold bright_magenta]█████╗[/bold bright_magenta] [bold bright_cyan]██╗[/bold bright_cyan]     [bold bright_green]██╗[/bold bright_green][bold bright_yellow]████████╗[/bold bright_yellow][bold bright_red]██╗  ██╗[/bold bright_red][bold bright_magenta]███████╗[/bold bright_magenta] [bold bright_cyan]█████╗[/bold bright_cyan]
       [bold bright_magenta]██╔══██╗[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]╚══██╔══╝[/bold bright_yellow][bold bright_red]██║  ██║[/bold bright_red][bold bright_magenta]██╔════╝[/bold bright_magenta][bold bright_cyan]██╔══██╗[/bold bright_cyan]
       [bold bright_magenta]███████║[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]███████║[/bold bright_red][bold bright_magenta]█████╗[/bold bright_magenta]  [bold bright_cyan]███████║[/bold bright_cyan]
       [bold bright_magenta]██╔══██║[/bold bright_magenta][bold bright_cyan]██║[/bold bright_cyan]     [bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]██╔══██║[/bold bright_red][bold bright_magenta]██╔══╝[/bold bright_magenta]  [bold bright_cyan]██╔══██║[/bold bright_cyan]
       [bold bright_magenta]██║  ██║[/bold bright_magenta][bold bright_cyan]███████╗[/bold bright_cyan][bold bright_green]██║[/bold bright_green][bold bright_yellow]   ██║[/bold bright_yellow]   [bold bright_red]██║  ██║[/bold bright_red][bold bright_magenta]███████╗[/bold bright_magenta][bold bright_cyan]██║  ██║[/bold bright_cyan]
       [bold bright_magenta]╚═╝  ╚═╝[/bold bright_magenta][bold bright_cyan]╚══════╝[/bold bright_cyan][bold bright_green]╚═╝[/bold bright_green][bold bright_yellow]   ╚═╝[/bold bright_yellow]   [bold bright_red]╚═╝  ╚═╝[/bold bright_red][bold bright_magenta]╚══════╝[/bold bright_magenta][bold bright_cyan]╚═╝  ╚═╝[/bold bright_cyan]

                  [bold bright_white]🧬  B I O I N F O R M A T I C S  🧬[/bold bright_white]
"""


def show_banner():
    """Display the Alithea banner with helpful context"""
    console.print(ALITHEA_BANNER)
    env = Config.get_environment()
    api = Config.get_api_endpoint()
    
    # Color-coded environment indicator
    env_color = {
        'dev': 'green',
        'staging': 'yellow', 
        'prod': 'red'
    }.get(env, 'cyan')
    
    info = (
        f"[bold bright_white]HLA-Compass Platform SDK[/bold bright_white]\n"
        f"[dim white]Version[/dim white] [bold bright_cyan]{__version__}[/bold bright_cyan]   "
        f"[dim white]Environment[/dim white] [bold {env_color}]{env.upper()}[/bold {env_color}]\n"
        f"[dim white]API Endpoint[/dim white] [bright_blue]{api}[/bright_blue]\n"
        f"[bright_magenta]✨[/bright_magenta] [italic]Immuno-Peptidomics • Module Development • AI-Powered Analysis[/italic] [bright_magenta]✨[/bright_magenta]"
    )
    console.print(Panel.fit(
        info, 
        title="[bold bright_cyan]🔬 Alithea Bio[/bold bright_cyan]", 
        subtitle="[bright_blue]https://alithea.bio[/bright_blue]", 
        border_style="bright_cyan",
        padding=(1, 2)
    ))


@click.group()
@click.version_option(version=__version__)
def cli():
    """HLA-Compass SDK - Module development tools"""
    pass


@cli.command()
@click.argument('name')
@click.option('--template', default='minimal', help='Module template to use (default: minimal)')
@click.option('--type', 'module_type', type=click.Choice(['no-ui', 'with-ui']), 
              default=None, help='Module type (auto-detected from template)')
@click.option('--compute', type=click.Choice(['lambda', 'fargate', 'sagemaker']), 
              default='lambda', help='Compute type')
@click.option('--no-banner', is_flag=True, help='Skip the Alithea banner display')
@click.option('--yes', is_flag=True, help='Assume yes for all prompts (non-interactive mode)')
def init(name: str, template: str, module_type: str | None, compute: str, no_banner: bool, yes: bool):
    """Create a new HLA-Compass module
    
    Examples:
        hla-compass init my-module                    # Minimal template
        hla-compass init my-module --template peptide-analyzer  # Ready-to-run
        hla-compass init my-module --template base-module --type with-ui
    """
    # Show the beautiful Alithea banner only during module creation
    if not no_banner:
        show_banner()
    
    # Auto-detect module type from template if not specified
    template_types = {
        'minimal': 'no-ui',
        'base-module': 'with-ui',
        'peptide-analyzer': 'with-ui'
    }
    
    if module_type is None:
        module_type = template_types.get(template, 'no-ui')
    
    console.print(f"[bold green]🧬 Creating HLA-Compass Module: [white]{name}[/white] 🧬[/bold green]")
    console.print(f"[dim]Template: {template} • Type: {module_type} • Compute: {compute}[/dim]\n")
    
    # Check if directory already exists
    module_dir = Path(name)
    if module_dir.exists():
        if not yes and not Confirm.ask(f"Directory '{name}' already exists. Continue?"):
            return
    
    # Find template directory - first check if we're in development mode
    pkg_templates_dir = Path(__file__).parent / "templates" / template
    repo_templates_dir = Path(__file__).parent.parent.parent.parent / "modules" / "templates" / template
    
    if pkg_templates_dir.exists():
        # Found in package (installed via pip)
        template_dir = pkg_templates_dir
    elif repo_templates_dir.exists():
        # Found in repository (development mode)
        template_dir = repo_templates_dir  
    else:
        # List available templates for user
        available_templates = []
        pkg_templates_base = Path(__file__).parent / "templates"
        if pkg_templates_base.exists():
            available_templates.extend([d.name for d in pkg_templates_base.iterdir() if d.is_dir()])
        
        repo_templates_base = Path(__file__).parent.parent.parent.parent / "modules" / "templates"
        if repo_templates_base.exists():
            repo_templates = [d.name for d in repo_templates_base.iterdir() if d.is_dir()]
            available_templates.extend([t for t in repo_templates if t not in available_templates])
        
        console.print(f"[red]Template '{template}' not found[/red]")
        if available_templates:
            console.print(f"[yellow]Available templates: {', '.join(available_templates)}[/yellow]")
        else:
            console.print("[yellow]No templates found. This may be a packaging issue.[/yellow]")
        return
    
    # Copy template
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Copying template files...", total=None)
        
        shutil.copytree(template_dir, module_dir, dirs_exist_ok=True)
        
        progress.update(task, description="Updating manifest...")
        
        # Update manifest.json
        manifest_path = module_dir / "manifest.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        manifest['name'] = name
        manifest['type'] = module_type
        manifest['computeType'] = compute
        # Use environment variables or defaults to avoid hanging prompts
        manifest['author']['name'] = os.environ.get('HLA_AUTHOR_NAME', os.environ.get('USER', 'Unknown'))
        manifest['author']['email'] = os.environ.get('HLA_AUTHOR_EMAIL', 'developer@example.com')
        manifest['author']['organization'] = os.environ.get('HLA_AUTHOR_ORG', 'Independent')
        manifest['description'] = os.environ.get('HLA_MODULE_DESC', f"HLA-Compass module: {name}")
        
        # Show what was set
        console.print(f"  Author: {manifest['author']['name']}")
        console.print(f"  Email: {manifest['author']['email']}")
        console.print(f"  Organization: {manifest['author']['organization']}")
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Remove frontend directory if no-ui
        if module_type == 'no-ui':
            frontend_dir = module_dir / "frontend"
            if frontend_dir.exists():
                shutil.rmtree(frontend_dir)
        
        # Create virtual environment only if not already in one
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            progress.update(task, description="Skipping venv (already in virtual environment)...")
        else:
            progress.update(task, description="Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', str(module_dir / 'venv')], 
                          capture_output=True)
        
        progress.update(task, description="Module created!", completed=True)
    
    # Display comprehensive success message with full workflow
    console.print(Panel.fit(
        f"[green]✓ Module '{name}' created successfully![/green]\n\n"
        f"[bold]Quick Start:[/bold]\n"
        f"1. cd {name}\n"
        f"2. pip install -r backend/requirements.txt  # Install dependencies\n"
        f"3. hla-compass test                         # Test against real API\n\n"
        f"[bold]Development Workflow:[/bold]\n"
        f"• Edit backend/main.py to implement your logic\n"
        f"• Add test data to examples/sample_input.json\n"
        f"• Document your module in docs/README.md\n"
        f"• Test iteratively: hla-compass test --input examples/sample_input.json\n\n"
        f"[bold]Sign & Deploy (Coming Soon):[/bold]\n"
        f"• Sign: hla-compass sign dist/{name}-1.0.0.zip\n"
        f"• Deploy: hla-compass deploy dist/{name}-1.0.0.zip --env dev\n"
        f"• List: hla-compass list\n\n"
        f"[bold]Help & Documentation:[/bold]\n"
        f"• Module docs: https://docs.hla-compass.com/modules\n"
        f"• Get help: hla-compass --help",
        title="Module Created - Development Guide",
        width=100
    ))


@cli.command()
@click.option('--manifest', default='manifest.json', help='Path to manifest.json')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON for automation')
def validate(manifest: str, output_json: bool):
    """Validate module structure and manifest"""
    if not output_json:
        console.print("[bold]Validating module...[/bold]")
    
    errors = []
    warnings = []
    
    # Check manifest exists
    manifest_path = Path(manifest)
    if not manifest_path.exists():
        if output_json:
            result = {"valid": False, "errors": ["manifest.json not found"], "warnings": []}
            print(json.dumps(result))
        else:
            console.print("[red]✗ manifest.json not found[/red]")
        sys.exit(1)
    
    # Load and validate manifest
    try:
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
    except json.JSONDecodeError as e:
        if output_json:
            result = {"valid": False, "errors": [f"Invalid JSON in manifest.json: {e}"], "warnings": []}
            print(json.dumps(result))
        else:
            console.print(f"[red]✗ Invalid JSON in manifest.json: {e}[/red]")
        sys.exit(1)
    
    # Required fields
    required_fields = ['name', 'version', 'type', 'computeType', 'author', 'inputs', 'outputs']
    for field in required_fields:
        if field not in manifest_data:
            errors.append(f"Missing required field: {field}")
    
    # Check backend structure
    module_dir = manifest_path.parent
    backend_dir = module_dir / "backend"
    
    if not backend_dir.exists():
        errors.append("backend/ directory not found")
    else:
        if not (backend_dir / "main.py").exists():
            errors.append("backend/main.py not found")
        if not (backend_dir / "requirements.txt").exists():
            warnings.append("backend/requirements.txt not found")
    
    # Check frontend for with-ui modules
    if manifest_data.get('type') == 'with-ui':
        frontend_dir = module_dir / "frontend"
        if not frontend_dir.exists():
            errors.append("frontend/ directory required for with-ui modules")
        elif not (frontend_dir / "index.tsx").exists():
            errors.append("frontend/index.tsx not found")
    
    # Display results
    if output_json:
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)
    else:
        if errors:
            console.print("[red]✗ Validation failed with errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            console.print("\n[yellow]Fix the errors above, then run 'hla-compass validate' again[/yellow]")
            sys.exit(1)
        else:
            console.print("[green]✓ Module structure valid[/green]")
            if warnings:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in warnings:
                    console.print(f"  • {warning}")
            console.print("\n[bold]Ready for next steps:[/bold]")
            console.print("  • Test: hla-compass test")
            console.print("  • Sign: hla-compass sign dist/*.zip (coming soon)")
            console.print("  • Deploy: hla-compass deploy dist/*.zip --env dev (coming soon)")
            sys.exit(0)


@cli.command()
@click.option('--input', 'input_file', help='Input JSON file')
@click.option('--local', is_flag=True, default=False, help='Test locally without API')
@click.option('--remote', is_flag=True, default=False, help='Test against real API')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON for automation')
def test(input_file: str | None, local: bool, remote: bool, verbose: bool, output_json: bool):
    """Test module locally or against real API"""
    
    # Determine test mode
    if remote and local:
        console.print("[red]Cannot use both --local and --remote flags[/red]")
        return
    
    # Default to remote if authenticated, otherwise local
    auth = Auth()
    if not remote and not local:
        remote = auth.is_authenticated()
        local = not remote
    
    if remote:
        if not output_json:
            console.print("[bold]Testing module with API authentication context...[/bold]")
        if not auth.is_authenticated():
            if output_json:
                result = {"ok": False, "status": "error", "error": {"type": "auth_error", "message": "Not authenticated"}}
                print(json.dumps(result))
            else:
                console.print("[yellow]⚠️  Not authenticated. Please login first.[/yellow]")
                console.print("Run: hla-compass auth login")
            sys.exit(1)
        if not output_json:
            console.print("[blue]ℹ️  Note: Module executes locally with API access. Remote execution coming soon.[/blue]")
    else:
        if not output_json:
            console.print("[bold]Testing module locally (no API access)...[/bold]")
    
    # Load test input
    if input_file:
        with open(input_file, 'r') as f:
            test_input = json.load(f)
    else:
        # Try to load example input
        example_path = Path("examples/sample_input.json")
        if example_path.exists():
            with open(example_path, 'r') as f:
                test_input = json.load(f)
        else:
            test_input = {}
            if not output_json:
                console.print("[yellow]No input file provided, using empty input[/yellow]")
    
    try:
        if remote:
            # Test using real API
            from .client import APIClient
            
            # Load manifest to get module name
            manifest_path = Path("manifest.json")
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json.load(f)
                    module_name = manifest.get('name', 'test-module')
            else:
                module_name = 'test-module'
            
            console.print(f"\n[blue]Executing module '{module_name}' via API...[/blue]")
            
            # For now, test by directly importing and running the module with API client
            # In future, this would execute via API Gateway
            import sys
            sys.path.insert(0, 'backend')
            from main import lambda_handler
            
            # Create event for Lambda handler
            event = {
                'parameters': test_input,
                'job_id': 'test-' + str(Path.cwd().name),
                'user_id': 'test-user',
                'organization_id': 'test-org'
            }
            
            # Mock context
            class Context:
                request_id = 'test-request'
            
            result = lambda_handler(event, Context())
            
        else:
            # Test locally
            tester = ModuleTester()
            if not output_json:
                console.print("\n[blue]Running local test...[/blue]")
            
            # Create mock context
            context = {
                'job_id': 'local-test',
                'user_id': 'local-user',
                'organization_id': 'local-org'
            }
            
            result = tester.test_local("backend/main.py", test_input, context)
        
        # Get module info for metadata
        module_name = 'unknown'
        module_version = '1.0.0'
        manifest_path = Path("manifest.json")
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
                module_name = manifest.get('name', 'unknown')
                module_version = manifest.get('version', '1.0.0')
        
        # Display results
        if output_json:
            # JSON output for automation
            import time
            from datetime import datetime
            
            if result.get('status') == 'success':
                json_result = {
                    "ok": True,
                    "status": "success",
                    "summary": result.get('summary', {}),
                    "metadata": {
                        "module": module_name,
                        "version": module_version,
                        "execution_time": datetime.now().isoformat()
                    }
                }
            else:
                error_info = result.get('error', {})
                json_result = {
                    "ok": False,
                    "status": "error",
                    "error": {
                        "type": error_info.get('type', 'execution_error'),
                        "message": error_info.get('message', 'Module execution failed')
                    },
                    "metadata": {
                        "module": module_name,
                        "version": module_version
                    }
                }
            
            print(json.dumps(json_result, indent=2))
            sys.exit(0 if json_result["ok"] else 1)
        else:
            # Human-readable output
            if result.get('status') == 'success':
                console.print("[green]✓ Test passed[/green]")
                if verbose:
                    console.print("\nTest Result:")
                    console.print(Syntax(
                        json.dumps(result, indent=2),
                        "json",
                        theme="monokai"
                    ))
                else:
                    # Show summary if available
                    if 'summary' in result:
                        console.print("\n[bold]Summary:[/bold]")
                        for key, value in result['summary'].items():
                            console.print(f"  {key}: {value}")
                sys.exit(0)
            else:
                console.print("[red]✗ Test failed[/red]")
                if 'error' in result:
                    console.print(f"Error: {result['error'].get('message', 'Unknown error')}")
                sys.exit(1)
            
    except Exception as e:
        if output_json:
            json_result = {
                "ok": False,
                "status": "error",
                "error": {
                    "type": "exception",
                    "message": str(e)
                },
                "metadata": {
                    "module": module_name if 'module_name' in locals() else 'unknown',
                    "version": module_version if 'module_version' in locals() else '1.0.0'
                }
            }
            print(json.dumps(json_result, indent=2))
        else:
            console.print(f"[red]Test failed with error: {e}[/red]")
            if verbose:
                import traceback
                console.print(traceback.format_exc())
        sys.exit(1)


@cli.group()
def auth():
    """Authentication commands"""
    pass


@auth.command()
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), 
              default='dev', help='Environment to login to')
def login(env: str):
    """Login to HLA-Compass platform"""
    console.print(f"[bold]Logging in to {env} environment...[/bold]")
    
    email = Prompt.ask("Email")
    password = Prompt.ask("Password", password=True)
    
    auth = Auth()
    
    try:
        success = auth.login(email, password, env)
        if success:
            console.print("[green]✓ Login successful![/green]")
            console.print(f"Environment: {env}")
            console.print("You can now test modules with: hla-compass test")
        else:
            console.print("[red]✗ Login failed[/red]")
            console.print("Please check your credentials and try again")
    except Exception as e:
        console.print(f"[red]Login error: {e}[/red]")


@auth.command()
def logout():
    """Logout from HLA-Compass platform"""
    console.print("[bold]Logging out...[/bold]")
    
    auth = Auth()
    auth.logout()
    
    console.print("[green]✓ Logged out successfully[/green]")


@auth.command()
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), 
              default='dev', help='Environment to register for')
def register(env: str):
    """Register as a developer (temporary credentials will be provided)"""
    console.print(f"[bold]Developer Registration for {env} environment[/bold]")
    console.print("[blue]ℹ️  Note: This creates a developer account with temporary credentials.[/blue]")
    
    email = Prompt.ask("Email")
    name = Prompt.ask("Full Name")
    organization = Prompt.ask("Organization", default="Independent")
    
    auth = Auth()
    
    try:
        # Note: auth.register ignores password and uses developer_register internally
        success = auth.register(email, None, name, organization, env)
        if success:
            console.print("[green]✓ Registration successful![/green]")
            console.print("Temporary credentials have been sent to your email.")
            console.print("You can login with: hla-compass auth login")
            sys.exit(0)
        else:
            console.print("[red]✗ Registration failed[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Registration error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('package_file')
def sign(package_file: str):
    """Sign a module package"""
    console.print("[bold blue]Module Signing[/bold blue]")
    console.print("[yellow]📝 Coming soon - Module signing will be available in the next release[/yellow]\n")
    
    console.print("This feature will:")
    console.print("• Cryptographically sign your module packages")
    console.print("• Ensure module integrity and authenticity")
    console.print("• Enable secure deployment to the platform\n")
    
    console.print("For now, you can still test and develop modules without signing.")


@cli.command()
@click.argument('package_file')
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), 
              default='dev', help='Target environment')
def deploy(package_file: str, env: str):
    """Deploy module to HLA-Compass platform"""
    console.print(f"[bold blue]Module Deployment to {env}[/bold blue]")
    console.print("[yellow]🚀 Coming soon - Module deployment will be available in the next release[/yellow]\n")
    
    console.print("This feature will:")
    console.print("• Upload your signed module package to the platform")
    console.print("• Register the module in the module registry")
    console.print("• Make it available for execution\n")
    
    console.print("For now, you can test modules locally with: hla-compass test")


@cli.command()
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), 
              default='dev', help='Environment to list from')
def list(env: str):
    """List deployed modules"""
    console.print(f"[bold blue]Module Listing for {env}[/bold blue]")
    console.print("[yellow]📋 Coming soon - Module listing will be available in the next release[/yellow]\n")
    
    console.print("This feature will:")
    console.print("• Show all your deployed modules")
    console.print("• Display module status and versions")
    console.print("• Provide deployment history\n")
    
    console.print("For now, you can manage modules through the web interface.")


def main():
    """Main entry point for CLI"""
    cli()


if __name__ == '__main__':
    main()