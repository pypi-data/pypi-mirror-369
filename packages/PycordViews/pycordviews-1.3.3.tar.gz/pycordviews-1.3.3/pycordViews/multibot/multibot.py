from queue import Empty
from multiprocessing import get_context
from multiprocessing.queues import Queue
from .process import ManageProcess
from discord import Intents
from sys import platform
from typing import Union, Optional


class Multibot:

    def __init__(self, global_timeout: int = 30):
        """
        Get instance to run few Discord bot
        """
        if platform == 'win32':
            ctx = get_context("spawn")
        else:
            ctx = get_context("forkserver")
        self.__main_queue: Queue = ctx.Queue()
        self.__process_queue: Queue = ctx.Queue()
        # Création du processus gérant les bots
        self.__DiscordProcess = ctx.Process(target=self._start_process)
        self.__DiscordProcess.start()
        
        self.global_timeout = global_timeout
        
    def __get_data_queue(self) -> Union[list[dict], dict]:
        """
        Récupère les données dans la queue processus
        """
        try:
            result = self.__process_queue.get(timeout=self.global_timeout)
            return result
        except Empty:
            return {'status': 'error', 'message': 'timeout request exceeded'}
        except ValueError:
            return {'status': 'critical error', 'message': 'queue was closed !'}

    def _start_process(self):
        """
        Initialise et exécute le gestionnaire de processus.
        """
        manager = ManageProcess(self.__main_queue, self.__process_queue)
        manager.run()

    def add_bot(self, bot_name: str, token: str, intents: Intents):
        """
        Add a bot in the process
        :param bot_name: Bot name
        :param token: Token bot
        :param intents: Intents bot to Intents discord class
        """
        self.__main_queue.put({"type": "ADD", "bot_name": bot_name, "token": token, 'intents': intents})
        response = self.__get_data_queue()
        return response  # Retourne le statut de l'ajout

    def remove_bot(self, bot_name: str) -> dict[str, str]:
        """
        Shutdown and remove à bot
        :param bot_name: Bot name to remove
        """
        self.__main_queue.put({"type": "REMOVE", "bot_name": bot_name})
        response = self.__get_data_queue()
        return response  # Retourne le statut de la suppression

    def start(self, *bot_names: str) -> list[dict[str, str]]:
        """
        Start bots
        :param bot_names: Bots name to start
        :return: List of data bot status
        """
        results = []
        for bot_name in bot_names:
            self.__main_queue.put({'type': "START", 'bot_name': bot_name})
            results.append(self.__get_data_queue())
        return results

    def stop(self, *bot_names: str) -> list[dict[str, str]]:
        """
        Stop bots
        :param bot_names: Bots name to start
        :return: Data status dict
        """
        results = []
        for bot_name in bot_names:
            self.__main_queue.put({'type': "STOP", 'bot_name': bot_name})
            results.append(self.__get_data_queue())
        return results

    def restart(self, *bot_names: str) -> list[dict[str, str]]:
        """
        Stop and start bots.
        This function is slow ! It's shutdown all bots properly.
        """
        results = []
        for bot_name in bot_names:
            self.__main_queue.put({'type': "RESTART", 'bot_name': bot_name})
            results.append(self.__get_data_queue())
        return results

    def restart_all(self):
        """
        Stop and restart all bots
        This function is slow ! It's shutdown all bots properly.
        """
        self.__main_queue.put({'type': "RESTARTALL"})
        return self.__get_data_queue()

    def start_all(self) -> list[dict[str, list[str]]]:
        """
        Start all bots in the process.
        """
        self.__main_queue.put({'type': "STARTALL"})
        return self.__get_data_queue()
    
    def stop_all(self) -> list[dict[str, list[str]]]:
        """
        Stop all bots in the process.
        This function is slow ! It's shutdown all bots properly.
        """
        self.__main_queue.put({'type': "STOPALL"})
        return self.__get_data_queue()

    def add_modules(self, *modules_name):
        """
        Adds modules (library) to the process (thus affecting bots).
        Only previously removed modules can be added again!
        To be run before launching a bot!
        :param modules_name: names of modules to be added
        """
        self.__main_queue.put({'type': "ADD_MODULES", 'modules_name': modules_name})
        return self.__get_data_queue()

    def remove_modules(self, *modules_name):
        """
        Removes modules (library) to the process (thus affecting bots).
        To be run before launching a bot!
        :param modules_name: names of modules to be removed
        """
        self.__main_queue.put({'type': "REMOVE_MODULES", 'modules_name': modules_name})
        return self.__get_data_queue()

    def is_started(self, bot_name: str) -> bool:
        """
        Return the current Websocket connexion status
        :param bot_name: Bot name
        :return: True if the Websocket is online, else False
        """
        self.__main_queue.put({'type': "IS_STARTED", 'bot_name': bot_name})
        return self.__get_data_queue()['message']

    def is_ready(self, bot_name: str) -> bool:
        """
        Return the current bot connexion status
        :param bot_name: Bot name
        :return: True if the bot if ready, else False
        """
        self.__main_queue.put({'type': "IS_READY", 'bot_name': bot_name})
        return self.__get_data_queue()['message']

    def is_ws_ratelimited(self, bot_name: str) -> bool:
        """
        Get the current ratelimit status of the bot
        :param bot_name: Bot name
        :return: True if the bot was ratelimited, else False
        """
        self.__main_queue.put({'type': "IS_WS_RATELIMITED", 'bot_name': bot_name})
        return self.__get_data_queue()['message']

    def reload_commands(self, *bot_names: str) -> list[dict[str, str]]:
        """
        Reload all commands for each bot when bots are ready
        :param bot_names: Bots name to reload commands
        """
        result = []
        for name in bot_names:
            self.__main_queue.put({'type': "RELOAD_COMMANDS", 'name': name})
            result.append(self.__get_data_queue())
        return result

    def add_pyFile_commands(self, bot_name: str, file: str, setup_function: str = 'setup', reload_command: bool = True) -> dict[str, str]:
        """
        Add and load a command bot file and dependencies.
        Files must have a function called ‘setup’ or an equivalent passed as a parameter.

        def setup(bot: Bot):
            ...

        :param bot_name: The bot's name to add commands file
        :param file: Relative or absolute commands file's path
        :param setup_function: Function name called by the process to give the Bot instance. Set to 'setup' by default.
        :param reload_command: Reload all command in the fil and dependencies. Default : True
        """
        self.__main_queue.put({'type': "ADD_COMMAND_FILE",
                               'bot_name': bot_name,
                               'file': file,
                               'setup_function': setup_function,
                               'reload_command': reload_command})
        return self.__get_data_queue()

    def modify_pyFile_commands(self, bot_name: str, file: str, setup_function: str = 'setup') -> dict[str, str]:

        """
        Modifies a file of commands and reloads it.
        Reloads only the file, not the bot commands!
        :param bot_name: The bot's name
        :param file: The file's relative or absolute path
        """

        self.__main_queue.put({'type': "MODIFY_COMMAND_FILE",
                               'bot_name': bot_name,
                               'file': file,
                               'setup_function': setup_function})
        return self.__get_data_queue()

    @property
    def bot_count(self) -> int:
        """
        Return the total number of bots
        """
        self.__main_queue.put({'type': "BOT_COUNT"})
        return self.__get_data_queue()['message']

    @property
    def started_bot_count(self) -> int:
        """
        Return the total number of started bots
        """
        self.__main_queue.put({'type': "STARTED_BOT_COUNT"})
        return self.__get_data_queue()['message']

    @property
    def shutdown_bot_count(self) -> int:
        """
        Return the total number of shutdown bots
        """
        self.__main_queue.put({'type': "SHUTDOWN_BOT_COUNT"})
        return self.__get_data_queue()['message']

    @property
    def get_bots_name(self) -> list[str]:
        """
        Return all bots name (not real name of bots)
        """
        self.__main_queue.put({'type': "BOTS_NAME"})
        return self.__get_data_queue()['message']
