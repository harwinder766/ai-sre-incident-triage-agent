FROM python:3.11-slim

WORKDIR /app

COPY simulator/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY simulator/ ./simulator/

EXPOSE 8001

CMD ["uvicorn", "simulator.services.payment_api.main:app", "--host", "0.0.0.0", "--port", "8001"]