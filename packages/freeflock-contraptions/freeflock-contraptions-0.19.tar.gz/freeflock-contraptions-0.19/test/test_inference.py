import os

import pytest
from pydantic import BaseModel

from packages.freeflock_contraptions.inference import OpenaiInference, GoogleInference

api_key = os.getenv("GEMINI_API_KEY")


@pytest.mark.asyncio
async def test_infer():
    inference_client = OpenaiInference()
    model_name = "o3-mini"
    system_prompt = "You are a helpful assistant."
    user_prompt = "What is the capital of France?"
    reasoning_effort = "low"
    result = await inference_client.infer(model_name, system_prompt, user_prompt, reasoning_effort)
    assert "paris" in result.lower()
    print(result)


@pytest.mark.asyncio
async def test_infer_json():
    inference_client = OpenaiInference()
    model_name = "o3-mini"
    system_prompt = "You are a helpful assistant."
    user_prompt = "What is the capital of France?"
    reasoning_effort = "low"
    result = await inference_client.infer_json(model_name, system_prompt, user_prompt, reasoning_effort, Capital)
    assert "paris" in result.capital.lower()
    print(result)


@pytest.mark.asyncio
async def test_infer():
    inference_client = GoogleInference(api_key)
    model_name = "gemini-2.0-flash"
    system_prompt = "You are a helpful assistant."
    user_prompt = "What is the capital of France?"
    result = await inference_client.infer(model_name, system_prompt, user_prompt)
    assert "paris" in result.lower()
    print(result)


@pytest.mark.asyncio
async def test_infer_json():
    inference_client = GoogleInference(api_key)
    model_name = "gemini-2.0-flash"
    system_prompt = "You are a helpful assistant."
    user_prompt = "What is the capital of France?"
    result = await inference_client.infer_json(model_name, system_prompt, user_prompt, Capital)
    assert "paris" in result.capital.lower()
    print(result)


@pytest.mark.asyncio
async def test_infer_from_file():
    inference_client = GoogleInference(api_key)
    model_name = "gemini-2.0-flash"
    system_prompt = "You are a helpful assistant."
    user_prompt = "Describe this image."
    file_path = "test_image.jpg"
    result = await inference_client.infer_from_file(model_name, system_prompt, user_prompt, file_path)
    assert "image" in result.lower()
    print(result)


class Capital(BaseModel):
    capital: str
