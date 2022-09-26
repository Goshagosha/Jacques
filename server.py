from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, parse_obj_as
from loguru import logger
from jacques.core.rule import Rule, RuleModel
from jacques.core.jacques import Jacques
import uvicorn
import argparse

# only for incoming post
class ExampleModel(BaseModel):
    dsl: str
    code: str


# only for post response
class Status(BaseModel):
    status: str


app = FastAPI()
jacques = Jacques()


@app.post("/push_example", response_model=Status)
async def push_example(example: ExampleModel):
    logger.info(f"Server received an example: {example}")
    jacques.push_example(example.dsl, example.code)
    return Status(status="example received")


@app.post("/process_all_examples", response_model=Status)
async def process_all_examples():
    jacques.process_all_examples()
    return Status(status="All examples processed")


@app.get(
    "/get_rules", response_model=List[RuleModel], response_model_exclude_unset=True
)
async def get_rules():
    rules = [rule.to_model() for rule in jacques.ruleset.values()]
    return rules


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    config = uvicorn.Config(app=app, host=args.host, port=args.port, log_level="info")
    server = uvicorn.Server(config=config)
    server.run()
