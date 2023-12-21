
FROM python:3.11
EXPOSE 8501
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
CMD ["streamlit", "run", "app.py"]
