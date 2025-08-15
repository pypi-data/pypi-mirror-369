"""
Live Agent SDK - 实时AI助手客户端SDK

这个SDK提供了与LiveKit服务器连接的客户端功能，支持实时音频通信和AI助手交互。

主要组件:
- LiveAgentClient: 主要的客户端类，处理与LiveKit的连接和音频流
- AgentConfig: 客户端配置类
- AudioPCMData: 音频数据包装类
- AudioPlayInConfig/AudioPlayOutConfig: 音频配置类
"""

from .agent_client import LiveAgentClient
from .agent_config import AgentConfig, AudioPlayInConfig, AudioPlayOutConfig, LiveKitConfig
from .audio_pcm_data import AudioPCMData

__version__ = "1.0.1"
__author__ = "Plaud AI"
__description__ = "Live Agent SDK - 实时AI助手客户端SDK"

__all__ = [
    "LiveAgentClient",
    "AgentConfig", 
    "AudioPlayInConfig",
    "AudioPlayOutConfig",
    "LiveKitConfig",
    "AudioPCMData"
] 