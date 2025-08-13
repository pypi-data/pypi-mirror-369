from typing import Type

from google import genai
from google.genai import types
from openai import AsyncOpenAI
from pydantic import BaseModel


class OpenaiInference:
    def __init__(self):
        self.openai_client = AsyncOpenAI(timeout=120)

    async def infer(self,
                    model_name: str,
                    system_prompt: str,
                    user_prompt: str,
                    reasoning_effort: str) -> str:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        completion = await self.openai_client.chat.completions.create(
            messages=messages,
            model=model_name,
            reasoning_effort=reasoning_effort
        )
        return completion.choices[0].message.content

    async def infer_json(self,
                         model_name: str,
                         system_prompt: str,
                         user_prompt: str,
                         reasoning_effort: str,
                         response_format: Type[BaseModel]) -> BaseModel:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        completion = await self.openai_client.beta.chat.completions.parse(
            response_format=response_format,
            messages=messages,
            model=model_name,
            reasoning_effort=reasoning_effort
        )
        return completion.choices[0].message.parsed


class GoogleInference:
    def __init__(self, api_key):
        self.google_client = genai.Client(api_key=api_key)

    async def infer(self,
                    model_name: str,
                    system_prompt: str,
                    user_prompt: str) -> str:
        response = await self.google_client.aio.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            ),
        )
        return response.text

    async def infer_json(self,
                         model_name: str,
                         system_prompt: str,
                         user_prompt: str,
                         response_format: Type[BaseModel]) -> BaseModel:
        response = await self.google_client.aio.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=response_format
            ),
        )
        return response.parsed

    async def infer_from_file(self,
                              model_name: str,
                              system_prompt: str,
                              user_prompt: str,
                              file_path: str) -> str:
        file = await self.google_client.aio.files.upload(file=file_path)
        response = await self.google_client.aio.models.generate_content(
            model=model_name,
            contents=[user_prompt, file],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            ),
        )
        return response.text
