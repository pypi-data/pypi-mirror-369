import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import copy

# Device config
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Image size
imsize = 512 if torch.cuda.is_available() else 256

# Transforms
loader = transforms.Compose([
    transforms.Resize(imsize),
    transforms.CenterCrop(imsize),
    transforms.ToTensor()
])
unloader = transforms.ToPILImage()

import numpy as np
import cv2

# Load image
def load_image(image_np):
    image_pil = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
    image = loader(image_pil).unsqueeze(0)
    return image.to(device, torch.float)

# Save image
def save_image(tensor):
    image = tensor.cpu().clone().squeeze(0)
    image_pil = unloader(image.clamp(0, 1))
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

# Loss Modules
class ContentLoss(nn.Module):
    def __init__(self, target):
        super(ContentLoss, self).__init__()
        self.target = target.detach()

    def forward(self, input):
        self.loss = F.mse_loss(input, self.target)
        return input

class StyleLoss(nn.Module):
    def __init__(self, target_feature):
        super(StyleLoss, self).__init__()
        self.target_gram = gram_matrix(target_feature).detach()

    def forward(self, input):
        G = gram_matrix(input)
        self.loss = F.mse_loss(G, self.target_gram)
        return input

# Normalization
class Normalization(nn.Module):
    def __init__(self, mean, std):
        super().__init__()
        self.mean = torch.tensor(mean).view(-1, 1, 1).to(device)
        self.std = torch.tensor(std).view(-1, 1, 1).to(device)
    def forward(self, img):
        return (img - self.mean) / self.std

# Gram matrix
def gram_matrix(input_tensor):
    b, c, h, w = input_tensor.size()
    features = input_tensor.view(b * c, h * w)
    G = torch.mm(features, features.t())
    return G.div(b * c * h * w)

# Layers to use
content_layers = ['conv_4']
style_layers = ['conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5']

def get_style_model_and_losses(cnn, norm_mean, norm_std, style_img, content_img):
    cnn = copy.deepcopy(cnn).to(device).eval()
    normalization = Normalization(norm_mean, norm_std).to(device)

    content_losses = []
    style_losses = []

    model = nn.Sequential(normalization)
    i = 0
    for layer in cnn.children():
        if isinstance(layer, nn.Conv2d):
            i += 1
            name = f'conv_{i}'
        elif isinstance(layer, nn.ReLU):
            name = f'relu_{i}'
            layer = nn.ReLU(inplace=False)
        elif isinstance(layer, nn.MaxPool2d):
            name = f'pool_{i}'
        elif isinstance(layer, nn.BatchNorm2d):
            name = f'bn_{i}'
        else:
            name = f'layer_{i}'

        model.add_module(name, layer)

        if name in content_layers:
            target = model(content_img).detach()
            cl = ContentLoss(target)
            model.add_module(f"content_loss_{i}", cl)
            content_losses.append(cl)

        if name in style_layers:
            sl = StyleLoss(model(style_img).detach())
            model.add_module(f"style_loss_{i}", sl)
            style_losses.append(sl)

    return model, style_losses, content_losses

def apply_neural_style_transfer(content_image_np, style_image_np, steps=300, style_weight=1e6, content_weight=1):
    print(f"Starting style transfer with content image and style image")
    content_img = load_image(content_image_np)
    style_img = load_image(style_image_np)
    print("Images loaded successfully.")

    assert content_img.size() == style_img.size(), \
        "Content and style images must be the same size."

    # Initialize input_img with content_img and add a small amount of random noise
    input_img = content_img.clone() + torch.randn_like(content_img) * 0.01
    input_img.clamp_(0, 1) # Ensure pixel values remain in valid range

    cnn = models.vgg19(pretrained=True).features.to(device).eval()
    cnn_norm_mean = [0.485, 0.456, 0.406]
    cnn_norm_std = [0.229, 0.224, 0.225]

    model, style_losses, content_losses = get_style_model_and_losses(
        cnn, cnn_norm_mean, cnn_norm_std, style_img, content_img)

    optimizer = optim.LBFGS([input_img.requires_grad_()])

    run = [0]
    while run[0] <= steps:
        def closure():
            input_img.data.clamp_(0, 1)
            optimizer.zero_grad()
            model(input_img)
            style_score = sum(sl.loss for sl in style_losses) * style_weight
            content_score = sum(cl.loss for cl in content_losses) * content_weight
            loss = style_score + content_score
            loss.backward()
            run[0] += 1
            if run[0] % 50 == 0:
                print(f"Step {run[0]}: Style {style_score.item():.4f} Content {content_score.item():.4f}")
            return loss
        optimizer.step(closure)

    input_img.data.clamp_(0, 1)
    output_image_np = save_image(input_img)
    print("Style transfer completed.")
    return output_image_np