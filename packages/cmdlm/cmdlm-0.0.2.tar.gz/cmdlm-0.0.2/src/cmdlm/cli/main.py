import logging
import warnings

# Force suppress all warnings
warnings.simplefilter("ignore")
warnings.filterwarnings("ignore", message=".*Valid config keys have changed in V2.*")
warnings.simplefilter("ignore", DeprecationWarning)
warnings.simplefilter("ignore", UserWarning)
warnings.simplefilter("ignore", RuntimeWarning)
warnings.simplefilter("ignore", PendingDeprecationWarning)

# Disable all logging except critical - target specific loggers
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logging.getLogger("litellm").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)

import sys

import click
from rich.console import Console
from rich.table import Table

from ..chat.control import CommandHandler
from ..config.manager import ConfigManager
from ..config.providers import ProviderType
from ..conversation.handler import ConversationHandler
from .setup import initial_setup

console = Console()


def get_input_from_pipe() -> str:
    """Read input from pipe if available"""
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""


def process_input(args: tuple, piped_input: str = "") -> str:
    """Process input from arguments and/or pipe"""
    if piped_input:
        return piped_input
    elif args:
        # Join args with spaces and preserve newlines
        return " ".join(args)
    return ""


@click.command()
@click.argument("prompt", nargs=-1, required=False)
@click.option("--provider", help="Use specific provider credentials")
@click.option("--model", help="Use specific model from the provider")
@click.option("--configure", is_flag=True, help="Configure a new provider")
@click.option("--reset", is_flag=True, help="Reset all configuration")
@click.option("--reset-provider", help="Reset configuration for specific provider")
@click.option("--set-default", help="Set default provider and model")
@click.option("--status", is_flag=True, help="Show configuration status")
@click.option(
    "--debug", is_flag=True, help="Show processed commands without sending to LLM"
)
@click.option(
    "--tools",
    help="Enable tools (comma-separated list of tool names, or 'all' for all tools)",
)
@click.option(
    "--tools-no-approval",
    is_flag=True,
    help="Skip human approval before executing tools (tools require approval by default)",
)
@click.option(
    "--system-prompt",
    help="Custom system prompt to use instead of default (can be prompt name or text)",
)
@click.option(
    "--system-prompt-file",
    help="Path to file containing custom system prompt",
)
@click.option(
    "--prompts",
    type=click.Choice(
        ["list", "edit", "create", "delete", "show"], case_sensitive=False
    ),
    help="Manage system prompts: list, edit, create, delete, or show",
)
@click.option(
    "--raw",
    is_flag=True,
    help="Disable markdown rendering and show raw text output",
)
@click.option(
    "--env-vars",
    type=click.Choice(["list", "set", "remove", "clear"], case_sensitive=False),
    help="Manage global environment variables: list, set, remove, or clear",
)
def cli(
    prompt,
    provider,
    model,
    configure,
    reset,
    reset_provider,
    set_default,
    status,
    debug,
    tools,
    tools_no_approval,
    system_prompt,
    system_prompt_file,
    prompts,
    raw,
    env_vars,
):
    """cmdlm - Command and use langauge models with ease from the command line"""
    config_manager = ConfigManager()

    # Handle configuration commands
    if configure:
        initial_setup()
        return

    # chat mode
    if prompt and prompt[0] == "chat":
        # Extract initial message from prompt tuple (everything after "chat")
        initial_message = " ".join(prompt[1:]) if len(prompt) > 1 else None

        try:
            # Use the traditional Rich interface
            handler = CommandHandler(
                provider=provider,
                model=model,
                debug=debug,
                tools=tools,
                tools_approval=not tools_no_approval,
                system_prompt=system_prompt,
                system_prompt_file=system_prompt_file,
                raw=raw,
            )
            handler.start_session(initial_message=initial_message)

        except Exception as e:
            # Use Rich's escape function to escape any markup in the error message
            from rich.markup import escape

            error_message = escape(str(e))
            console.print(
                f"\nFailed to process request: {error_message}", style="bold red"
            )
            raise click.Abort()

        return

    if reset:
        if click.confirm("Are you sure you want to reset all configuration?"):
            config_manager.reset_all()
            console.print(
                "✨ All configuration reset successfully.", style="bold green"
            )
        return

    if reset_provider:
        try:
            provider_type = ProviderType(reset_provider)
            if click.confirm(f"Are you sure you want to reset {reset_provider}?"):
                config_manager.reset_provider(provider_type)
                console.print(
                    f"✨ {reset_provider} configuration reset successfully.",
                    style="bold green",
                )
        except ValueError:
            # Check if this is a custom provider
            providers = config_manager.get_configured_providers()
            other_config = providers.get(ProviderType.OTHER, {})
            if other_config and other_config.get("provider_name") == reset_provider:
                if click.confirm(f"Are you sure you want to reset {reset_provider}?"):
                    config_manager.reset_provider(ProviderType.OTHER)
                    console.print(
                        f"✨ {reset_provider} configuration reset successfully.",
                        style="bold green",
                    )
            else:
                console.print(f"Invalid provider: {reset_provider}", style="bold red")
        return

    if set_default:
        try:
            providers = config_manager.get_configured_providers()
            provider_found = False
            provider_type = None

            # First try direct enum match
            try:
                provider_type = ProviderType(set_default)
                provider_found = True
            except ValueError:
                # Not a direct enum match, check other possibilities
                pass

            # Check if it's a custom (OTHER) provider
            if not provider_found:
                other_config = providers.get(ProviderType.OTHER, {})
                if other_config and other_config.get("provider_name") == set_default:
                    provider_type = ProviderType.OTHER
                    provider_found = True

            # Check if it matches any provider display name
            if not provider_found:
                for p_type, config in providers.items():
                    display_name = config_manager.get_provider_display_name(
                        p_type, config
                    ).lower()
                    if set_default.lower() == display_name:
                        provider_type = p_type
                        provider_found = True
                        break

            if not provider_found:
                console.print(
                    f"Provider '{set_default}' is not configured", style="bold red"
                )
                return

            if provider_type not in providers:
                console.print(
                    f"Provider '{set_default}' is not configured", style="bold red"
                )
                return

            # Get available models for this provider
            models = config_manager.get_provider_models(provider_type)

            if models:
                console.print("\nAvailable models for this provider:")
                for i, model_name in enumerate(models, 1):
                    console.print(f"  {i}. {model_name}")

                model_choice = click.prompt(
                    "Select model number or enter model name", default="1"
                )

                # Convert choice to model name if it's a number
                try:
                    choice_idx = int(model_choice) - 1
                    if 0 <= choice_idx < len(models):
                        model_name = models[choice_idx]
                    else:
                        model_name = model_choice
                except ValueError:
                    model_name = model_choice
            else:
                # Let user select a new default model
                model_name = click.prompt(
                    "Enter the default model name for this provider",
                    default=providers[provider_type]["default_model"],
                )

            config_manager.set_default_provider(provider_type, model_name)
            display_name = config_manager.get_provider_display_name(
                provider_type, providers[provider_type]
            )
            console.print(
                f"✨ Default provider set to {display_name} with model {model_name}",
                style="bold green",
            )
        except Exception as e:
            console.print(f"Error setting default provider: {str(e)}", style="bold red")
        return

    if status:
        show_status()
        return

    if prompts:
        handle_prompts_command(prompts)
        return

    if env_vars:
        handle_env_vars_command(env_vars, config_manager)
        return

    # Check if configuration exists
    if not config_manager.get_configured_providers():
        console.print(
            "\n⚠️  No providers configured. Starting initial setup...", style="yellow"
        )
        initial_setup()
        return

    # Handle chat/prompt
    piped_input = get_input_from_pipe()
    prompt_text = process_input(prompt, piped_input)

    # Check for empty or whitespace-only input
    if prompt_text and prompt_text.strip():
        try:
            if provider and provider not in [p.value for p in ProviderType]:
                providers = config_manager.get_configured_providers()
                other_config = providers.get(ProviderType.OTHER, {})
                if other_config and other_config.get("provider_name") == provider:
                    provider = "other"  # Use the internal provider type

            handler = ConversationHandler(console, debug=debug, raw=raw)

            # Enable tools if specified
            if tools:
                if tools.lower() == "all":
                    handler.enable_tools(require_approval=not tools_no_approval)
                else:
                    tool_list = [name.strip() for name in tools.split(",")]
                    handler.enable_tools(
                        tool_names=tool_list, require_approval=not tools_no_approval
                    )

            # Handle system prompt if provided
            resolved_system_prompt = None
            if system_prompt or system_prompt_file:
                from ..utils.prompts import PromptsManager

                try:
                    resolved_system_prompt = PromptsManager.resolve_system_prompt(
                        system_prompt, system_prompt_file
                    )
                except Exception as e:
                    console.print(
                        f"Error with system prompt: {str(e)}", style="bold red"
                    )
                    raise click.Abort()

            handler.handle_prompt(
                prompt_text,
                provider=provider,
                model=model,
                system_prompt=resolved_system_prompt,
            )
        except Exception as e:
            from rich.markup import escape

            error_message = escape(str(e))
            console.print(
                f"\nFailed to process request: {error_message}", style="bold red"
            )
            raise click.Abort()
    elif prompt_text is not None and not prompt_text.strip():
        # Handle case where user provided empty input (from piped input or arguments)
        console.print(
            "No input provided. Use --help for usage information.", style="yellow"
        )
    else:
        show_status()


