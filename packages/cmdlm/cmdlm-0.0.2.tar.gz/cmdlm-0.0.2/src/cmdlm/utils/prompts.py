import json
import shutil
from pathlib import Path
from typing import Dict, Optional

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant"""


class PromptsManager:
    """Manages system prompts configuration"""

    def __init__(self):
        """Initialize prompts manager"""
        self.config_dir = Path.home() / ".cmdlm" / "prompts"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_file = self.config_dir / "prompts.json"

        # Shipped prompts directory
        self.shipped_prompts_dir = Path(__file__).parent.parent / "prompts"

        # Create default prompts if file doesn't exist
        if not self.prompts_file.exists():
            self.save_prompts(
                {
                    "default": DEFAULT_SYSTEM_PROMPT,
                }
            )

        # Copy shipped prompts to user directory if they don't exist
        self._ensure_user_prompts()

    def _ensure_user_prompts(self):
        """Ensure user prompts directory has copies of shipped prompts"""
        if not self.shipped_prompts_dir.exists():
            return

        # Copy shipped prompts to user directory for easy editing
        for shipped_prompt in self.shipped_prompts_dir.glob("*.txt"):
            user_prompt = self.config_dir / shipped_prompt.name
            if not user_prompt.exists():
                try:
                    shutil.copy2(shipped_prompt, user_prompt)
                except Exception:
                    # If copy fails, create a basic version
                    try:
                        content = shipped_prompt.read_text(encoding="utf-8")
                        user_prompt.write_text(content, encoding="utf-8")
                    except Exception:
                        pass

    def load_prompts(self) -> Dict[str, str]:
        """Load saved prompts from JSON file"""
        try:
            if self.prompts_file.exists():
                return json.loads(self.prompts_file.read_text())
            return {"default": DEFAULT_SYSTEM_PROMPT}
        except Exception:
            return {"default": DEFAULT_SYSTEM_PROMPT}

    def load_text_prompts(self) -> Dict[str, str]:
        """Load prompts from text files in the user prompts directory"""
        prompts = {}
        if self.config_dir.exists():
            for file in self.config_dir.glob("*.txt"):
                name = file.stem
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        prompts[name] = f.read().strip()
                except Exception:
                    continue
        return prompts

    def get_all_prompts(self) -> Dict[str, str]:
        """Get all prompts from both JSON and text files, preferring text files"""
        json_prompts = self.load_prompts()
        text_prompts = self.load_text_prompts()

        # Merge prompts, with text files taking precedence
        all_prompts = {**json_prompts, **text_prompts}
        return all_prompts

    def save_prompts(self, prompts: Dict[str, str]):
        """Save prompts to JSON file"""
        self.prompts_file.write_text(json.dumps(prompts, indent=2))

    def get_prompt(self, name: str = "default") -> str:
        """Get a specific prompt, checking text files first, then JSON, then shipped"""
        # First check user text files
        text_prompts = self.load_text_prompts()
        if name in text_prompts:
            return text_prompts[name]

        # Then check JSON prompts
        json_prompts = self.load_prompts()
        if name in json_prompts:
            return json_prompts[name]

        # Finally check shipped prompts
        shipped_file = self.shipped_prompts_dir / f"{name}.txt"
        if shipped_file.exists():
            try:
                return shipped_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass

        # Return default if not found
        return DEFAULT_SYSTEM_PROMPT

    def get_compact_prompt(self) -> str:
        """Get the compact prompt from shipped prompts"""
        return self.get_prompt("compact")

    def save_prompt(self, name: str, prompt: str, use_text_file: bool = True):
        """Save a prompt either as a text file or to JSON

        Args:
            name: Name of the prompt
            prompt: Content of the prompt
            use_text_file: If True, save as .txt file; if False, save to JSON
        """
        if use_text_file:
            # Save as text file
            prompt_file = self.config_dir / f"{name}.txt"
            prompt_file.write_text(prompt, encoding="utf-8")
        else:
            # Save to JSON
            prompts = self.load_prompts()
            prompts[name] = prompt
            self.save_prompts(prompts)

    def delete_prompt(self, name: str) -> bool:
        """Delete a saved prompt (both text file and JSON entry)"""
        if name == "default":
            return False

        deleted = False

        # Try to delete text file
        prompt_file = self.config_dir / f"{name}.txt"
        if prompt_file.exists():
            try:
                prompt_file.unlink()
                deleted = True
            except Exception:
                pass

        # Try to delete from JSON
        prompts = self.load_prompts()
        if name in prompts:
            del prompts[name]
            self.save_prompts(prompts)
            deleted = True

        return deleted

    def list_prompts(self) -> Dict[str, str]:
        """Get all saved prompts"""
        return self.get_all_prompts()

    def get_prompt_file_path(self, name: str) -> Optional[Path]:
        """Get the file path for a text prompt if it exists"""
        prompt_file = self.config_dir / f"{name}.txt"
        return prompt_file if prompt_file.exists() else None

    def create_prompt_file(self, name: str, content: str = "") -> Path:
        """Create a new prompt text file"""
        prompt_file = self.config_dir / f"{name}.txt"
        if not content:
            content = f"# {name.title()} System Prompt\n\n# Edit this file to customize your {name} prompt\n\nYou are a helpful assistant."

        prompt_file.write_text(content, encoding="utf-8")
        return prompt_file

    def get_prompts_directory(self) -> Path:
        """Get the user prompts directory path"""
        return self.config_dir

    @staticmethod
    def resolve_system_prompt(
        system_prompt: str, system_prompt_file: str = None
    ) -> str:
        """Resolve system prompt from text, file path, or prompt name

        Args:
            system_prompt: Direct system prompt text or prompt name
            system_prompt_file: Path to file containing system prompt

        Returns:
            System prompt text

        Raises:
            ValueError: If both or neither arguments are provided
            FileNotFoundError: If system_prompt_file doesn't exist
            IOError: If system_prompt_file cannot be read
        """
        if system_prompt and system_prompt_file:
            raise ValueError(
                "Cannot specify both --system-prompt and --system-prompt-file"
            )

        if not system_prompt and not system_prompt_file:
            raise ValueError(
                "Must specify either --system-prompt or --system-prompt-file"
            )

        if system_prompt_file:
            try:
                file_path = Path(system_prompt_file)
                if not file_path.exists():
                    raise FileNotFoundError(
                        f"System prompt file not found: {system_prompt_file}"
                    )

                content = file_path.read_text(encoding="utf-8").strip()
                if not content:
                    raise ValueError(
                        f"System prompt file is empty: {system_prompt_file}"
                    )

                return content
            except Exception as e:
                if isinstance(e, (FileNotFoundError, ValueError)):
                    raise
                raise IOError(
                    f"Failed to read system prompt file: {system_prompt_file}"
                ) from e

        # If system_prompt is provided, it could be either text or a prompt name
        if system_prompt:
            # First check if it's a prompt name that exists
            try:
                manager = PromptsManager()
                # Check if it's a known prompt name
                if system_prompt in manager.get_all_prompts():
                    return manager.get_prompt(system_prompt)
            except Exception:
                # If there's an error accessing prompts, treat as literal text
                pass

            # Treat as literal text
            return system_prompt.strip()

        # This shouldn't be reached, but just in case
        return DEFAULT_SYSTEM_PROMPT

    @staticmethod
    def resolve_system_prompt_with_fallback(
        system_prompt: str = None, system_prompt_file: str = None
    ) -> str:
        """Resolve system prompt with fallback to default, never raises exceptions

        Args:
            system_prompt: Direct system prompt text or prompt name
            system_prompt_file: Path to file containing system prompt

        Returns:
            System prompt text (never None)
        """
        try:
            if system_prompt or system_prompt_file:
                return PromptsManager.resolve_system_prompt(
                    system_prompt, system_prompt_file
                )
        except Exception:
            pass

        # Fallback to default
        try:
            manager = PromptsManager()
            return manager.get_prompt("default")
        except Exception:
            return DEFAULT_SYSTEM_PROMPT
