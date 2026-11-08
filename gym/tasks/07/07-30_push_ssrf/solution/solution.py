async def exercise(http, brief, previous):
    path = "/tasks/" + previous["id"] + "/pushNotificationConfigs"
    return (
        await http.post(
            path,
            json={
                "taskId": previous["id"],
                "id": "planner",
                "url": "https://169.254.169.254/latest",
            },
        )
    ).status_code
