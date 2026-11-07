from common.protocol import request


async def quote(service, brief):
    return await service.unary("SendMessage", request(brief))
