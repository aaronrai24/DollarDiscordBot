FROM python:3.12-bullseye
WORKDIR /app
COPY ./scripts/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]