def show_status():
    """Show current configuration status"""
    config_manager = ConfigManager()
    default_provider, _ = config_manager.get_default_provider()
    providers = config_manager.get_configured_providers()

    table = Table(title="Configured Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Models", style="green")
    table.add_column("Default Model", style="yellow")
    table.add_column("Status", style="yellow")

    for provider, config in providers.items():
        display_name = config_manager.get_provider_display_name(provider, config)

        # Get all models for this provider
        models = config_manager.get_provider_models(provider)

        # Strip provider prefix from model names for display
        display_models = []
        provider_prefix = f"{provider.value}/"
        for model in models:
            if model.startswith(provider_prefix):
                display_models.append(model[len(provider_prefix) :])
            else:
                display_models.append(model)

        models_str = ", ".join(display_models)

        # Also strip prefix from default model
        default_model = config.get("default_model", "")
        if default_model.startswith(provider_prefix):
            default_model_display = default_model[len(provider_prefix) :]
        else:
            default_model_display = default_model

        status = "DEFAULT" if provider == default_provider else "Configured"

        table.add_row(display_name, models_str, default_model_display, status)

    # Get available commands
    from cmdlm.commands import CommandManager

    command_manager = CommandManager()
    available_commands = command_manager.get_available_commands()

    console.print("\n CMD-LM", style="bold blue")
    console.print(table)

    # Display available commands
    command_table = Table(title="Available Commands")
    command_table.add_column("Command", style="cyan")
    command_table.add_column("Description", style="white")

    # Add standard @ commands first
    for cmd_name in sorted(available_commands):
        processor = command_manager.get_processor(cmd_name)
        if (
            processor and cmd_name != "shell"
        ):  # Skip shell as we'll display it differently
            command_table.add_row(f"@{cmd_name}(arg)", processor.description)

    # Add shell command using $() syntax
    shell_processor = command_manager.get_processor("shell")
    if shell_processor:
        command_table.add_row("$(command)", shell_processor.description)

    console.print(command_table)

    console.print("\nUsage:", style="bold")
    console.print(
        '  cmdlm "your prompt"                        - Use default provider and model'
    )
    console.print(
        '  cmdlm --provider <n> "prompt"          - Use specific provider with its default model'
    )
    console.print(
        '  cmdlm --provider <n> --model <n> "prompt" - Use specific provider and model'
    )
    console.print(
        '  cmdlm --system-prompt "text" "prompt"   - Use custom system prompt'
    )
    console.print(
        '  cmdlm --system-prompt-file path "prompt" - Use system prompt from file'
    )
    console.print(
        '  cmdlm --debug "prompt"                   - Debug mode: show processed commands without sending to LLM'
    )
    console.print('\nNote: For custom providers configured as "other", use either:')
    console.print('  cmdlm --provider other "prompt"           - Using internal name')
    console.print(
        '  cmdlm --provider <custom_name> "prompt"   - Using your configured name'
    )

    console.print("\nConfiguration:", style="bold")
    console.print("  cmdlm --configure             - Configure providers")
    console.print("  cmdlm --reset                - Reset all configuration")
    console.print("  cmdlm --reset-provider <n> - Reset specific provider")
    console.print("  cmdlm --set-default <n>   - Set default provider and model")
    console.print("  cmdlm --status               - Show current status")
    console.print("  cmdlm --env-vars <action>   - Manage global environment variables")
    console.print("                               Actions: list, set, remove, clear")


