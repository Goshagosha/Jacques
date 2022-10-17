from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, parse_obj_as
from loguru import logger
from jacques.core.rule import OverridenRule, Rule, RuleModel
from jacques.core.jacques import Jacques
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


@app.get(
    "/get_rule_source/{rule_name}", response_model=OverridenRule.OverridenRuleModel
)
async def get_rule_source(rule_name: str):
    logger.info(f"Server received a request for rule source: {rule_name}")
    rule = jacques.ruleset[rule_name]
    return rule.to_overriden_rule_model()


@app.post("/override_rule", response_model=Status)
async def override(rule: OverridenRule.OverridenRuleModel):
    logger.info(f"Server received a rule override: {rule}")
    try:
        jacques.override_rule(OverridenRule.from_model(rule))
    except Exception as e:
        logger.error(f"Rule override failed: {e}")
        return Status(id=rule.name, status="warning")
    return Status(id=rule.name, status="ok")


@app.get("/process_all_examples", response_model=Status)
async def process_all_examples():
    jacques.process_all_examples()
    return Status(id=-1, status="All examples processed")


@app.get(
    "/get_rules", response_model=List[RuleModel], response_model_exclude_unset=True
)
async def get_rules():
    rules = [rule.to_model() for rule in jacques.ruleset.values()]
    return rules


@app.get("/reset", response_model=Status)
async def get_rules():
    jacques.reset()
    return Status(id=-1, status="ok")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    config = uvicorn.Config(app=app, host=args.host, port=args.port, log_level="info")
    server = uvicorn.Server(config=config)
    server.run()
