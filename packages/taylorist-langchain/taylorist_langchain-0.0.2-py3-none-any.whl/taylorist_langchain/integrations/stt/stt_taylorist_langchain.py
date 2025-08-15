from typing import Any, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from taylorist import TayloristSTT, STTModel, STTProvider, OutputSTT

class TayloristSTTChatModel(BaseChatModel):

    service: Optional[TayloristSTT] = None
    api_key: str
    project_id: str
    provider: STTProvider
    model: STTModel
    
    def model_post_init(self, context):
        self.service = TayloristSTT(api_key=self.api_key)

    @property
    def _llm_type(self) -> str:
        return "taylorist-abstract-stt"
    
    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        return "\n".join([f"{m.type.upper()}: {m.content}" for m in messages])
    
    async def _agenerate(self, 
                         messages, 
                         stop = None, 
                         run_manager = None, 
                         **kwargs):
        """
        Parameters:
        message -> enter to file path of audio

        Returned -- *OutputSTT*:
        text -> raw text of model response
        total_cost -> model call cost
        """
        prompt = self._convert_messages_to_prompt(messages)

        output: OutputSTT = await self.service.chat_async(
            project_id= self.project_id,
            provider=self.provider,
            model= self.model,
            audio_file_path= prompt,
        )

        ai_message = AIMessage(
            content= output.text,
            metadata = {"taylorist_raw": output.dict()}
        )

        return ChatResult(generations=[ChatGeneration(message=ai_message)])