from copy import copy

from backend.commands.RepoCommands import iCommand


class CommandController:
    __slots__ = ["_commands", "_current_command_number", "_current_command_return", "_undo_command_return", "_max_len"]

    def __init__(self, m_len=30):
        self._commands = []
        self._current_command_number: int = 0
        self._current_command_return = None
        self._undo_command_return = None
        self._max_len = m_len - 1  # нумерация с 0

    def remove_from_memory(self):  # должен удалять и лишний хвост! проверить!
        if self._current_command_number > self._max_len:
            self._commands.pop(0)
            self._current_command_number -= 1
        if len(self._commands) > self._current_command_number:
            for i in range(self._current_command_number, copy(len(self._commands))):
                self._commands.pop(self._current_command_number)

    def push_command(self, command):  # iCommand):  # добавить новую команду в место current_command_number
        self.remove_from_memory()
        self._commands.append(command)

    def do_command(self):
        if len(self._commands) > self._current_command_number:
            self._current_command_return = self._commands[self._current_command_number].do()
            self._current_command_number += 1
            return self._current_command_return

    def redo_command(self):
        if len(self._commands) > self._current_command_number:
            self._current_command_return = self._commands[self._current_command_number].redo()
            self._current_command_number += 1
            return self._current_command_return

    def undo_command(self):
        if self._current_command_number > 0:
            self._current_command_number -= 1
            self._undo_command_return = self._commands[self._current_command_number].undo()
            return self._undo_command_return

    def clear(self):
        self._commands = []
        self._current_command_number: int = 0
        self._current_command_return = None
        self._undo_command_return = None



"""
a = CommandController(5)
a.push_command(1)
a.do_command()
a.push_command(2)
a.do_command()
a.push_command(3)
a.do_command()
a.push_command(4)
a.do_command()
a.push_command(5)
a.do_command()
a.push_command(6)
a.do_command()
a.push_command(7)
a.do_command()
a.undo_command()
a.undo_command()
a.undo_command()
a.redo_command()
a.push_command(8)
a.do_command()
a.push_command(9)
a.do_command()
a.push_command(9)
a.do_command()
b = 0
"""
