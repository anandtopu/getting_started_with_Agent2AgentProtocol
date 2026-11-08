"""File signatures, PDF cross-reference offsets and actual multi-part A2A output."""

import base64
import xml.etree.ElementTree as ET

from common.artifact_files import floor_plan, quote_pdf
from common.protocol import as_dict, request
from common.testing import client


def test_real_file_formats():
    part = quote_pdf(40, 96000)
    data = part.raw
    assert data.startswith(b"%PDF-1.4") and data.endswith(b"%%EOF\n")
    xref = int(data.split(b"startxref\n")[1].splitlines()[0])
    assert data[xref:].startswith(b"xref\n")
    rows = data[xref:].splitlines()[3:8]
    for index, row in enumerate(rows, 1):
        assert data[int(row[:10]) :].startswith(f"{index} 0 obj".encode())
    assert b"USD 960.00" in data
    assert ET.fromstring(floor_plan().raw).tag.endswith("svg")


async def test_catering_quote_contains_data_and_pdf():
    async with client("catering") as http:
        response = await http.post(
            "/message:send",
            json=as_dict(request({"guests": 40, "dietary": {"vegan": 40}, "include_files": True})),
        )
        parts = response.json()["task"]["artifacts"][0]["parts"]
        assert parts[0]["data"]["guests"] == 40
        assert parts[1]["mediaType"] == "application/pdf"
        assert base64.b64decode(parts[1]["raw"]).startswith(b"%PDF-")
