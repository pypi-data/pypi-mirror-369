# FastAPI 服务
from fastapi import FastAPI
from pydantic import BaseModel
from winwin.ark.batch_infer import create_batch_inference_job, list_batch_inference_jobs

app = FastAPI()


class Request(BaseModel):
    input: str


class JobsRequest(BaseModel):
    job_ids: list[str]


@app.post("/batch_infer/add")
async def batch_infer(request: Request):
    return await create_batch_inference_job(request.input)


@app.get("/batch_infer/jobs/status/{job_id}")
async def job_status(job_id: str):
    return await list_batch_inference_jobs([job_id])


@app.post("/batch_infer/jobs/status")
async def jobs_status(request: JobsRequest):
    return await list_batch_inference_jobs(request.job_ids)


@app.get("/status")
async def status():
    return "OK"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", port=4001, reload=True)
