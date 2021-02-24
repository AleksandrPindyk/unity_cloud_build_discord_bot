import os
import re
import sys
import json
import asyncio
import logging
import discord
from config import log_config
from config.config import AppConfig, DiscordBotConfig
from unity_cloud_build_worker import UnityCloudBuildWorker


log_config.setup_logging()


class DiscordBot(discord.Client):
    def __init__(self):
        super(DiscordBot, self).__init__()
        self._config = None  # type: DiscordBotConfig
        self._log_tag = '[DiscordBot]'
        self._logger = logging.getLogger(__name__)
        self._unity_cloud_build_worker = None  # type: UnityCloudBuildWorker
        self._available_commands = [
            'help',
            'supported_builds',
            'build_target_info',
            'build'
        ]
        self._server_text_channels = {}
        self._mention_end = '> '
        self._mention_end_len = len(self._mention_end)

    async def run_bot(self):
        config = self._load_config()
        self._config = config.discord_bot
        self._unity_cloud_build_worker = UnityCloudBuildWorker(config.unity_cloud_build)
        await self._unity_cloud_build_worker.start_worker()
        await self.start(self._config.token, bot=True)
        self._logger.info(f'{self._log_tag} Bot started successfully!')

    async def stop_bot(self):
        await self.close()
        await self._unity_cloud_build_worker.stop_worker()
        self._logger.info(f'{self._log_tag} Bot stopped successfully!')

    async def on_ready(self):
        self_guild = self._config.guild
        for guild in self.guilds:
            if guild.name == self_guild:
                self._logger.info(f'{self._log_tag} connected to the server: {self_guild}')
                self._fill_server_text_channels()
                return
        self._logger.error(f'{self._log_tag} fails connect to the server: {self_guild}')
        await self.stop_bot()
        sys.exit()

    async def on_message(self, message: discord.Message):
        try:
            # Do not process self messages or messages not from bot supported channels
            message_channel = message.channel.name
            if message.author == self.user or message_channel not in self._config.bot_channels:
                return

            if message_channel == 'build':
                await self._process_build_event(message)
            else:
                # React only for messages that mention bot
                for mention in message.mentions:
                    if self.user == mention:
                        await self._process_bot_command(message)
                        return
        except Exception as e:
            self._logger.exception(f'{self._log_tag} Exception: {e}')

    async def _process_bot_command(self, message: discord.Message):
        command, params = self._get_command_for_bot(message)
        if command == 'help':
            await self._help(message)
        elif command == 'supported_builds':
            await self._supported_builds(message)
        elif command == 'build':
            await self._start_build(message, params)
        elif command == 'build_target_info':
            await self._build_target_info(message, params)
        else:
            self._logger.debug(f'{self._log_tag} Unsupported command for bot: {command}')

    async def _process_build_event(self, message: discord.Message):
        try:
            if message.author.name != 'Unity' or len(message.embeds) <= 0:
                return

            to_delete_idx = None
            build_success = False
            embed = message.embeds[0]
            for idx, field in enumerate(embed.fields):
                field_name = field.name
                if field_name == 'Build success':
                    build_success = True
                elif field_name == 'Download':
                    to_delete_idx = idx

            if build_success:
                if to_delete_idx is not None:
                    embed.remove_field(to_delete_idx)
                channel = self._server_text_channels['testing']
                await channel.send(embed=embed)
        except Exception as e:
            self._logger.exception(f'{self._log_tag} Exception: {e}')

    def _get_command_for_bot(self, message: discord.Message) -> tuple:
        msg = message.content.lower()
        msg = msg[msg.find(self._mention_end) + self._mention_end_len:]
        end_cmd_index = msg.find(' ')
        if end_cmd_index <= 0:
            return msg, ''

        cmd = msg[:end_cmd_index]
        params = msg[end_cmd_index + 1:]
        return cmd, params

    async def _help(self, message: discord.Message):
        msg = 'Available commands:'
        for command in self._available_commands:
            msg += f'\n{command}'
        await message.channel.send(msg)

    async def _supported_builds(self, message: discord.Message):
        builds_list = self._unity_cloud_build_worker.cmd_supported_builds()
        msg = 'Supported builds:'
        for build in builds_list:
            msg += f'\n{build}'
        await message.channel.send(msg)

    async def _start_build(self, message: discord.Message, params: str):
        await message.channel.send('Send start build command to Unity Cloud Build')
        result = await self._unity_cloud_build_worker.cmd_start_build(params)
        await message.channel.send(result)

    async def _build_target_info(self, message: discord.Message, params: str):
        await message.channel.send('Send build target info command to Unity Cloud Build')
        result = await self._unity_cloud_build_worker.cmd_build_target_info(params)
        await message.channel.send(result)

    def _fill_server_text_channels(self):
        for channel in self.get_all_channels():
            if channel.type.name == 'text':
                self._server_text_channels[channel.name] = channel

    def _load_config(self) -> AppConfig:
        def as_env_var(dct):
            def _parse_env_var(value):
                if isinstance(value, str):
                    for env_name in re.findall('\${(.+?)}', value):
                        value = re.sub('\${%s}' % env_name, os.environ.get(env_name, ''), value)
                return value

            return {_parse_env_var(k): _parse_env_var(v) for k, v in dct.items()}

        try:
            app_config_path = os.path.join(os.path.dirname(__file__), 'config/config.json')
            with open(app_config_path, 'r') as file:
                config_json = json.load(file, object_hook=as_env_var)
            return AppConfig.load(config_json)
        except Exception as e:
            self._logger.exception(f'{self._log_tag} Exception: {e}')
            sys.exit()


async def main():
    bot = DiscordBot()
    await bot.run_bot()


if __name__ == '__main__':
    asyncio.run(main())
