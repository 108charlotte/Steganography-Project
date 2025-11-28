from flask import Flask, render_template, request
from PIL import Image
import os
import math

app = Flask(__name__)

image_names = ["trees", "sky", "city", "low saturation", "high saturation"]
method_names = ["method 1", "method 2"]
info_names = ["Hello world", "Jane Eyre", "Macbeth"]

@app.route("/")
def main():
    return render_template('index.html', image_names=image_names, method_names=method_names, info_names=info_names)

@app.route("/run_stego", methods=['POST'])
def choose_alg(): 
    if request.method == 'POST': 
        selected_img = request.form.get('image_dropdown')
        img = "placeholder"
        match selected_img: 
            case "trees": 
                img = "/static/images/placeholder_img.png"
            case "sky": 
                img = "/static/images/placeholder_img.png"
            case "city": 
                img = "/static/images/placeholder_img.png"
            case "low saturation": 
                img = "/static/images/placeholder_img.png"
            case "high saturation": 
                img = "/static/images/placeholder_img.png"
        
        if img == "placeholder":
            return render_template('index.html', error="There was an error retreiving this image", image_names=image_names, method_names=method_names, info_names=info_names) 
        
        selected_info = request.form.get('info_dropdown')
        info = "placeholder"
        match selected_info: 
            case "Hello world": 
                info = "/static/texts/hello_world.txt"
            case "Jane Eyre": 
                info = "/static/texts/jane_eyre.txt"
            case "Macbeth": 
                info = "/static/texts/macbeth.txt"
        
        if info == "placeholder":
            return render_template('index.html', error="There was an error retreiving this information", image_names=image_names, method_names=method_names, info_names=info_names) 

        # using built-in python hash function
        # used chatGPT help to fix path not found error (building correct filesystem path)
        info_path = os.path.join(app.root_path, info.lstrip("/"))
        file = open(info_path, "r")
        content = file.read()
        hashed_info = str(hash(content))
        file.close()

        selected_stego = request.form.get('stego_dropdown')
        new_img = "placeholder"
        match selected_stego: 
            case "method 1": 
                new_img = stego_1(img, selected_img, hashed_info)
            case "method 2": 
                new_img = stego_2(img, selected_img)
        
        if new_img == "placeholder": 
            return render_template('index.html', error="There was an error generating the new image", image_names=image_names, method_names=method_names, info_names=info_names)
        
        return render_template('index.html', image_names=image_names, method_names=method_names, info_names=info_names, selection=[selected_img, selected_stego, selected_info], output_image=f"/static/images/stego_{selected_img}.png")

# credit to this article for this approach and code: https://www.geeksforgeeks.org/python/morse-code-translator-python/
MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-'}

def encrypt(message): 
    cipher = ''
    for letter in message: 
        if letter != ' ': 
            cipher += MORSE_CODE_DICT[letter] + ' '
        else: 
            cipher += ' '
    return cipher

def stego_1(img, name, hashed_data): 
    morse_code = encrypt(hashed_data.upper())
    # used chatgpt help to fix image path loading error
    if img.startswith("/"):
        img_path = os.path.join(app.root_path, img.lstrip("/"))
    else:
        img_path = os.path.join(app.root_path, img)

    original_img = Image.open(img_path).convert('RGB')
    width, height = original_img.size
    new_image = Image.new('RGB', (width, height))

    new_image.paste(original_img)

    pixels = new_image.load()

    width, height = new_image.size
    # function to follow for y values to mess with
    k = width/5
    # copilot help to scale function to fit within image dimensions
    scale = height/2
    encoded_index = 0
    # used chatGPT to space data points evenly across image x-values
    morse_len = len(morse_code)
    x_spacing = width/morse_len
    for i in range(morse_len):
        x = int(i * x_spacing)
        x = min(x, width-1)
        # getting y value
        y_func = ((x - width/2)**2) * math.sin(k * (x - width/2))
        y_func = int(y_func / scale)
        y = min(y_func, height)

        r,g,b = pixels[x, y]

        # getting what to actually do to pixels
        # loops morse code (chatGPT suggestion)
        curr_char = morse_code[encoded_index]
        encoded_index += 1

        if curr_char == ".": 
            r += 150
        elif curr_char == "-": 
            g += 150
        elif curr_char == " ": 
            b += 100

        new_image.putpixel((x,y), (min(255, r), min(255, g), min(255, b)))

    # save with a .png extension so browsers can load it
    output_path = os.path.join(app.root_path, "static", "images", f"stego_{name}.png")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    new_image.save(output_path)
    return 1

def decrypt_stego_1(img): 
    print("idk")

def stego_2(img, name): 
    # used chatgpt help to fix image path loading error
    if img.startswith("/"):
        img_path = os.path.join(app.root_path, img.lstrip("/"))
    else:
        img_path = os.path.join(app.root_path, img)

    original_img = Image.open(img_path).convert('RGB')
    width, height = original_img.size
    new_image = Image.new('RGB', (width, height))

    new_image.paste(original_img)

    pixels = new_image.load()

    width, height = new_image.size
    for x in range(width):
        for y in range(height):
            r,g,b = pixels[x, y]
            new_image.putpixel((x,y), (r, g, b))

    # save with a .png extension so browsers can load it
    output_path = os.path.join(app.root_path, "static", "images", f"stego_{name}.png")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    new_image.save(output_path)
    return 1

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")