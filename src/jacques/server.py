from typing import List
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from loguru import logger
from .core.rule import OverridenRule, RuleModel
from .core.jacques import Jacques


# only for incoming post
class ExampleModel(BaseModel):
    id: str
    dsl: str
    code: str


class ExportRequest(BaseModel):
    filename: str


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
    """Send an example to Jacques

    :param example: ExampleModel - example to be sent
    :return: Status"""
    logger.info(f"Server received an example: {example}")
    _id = example.id
    try:
        jacques.push_example(example.dsl, example.code)
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Server failed to push example: {e}")
        return Status(id=_id, status="warning")
    return Status(id=_id, status="ok")


@app.get(
    "/get_rule_source/{rule_id}",
    response_model=OverridenRule.OverridenRuleModel,
)
async def get_rule_source(rule_id: str):
    """Request a rule source code.

    :param rule_id: rule id
    :return: rule source code"""
    logger.info(f"Server received a request for rule source: {rule_id}")
    rule = jacques.ruleset[rule_id]
    return rule.to_overriden_rule_model()


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """Makes a request to the server to translate a DSL string into Python code.

    :param request: A TranslationRequest object containing the DSL string.
    :return: A TranslationResponse object containing the Python code."""
    logger.info(f"Server received a translation request: {request}")
    try:
        result = jacques.code_generator(request.dsl)[0]
        return TranslationResponse(result=result)
    except Exception as e:  # pylint: disable=broad-except
        logger.info(f"Server failed to translate: {e}")
        return TranslationResponse(result="")


@app.post("/override_rule", response_model=Status)
async def override(rule: OverridenRule.OverridenRuleModel):
    """Sends a rule override to backend

    :param rule: rule override object
    :return: status of the operation"""
    logger.info(f"Server received a rule override: {rule}")
    try:
        jacques.override_rule(OverridenRule.from_model(rule))
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Rule override failed: {e}")
        return Status(id=rule.id, status="warning")
    return Status(id=rule.id, status="ok")


@app.post("/process_all_examples", response_model=Status)
async def process_all_examples():
    """Process all examples supplied to jacques -- request

    :return: Status object"""
    jacques.process_all_examples()
    return Status(id=-1, status="All examples processed")


@app.get(
    "/get_rules",
    response_model=List[RuleModel | OverridenRule.OverridenRuleModel],
    response_model_exclude_unset=True,
)
async def get_rules():
    """Get all rules request:

    :return: list of rules"""
    rules = [rule.to_model() for rule in jacques.ruleset.values()]
    return rules


@app.post("/export_rules", response_model=Status)
async def export_rules(filename: ExportRequest):
    """Export rules to a file

    :param filename: filename to export to
    :return: Status object"""
    filename = filename.filename
    logger.info(f"Server received a request to export rules to {filename}")
    jacques.export_rules(filename)
    return Status(id=-1, status="ok")


@app.get("/reset", response_model=Status)
async def reset():
    """Reset the backend state.

    :return: Status object"""
    jacques.reset()
    return Status(id=-1, status="ok")


class JacquesServer:  # pylint: disable=too-few-public-methods # server should be singleton
    """
    JacquesServer is a class that runs a FastAPI server providing REST API to interact with backend.
    """

    def __init__(self, host: str, port: int):
        """
        :param host: host to run server on
        :param port: port to run server on
        """
        config = uvicorn.Config(app=app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config=config)
        server.run()
