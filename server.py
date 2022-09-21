from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger
from jacques.core.jacques import Jacques


class Example(BaseModel):
    dsl: str
    code: str


class Rule(BaseModel):
    dsl: str
    code: str


class Status(BaseModel):
    status: str


app = FastAPI()
jacques = Jacques()


@app.post("/push_example", response_model=Status)
async def push_example(example: Example):
    logger.info(f"Server received an example: {example}")
    jacques.push_example(example.dsl, example.code)
    return Status(status="example received")


@app.post("/process_all_examples", response_model=Status)
async def process_all_examples():
    jacques.process_all_examples()
    return Status(status="All examples processed")
