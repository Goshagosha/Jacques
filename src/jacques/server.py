from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from loguru import logger
from .core.rule import OverridenRule, RuleModel
from .core.jacques import Jacques
import uvicorn
import argparse

# only for incoming post
class ExampleModel(BaseModel):
    id: str
    dsl: str
    code: str


# only for post response
class Status(BaseModel):
    id: str
    status: str


class TranslationRequest(BaseModel):
    dsl: str


class TranslationResponse(BaseModel):
    result: str


app = FastAPI()
jacques = Jacques()


@app.post("/push_example", response_model=Status)
async def push_example(example: ExampleModel):
    logger.info(f"Server received an example: {example}")
    id = example.id
    try:
        jacques.push_example(example.dsl, example.code)
    except Exception as e:
        logger.error(f"Server failed to push example: {e}")
        return Status(id=id, status="warning")
    return Status(id=id, status="ok")


@app.get("/get_rule_source/{rule_id}", response_model=OverridenRule.OverridenRuleModel)
async def get_rule_source(rule_id: str):
    logger.info(f"Server received a request for rule source: {rule_id}")
    rule = jacques.ruleset[rule_id]
    return rule.to_overriden_rule_model()


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    logger.info(f"Server received a translation request: {request}")
    result = jacques.code_generator(request.dsl)[0]
    return TranslationResponse(result=result)


@app.post("/override_rule", response_model=Status)
async def override(rule: OverridenRule.OverridenRuleModel):
    logger.info(f"Server received a rule override: {rule}")
    try:
        jacques.override_rule(OverridenRule.from_model(rule))
    except Exception as e:
        logger.error(f"Rule override failed: {e}")
        return Status(id=rule.id, status="warning")
    return Status(id=rule.id, status="ok")


@app.post("/process_all_examples", response_model=Status)
async def process_all_examples():
    jacques.process_all_examples()
    return Status(id=-1, status="All examples processed")


@app.get(
    "/get_rules",
    response_model=List[RuleModel | OverridenRule.OverridenRuleModel],
    response_model_exclude_unset=True,
)
async def get_rules():
    rules = [rule.to_model() for rule in jacques.ruleset.values()]
    return rules


@app.get("/reset", response_model=Status)
async def reset():
    jacques.reset()
    return Status(id=-1, status="ok")


class JacquesServer:
    def __init__(self, host: str, port: int):
        config = uvicorn.Config(app=app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config=config)
        server.run()
