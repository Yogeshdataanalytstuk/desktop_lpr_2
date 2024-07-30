import torch
import os
import sys
import cv2
import numpy as np
from alphabets import plate_chr  # Import character mapping for license plates
from LPRNet import build_lprnet  # Import the model architecture
from plateNet import myNet_ocr




def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

def preprocess_image(img, img_size):
    """ Resize and normalize the image """
    img = cv2.resize(img, img_size)
    img = img.astype(np.float32) / 255.0
    img -= 0.588
    img /= 0.193
    img = img.transpose(2, 0, 1)  # Channels first
    return torch.tensor(img).unsqueeze(0)  # Add batch dimension

def decode_plate(preds):
    """ Decode the predictions to a string """
    preds = preds[preds != 0]
    unique_preds = [pred for i, pred in enumerate(preds) if pred != preds[i-1]]
    return ''.join(plate_chr[int(p)] for p in unique_preds)

def load_model(model_path, device):
    """ Load the model from the specified path """
    model = build_lprnet(len(plate_chr), export=True)
    model.load_state_dict(torch.load(model_path, map_location=device)['state_dict'])
    model.to(device).eval()
    return model

def recognize_plate(img, model, device):
    """ Recognize the license plate from the image """
    img = preprocess_image(img, (168, 48))  # Image dimensions expected by the model
    with torch.no_grad():
        preds = model(img.to(device)).argmax(dim=2)
    return decode_plate(preds.view(-1).cpu().numpy())

def init_model(device, model_path):
    check_point = torch.load(model_path, map_location=device)
    model_state = check_point['state_dict']
    cfg = check_point['cfg']
    model = myNet_ocr(num_classes=len(plate_chr), export=True, cfg=cfg)
    model.load_state_dict(model_state)
    model.to(device)
    model.eval()
    return model


# Example usage
def numperpred(image_array):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = resource_path("saved_model/best.pth")
    model = init_model(device, model_path)
    plate_text = recognize_plate(image_array, model, device)
    #print("Recognized License Plate:", plate_text)
    return plate_text
