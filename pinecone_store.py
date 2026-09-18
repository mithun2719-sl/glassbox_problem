from config import PINECONE_API_KEY, PINECONE_INDEX


def connection_status() -> dict:
    return {"configured": bool(PINECONE_API_KEY), "index": PINECONE_INDEX, "note": "Local lexical retrieval is used for the offline demo; this module is the Pinecone integration boundary."}
