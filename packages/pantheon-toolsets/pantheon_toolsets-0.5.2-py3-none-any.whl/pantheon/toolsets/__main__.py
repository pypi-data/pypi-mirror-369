import fire


async def remote_call(service_name_or_id: str, method_name: str, **kwargs):
    """Remote call a method of a toolset.

    Args:
        service_name_or_id: The name or id of the toolset.
        method_name: The name of the method to call.
        **kwargs: The keyword arguments to pass to the method.
    """
    from .utils.remote import connect_remote
    from pprint import pprint
    print("Connecting to service", service_name_or_id, "\n")
    service = await connect_remote(service_name_or_id)
    print("Invoking method", method_name, "with kwargs:")
    pprint(kwargs)
    print()
    result = await service.invoke(method_name, kwargs)
    print("Result:")
    pprint(result)


async def build_rag_db(yaml_path: str, output_dir: str):
    """Build a RAG database from a YAML file.

    Args:
        yaml_path: The path to the YAML file.
        output_dir: The path to the output directory.
    """
    from .utils.rag.build import build_all
    await build_all(yaml_path, output_dir)


fire.Fire({
    "build_rag_db": build_rag_db,
    "remote_call": remote_call,
})
