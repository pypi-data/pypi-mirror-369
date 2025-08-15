from pydantic import BaseModel

class OutputAI(BaseModel):
      project_id: str

"""
{
  "project_id": "723f4e98-d616-4ce2-9a1b-2ed4a1bafd17",
  "model_name": "mistral-medium-2505",
  "latency": 1.3263087999075651,
  "input": "selam",
  "reasoning": "stop",
  "output": "Merhaba! 👋 Nasıl yardımcı olabilirim? Bir proje hakkında sorularınız mı var, yoksa kodlama konusunda yardım mı istiyorsunuz? 😊",
  "input_token": 15,
  "cached_token": 0,
  "reasoning_token": 0,
  "output_token": 46,
  "input_cost": 0.00007500000000000001,
  "cached_cost": 0,
  "reasoning_cost": 0,
  "output_cost": 0.00069,
  "total_cost": 0.00069
}
"""

class OutputLLM(OutputAI):
      project_id: str
      model_name: str
      latency: float
      input: str
      reasoning: str
      output: str
      input_token: int
      cached_token: int
      reasoning_token: int
      output_token: int
      input_cost: float
      cached_cost: float
      reasoning_cost: float
      output_cost: float
      total_cost: float

class OutputSTT(OutputAI):
      project_id: str
      model_name: str
      audio_file_minute: int
      text: str
      total_cost: float

class OutputTTS(OutputAI):
      project_id: str
      model_name: str
      file_path: str
      mp3_minute: int
      total_cost: float