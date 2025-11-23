FROM python:3.9-slim
WORKDIR /app
COPY src/ .
RUN pip install -r requirements.txt
RUN mkdir -p /app/logs
RUN chmod -R 777 /app/logs
CMD ["python", "app.py"]