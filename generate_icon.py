from PIL import Image, ImageDraw, ImageFont
import os

def create_game_icon():
    # 512x512 पिक्सल का हाई-क्वालिटी आइकॉन साइज
    size = (512, 512)
    image = Image.new("RGB", size, color=(40, 100, 40)) # हरा-भरा फार्मिंग बैकग्राउंड
    draw = ImageDraw.Draw(image)
    
    # बीच में गेहूं का प्रतीक या सुंदर डिजाइन (गोलाकार क्षेत्र)
    draw.ellipse([100, 60, 412, 370], fill=(210, 180, 140)) # हल्का भूरा बेस
    draw.rectangle([236, 120, 276, 320], fill=(255, 215, 0)) # सुनहरा गेहूं का डंठल
    
    # गेहूं के दाने (छोटे डॉट्स)
    for y in range(140, 300, 30):
        draw.ellipse([210, y, 230, y+20], fill=(255, 255, 100))
        draw.ellipse([282, y, 302, y+20], fill=(255, 255, 100))

    # नीचे टेक्स्ट "Farming Game" लिखना
    try:
        # सिस्टम फोंट का उपयोग करने का प्रयास
        font = ImageFont.truetype("arial.ttf", 45)
    except:
        font = ImageFont.load_default()
        
    # टेक्स्ट को सेंटर में लिखना
    text = "Farming Game"
    # textbbox का उपयोग करके टेक्स्ट की चौड़ाई/ऊंचाई निकालना
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (size[0] - text_width) / 2
    text_y = 410
    
    # टेक्स्ट के लिए बैकग्राउंड पट्टी
    draw.rectangle([text_x - 15, text_y - 10, text_x + text_width + 15, text_y + text_height + 15], fill=(20, 50, 20))
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
    
    # आइकॉन को सेव करना
    image.save("icon.png")
    print("Icon generated successfully as icon.png!")

if __name__ == "__main__":
    create_game_icon()

