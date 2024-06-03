from typing import Iterable
from langchain_core.messages.ai import AIMessageChunk

global metadata
def streaming_parser(chunks: Iterable[AIMessageChunk])-> Iterable[str]:
    global metadata
    for chunk in chunks:
        metadata = chunk.response_metadata
        chunk.content = chunk.content.replace("src", '').replace(".pdf", '').replace('\\', '')
        yield chunk.content

def get_metadata():
    global metadata
    return metadata