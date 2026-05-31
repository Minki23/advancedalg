FROM python:3.11-slim
WORKDIR /app
COPY CITIZEN_DATA_MANAGER.py /app/CITIZEN_DATA_MANAGER.py
RUN pip install fastapi uvicorn
CMD ["python", "CITIZEN_DATA_MANAGER.py", "api"]
