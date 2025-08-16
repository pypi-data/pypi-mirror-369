async def openai_embedding(texts: list[str], model: str = "text-embedding-3-large") -> list[list[float]]:
    import openai
    client = openai.AsyncOpenAI()
    resp = await client.embeddings.create(input=texts, model=model)
    return [d.embedding for d in resp.data]
