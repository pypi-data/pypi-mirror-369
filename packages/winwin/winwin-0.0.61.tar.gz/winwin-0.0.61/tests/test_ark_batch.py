import os
import uvloop
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

from winwin.ark.batch_infer import *


async def test_async_batch_inference():
    upload_file = Path(__file__).parent / "resource/data.jsonl"
    response = await create_batch_inference_job(upload_file)
    print(f"response: {response}")
