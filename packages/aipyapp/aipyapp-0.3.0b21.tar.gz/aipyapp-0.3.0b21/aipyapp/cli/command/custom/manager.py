
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from loguru import logger

from ..base import CommandMode
from .markdown import CustomCommandConfig, MarkdownCommand

class CustomCommandManager:
    """Manager for custom markdown-based commands"""
    
    def __init__(self):
        self.command_dirs: set[Path] = set()
        self.commands: Dict[str, 'MarkdownCommand'] = {}
        self.log = logger.bind(src="CustomCommandManager")
        
    def add_command_dir(self, command_dir: str | Path):
        """Add a custom command directory"""
        self.command_dirs.add(Path(command_dir))
        self.log.info(f"Added custom command directory: {command_dir}")
    
    def scan_commands(self) -> List['MarkdownCommand']:
        """Scan the command directories for markdown commands"""
        commands = []
        
        for command_dir in self.command_dirs:
            if not command_dir.exists():
                # Create default directory if it doesn't exist
                if command_dir.name == "custom_commands":
                    self._ensure_default_command_dir(command_dir)
                else:
                    self.log.warning(f"Command directory does not exist: {command_dir}")
                    continue
        
            # Scan for .md files
            for md_file in command_dir.rglob("*.md"):
                try:
                    # Calculate relative path to determine command name
                    rel_path = md_file.relative_to(command_dir)
                    command = self._load_command_from_file(md_file, command_dir)
                    if command:
                        commands.append(command)
                        self.commands[command.name] = command
                        self.log.info(f"Loaded custom command: {command.name} from {rel_path}")
                except Exception as e:
                    self.log.error(f"Failed to load command from {md_file}: {e}")
        
        if commands:
            self.log.info(f"Loaded {len(commands)} custom commands")
        return commands
    
    def _load_command_from_file(self, md_file: Path, command_dir: Path) -> Optional['MarkdownCommand']:
        """Load a command from a markdown file"""
        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter, body = self._parse_frontmatter(content)
            
            # Calculate command name based on directory structure
            rel_path = md_file.relative_to(command_dir)
            # Convert path to command name: test/debug.md -> test/debug
            base_command_name = str(rel_path.with_suffix('')).replace('\\', '/')
            
            # Determine final command name
            if frontmatter and 'name' in frontmatter:
                # Replace the last component (filename) with the custom name
                path_parts = base_command_name.split('/')
                if len(path_parts) > 1:
                    # Has directory: test/custom_name.md + name: special -> test/special
                    path_parts[-1] = frontmatter['name']
                    final_command_name = '/'.join(path_parts)
                else:
                    # Root level: custom_name.md + name: special -> special
                    final_command_name = frontmatter['name']
            else:
                # No custom name, use directory-based name
                final_command_name = base_command_name
            
            final_command_name = 'usercmd/' + final_command_name
            if frontmatter:
                # File has frontmatter, parse configuration from it
                config = self._parse_command_config(frontmatter, final_command_name)
                config.name = final_command_name
            else:
                # No frontmatter, use default configuration
                self.log.info(f"No frontmatter found in {md_file}, using default configuration")
                config = self._create_default_config(final_command_name, content)
                body = content  # Use entire content as body
            
            return MarkdownCommand(config, body, md_file)
        except Exception as e:
            self.log.error(f"Error loading command from {md_file}: {e}")
            return None
    
    def _parse_frontmatter(self, content: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Parse YAML frontmatter from markdown content"""
        # Use regex to match YAML frontmatter pattern
        pattern = r'^\s*---\n(.*?)\n---\n?(.*)'
        match = re.match(pattern, content, re.DOTALL)
        
        if not match:
            return None, content
        
        yaml_content = match.group(1)
        body_content = match.group(2)
        
        try:
            frontmatter = yaml.safe_load(yaml_content) if yaml_content.strip() else {}
            return frontmatter, body_content
        except yaml.YAMLError as e:
            self.log.error(f"Invalid YAML frontmatter: {e}")
            return None, content
    
    def _create_default_config(self, default_name: str, content: str = "") -> CustomCommandConfig:
        """Create default configuration for pure markdown files"""
        mode = CommandMode.TASK
        
        return CustomCommandConfig(
            name=default_name,
            description=f"Custom command: {default_name}",
            modes=[mode],
            arguments=[],
            subcommands={},
            template_vars={},
            task=True
        )
    
    def _parse_command_config(self, frontmatter: Dict[str, Any], default_name: str) -> CustomCommandConfig:
        """Parse command configuration from frontmatter"""
        config = CustomCommandConfig(
            name=frontmatter.get('name', default_name),
            description=frontmatter.get('description', ''),
            arguments=frontmatter.get('arguments', []),
            subcommands=frontmatter.get('subcommands', {}),
            template_vars=frontmatter.get('template_vars', {}),
            task=frontmatter.get('task')
        )
        
        # Parse modes
        mode_strings = frontmatter.get('modes', ['task'])
        config.modes = []
        for mode_str in mode_strings:
            try:
                mode = CommandMode[mode_str.upper()]
                config.modes.append(mode)
            except KeyError:
                self.log.warning(f"Invalid command mode: {mode_str}, using TASK as default")
                config.modes.append(CommandMode.TASK)
        
        return config
    
    def get_command(self, name: str) -> Optional['MarkdownCommand']:
        """Get a custom command by name"""
        return self.commands.get(name)
    
    def get_all_commands(self) -> List['MarkdownCommand']:
        """Get all loaded custom commands"""
        return list(self.commands.values())
    
    def reload_commands(self) -> List['MarkdownCommand']:
        """Reload all custom commands"""
        self.commands.clear()
        return self.scan_commands()
    
    def validate_command_name(self, name: str, existing_commands: List[str]) -> bool:
        """Validate that a command name doesn't conflict with existing commands"""
        if name in existing_commands:
            self.log.warning(f"Custom command '{name}' conflicts with existing command")
            return False
        return True