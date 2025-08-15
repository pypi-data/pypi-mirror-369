# Standard Packages
from typing import Optional

# Server
from taylorist.server.server import TayloristServer

# Types
from taylorist.ai.types.io_types import OutputSTT

# Converters
from taylorist.converters.converter_input import ConverterJson, Payload, FileDownload

class TayloristSTT:
      def __init__(self, api_key: str) -> None:
            self.api_key = api_key
            self.__server = TayloristServer()

      def chat(self) -> OutputSTT:
            pass

      async def chat_async(self,
                     audio_file_path: str,
                     project_id: Optional[str] = None,
                     provider: Optional[str] = "Deepgram",
                     model: Optional[str] = "suno-3"
                     ) -> OutputSTT:
            
            payload = ConverterJson.convert_stt_json(
                  api_key= self.api_key,
                  project_id= project_id,
                  provider= provider,
                  model= model,
                  audio_file_path= audio_file_path
            )

            api : OutputSTT = await self.__server.chat_async(
                  modality= "stt",
                  payload= payload
            )

            return api