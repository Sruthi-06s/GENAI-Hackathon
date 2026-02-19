import torch
from torchvision.models import mobilenet_v2
from PIL import Image
import torchvision.transforms as transforms

classes = ["Bacterial Leaf Blight", "Brown Spot", "Healthy Rice Leaf"]


model = mobilenet_v2()
model.classifier[1] = torch.nn.Linear(1280, len(classes))
model.load_state_dict(torch.load("model/model.pth", map_location="cpu"))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def predict(image_path):
    img = Image.open(image_path).convert("RGB")
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)
        pred = torch.argmax(outputs, 1).item()

    return classes[pred]
