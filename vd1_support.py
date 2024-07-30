import torch
from plateNet import myNet_ocr
from alphabets import plate_chr
import cv2
import numpy as np


def init_model(device, model_path):
    check_point = torch.load(model_path, map_location=device)
    model_state = check_point['state_dict']
    cfg = check_point['cfg']
    model = myNet_ocr(num_classes=len(plate_chr), export=True, cfg=cfg)  # export  True 用来推理
    # model =build_lprnet(num_classes=len(plate_chr),export=True)
    model.load_state_dict(model_state)

    model.to(device)
    model.eval()
    return model
mean_value,std_value=(0.588,0.193)
def image_processing(img,device,img_size):
    img_h,img_w= img_size
    img = cv2.resize(img, (img_w,img_h))
    # img = np.reshape(img, (48, 168, 3))

    # normalize
    img = img.astype(np.float32)
    img = (img / 255. - mean_value) / std_value
    img = img.transpose([2, 0, 1])
    img = torch.from_numpy(img)

    img = img.to(device)
    img = img.view(1, *img.size())
    return img
def decodePlate(preds):
    pre=0
    newPreds=[]
    for i in range(len(preds)):
        if preds[i]!=0 and preds[i]!=pre:
            newPreds.append(preds[i])
        pre=preds[i]
    return newPreds
def get_plate_result(img,device,model,img_size):
    # img = cv2.imread(image_path)
    input = image_processing(img,device,img_size)
    preds = model(input)
    preds =preds.argmax(dim=2)
    # print(preds)
    preds=preds.view(-1).detach().cpu().numpy()
    newPreds=decodePlate(preds)
    plate=""
    for i in newPreds:
        plate+=plate_chr[int(i)]
    return plate
def preprocess(plate):
    device = torch.device("cpu")
    img_h=48
    img_w=168
    img_size = (img_h, img_w)
    model_path='best.pth'
    model = init_model(device,model_path )
    platetext = get_plate_result(plate, device, model, img_size)
    return platetext



