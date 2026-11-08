from common.protocol import as_dict, request


async def exercise(http, brief, previous):
    return (
        await http.post(
            "/message:send",
            headers={"Authorization": "Bearer owner", "X-Tenant": "other"},
            json=as_dict(request(brief)),
        )
    ).status_code
