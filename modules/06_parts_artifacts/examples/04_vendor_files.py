"""Receive a real PDF quote and SVG floor plan as raw file Parts.

Concepts: artifact Parts, raw bytes, base64 and media types.
Spec: https://a2a-protocol.org/v1.0.1/specification/
Run: uv run python modules/06_parts_artifacts/examples/04_vendor_files.py
Agents: in-process; no separate services or LLM.
Expected: venues has mediaType image/svg+xml; catering has application/pdf.
"""

import asyncio
import base64
import json

from common.protocol import as_dict, request
from common.testing import client


async def main() -> None:
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
                        # KEY IDEA: ProtoJSON carries binary Parts as base64 text.
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
