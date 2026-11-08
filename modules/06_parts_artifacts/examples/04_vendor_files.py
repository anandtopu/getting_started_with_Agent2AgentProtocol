"""Receive a real PDF quote and SVG floor plan as raw file Parts."""

import asyncio
import base64
import json

from common.protocol import as_dict, request
from common.testing import client


async def main():
    for vendor in ("venues", "catering"):
        async with client(vendor) as http:
            task = (
                await http.post(
                    "/message:send",
                    json=as_dict(
                        request({"guests": 40, "dietary": {"vegan": 40}, "include_files": True})
                    ),
                )
            ).json()["task"]
            for artifact in task["artifacts"]:
                for part in artifact["parts"]:
                    if "raw" in part:
                        data = base64.b64decode(part["raw"])
                        print(
                            json.dumps(
                                {
                                    "vendor": vendor,
                                    "artifactId": artifact["artifactId"],
                                    "filename": part["filename"],
                                    "mediaType": part["mediaType"],
                                    "bytes": len(data),
                                }
                            )
                        )


if __name__ == "__main__":
    asyncio.run(main())
