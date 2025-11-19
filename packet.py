class EventType:
  ALL = 'realtime.event'                    # 所有事件
  CONNECTED = 'client.connected'            # 客户端已连接
  CONNECTING = 'client.connecting'          # 客户端连接中
  INTERRUPTED = 'client.interrupted'        # 客户端已中断
  DISCONNECTED = 'client.disconnected'      # 客户端已断开
  ERROR = 'client.error'                    # 客户端发生错误

  # 音频控制事件
  AUDIO_UNMUTED = 'client.audio.unmuted'    # 音频已取消静音
  AUDIO_MUTED = 'client.audio.muted'        # 音频已静音
  AUDIO_INPUT_DUMP = 'client.audio.input.dump' # 音频输入数据导出
  
  # 设备变更事件
  AUDIO_INPUT_DEVICE_CHANGED = 'client.input.device.changed'   # 音频输入设备已改变
  AUDIO_OUTPUT_DEVICE_CHANGED = 'client.output.device.changed' # 音频输出设备已改变

  # 降噪控制事件
  DENOISER_ENABLED = 'client.denoiser.enabled'   # 降噪已启用
  DENOISER_DISABLED = 'client.denoiser.disabled' # 降噪已禁用

  # 服务端对话事件
  CHAT_CREATED = 'chat.created'      # 对话已创建
  CHAT_UPDATED = 'chat.updated'      # 对话已更新
  
  # 会话状态事件
  CONVERSATION_CHAT_CREATED = 'conversation.chat.created'           # 会话对话已创建
  CONVERSATION_CHAT_IN_PROGRESS = 'conversation.chat.in.progress'   # 对话进行中
  CONVERSATION_CHAT_COMPLETED = 'conversation.chat.completed'       # 对话已完成
  CONVERSATION_CHAT_FAILED = 'conversation.chat.failed'            # 对话失败
  CONVERSATION_CHAT_CANCELLED = 'conversation.chat.cancelled'      # 对话已取消
  CONVERSATION_CHAT_REQUIRES_ACTION = 'conversation.chat.requires_action' # 对话需要端插件响应
  
  # 消息事件
  CONVERSATION_MESSAGE_DELTA = 'conversation.message.delta'         # 文本消息增量返回
  CONVERSATION_MESSAGE_COMPLETED = 'conversation.message.completed' # 文本消息完成
  
  # 音频事件
  CONVERSATION_AUDIO_DELTA = 'conversation.audio.delta'           # 语音消息增量返回
  CONVERSATION_AUDIO_COMPLETED = 'conversation.audio.completed'   # 语音回复完成
  
  # 语音识别事件
  CONVERSATION_AUDIO_TRANSCRIPT_UPDATE = 'conversation.audio_transcript.update'     # 用户语音识别实时字幕更新
  CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED = 'conversation.audio_transcript.completed' # 用户语音识别完成
  
  # 语音检测事件
  INPUT_AUDIO_BUFFER_SPEECH_STARTED = 'input_audio_buffer.speech_started' # 检测到用户开始说话
  INPUT_AUDIO_BUFFER_SPEECH_STOPPED = 'input_audio_buffer.speech_stopped' # 检测到用户停止说话
  
  # 缓冲区事件
  INPUT_AUDIO_BUFFER_COMPLETED = 'input_audio_buffer.completed'   # 语音输入缓冲区提交完成
  INPUT_AUDIO_BUFFER_CLEARED = 'input_audio_buffer.cleared'      # 语音输入缓冲区已清除
  
  # 其他事件
  SERVER_ERROR = 'error'              # 服务端错误
  CONVERSATION_CLEARED = 'conversation.cleared' # 对话上下文已清除
  DUMP_AUDIO = 'dump.audio'            # 音频导出


update = { 
    "id": "event_id_123456", 
    "event_type": "chat.update", 
    "data": {
        "need_play_prologue": True,
        "chat_config": { 
            "auto_save_history": True,
            "user_id": "quecpython_user",
        }, 
        "input_audio": {
            "format": "pcm",
            "codec": "g711a",
            "sample_rate": 8000,
            "channel": 1,
            "bit_depth": 16
        },
        "output_audio": {
            "codec": "g711a",
            "pcm_config": {
                "sample_rate": 8000,
                "frame_size_ms": 100,
                "limit_config": { 
                    "period": 1,
                    "max_frame_num": 11
                },
            },
            "speech_rate": 0,
        },
        "turn_detection": {
            "type": "server_vad",
            "interrupt_config": {
                "mode": "keyword_contains",
                "keywords": [
                    "闭嘴",
                    "你好扣子"
                ]
            }
        },
        "asr_config":{
            "enable_ddc": True,
            "hot_words":[
              "闭嘴",
              "你好扣子"
            ]
        },
        "event_subscriptions": [
            "error",
            "conversation.audio_transcript.completed",
            "conversation.message.completed",
            "conversation.audio.delta",
            "conversation.chat.failed",
            "conversation.chat.cancelled"
        ]
    }
}

interrupt = {
    "id": "event_id_123457",
    "event_type": "chat.update",
    "data": {
        "turn_detection": {
            "type":"server_vad",
            "interrupt_config": {
                "mode": "keyword_contains",
                "keywords": [
                    "闭嘴",
                    "你好扣子"
                ]
            }
        },
        "asr_config":{
            "hot_words":[
              "闭嘴",
              "你好扣子"
            ]
        }
    }
}


append = {
  "id": "event_id_123458",
  "event_type": "input_audio_buffer.append",
  "data": {
     "delta": "base64EncodedAudioDelta"
  }
}

cancel = {
  "id": "event_id_123459",
  "event_type": "conversation.chat.cancel"
}

disconnected = {
  "event_type": "client.disconnected"
}
