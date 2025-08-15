from typing import List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from taylorist import TayloristTTS, TTSProvider, TTSModel, TTSVoice, OutputTTS

class TayloristTTSChatModel(BaseChatModel):
    
    service: Optional[TayloristTTS] = None
    api_key: str
    project_id: str
    provider: TTSProvider
    model: TTSModel
    voice: TTSVoice

    @property
    def _llm_type(self) -> str:
        return "taylorist-abstract-tts"
    
    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        return "\n".join([f"{m.type.upper()}: {m.content}" for m in messages])
    
    async def agenerate(self, messages, stop = None, callbacks = None, *, tags = None, metadata = None, run_name = None, run_id = None, **kwargs):
        prompt = self._convert_messages_to_prompt(messages)

        output: OutputTTS = await self.service.chat_async(
            project_id= self.project_id,
            provider= self.provider,
            model= self.model,
            voice= self.voice,
            prompt= prompt
        )

        ai_message = AIMessage(
            content= output.file_path,
            metadata = {"taylorist_raw": output.dict()}
        )

        return ChatResult(generations=[ChatGeneration(message=ai_message)])