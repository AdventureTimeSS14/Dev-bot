FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y libmariadb-dev gcc g++ build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install discord.py disnake discord.py-self

COPY .env /app/.env
ENV $(cat /app/.env | xargs)

CMD ["python", "main.py"]
