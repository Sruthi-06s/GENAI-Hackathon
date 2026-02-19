import torch
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from torchvision.models import mobilenet_v2

# Dataset path
data_dir = "../../dataset/crop"

# Transform images
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# Load dataset
dataset = ImageFolder(data_dir, transform=transform)
loader = DataLoader(dataset, batch_size=16, shuffle=True)

# Load pretrained MobileNetV2
model = mobilenet_v2(pretrained=True)
model.classifier[1] = torch.nn.Linear(1280, len(dataset.classes))

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Train (few epochs for hackathon)
for epoch in range(3):  # 3 epochs = fast hackathon demo
    total_loss = 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
    print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}")

# Save model
torch.save(model.state_dict(), "model.pth")
print("Model trained and saved ✅")
