FROM python:3.11-slim
COPY . .
#COPY requirements.txt

RUN pip install --user -r requirements.txt

WORKDIR /
ENV PYTHONPATH /

CMD ["python", "./telegramm_bot.py"]