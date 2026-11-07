FROM python:3.13-slim
WORKDIR /course
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /usr/local/bin/uv
COPY . .
RUN uv sync --locked --no-dev
RUN useradd --create-home learner && chown -R learner:learner /course
USER learner
ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "--no-sync", "maplewood", "--vendor", "venues", "--host", "0.0.0.0"]
