import torch
import torchvision
from torchvision import transforms
from torchvision import models
from PIL import Image

# dev = torch.device('cuda:0')
dev = None

transform = transforms.Compose([
  transforms.Resize(256),
  transforms.CenterCrop(224),
  transforms.ToTensor(),
  transforms.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225])
])

img = Image.open('appl.png').convert('RGB')

tens = transform(img).unsqueeze(0)

tens = tens.requires_grad_(True)

model = models.wide_resnet50_2(pretrained=True)

if dev:
  tens.to(dev)
  model.to(dev)

model.eval()

optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)

torchvision.utils.save_image(tens, "out1.png")

for i in range(100):

    optimizer.zero_grad()
    
    output = model(tens)
    
    soft_data = torch.nn.functional.softmax(output[0], dim=0)
    
    loss = 1 - soft_data[soft_data.argmax()]
    
    loss.backward()
    
    optimizer.step()
    
    print(i)

torchvision.utils.save_image(tens, "out2.png")