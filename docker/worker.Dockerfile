FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app/src

COPY . /app

CMD ["python", "-m", "cortex.workers.entrypoints.cpu"]
