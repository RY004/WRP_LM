FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app/src

COPY . /app
RUN python -m pip install --no-cache-dir .

CMD ["python", "-m", "saturn.workers.entrypoints.cpu"]
