import argparse
import os

# Fix Windows console encoding for MLflow output
os.environ["PYTHONIOENCODING"] = "utf-8"

import mlflow
import mlflow.pytorch
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("food11")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["processed", "mini"], default="mini")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    dataset_name = (
        "food11_processed_mini"
        if args.dataset == "mini"
        else "food11_processed"
    )
    data_dir = f"data/{dataset_name}"

    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])

    train_dataset = datasets.ImageFolder(
        f"{data_dir}/training",
        transform=transform
    )
    val_dataset = datasets.ImageFolder(
        f"{data_dir}/validation",
        transform=transform
    )
    test_dataset = datasets.ImageFolder(
        f"{data_dir}/evaluation",
        transform=transform
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=args.batch_size
    )

    print("Loading pretrained ResNet18...")

    model = models.resnet18(weights="DEFAULT")
    model.fc = nn.Linear(model.fc.in_features, 11)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    with mlflow.start_run():
        mlflow.log_params({
            "dataset": args.dataset,
            "epochs": args.epochs,
            "lr": args.lr,
            "batch_size": args.batch_size,
        })

        for epoch in range(args.epochs):
            model.train()
            total_loss = 0.0

            for images, labels in train_loader:
                images = images.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                outputs = model(images)
                loss = criterion(outputs, labels)

                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            train_loss = total_loss / len(train_loader)

            model.eval()
            val_loss = 0.0
            correct = 0
            total = 0

            with torch.no_grad():
                for images, labels in val_loader:
                    images = images.to(device)
                    labels = labels.to(device)

                    outputs = model(images)
                    loss = criterion(outputs, labels)

                    val_loss += loss.item()

                    _, predicted = torch.max(outputs, 1)

                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

            val_loss /= len(val_loader)
            val_accuracy = correct / total

            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("val_loss", val_loss, step=epoch)
            mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)

            print(
                f"Epoch {epoch + 1}/{args.epochs} "
                f"- train_loss: {train_loss:.4f} "
                f"- val_loss: {val_loss:.4f} "
                f"- val_accuracy: {val_accuracy:.4f}"
            )

        # Test evaluation
        model.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for images, labels in test_loader:
                images = images.to(device)
                labels = labels.to(device)

                outputs = model(images)
                _, predicted = torch.max(outputs, 1)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        test_accuracy = correct / total

        mlflow.log_metric("test_accuracy", test_accuracy)

        # Save model using pickle serialization for compatibility
        mlflow.pytorch.log_model(
            model,
            "model",
            serialization_format="pickle"
        )

        print(f"Test accuracy: {test_accuracy:.4f}")
        print("Training completed successfully.")
        print("Model logged to MLflow successfully.")


if __name__ == "__main__":
    main()