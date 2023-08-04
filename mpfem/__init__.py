import json
from types import MethodType
from typing import Optional, Dict

from mcdreforged.api.types import PluginServerInterface, CommandSource
from mcdreforged.command.builder.common import CommandSuggestions, CommandSuggestion
from mcdreforged.command.command_manager import CommandManager, TraversePurpose

suggest_command_backup: Optional[MethodType] = None


def suggest_command(self: CommandManager, command: str, source: CommandSource) -> CommandSuggestions:
    suggestions: CommandSuggestions = self._traverse(command, source, TraversePurpose.SUGGEST)
    suggestions_mc = []
    query_result = source.get_server().rcon_query('fpmemgetdata {} "{}"'.format(len(command), command.replace('"', '\\"')))
    if query_result is not None:
        try:
            suggestions_obj: Dict[str, str] = json.loads(query_result)
        except Exception:
            return suggestions
        for suggest_segment, command_read in suggestions_obj.items():
            suggestion = CommandSuggestion(command_read, suggest_segment)
            if suggestion not in suggestions:
                suggestions_mc.append(suggestion)
        suggestions.extend(suggestions_mc)
    return suggestions


def on_load(server: PluginServerInterface, old):
    global suggest_command_backup
    command_manager = server._mcdr_server.command_manager
    suggest_command_backup = command_manager.suggest_command
    command_manager.suggest_command = MethodType(suggest_command, command_manager)


def on_unload(server: PluginServerInterface):
    global suggest_command_backup
    command_manager = server._mcdr_server.command_manager
    if suggest_command_backup is None:
        command_manager.suggest_command = suggest_command_backup
        suggest_command_backup = None
