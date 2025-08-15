# Plaud Live Agent SDK

Plaud实时AI助手客户端SDK，基于LiveKit WebRTC技术构建，提供高性能的实时音频通信和AI助手交互功能。

## 特性

- 🎤 **实时音频通信**: 基于WebRTC的低延迟音频传输
- 🤖 **AI助手集成**: 支持与各种AI助手服务集成
- 🔧 **易于使用**: 简洁的API设计，快速上手
- 📱 **跨平台**: 支持Windows、macOS、Linux
- 🚀 **高性能**: 优化的音频处理管道

## 包结构

```
pkg/
├── live_agent_sdk/         # 核心SDK包
│   ├── __init__.py         # 包初始化文件
│   ├── agent_client.py     # 主要客户端类
│   ├── agent_config.py     # 配置类
│   ├── audio_pcm_data.py   # 音频数据类
├── examples/               # 使用示例
│   └── basic_usage.py
├── setup.py                # 安装配置
├── pyproject.toml          # 现代Python包配置
├── README.md               # 详细文档
├── requirements.txt        # 依赖列表
├── MANIFEST.in             # 包文件清单
├── build_and_install.sh    # 构建脚本
```

## 安装

### 从PyPI安装（推荐）

```bash
pip install plaud-live-agent-sdk
```

### 开发环境安装

```bash
pip install plaud-live-agent-sdk[dev,audio]
```

## 快速开始

### 基本使用

```python
import asyncio
from live_agent_sdk import (
    LiveAgentClient,
    AgentConfig,
    AudioPlayInConfig,
    AudioPlayOutConfig,
    AudioPCMData
)

async def main():
    # 1. 创建客户端配置
    config = AgentConfig(
        agent_name="my-assistant",
        audio_play_in_config=AudioPlayInConfig(sample_rate=48000, channels=1),
        audio_play_out_config=AudioPlayOutConfig(sample_rate=48000, channels=1)
    )
    
    # 2. 创建客户端
    client = LiveAgentClient(config=config)
    
    # 3. 注册音频输出回调
    def handle_audio_output(audio_data):
        # 处理接收到的音频数据
        print(f"收到音频: {len(audio_data.data)} 字节")
    
    client.register_play_out_audio_stream(callback=handle_audio_output)
    
    # 4. 连接到房间
    await client.connect(participant_id="user-123", room_id="room-456")
    
    # 5. 发送音频数据
    audio_data = AudioPCMData(data=your_audio_data)
    await client.push_audio_frame(audio_data)
    
    # 6. 保持连接
    await asyncio.sleep(10)
    
    # 7. 断开连接
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 完整示例

参考 `examples/basic_usage.py` 查看基本使用示例。

## API 参考

### LiveAgentClient

主要的客户端类，处理与LiveKit服务器的连接和音频流。

#### 构造函数

```python
LiveAgentClient(config: AgentConfig)
```

#### 方法

- `register_play_out_audio_stream(callback)`: 注册音频输出处理回调
- `connect(participant_id, room_id)`: 连接到LiveKit房间
- `disconnect()`: 断开连接
- `push_audio_frame(audio_data)`: 发送音频帧

#### 属性

- `is_connected`: 连接状态
- `agent_name`: 代理名称

### AgentConfig

客户端配置类。

```python
AgentConfig(
    agent_name: str,
    audio_play_in_config: AudioPlayInConfig = AudioPlayInConfig(sample_rate=16000, channels=1),
    audio_play_out_config: AudioPlayOutConfig = AudioPlayOutConfig(sample_rate=16000, channels=1)
)
```

### AudioPlayInConfig / AudioPlayOutConfig

音频配置类。

```python
AudioPlayInConfig(sample_rate: int, channels: int)
AudioPlayOutConfig(sample_rate: int, channels: int)
```

### AudioPCMData

音频数据包装类。

```python
AudioPCMData(data: numpy.ndarray)
```

## 配置说明

### LiveKit服务器配置

SDK默认使用演示服务器配置，生产环境请使用自己的LiveKit服务器：

```python
# 默认配置
url = "wss://live-agent-demo-zeah44xr.livekit.cloud"
api_key = "API64Nz8xJApJHa"
api_secret = "QfbOfwD6TuD12MWTQU0bTAWTOfJu3y2C3JJA9etwwN5B"
```

### 音频格式

SDK使用PCM音频格式，支持以下参数：

- **采样率**: 16000Hz, 48000Hz (推荐)
- **声道数**: 1 (单声道), 2 (立体声)
- **数据类型**: int16

## 错误处理

SDK包含完善的错误处理机制：

```python
try:
    await client.connect(participant_id="user", room_id="room")
except Exception as e:
    print(f"连接失败: {e}")
```

## 开发

### 本地开发安装

```bash
git clone https://github.com/plaud-ai/live-agent-sdk.git
cd live-agent-sdk
pip install -e .
```

### 安装开发版本

```bash
pip install -e .[dev]
```

### 运行测试

```bash
# 安装测试依赖
pip install -e .[dev]

# 运行测试
pytest tests/
```

### 构建包

```bash
# 使用构建脚本
./build_and_install.sh

# 或手动构建
python3 setup.py sdist bdist_wheel
```

## 故障排除

### 常见问题

1. **导入错误**: 确保已正确安装 SDK
2. **连接失败**: 检查网络连接和服务器配置
3. **音频问题**: 检查音频格式和采样率设置

### 调试

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 许可证

MIT License

## 支持

- 文档: README.md
- 问题反馈: [GitHub Issues](https://github.com/plaud-ai/live-agent-sdk/issues)
- 邮箱: dev-support@plaud.ai 