import streamlit as st
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import pickle
import numpy as np

# Load model
with open('model.pkl', 'rb') as f:
    model_transfer = pickle.load(f)

# Class names
class_names = ['Affenpinscher',
 'Afghan hound',
 'Airedale terrier',
 'Akita',
 'Alaskan malamute',
 'American eskimo dog',
 'American foxhound',
 'American staffordshire terrier',
 'American water spaniel',
 'Anatolian shepherd dog',
 'Australian cattle dog',
 'Australian shepherd',
 'Australian terrier',
 'Basenji',
 'Basset hound',
 'Beagle',
 'Bearded collie',
 'Beauceron',
 'Bedlington terrier',
 'Belgian malinois',
 'Belgian sheepdog',
 'Belgian tervuren',
 'Bernese mountain dog',
 'Bichon frise',
 'Black and tan coonhound',
 'Black russian terrier',
 'Bloodhound',
 'Bluetick coonhound',
 'Border collie',
 'Border terrier',
 'Borzoi',
 'Boston terrier',
 'Bouvier des flandres',
 'Boxer',
 'Boykin spaniel',
 'Briard',
 'Brittany',
 'Brussels griffon',
 'Bull terrier',
 'Bulldog',
 'Bullmastiff',
 'Cairn terrier',
 'Canaan dog',
 'Cane corso',
 'Cardigan welsh corgi',
 'Cavalier king charles spaniel',
 'Chesapeake bay retriever',
 'Chihuahua',
 'Chinese crested',
 'Chinese shar-pei',
 'Chow chow',
 'Clumber spaniel',
 'Cocker spaniel',
 'Collie',
 'Curly-coated retriever',
 'Dachshund',
 'Dalmatian',
 'Dandie dinmont terrier',
 'Doberman pinscher',
 'Dogue de bordeaux',
 'English cocker spaniel',
 'English setter',
 'English springer spaniel',
 'English toy spaniel',
 'Entlebucher mountain dog',
 'Field spaniel',
 'Finnish spitz',
 'Flat-coated retriever',
 'French bulldog',
 'German pinscher',
 'German shepherd dog',
 'German shorthaired pointer',
 'German wirehaired pointer',
 'Giant schnauzer',
 'Glen of imaal terrier',
 'Golden retriever',
 'Gordon setter',
 'Great dane',
 'Great pyrenees',
 'Greater swiss mountain dog',
 'Greyhound',
 'Havanese',
 'Ibizan hound',
 'Icelandic sheepdog',
 'Irish red and white setter',
 'Irish setter',
 'Irish terrier',
 'Irish water spaniel',
 'Irish wolfhound',
 'Italian greyhound',
 'Japanese chin',
 'Keeshond',
 'Kerry blue terrier',
 'Komondor',
 'Kuvasz',
 'Labrador retriever',
 'Lakeland terrier',
 'Leonberger',
 'Lhasa apso',
 'Lowchen',
 'Maltese',
 'Manchester terrier',
 'Mastiff',
 'Miniature schnauzer',
 'Neapolitan mastiff',
 'Newfoundland',
 'Norfolk terrier',
 'Norwegian buhund',
 'Norwegian elkhound',
 'Norwegian lundehund',
 'Norwich terrier',
 'Nova scotia duck tolling retriever',
 'Old english sheepdog',
 'Otterhound',
 'Papillon',
 'Parson russell terrier',
 'Pekingese',
 'Pembroke welsh corgi',
 'Petit basset griffon vendeen',
 'Pharaoh hound',
 'Plott',
 'Pointer',
 'Pomeranian',
 'Poodle',
 'Portuguese water dog',
 'Saint bernard',
 'Silky terrier',
 'Smooth fox terrier',
 'Tibetan mastiff',
 'Welsh springer spaniel',
 'Wirehaired pointing griffon',
 'Xoloitzcuintli',
 'Yorkshire terrier']  # <-- Paste your full class_names list here

# VGG16 for dog detection
VGG16 = models.vgg16(pretrained=True)
VGG16.eval()
use_cuda = torch.cuda.is_available()
if use_cuda:
    VGG16 = VGG16.cuda()

# Standard normalization
standard_normalization = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                              std=[0.229, 0.224, 0.225])

# Load and preprocess image
def load_input_image(img):
    image = Image.open(img).convert('RGB')
    prediction_transform = transforms.Compose([
        transforms.Resize(size=(224, 224)),
        transforms.ToTensor(),
        standard_normalization
    ])
    image = prediction_transform(image)[:3, :, :].unsqueeze(0)
    return image

# VGG16 dog detector
def VGG16_predict(img):
    image = Image.open(img).convert('RGB')
    transform = transforms.Compose([
        transforms.Resize((244, 244)),
        transforms.ToTensor()
    ])
    img_tensor = transform(image)[:3, :, :].unsqueeze(0)
    if use_cuda:
        img_tensor = img_tensor.cuda()
    output = VGG16(img_tensor)
    return torch.argmax(output).item()

def dog_detector(img_path):
    idx = VGG16_predict(img_path)
    return 151 <= idx <= 268

# Predict breed
def predict_breed_transfer(model, class_names, img_path):
    img = load_input_image(img_path)
    model.eval()
    model.cpu()
    idx = torch.argmax(model(img))
    return class_names[idx]

# Streamlit UI
st.title("Dog Breed Identifier 🐶")

uploaded_file = st.file_uploader("Upload an image of a dog", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

    with open("temp_img.jpg", "wb") as f:
        f.write(uploaded_file.read())

    if dog_detector("temp_img.jpg"):
        prediction = predict_breed_transfer(model_transfer, class_names, "temp_img.jpg")
        st.success(f"Dogs Detected!\nIt looks like a **{prediction}**")
    else:
        st.error("Error! Can't detect a dog in the image.")
