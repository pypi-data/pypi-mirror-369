# Standard Packages
from typing import Optional
from dataclasses import dataclass
from abc import ABC

# Types
from taylorist.ai.types.io_types import OutputLLM

# Modality Provider-Model Definations
from taylorist.ai.llm.model_defination import LLMModel
from taylorist.ai.llm.provider_defination import LLMProvider

# Server
from taylorist.server.server import TayloristServer

# Converters
from taylorist.converters.converter_input import ConverterJson, Payload

class TayloristLLM:
      def __init__(self, api_key: str):
            self.__server = TayloristServer()
            self.api_key = api_key


      def chat(self, 
               prompt: str,
               model: Optional[LLMModel] = "gpt-3.5-turbo",
               provider: Optional[LLMProvider] = "OpenAI",
               instruction: Optional[str] = "",
               project_id: Optional[str] = None,
               top_p: Optional[float] = 1,
               temperature: Optional[float] = 1,
               max_tokens: Optional[float] = None) -> OutputLLM:
            pass

      async def chat_async(self,
                     prompt: str,
                     model: Optional[LLMModel] = "gpt-4o",
                     provider: Optional[LLMProvider] = "OpenAI",
                     instruction: Optional[str] = "",
                     project_id: Optional[str] = None,
                     top_p: Optional[float] = 1,
                     temperature: Optional[float] = 1,
                     max_tokens: Optional[int] = 1000) -> OutputLLM:
      
            payload = ConverterJson.convert_llm_json(
                  api_key= self.api_key,
                  project_id= project_id,
                  provider= provider,
                  model= model,
                  instruction= instruction,
                  prompt= prompt,
                  top_p= top_p,
                  temperature= temperature,
                  max_tokens= max_tokens
            )

            api : OutputLLM = await self.__server.chat_async(
                  modality= "llm",
                  payload= payload
            )

            return api

async def main():
      llm = TayloristLLM()

      search = await llm.chat_async(prompt= "Bana havayı araştır")