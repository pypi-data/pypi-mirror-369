# Standard Packages
from pathlib import Path
from typing import Optional

# Modality Definations - Provider | Model
from taylorist.ai.tts.provider_defination import TTSProvider
from taylorist.ai.tts.model_defination import TTSModel

# I/O Types
from taylorist.ai.types.io_types import OutputTTS

# Server
from taylorist.server.server import TayloristServer

# Converters
from taylorist.converters.converter_input import ConverterJson, Payload, FileDownload

class TayloristTTS:
      def __init__(self, api_key: str) -> None:
            self.__server = TayloristServer()
            self.api_key = api_key

      def chat(self,
               prompt: str,
               instruction: Optional[str] = None,
               voice: Optional[str] = None,
               model: Optional[TTSModel] = "tts-1",
               provider: Optional[TTSProvider] = "OpenAI",
               project_id: Optional[str] = None) -> OutputTTS:
            pass


      async def chat_async(self,
                           prompt: str,
                           instruction: Optional[str] = None,
                           voice: Optional[str] = None,
                           model: Optional[TTSModel] = "tts-1",
                           provider: Optional[TTSProvider] = "OpenAI",
                           project_id: Optional[str] = None) -> OutputTTS:
            
            """create-payload"""
            payload = ConverterJson.convert_tts_json(
                  api_key= self.api_key,
                  project_id= project_id,
                  provider= provider,
                  model= model,
                  instruction= instruction,
                  prompt = prompt,
                  voice= voice
            )
            
            """api request"""
            api : OutputTTS = await self.__server.chat_async(
                  modality= "tts",
                  payload= payload,
            )

            filename = Path(api.file_path).name

            """file download"""
            file_download = await self.__server.file_download(
                  modality="tts",
                  file= FileDownload(
                        file_download= True,
                        filepath= filename
                  )
            )
            api.file_path = str(file_download)

            """returned"""    
            return api