"""
Live Agent SDK 基本使用示例

这个示例展示了如何使用Live Agent SDK进行基本的音频通信。
"""

import asyncio
import numpy as np
from live_agent_sdk import (
    LiveAgentClient,
    AgentConfig,
    AudioPlayInConfig,
    AudioPlayOutConfig,
    AudioPCMData
)


def handle_audio_output(audio_data: AudioPCMData):
    """
    处理接收到的音频数据
    
    Args:
        audio_data: 音频PCM数据
    """
    print(f"接收到音频数据: {len(audio_data.data)} 字节")
    # 在这里可以添加音频播放逻辑
    # 例如: 将音频数据发送到扬声器


async def main():
    """主函数示例"""
    
    # 1. 创建客户端配置
    config = AgentConfig(
        agent_name="example-assistant",
        audio_play_in_config=AudioPlayInConfig(sample_rate=48000, channels=1),
        audio_play_out_config=AudioPlayOutConfig(sample_rate=48000, channels=1)
    )
    
    # 2. 创建客户端实例
    client = LiveAgentClient(config=config)
    
    # 3. 注册音频输出处理回调
    client.register_play_out_audio_stream(callback=handle_audio_output)
    
    try:
        # 4. 连接到LiveKit房间
        print("正在连接到LiveKit房间...")
        await client.connect(participant_id="example-user", room_id="example-room")
        print("✅ 连接成功!")
        
        # 5. 模拟发送音频数据
        print("模拟发送音频数据...")
        # 创建测试音频数据 (1秒的静音)
        test_audio = np.zeros(48000, dtype=np.int16)  # 48000Hz采样率，1秒
        audio_data = AudioPCMData(data=test_audio)
        
        # 发送音频帧
        await client.push_audio_frame(audio_data)
        print("✅ 音频数据发送成功!")
        
        # 6. 保持连接一段时间
        print("保持连接10秒...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    
    finally:
        # 7. 断开连接
        if client.is_connected:
            await client.disconnect()
            print("✅ 连接已断开")


if __name__ == "__main__":
    asyncio.run(main()) 