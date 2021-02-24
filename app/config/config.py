from dataclasses import dataclass


class BaseConfig:
    @classmethod
    def load(cls, config: dict):
        return cls(**config)


@dataclass
class DiscordBotConfig(BaseConfig):
    token: str
    guild: str
    bot_name: str
    bot_channels: list


@dataclass
class UnityCloudBuildConfig(BaseConfig):
    base_url: str
    api_key: str
    project_id: str
    project_name: str
    cloud_build_targets: dict


@dataclass
class AppConfig:
    discord_bot: DiscordBotConfig
    unity_cloud_build: UnityCloudBuildConfig

    @classmethod
    def load(cls, config: dict):
        return cls(
            discord_bot=DiscordBotConfig.load(config['discord_bot']),
            unity_cloud_build=UnityCloudBuildConfig.load(config['unity_cloud_build'])
        )
