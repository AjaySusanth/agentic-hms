"""
YAML config loader for integration configs.
Loads, validates, and indexes per-client configs from the configs/integrations/ directory.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from agents.templates.schemas import IntegrationConfig


# Default config directory: apps/api/configs/integrations/
CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "configs" / "integrations"


class ConfigLoader:
    """
    Loads and manages integration YAML configs.
    Configs are validated against IntegrationConfig schema on load.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or CONFIG_DIR
        self._configs: Dict[str, IntegrationConfig] = {}
        self._loaded = False

    def _ensure_loaded(self):
        """Lazy-load all configs on first access."""
        if not self._loaded:
            self._load_all()
            self._loaded = True

    def _load_all(self):
        """Scan the config directory and load all .yaml/.yml files."""
        if not self.config_dir.exists():
            print(f"[ConfigLoader] Config directory not found: {self.config_dir}")
            return

        for filepath in sorted(self.config_dir.glob("*.yaml")):
            self._load_file(filepath)
        for filepath in sorted(self.config_dir.glob("*.yml")):
            self._load_file(filepath)

    def _load_file(self, filepath: Path):
        """Load and validate a single config file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)

            config = IntegrationConfig(**raw)

            # Resolve auth env variable if needed
            if config.auth.value_env:
                env_value = os.getenv(config.auth.value_env)
                if not env_value:
                    print(f"[ConfigLoader] Warning: env var '{config.auth.value_env}' not set for {config.service_name}")

            # Index by service_name (lowercase, for lookup)
            key = config.service_name.lower().replace(" ", "_")
            self._configs[key] = config
            print(f"[ConfigLoader] Loaded: {config.service_name} ({config.service_type})")

        except Exception as e:
            print(f"[ConfigLoader] Error loading {filepath.name}: {e}")

    def load(self, service_name: str) -> Optional[IntegrationConfig]:
        """Load a specific config by service name."""
        self._ensure_loaded()
        key = service_name.lower().replace(" ", "_")
        return self._configs.get(key)

    def get_by_type(self, service_type: str) -> List[IntegrationConfig]:
        """Get all configs that match a given service type (for discovery)."""
        self._ensure_loaded()
        return [c for c in self._configs.values() if c.service_type == service_type]

    def list_all(self) -> List[IntegrationConfig]:
        """Get all loaded configs."""
        self._ensure_loaded()
        return list(self._configs.values())

    def reload(self):
        """Force reload all configs (e.g., after adding a new YAML file)."""
        self._configs.clear()
        self._loaded = False
        self._ensure_loaded()
