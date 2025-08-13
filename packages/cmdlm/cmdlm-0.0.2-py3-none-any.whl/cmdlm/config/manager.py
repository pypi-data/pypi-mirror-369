import json
import os
from base64 import b64encode
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .providers import PROVIDER_CONFIGS, ProviderType


class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".cmdlm"
        self.config_file = self.config_dir / "config.json"
        self.secrets_file = self.config_dir / "secrets.enc"
        self._init_encryption()
        self.ensure_config_dir()

    def _init_encryption(self):
        """Initialize encryption key"""
        salt = b"cmdlm_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = b64encode(kdf.derive(b"cmdlm_secret_key"))
        self._fernet = Fernet(key)

    def set_default_provider(self, provider: ProviderType, model_name: str = None):
        """Set default provider and optionally update its default model

        Args:
            provider: Provider to set as default
            model_name: Optional new default model for the provider
        """
        config = self.load_config()
        if "providers" not in config or provider.value not in config["providers"]:
            raise ValueError(f"Provider {provider.value} is not configured")

        config["default_provider"] = provider.value

        if model_name:
            # Update the default model for the provider
            provider_config = config["providers"][provider.value]

            # Check if we're using the new multi-model structure
            if "models" in provider_config:
                provider_config["default_model"] = model_name

                # Make sure the model exists in the models list
                if model_name not in provider_config["models"]:
                    provider_config["models"].append(model_name)
            else:
                # Legacy structure - just update the default model
                provider_config["default_model"] = model_name

        self.save_config(config)

    def ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.save_config({})
        if not self.secrets_file.exists():
            self.secrets_file.write_bytes(self._fernet.encrypt(b"{}"))

    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                return json.loads(self.config_file.read_text())
            return {}
        except json.JSONDecodeError:
            return {}

    def save_config(self, config: Dict):
        """Save configuration to file"""
        self.config_file.write_text(json.dumps(config, indent=2))

    def load_secrets(self) -> Dict[str, str]:
        """Load encrypted secrets"""
        try:
            if not self.secrets_file.exists() or self.secrets_file.stat().st_size == 0:
                return {}
            encrypted_data = self.secrets_file.read_bytes()
            decrypted_data = self._fernet.decrypt(encrypted_data)
            data = json.loads(decrypted_data)

            # Ensure backward compatibility - migrate old format if needed
            if isinstance(data, dict) and "global_env" not in data:
                # Check if we have any non-provider secrets that should be global
                global_vars = {}
                provider_vars = {}

                for key, value in data.items():
                    # If key doesn't start with a known provider prefix, consider it global
                    is_provider_var = any(
                        key.startswith(f"{provider.value}_")
                        for provider in ProviderType
                    )

                    if is_provider_var:
                        provider_vars[key] = value
                    else:
                        # This might be a global env var from old format
                        pass  # For now, don't auto-migrate to avoid confusion

                # Return the data with empty global_env if it doesn't exist
                if "global_env" not in data:
                    data["global_env"] = {}

            return data
        except Exception:
            return {}

    def load_environment(self, provider: str) -> None:
        """Set up environment variables for the specified provider

        Args:
            provider: The provider name (e.g., 'anthropic', 'openai', 'other')
        """
        secrets = self.load_secrets()

        # First, load global environment variables
        self.load_global_environment()

        if provider == ProviderType.OTHER.value:
            for key, value in secrets.items():
                if key.startswith(f"{provider}_"):
                    env_var = key.split(f"{provider}_", 1)[1]
                    os.environ[env_var] = value
        else:
            for key, value in secrets.items():
                if key.startswith(f"{provider}_"):
                    env_var = key.replace(f"{provider}_", "")
                    os.environ[env_var] = value

    def save_secrets(self, secrets: Dict[str, str]):
        """Save encrypted secrets"""
        encrypted_data = self._fernet.encrypt(json.dumps(secrets).encode())
        self.secrets_file.write_bytes(encrypted_data)

    def save_provider_config(
        self,
        provider: ProviderType,
        model_name: str,
        env_vars: Dict[str, str],
        is_default: bool = False,
        additional_config: Dict = None,
        is_new_model: bool = False,
    ):
        """Save provider configuration with model

        Args:
            provider: Provider type
            model_name: Default model for this provider
            env_vars: Environment variables for provider
            is_default: Whether this should be the default provider
            additional_config: Additional params (e.g., provider name for OTHER type)
            is_new_model: If True, this is adding a model to an existing provider
        """
        secrets = self.load_secrets()
        config = self.load_config()

        # Initialize providers if it doesn't exist
        if "providers" not in config:
            config["providers"] = {}

        # Check if we're adding to an existing provider
        provider_exists = provider.value in config.get("providers", {})

        # Only save env vars if this is a new provider or we're explicitly updating them
        if not provider_exists or not is_new_model:
            if provider == ProviderType.OTHER:
                for key, value in env_vars.items():
                    secrets[f"{provider.value}_{key}"] = value
            else:
                for key, value in env_vars.items():
                    secrets[f"{provider.value}_{key}"] = value

            self.save_secrets(secrets)

        # Create or update the provider configuration
        if not provider_exists:
            # New provider
            config["providers"][provider.value] = {
                "default_model": model_name,
                "models": [model_name],  # New: list of models
                "env_vars": list(env_vars.keys()),
            }
            if additional_config:
                config["providers"][provider.value].update(additional_config)
        else:
            # Existing provider
            provider_config = config["providers"][provider.value]

            # Update env_vars list if needed
            if not is_new_model:
                provider_config["env_vars"] = list(env_vars.keys())

            # Update or add models
            if "models" not in provider_config:
                # Migrate from old format to new format
                current_model = provider_config.get("default_model")
                provider_config["models"] = (
                    [current_model, model_name]
                    if current_model and current_model != model_name
                    else [model_name]
                )
            else:
                # Add new model if it's not already in the list
                if model_name not in provider_config["models"]:
                    provider_config["models"].append(model_name)

            # Update default model if specified
            if is_new_model:
                provider_config["default_model"] = model_name

            # Update additional config if provided
            if additional_config:
                provider_config.update(additional_config)

        # Set as default provider if needed
        if is_default or "default_provider" not in config:
            config["default_provider"] = provider.value

        self.save_config(config)

    def get_provider_models(self, provider: ProviderType) -> List[str]:
        """Get all models configured for a provider

        Args:
            provider: Provider type

        Returns:
            List of model names
        """
        config = self.load_config()
        provider_config = config.get("providers", {}).get(provider.value, {})

        # Check if we're using the new multi-model structure
        if "models" in provider_config:
            return provider_config["models"]
        elif "default_model" in provider_config:
            # Legacy structure - return single model as a list
            return [provider_config["default_model"]]
        return []

    def get_configured_providers(self) -> Dict[ProviderType, Dict[str, Any]]:
        """Get dictionary of configured providers and their configurations

        Returns:
            Dict mapping ProviderType to provider configuration dict containing
            'default_model' and 'env_vars'
        """
        config = self.load_config()
        providers = config.get("providers", {})
        return {ProviderType(p): data for p, data in providers.items()}

    def get_provider_credentials(self, provider: ProviderType) -> Dict[str, str]:
        """Get provider credentials

        Args:
            provider: Provider type

        Returns:
            Dict of environment variables for the provider
        """
        secrets = self.load_secrets()
        provider_secrets = {}

        for key, value in secrets.items():
            if key.startswith(f"{provider.value}_"):
                if provider == ProviderType.OTHER:
                    env_var = key.split(f"{provider.value}_", 1)[1]
                else:
                    env_var = key.replace(f"{provider.value}_", "")
                provider_secrets[env_var] = value

        return provider_secrets

    def get_default_provider(self) -> Tuple[Optional[ProviderType], Optional[str]]:
        """Get default provider and its default model

        Returns:
            Tuple of (ProviderType, model_name) or (None, None) if not set
        """
        config = self.load_config()
        provider_name = config.get("default_provider")

        if provider_name:
            try:
                provider = ProviderType(provider_name)
                provider_config = config.get("providers", {}).get(provider_name, {})
                return provider, provider_config.get("default_model")
            except ValueError:
                return None, None
        return None, None

    def get_provider_display_name(self, provider: ProviderType, config: Dict) -> str:
        """Get display name for provider

        Args:
            provider: Provider type
            config: Provider configuration dictionary

        Returns:
            str: Display name for the provider
        """
        if provider == ProviderType.OTHER:
            return config.get("provider_name", "Other Provider")
        return PROVIDER_CONFIGS[provider].name

    def validate_provider_setup(
        self,
        provider: str,
        model_name: str,
        env_vars: Dict[str, str] = None,
        custom_provider: Optional[str] = None,
    ) -> bool:
        """Validate provider setup using LiteLLM

        Args:
            provider: Provider name
            model_name: Model name to test
            env_vars: Optional new environment variables for validation

        Returns:
            bool: True if validation successful
        """
        try:
            current_env = dict(os.environ)
            os.environ.clear()

            if env_vars:
                for key, value in env_vars.items():
                    os.environ[key] = value
            else:
                self.load_environment(provider)

            try:
                from litellm import completion

                # actual_model = model_name
                # if provider == ProviderType.OTHER.value and custom_provider:
                #     actual_model = f"{custom_provider}/{model_name}"

                completion(
                    model=model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1,
                )
                return True
            except Exception as e:
                print(f"Validation error: {str(e)}")
                return False
            finally:
                os.environ.clear()
                os.environ.update(current_env)
        except Exception as e:
            print(f"Setup validation error: {str(e)}")
            return False

    def reset_provider(self, provider: ProviderType):
        """Reset specific provider configuration"""
        secrets = self.load_secrets()
        config = self.load_config()
        provider_config = config.get("providers", {}).get(provider.value, {})

        for env_var in provider_config.get("env_vars", []):
            key = f"{provider.value}_{env_var}"
            if key in secrets:
                del secrets[key]

        if "providers" in config and provider.value in config["providers"]:
            del config["providers"][provider.value]

        if config.get("default_provider") == provider.value:
            config.pop("default_provider", None)

            # Remove default_model from root config if it exists
            if "default_model" in config:
                config.pop("default_model", None)

            remaining = list(config.get("providers", {}).keys())
            if remaining:
                config["default_provider"] = remaining[0]
                # Use "default_model" key instead of "model"
                if "default_model" in config["providers"][remaining[0]]:
                    config["default_model"] = config["providers"][remaining[0]][
                        "default_model"
                    ]

        self.save_secrets(secrets)
        self.save_config(config)

    def _validate_env_var_name(self, name: str) -> bool:
        """Validate environment variable name

        Args:
            name: Environment variable name to validate

        Returns:
            bool: True if name is valid
        """
        if not name or not isinstance(name, str):
            return False

        # Environment variable names should start with letter or underscore
        # and contain only letters, numbers, and underscores
        import re

        return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name))

    def load_global_environment(self) -> None:
        """Load global environment variables that are always available"""
        try:
            secrets = self.load_secrets()
            global_env = secrets.get("global_env", {})

            for key, value in global_env.items():
                os.environ[key] = value
        except Exception as e:
            # Log error but don't fail - global env vars are optional
            pass

    def get_global_env_vars(self) -> Dict[str, str]:
        """Get all global environment variables

        Returns:
            Dict of global environment variables
        """
        secrets = self.load_secrets()
        return secrets.get("global_env", {})

    def set_global_env_var(self, key: str, value: str) -> None:
        """Set a global environment variable

        Args:
            key: Environment variable name
            value: Environment variable value

        Raises:
            ValueError: If key is invalid
        """
        # Validate environment variable name
        if not self._validate_env_var_name(key):
            raise ValueError(f"Invalid environment variable name: {key}")

        secrets = self.load_secrets()
        if "global_env" not in secrets:
            secrets["global_env"] = {}

        secrets["global_env"][key] = value
        self.save_secrets(secrets)

    def remove_global_env_var(self, key: str) -> bool:
        """Remove a global environment variable

        Args:
            key: Environment variable name to remove

        Returns:
            bool: True if variable was removed, False if it didn't exist
        """
        secrets = self.load_secrets()
        global_env = secrets.get("global_env", {})

        if key in global_env:
            del global_env[key]
            secrets["global_env"] = global_env
            self.save_secrets(secrets)
            return True
        return False

    def set_global_env_vars(self, env_vars: Dict[str, str]) -> None:
        """Set multiple global environment variables

        Args:
            env_vars: Dictionary of environment variables to set

        Raises:
            ValueError: If any key is invalid
        """
        # Validate all environment variable names first
        for key in env_vars.keys():
            if not self._validate_env_var_name(key):
                raise ValueError(f"Invalid environment variable name: {key}")

        secrets = self.load_secrets()
        if "global_env" not in secrets:
            secrets["global_env"] = {}

        secrets["global_env"].update(env_vars)
        self.save_secrets(secrets)

    def clear_global_env_vars(self) -> None:
        """Clear all global environment variables"""
        secrets = self.load_secrets()
        secrets["global_env"] = {}
        self.save_secrets(secrets)

    def reset_all(self):
        """Reset all configuration"""
        self.secrets_file.write_bytes(self._fernet.encrypt(b"{}"))
        self.save_config({})