def handle_env_vars_command(command: str, config_manager: ConfigManager):
    """Handle environment variables management commands"""

    if command == "list":
        env_vars = config_manager.get_global_env_vars()

        if not env_vars:
            console.print("No global environment variables configured", style="yellow")
            return

        table = Table(title="🌍 Global Environment Variables")
        table.add_column("Variable", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        for key, value in sorted(env_vars.items()):
            # Mask sensitive values
            if any(
                sensitive in key.upper()
                for sensitive in ["KEY", "TOKEN", "SECRET", "PASSWORD", "PASS"]
            ):
                masked_value = (
                    value[:4] + "*" * (len(value) - 8) + value[-4:]
                    if len(value) > 8
                    else "*" * len(value)
                )
            else:
                masked_value = value

            table.add_row(key, masked_value)

        console.print(table)
        console.print(
            "\nThese variables are automatically loaded in all chat and CLI sessions",
            style="dim",
        )

    elif command == "set":
        var_name = click.prompt("Environment variable name", type=str)
        var_value = click.prompt(f"Value for {var_name}", type=str, hide_input=False)

        try:
            config_manager.set_global_env_var(var_name, var_value)
            console.print(
                f"✅ Environment variable '{var_name}' set successfully", style="green"
            )
        except ValueError as e:
            console.print(f"❌ {str(e)}", style="red")
            return

    elif command == "remove":
        env_vars = config_manager.get_global_env_vars()

        if not env_vars:
            console.print("No global environment variables to remove", style="yellow")
            return

        console.print("Available environment variables:")
        for i, key in enumerate(sorted(env_vars.keys()), 1):
            console.print(f"  {i}. {key}")

        choice = click.prompt("Select variable to remove (number or name)", type=str)

        # Handle numeric choice
        try:
            choice_idx = int(choice) - 1
            var_names = sorted(env_vars.keys())
            if 0 <= choice_idx < len(var_names):
                var_name = var_names[choice_idx]
            else:
                var_name = choice
        except ValueError:
            var_name = choice

        if config_manager.remove_global_env_var(var_name):
            console.print(
                f"✅ Environment variable '{var_name}' removed successfully",
                style="green",
            )
        else:
            console.print(
                f"❌ Environment variable '{var_name}' not found", style="red"
            )

    elif command == "clear":
        env_vars = config_manager.get_global_env_vars()

        if not env_vars:
            console.print("No global environment variables to clear", style="yellow")
            return

        if click.confirm(
            f"Are you sure you want to clear all {len(env_vars)} global environment variables?"
        ):
            config_manager.clear_global_env_vars()
            console.print("✅ All global environment variables cleared", style="green")


def handle_prompts_command(command: str):
    """Handle prompts management commands"""
    import os
    import subprocess

    from ..utils.prompts import PromptsManager

    prompts_manager = PromptsManager()

    if command == "list":
        prompts = prompts_manager.list_prompts()

        if not prompts:
            console.print("No prompts found", style="yellow")
            return

        table = Table(title="📝 Available System Prompts")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Source", style="dim")
        table.add_column("Preview", style="white")

        for name, prompt in prompts.items():
            # Determine source
            if prompts_manager.get_prompt_file_path(name):
                source = "text file"
            else:
                source = "JSON"

            # Create preview
            preview = prompt[:80] + "..." if len(prompt) > 80 else prompt
            preview = preview.replace("\n", " ").replace("\r", " ")

            table.add_row(name, source, preview)

        console.print(table)

        prompts_dir = prompts_manager.get_prompts_directory()
        console.print(f"\nPrompts directory: {prompts_dir}", style="dim")
        console.print("Use 'cmdlm --prompts edit <name>' to edit a prompt", style="dim")

    elif command == "edit":
        prompt_name = click.prompt("Enter prompt name to edit", type=str)

        # Check if prompt exists
        if prompt_name not in prompts_manager.get_all_prompts():
            create_new = click.confirm(
                f"Prompt '{prompt_name}' doesn't exist. Create it?"
            )
            if not create_new:
                return

            # Create new prompt file
            prompt_file = prompts_manager.create_prompt_file(prompt_name)
            console.print(f"Created new prompt file: {prompt_file}", style="green")
        else:
            # Get existing prompt file path or create one
            prompt_file = prompts_manager.get_prompt_file_path(prompt_name)
            if not prompt_file:
                # Convert JSON prompt to text file
                existing_content = prompts_manager.get_prompt(prompt_name)
                prompt_file = prompts_manager.create_prompt_file(
                    prompt_name, existing_content
                )
                console.print(f"Converted to text file: {prompt_file}", style="green")

        # Open in editor
        editor = os.environ.get("EDITOR", "nano")
        try:
            subprocess.run([editor, str(prompt_file)], check=True)
            console.print(
                f"✅ Prompt '{prompt_name}' edited successfully", style="green"
            )
            console.print(
                f"Use --system-prompt {prompt_name} to use this prompt", style="dim"
            )
        except subprocess.CalledProcessError:
            console.print(f"Failed to open editor: {editor}", style="red")
            console.print(
                f"Please edit the file manually: {prompt_file}", style="yellow"
            )
        except FileNotFoundError:
            console.print(f"Editor not found: {editor}", style="red")
            console.print(
                f"Set EDITOR environment variable or edit manually: {prompt_file}",
                style="yellow",
            )

    elif command == "create":
        prompt_name = click.prompt("Enter name for new prompt", type=str)

        if prompt_name in prompts_manager.get_all_prompts():
            if not click.confirm(f"Prompt '{prompt_name}' already exists. Overwrite?"):
                return

        # Create new prompt file
        prompt_file = prompts_manager.create_prompt_file(prompt_name)
        console.print(f"Created new prompt file: {prompt_file}", style="green")

        # Optionally open in editor
        if click.confirm("Open in editor now?"):
            editor = os.environ.get("EDITOR", "nano")
            try:
                subprocess.run([editor, str(prompt_file)], check=True)
                console.print(
                    f"✅ Prompt '{prompt_name}' created and edited", style="green"
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                console.print(
                    f"Please edit the file manually: {prompt_file}", style="yellow"
                )

        console.print(
            f"Use --system-prompt {prompt_name} to use this prompt", style="dim"
        )

    elif command == "delete":
        prompt_name = click.prompt("Enter prompt name to delete", type=str)

        if prompt_name == "default":
            console.print("Cannot delete the default prompt", style="red")
            return

        if prompt_name not in prompts_manager.get_all_prompts():
            console.print(f"Prompt '{prompt_name}' not found", style="red")
            return

        if click.confirm(f"Are you sure you want to delete prompt '{prompt_name}'?"):
            if prompts_manager.delete_prompt(prompt_name):
                console.print(f"✅ Prompt '{prompt_name}' deleted", style="green")
            else:
                console.print(f"Failed to delete prompt '{prompt_name}'", style="red")

    elif command == "show":
        prompt_name = click.prompt("Enter prompt name to show", type=str)

        if prompt_name not in prompts_manager.get_all_prompts():
            console.print(f"Prompt '{prompt_name}' not found", style="red")
            return

        prompt_content = prompts_manager.get_prompt(prompt_name)

        console.print(f"\n📝 Prompt: {prompt_name}", style="bold cyan")
        console.print("=" * 50)
        console.print(prompt_content)
        console.print("=" * 50)

        # Show source info
        prompt_file = prompts_manager.get_prompt_file_path(prompt_name)
        if prompt_file:
            console.print(f"Source: {prompt_file}", style="dim")
        else:
            console.print("Source: JSON storage", style="dim")

        console.print(
            f"\nUse --system-prompt {prompt_name} to use this prompt", style="dim"
        )


def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n\nOperation cancelled by user", style="yellow")
        sys.exit(1)


if __name__ == "__main__":
    main()
