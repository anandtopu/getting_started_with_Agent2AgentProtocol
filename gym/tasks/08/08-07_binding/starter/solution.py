from common.protocol import request


async def quote(service, brief):
    # YOUR CODE HERE: route to the requested operation with the supplied brief.
    return await service.unary("SendMessage", request({"guests": 1}))
