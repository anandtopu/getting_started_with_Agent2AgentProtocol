async def exercise(http, brief, previous):
    response = await http.get("/tasks/never-created")
    return {
        "status": response.status_code,
        "reason": response.json()["error"]["details"][0]["reason"],
    }
