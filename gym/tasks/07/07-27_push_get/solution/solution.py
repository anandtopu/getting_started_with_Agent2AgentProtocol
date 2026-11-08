async def exercise(http, brief, previous):
    path = "/tasks/" + previous["id"] + "/pushNotificationConfigs"
    return (await http.get(path + "/planner")).json()
