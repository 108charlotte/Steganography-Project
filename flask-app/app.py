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
        content = file.read().upper()
        file.close()

        selected_stego = request.form.get('stego_dropdown')
        new_img = "placeholder"
        match selected_stego: 
            case "method 1": 
                new_img = stego_1(img, selected_img, content)
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
                    '0':'-----', ',':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-', '!':'-.-.--', 
                    '_':'..--.-', '=':'.-.-'}

def encrypt(message): 
    cipher = ''
    for letter in message: 
        if letter != ' ' and letter != "\n": 
            cipher += MORSE_CODE_DICT[letter] + " "
        elif letter == ' ': 
            cipher += ' '
    return cipher

def stego_1(img, name, hashed_data): 
    morse_code = encrypt(hashed_data)
    print("stego 1 morese code: " + morse_code)
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
        y = max(0, min(y_func, height - 1))

        r,g,b = pixels[x, y]

        # getting what to actually do to pixels
        # loops morse code (chatGPT suggestion)
        curr_char = morse_code[encoded_index]
        encoded_index += 1

        if curr_char == ".": 
            # sets least significant bit to 0
            r = 10*int(r/10)
            # sets other lowest bits to 1 if 0
            if g % 10 == 0: 
                g = 10*int(g/10) + 1
            if b % 10 == 0: 
                b = 10*int(b/10) + 1
        elif curr_char == "-": 
            g = 10*int(g/10)
            if r % 10 == 0: 
                r = 10*int(r/10) + 1
            if b % 10 == 0: 
                b = 10*int(b/10) + 1
        elif curr_char == " ": 
            b = 10*int(b/10)
            if g % 10 == 0: 
                g = 10*int(g/10) + 1
            if r % 10 == 0: 
                r = 10*int(r/10) + 1

        new_image.putpixel((x,y), (r, g, b))

    # save with a .png extension so browsers can load it
    output_path = os.path.join(app.root_path, "static", "images", f"stego_{name}.png")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    new_image.save(output_path)
    return 1

def decrypt_morse(message):
    decipher = ""
    citext = ""
    for letter in message: 
        if letter != " ": 
            citext += letter
        else: 
            if citext: 
                try: 
                    decipher += list(MORSE_CODE_DICT.keys())[list(MORSE_CODE_DICT.values()).index(citext)]
                except ValueError:
                    # if smth weird happens
                    pass
                citext = ''
    return decipher

def get_morse_len(info_path): 
    file = open(info_path, "r")
    morse_len = len(encrypt(file.read().upper()))
    file.close()
    return morse_len

@app.route("/decrypt_stego", methods=['POST'])
def decrypt_stego(): 
    selected_stego = request.form.get('selected_stego')
    selected_img = request.form.get('selected_image')
    selected_info = request.form.get('selected_info')
    img = "placeholder"
    match selected_img: 
        case "trees": 
            img = "/static/images/stego_trees.png"
        case "sky": 
            img = "/static/images/stego_sky.png"
        case "city": 
            img = "/static/images/stego_city.png"
        case "low saturation": 
            img = "/static/images/stego_low_saturation.png"
        case "high saturation": 
            img = "/static/images/stego_high_saturation.png"
    
    if img == "placeholder":
        return render_template('index.html', error="There was an error retreiving this image", image_names=image_names, method_names=method_names, info_names=info_names) 
    
    # getting info so that morse_len can be calculated, would have had to be shared between people previously
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

    decrypted = ""

    if selected_stego == "method 1": 
        # copilot help to fix filepath issues
        # resolve the '/static/...' info path to the filesystem before reading
        info_fs_path = os.path.join(app.root_path, info.lstrip('/'))
        decrypted = decrypt_stego_1(img, get_morse_len(info_fs_path))
    
    # chatGPT help to save file at defined location
    save_path = os.path.join(app.root_path, "static", "texts", f"{selected_info} Stego.txt")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w") as file: 
        file.write(decrypted)

    return render_template('index.html', image_names=image_names, method_names=method_names, info_names=info_names, selection=[selected_img, selected_stego, selected_info])

# decrypter must know length of message, k, and scale
def decrypt_stego_1(img, morse_len): 
    if img.startswith("/"):
        img_path = os.path.join(app.root_path, img.lstrip("/"))
    else:
        img_path = os.path.join(app.root_path, img)

    stego_img = Image.open(img_path).convert('RGB')
    width, height = stego_img.size

    pixels = stego_img.load()

    k = width/5
    scale = height/2

    x_spacing = width/morse_len

    morse_code_result = ""
    for i in range(morse_len):
        x = int(i * x_spacing)
        x = min(x, width-1)
        # getting y value
        y_func = ((x - width/2)**2) * math.sin(k * (x - width/2))
        y_func = int(y_func / scale)
        y = max(0, min(y_func, height - 1))

        r,g,b = pixels[x, y]

        if r % 10 == 0: 
            morse_code_result += "."
        elif g % 10 == 0: 
            morse_code_result += "-"
        elif b % 10 == 0: 
            morse_code_result += " "
    print(morse_code_result) # this is working
    decrypted = decrypt_morse(morse_code_result)
    print("decrypted: " + decrypted)
    return decrypted


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