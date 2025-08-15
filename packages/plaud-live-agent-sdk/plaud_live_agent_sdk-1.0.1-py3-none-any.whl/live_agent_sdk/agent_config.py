import os
from typing import Optional
from dataclasses import dataclass

class LiveKitConfig:
    def __init__(self, url: str, api_key: str, api_secret: str):
        self.url = url
        self.api_key = api_key
        self.api_secret = api_secret

@dataclass
class AudioPlayInConfig:
    sample_rate: int   # 采样率
    channels: int      # 声道数


@dataclass
class AudioPlayOutConfig:
    sample_rate: int   # 采样率
    channels: int      # 声道数


class AgentConfig:

    # _rtc_server_config: LiveKitConfig

    agent_name: str

    audio_play_in_config: AudioPlayInConfig
    audio_play_out_config: AudioPlayOutConfig

    
    def __init__(self, agent_name: str, audio_play_in_config: AudioPlayInConfig = AudioPlayInConfig(sample_rate=16000, channels=1), 
    audio_play_out_config: AudioPlayOutConfig = AudioPlayOutConfig(sample_rate=16000, channels=1)):
        # todo: 先写死，后续将这些东西注入到开发者配置内
        # self._livekit_server_config = LiveKitConfig(
        #     url=os.getenv("wss://livekit.plaud.work"),
        #     api_key=os.getenv("APIBr9quNb6J3Yd"),
        #     api_secret=os.getenv("OnddFINgobl1IgI8cSVlUw4BvLyGec2XX1WSXGiP91W")
        # )
        self.agent_name = agent_name
        self.audio_play_in_config = audio_play_in_config
        self.audio_play_out_config = audio_play_out_config
        return
    
    @property
    def livekit_server_config(self) -> LiveKitConfig:
        return self._livekit_server_config