# io
from taylorist.ai.types.io_types import OutputAI, OutputLLM, OutputSTT, OutputTTS

class ConverterOutputType:

      @staticmethod
      def convert_ai_output(modality: str, api_response) -> OutputAI:
            match modality:
                  case "llm":
                        return ConverterOutputType.convert_to_output_llm(api_response)
                  case "tts":
                        return ConverterOutputType.convert_to_output_tts(api_response)
                  case "stt":
                        return ConverterOutputType.convert_to_output_stt(api_response)
                  
      @staticmethod
      def convert_to_output_llm(api_response) -> OutputLLM:
            return OutputLLM(
                  project_id= api_response["project_id"],
                  model_name= api_response["model_name"],
                  latency= api_response["latency"],
                  input= api_response["input"],
                  reasoning= api_response["reasoning"],
                  output= api_response["output"],
                  input_token= api_response["input_token"],
                  cached_token= api_response["cached_token"],
                  reasoning_token= api_response["reasoning_token"],
                  output_token= api_response["output_token"],
                  input_cost= api_response["input_cost"],
                  cached_cost= api_response["cached_cost"],
                  reasoning_cost= api_response["reasoning_cost"],
                  output_cost= api_response["output_cost"],
                  total_cost= api_response["total_cost"]
            )

      @staticmethod
      def convert_to_output_stt(api_response) -> OutputSTT:
            return OutputSTT(
                  project_id= api_response["project_id"],
                  model_name= api_response["model"],
                  audio_file_minute= api_response["audio_file_minute"],
                  text= api_response["text"],
                  total_cost= api_response["total_cost"]
            )

      @staticmethod
      def convert_to_output_tts(api_response) -> OutputTTS:
            return OutputTTS(
                  project_id= api_response["project_id"],
                  model_name= api_response["model_name"],
                  file_path= api_response["file_path"],
                  mp3_minute= api_response["mp3_minutes"],
                  total_cost= api_response["total_cost"]
            )