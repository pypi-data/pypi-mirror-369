from typing import Any, Dict, List, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from taylorist import TayloristLLM, LLMModel, LLMProvider, OutputLLM

class TayloristLLMChatModel(BaseChatModel):

    api_key: str
    service: Optional[TayloristLLM] = None
    project_id: str
    provider: LLMProvider
    model: LLMModel
    instruction: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        self.service = TayloristLLM(api_key=self.api_key)

    @property
    def _llm_type(self) -> str:
        return "taylorist-abstract-llm"

    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        return "\n".join([f"{m.type.upper()}: {m.content}" for m in messages])

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        prompt = self._convert_messages_to_prompt(messages)
        output: OutputLLM = await self.service.chat_async(
            project_id=self.project_id,
            provider=self.provider,
            model=self.model,
            instruction=self.instruction,
            prompt=prompt
        )
        ai_message = AIMessage(
            content=output.output,
            metadata={"taylorist_raw": output.dict()}
        )
        return ChatResult(generations=[ChatGeneration(message=ai_message)])

    async def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        return await self._agenerate(messages, stop, run_manager, **kwargs)
