async def exercise(http, brief, previous):
    return (
        await http.post("/rpc", content="{not-json", headers={"Content-Type": "application/json"})
    ).json()["error"]["code"]
