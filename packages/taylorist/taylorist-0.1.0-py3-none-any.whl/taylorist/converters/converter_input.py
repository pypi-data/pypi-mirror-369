from typing import Union, Optional
from dataclasses import dataclass

@dataclass
class FileDownload:
      file_download: Optional[bool]
      filepath: Optional[str]

@dataclass
class Payload:
      json_data: Optional[dict]
      form_data: Optional[dict]
      file_data: Optional[dict]
      output_download: Optional[FileDownload]

class ConverterJson:

      @staticmethod
      def convert_llm_json(
            api_key: str,
            project_id: str,
            provider: str,
            model: str,
            instruction: str,
            prompt: str,
            top_p: float,
            temperature: float,
            max_tokens: int) -> Payload:
            
            return Payload(
                  json_data= {
                        "api_key": api_key,
                        "project_id": project_id,
                        "provider": provider,
                        "model": model,
                        "instruction": instruction,
                        "prompt": prompt,
                        "temperature": temperature,
                        "top_p": top_p,
                        "max_tokens": max_tokens
                  },
                  form_data= None,
                  file_data= None,
                  output_download= None
            )
      
      @staticmethod
      def convert_stt_json(
            api_key: str,
            audio_file_path: str,
            project_id: str,
            provider: str,
            model: str
      ) -> Payload:
            return Payload(
                  json_data= {
                  },
                  form_data = {
                        "api_key": api_key,
                        "project_id": project_id,
                        "provider": provider,
                        "model": model
                  },
                  file_data= {
                        "audio_file": open(audio_file_path, "rb")
                  },
                  output_download= FileDownload(
                        file_download= False,
                        filepath= None
                  )
            )
            

      @staticmethod
      def convert_tts_json(
            api_key: str,
            project_id: str,
            provider: str,
            model: str,
            instruction: str,
            prompt: str,
            voice: str
      ) -> Payload:
            return Payload(
                  json_data={
                        "api_key": api_key,
                        "project_id": project_id,
                        "provider": provider,
                        "model": model,
                        "voice": voice,
                        "instruction": instruction,
                        "prompt": prompt
                  },
                  form_data= None,
                  file_data= None,
                  output_download= FileDownload(
                        file_download= True,
                        filepath= ""
                  )
            )