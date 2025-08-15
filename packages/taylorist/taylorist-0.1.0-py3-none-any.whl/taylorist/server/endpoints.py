class Endpoints:
      def __init__(self) -> None:
            pass

      @staticmethod
      def get_endpoint(modality: str) -> str:
            if modality == "llm":
                  return "/llm-ai/chat"
            elif modality == "tts":
                  return "/tts-ai/chat"
            elif modality == "stt":
                  return "/stt-ai/chat"
            
      @staticmethod
      def get_endpoint_async(modality:str) -> str:
            if modality == "llm":
                  return "/llm-ai/chat_async"
            elif modality == "tts":
                  return "/tts-ai/chat_async"
            elif modality == "stt":
                  return "/stt-ai/chat_async"
            
      @staticmethod
      def get_file_endpoint(modality: str) -> str:
            if modality == "llm":
                  return ""
            elif modality == "stt":
                  return ""
            elif modality == "tts":
                  return "tts-ai/download"