FROM python:3.11-slim
RUN mkdir -p "/C:/Users/User/Desktop/USJ courses/semester 3 AI/MLOPS/Lab 1/mlops-lab-1" \
    && ln -s /mlflow-data/mlruns "/C:/Users/User/Desktop/USJ courses/semester 3 AI/MLOPS/Lab 1/mlops-lab-1/mlruns"
RUN pip install --no-cache-dir mlflow

EXPOSE 5000

CMD ["mlflow", "server", \
     "--host", "0.0.0.0", "--port", "5000", \
     "--backend-store-uri", "sqlite:////mlflow-data/mlflow.db", \
     "--default-artifact-root", "/mlflow-data/mlruns", \
     "--disable-security-middleware"]
