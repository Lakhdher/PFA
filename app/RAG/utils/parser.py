from typing import Iterable
from langchain_core.messages.ai import AIMessageChunk

global metadata
def streaming_parser(chunks: Iterable[AIMessageChunk])-> Iterable[str]:
    for chunk in chunks:
        metadata = chunk.response_metadata
        yield chunk.content
    