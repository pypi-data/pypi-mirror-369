from openai import OpenAI
from typing import Dict, Any, Optional

class LLMClient:
    """LLM客户端，封装OpenAI API调用"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = OpenAI(
            api_key=config.get('api_key'),
            base_url=config.get('base_url')
        )
    
    def generate_command(self, user_input: str, prompt: Optional[str] = None) -> str:
        """根据用户输入生成命令"""
        if not prompt:
            prompt = self.config.get('default_prompt', '你现在是一个终端助手,用户输入想要生成的命令,你来输出一个命令,不要任何多余的文本!')
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.get('model'),
                messages=messages,
                temperature=0.1,
                max_tokens=100
            )
            
            command = response.choices[0].message.content.strip()
            return command
        except Exception as e:
            raise Exception(f"LLM调用失败: {str(e)}")
