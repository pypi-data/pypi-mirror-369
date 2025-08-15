# Standard Package
import httpx
import aiofiles
from uuid import uuid4

# Taylorist Exceptions
from taylorist.errors.exception import TayloristException, TayloristAPIException

# Type
from taylorist.ai.types.io_types import OutputAI

# Helpers
from .endpoints import Endpoints
from ..converters.converter_output import ConverterOutputType
from ..converters.converter_input import Payload, ConverterJson, FileDownload
from pathlib import Path

class TayloristServer:
      def __init__(self) -> None:
            self.base_url = "https://taylorist-server-production.up.railway.app"
            self.project_root = Path(__file__).resolve().parents[2]
            self.download_root = self.project_root / "speech"     

      def chat(self, input) -> OutputAI:
            pass

      async def chat_async(self, modality: str, payload: Payload) -> OutputAI:
            try:
                  url = f"{self.base_url}{Endpoints.get_endpoint_async(modality)}"

                  timeout = httpx.Timeout(30.0)

                  async with httpx.AsyncClient(timeout= timeout) as client:
                        response = await client.post(url, json= payload.json_data, data=payload.form_data, files= payload.file_data)

                        if response.status_code == 200:
                              response_data = response.json()

                              return ConverterOutputType.convert_ai_output(modality= modality, api_response= response_data)
                        else:
                              raise TayloristAPIException(status_code= response.status_code, message= str(response))

            except httpx.HTTPError as ex:
                  raise TayloristException(status_code= 500, message=str(ex))
            
      async def file_download(self, modality: str, file: FileDownload):
            if not file.filepath:
                  raise TayloristException(400, "filepath parametresi boş")

            url = f"{self.base_url}/{Endpoints.get_file_endpoint(modality)}/{file.filepath}"

            async with httpx.AsyncClient() as client, \
                        client.stream("GET", url) as resp:
                  resp.raise_for_status()

                  target_dir = self.download_root / modality      
                  target_dir.mkdir(parents=True, exist_ok=True)
                  target_file = target_dir / f"{uuid4()}.mp3"

                  total = 0
                  async with aiofiles.open(target_file, "wb") as out_f:
                        async for chunk in resp.aiter_bytes():
                              if chunk:
                                    await out_f.write(chunk)
                                    total += len(chunk)

                  return target_file