from .agent_config import AgentConfig,LiveKitConfig,AudioPlayInConfig,AudioPlayOutConfig
from livekit import rtc
from livekit.api import (
  AccessToken,
  RoomAgentDispatch,
  RoomConfiguration,
  VideoGrants,
)
from .audio_pcm_data import AudioPCMData
from typing import Optional, Callable, Awaitable
import asyncio

class LiveAgentClient:

    is_connected: bool = False

    agent_name: Optional[str] = None

    _room: Optional[rtc.Room] = None

    _livekit_config: LiveKitConfig = LiveKitConfig(
            url="wss://live-agent-demo-zeah44xr.livekit.cloud",
            api_key="API64Nz8xJApJHa",
            api_secret="QfbOfwD6TuD12MWTQU0bTAWTOfJu3y2C3JJA9etwwN5B"
    )

    _audio_play_in_config: AudioPlayInConfig = AudioPlayInConfig(sample_rate=16000, channels=1)

    _audio_play_out_config: AudioPlayOutConfig = AudioPlayOutConfig(sample_rate=16000, channels=1)

    _agent_audio_stream: Optional[rtc.AudioStream] = None
    
    # 音频输出回调列表
    _play_out_callback: Callable[[AudioPCMData], None] = None

    _audio_source: Optional[rtc.AudioSource] = None

    _audio_track: Optional[rtc.LocalAudioTrack] = None

    def __init__(self, config: AgentConfig):
        # self._livekit_config = config.livekit_config

        self._audio_play_in_config = config.audio_play_in_config

        self._audio_play_out_config = config.audio_play_out_config

        self._agent_name = config.agent_name

        return
    
    # @property
    # def agent_audio_stream(self) -> Optional[rtc.AudioStream]:
    #     return self._agent_audio_stream
    
    def register_play_out_audio_stream(self, callback: Callable[[AudioPCMData], None]):
        """
        注册音频输出流处理回调
        
        Args:
            callback: 处理音频数据的回调函数，函数签名为 def process(audio_data: AudioPCMData)
        """
        self._play_out_callback = callback
        print(f"Registered audio output callback.")
    
    async def _process_audio_stream(self, stream: rtc.AudioStream):
        """处理音频流并调用所有注册的回调"""
        try:
            print("Starting to process audio stream...")
            async for audio_event in stream:
                
                try:
                    # 创建AudioPCMData对象
                    audio_pcm = AudioPCMData(
                        data=audio_event.frame.data,
                    )
                    
                    # 调用回放的回调
                    try:
                        self._play_out_callback(audio_pcm)
                    except Exception as e:
                        print(f"Error in audio output callback: {e}")
                            
                except Exception as e:
                    print(f"Error processing audio frame: {e}")
                    
        except Exception as e:
            print(f"Error in audio stream processing: {e}")
        finally:
            print("Audio stream processing stopped")

    async def connect(self, participant_id: str, room_id: str):
        # 1. get token
        token = self._generate_token(identity=participant_id, room=room_id)
        
        # 2. connect to room
        room = rtc.Room()
        await room.connect(url=self._livekit_config.url, token=token)

        # 3. public the audio track to room session(audio stream)
        audio_source = rtc.AudioSource(
            sample_rate=self._audio_play_in_config.sample_rate,
            num_channels=self._audio_play_in_config.channels
        )

        audio_track = rtc.LocalAudioTrack.create_audio_track(
            name= f"{self._agent_name}_microphone",
            source=audio_source
        )

        await room.local_participant.publish_track(audio_track, rtc.TrackPublishOptions(
            source=rtc.TrackSource.SOURCE_MICROPHONE
        ))

        # 4. when remote audio track is subscribed, register a audio stream to play the audio
        @room.on("track_subscribed")
        def on_remote_audio_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                print(f"Received audio track from {participant.identity}")
                self._agent_audio_stream = rtc.AudioStream(
                    track=track,
                    sample_rate=self._audio_play_out_config.sample_rate,
                    channels=self._audio_play_out_config.channels
                )
                # 启动音频处理任务
                asyncio.create_task(self._process_audio_stream(rtc.AudioStream(track)))
        
        self._audio_source = audio_source
        self._audio_track = audio_track
        self._room = room 
        self.is_connected = True
        return
    
    async def disconnect(self):
        # 1. unpublish the audio track from the session
        if self._audio_track is not None:
            await self._room.local_participant.unpublish_track(self._audio_track.sid)
        self._audio_track = None

        # 2. close the audio source
        if self._audio_source is not None:
            await self._audio_source.aclose()
        self._audio_source = None

        # 3. disconnect from the room
        if self.is_connected and self._room is not None:
            await self._room.disconnect()
        self._room = None
        self.is_connected = False

        return
    
    def close(self):
        pass

    async def push_audio_frame(self, audio_pcm_data: AudioPCMData):
        
        if not self.is_connected:
            raise Exception("Client not connected to a room")
        
        if self._audio_source is None:
            raise ConnectionError("Audio source not initialized")

        samples_per_channel = len(audio_pcm_data.data) 
        
        frame=rtc.AudioFrame.create(
            self._audio_play_in_config.sample_rate, \
            self._audio_play_in_config.channels, \
            samples_per_channel
        )

        frame.data[:] = audio_pcm_data.data
        
        await self._audio_source.capture_frame(frame)
    
    def _generate_token(self, identity: str, room: str) -> str:
        api_key = self._livekit_config.api_key
        api_secret = self._livekit_config.api_secret

         # todo: 
         # 1. participant name 是否需要添加，目前meeting bot 和硬件都没有这个诉求
         # 2. agent name 需要进行唯一限定，目前没有唯一性校验
        token = AccessToken(api_key, api_secret) \
            .with_identity(identity=identity) \
            .with_name(name=identity) \
            .with_grants(VideoGrants(
                room_join=True,
                room=room
            )) \
            .with_room_config(
            RoomConfiguration(
                name=room,
                agents=[
                    RoomAgentDispatch(agent_name=self._agent_name)
                ],
            )) \
            .to_jwt()
        return token