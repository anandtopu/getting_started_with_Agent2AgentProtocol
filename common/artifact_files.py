"""Small valid synthetic files for the Parts lesson; no external storage required."""

from a2a.types import Part


def quote_pdf(guests, cents):
    text = f"Maplewood catering quote: {guests} guests; USD {cents / 100:.2f}. Approval required."
    stream = f"BT /F1 12 Tf 36 760 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output, offsets = bytearray(b"%PDF-1.4\n"), [0]
    for index, value in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode() + value + b"\nendobj\n")
    start = len(output)
    output.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode()
    )
    return Part(raw=bytes(output), filename="catering-quote.pdf", media_type="application/pdf")


def floor_plan():
    image = b'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360"><rect width="640" height="360" fill="white"/><rect x="20" y="20" width="600" height="320" fill="#edf4fa" stroke="#173d57" stroke-width="4"/><rect x="220" y="30" width="200" height="55" fill="#173d57"/><text x="275" y="65" fill="white" font-size="18">STAGE</text><g fill="#73b4ba"><rect x="80" y="140" width="180" height="130"/><rect x="380" y="140" width="180" height="130"/></g><text x="247" y="315" font-size="18">EXIT / AISLE</text></svg>'
    return Part(raw=image, filename="granite-floor-plan.svg", media_type="image/svg+xml")
