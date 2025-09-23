FROM python:3.10-slim
RUN apt-get update && apt-get install -y ffmpeg
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "HoshiidesuBot/main.py"]