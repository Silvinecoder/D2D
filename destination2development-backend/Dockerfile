FROM python:3.13-slim

WORKDIR /destination2development-backend

RUN pip install uv

COPY pyproject.toml uv.lock README.md ./

RUN uv sync

COPY . .

COPY app/scripts/start.sh /start.sh

RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]