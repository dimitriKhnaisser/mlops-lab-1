import os

import mlflow
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
from torchvision import transforms

app = FastAPI()

MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000"
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

LABELS = {
    0: "Bread",
    1: "Dairy product",
    2: "Dessert",
    3: "Egg",
    4: "Fried food",
    5: "Meat",
    6: "Noodles-Pasta",
    7: "Rice",
    8: "Seafood",
    9: "Soup",
    10: "Vegetable-Fruit",
}

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])

model = None


def get_model():
    global model

    if model is None:
        model = mlflow.pyfunc.load_model("models:/food11@champion")

    return model


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image = Image.open(file.file).convert("RGB")
        image_tensor = transform(image).unsqueeze(0)

        predictions = get_model().predict(image_tensor.numpy())

        logits = torch.tensor(predictions)
        probabilities = torch.softmax(logits, dim=1)

        confidence, predicted_class = torch.max(probabilities, dim=1)

        class_id = predicted_class.item()

        return {
            "category": LABELS[class_id],
            "confidence": round(confidence.item(), 4),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))