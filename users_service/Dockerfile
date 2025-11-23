FROM python:3.11-slim
WORKDIR /app

COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ../common /app/common
COPY . /app/users_service

ENV PYTHONPATH="/app"

EXPOSE 5000

CMD ["python", "-m", "users_service.app"]