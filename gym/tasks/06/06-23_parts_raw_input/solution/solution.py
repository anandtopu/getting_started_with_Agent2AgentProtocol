from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    from a2a.types import Part

    message = request(brief)
    message.message.parts.append(
        Part(
            raw=b"synthetic-artwork", filename="artwork.bin", media_type="application/octet-stream"
        )
    )
    return (await http.post("/message:send", json=as_dict(message))).json()["task"]
