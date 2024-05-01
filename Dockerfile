FROM python:3.12-bullseye
COPY ./scripts/requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]