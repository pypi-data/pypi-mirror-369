from typing import List

from funcdesc.desc import NotDef
from funcdesc.pydantic import desc_to_pydantic, Description
from openai import pydantic_function_tool
from funcdesc import parse_func
from hypha_rpc.utils.schema import schema_function


def desc_to_openai_dict(
        desc: Description,
        skip_params: List[str] = [],
        litellm_mode: bool = False,
        ) -> dict:

    # remove skip_params from desc.inputs
    new_inputs = []
    for arg in desc.inputs:
        if arg.name in skip_params:
            continue
        new_inputs.append(arg)
    desc.inputs = new_inputs

    pydantic_model = desc_to_pydantic(desc)['inputs']
    oai_func_dict = pydantic_function_tool(pydantic_model)
    oai_params = oai_func_dict["function"]["parameters"]["properties"]

    parameters = {}
    required = []

    for arg in desc.inputs:
        pdict = {
            "description": arg.doc or "",
        }
        oai_pdict = oai_params[arg.name]
        if "type" in oai_pdict:
            pdict["type"] = oai_pdict["type"]
        if "items" in oai_pdict:
            pdict["items"] = oai_pdict["items"]
        if "anyOf" in oai_pdict:
            pdict["anyOf"] = oai_pdict["anyOf"]

        parameters[arg.name] = pdict

        if litellm_mode:
            if arg.default is NotDef:
                required.append(arg.name)
        else:
            required.append(arg.name)

    func_dict = {
        "type": "function",
        "function": {
            "name": desc.name,
            "description": desc.doc or "",
            "strict": not litellm_mode,
        },
    }
    if (not litellm_mode) or (len(parameters) > 0):
        func_dict["function"]["parameters"] = {
            "type": "object",
            "properties": parameters,
            "required": required,
            "additionalProperties": False,
        }
    return func_dict


def func_to_hypha_schema_func(func):
    desc = parse_func(func)
    schema = desc_to_openai_dict(desc)
    sfunc = schema_function(
        func,
        name=schema.get("name"),
        description=schema.get("description"),
        parameters=schema.get("parameters"),
    )
    return sfunc
