from openai import OpenAI, AsyncOpenAI
from tqdm import tqdm
import asyncio
from types import SimpleNamespace

class VllmOnlinePredictor:
    def __init__(self, model_path, url="http://localhost:8000/v1", api_key="EMPTY" max_concurrent_requests=256):
        self.client = AsyncOpenAI(api_key=api_key, base_url=url)
        self.model_path = model_path
        self.max_concurrent_requests =  max_concurrent_requests
        print("Warning:sampling_params only use temperature, top_p, max_tokens, n")

    async def _generate_one(self, message, sampling_params, enable_thinking):
        async with self.semaphore:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_path,
                    messages=message,
                    temperature=sampling_params.temperature,
                    top_p=sampling_params.top_p,
                    max_tokens=sampling_params.max_tokens,
                    n=sampling_params.n,
                    extra_body={
                        "repetition_penalty": sampling_params.repetition_penalty,
                        "chat_template_kwargs": {"enable_thinking": enable_thinking}
                    },
                )
            except Exception as e:
                print(f"Error: {e}")
                response = SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content="")) for _ in range(sampling_params.n)]
                )
            self.pbar.update(1)
            return response

    async def _generate(self, messages, sampling_params, enable_thinking):
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        self.pbar = tqdm(total=len(messages), desc="Generating")
        tasks = [
            self._generate_one(message, sampling_params, enable_thinking)
            for message in messages
        ]
        responses = await asyncio.gather(*tasks)
        self.pbar.close()
        return responses

    def generate(self, messages, sampling_params, enable_thinking=False):
        return asyncio.run(self._generate(messages, sampling_params, enable_thinking))
