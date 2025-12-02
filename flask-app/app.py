from flask import Flask, render_template, request
from PIL import Image, ExifTags
import os
import math

# chatGPT suggestion on library to normalize characters w/ accents (like those found in jane eyre w/ charlotte bronte's name)
import unicodedata

# chatGPT function to open an image and ensure orientation remains correct
def open_image_fixed(path):
    img = Image.open(path)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation, None)
            if orientation_value == 3:
                img = img.rotate(180, expand=True)
            elif orientation_value == 6:
                img = img.rotate(270, expand=True)
            elif orientation_value == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    return img.convert('RGB')

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
                img = "/static/images/sky.jpg"
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
        content = normalize_text(file.read())
        file.close()

        selected_stego = request.form.get('stego_dropdown')

        # displays placeholder image so that user can know its loading
        rendered_page = render_template('index.html', image_names=image_names, method_names=method_names, info_names=info_names, selection=[selected_img, selected_stego, selected_info], output_image="/static/images/placeholder_img.png")

        # generate the stego image and capture the embedded/encrypted payload
        payload = None
        match selected_stego:
            case "method 1":
                payload = stego_1(img, selected_img, content)
            case "method 2":
                payload = stego_2(img, selected_img, content)

        if not payload:
            return render_template('index.html', error="There was an error generating the new image", image_names=image_names, method_names=method_names, info_names=info_names)

        # copilot: save the embedded/encrypted text so the frontend can show it before decryption
        save_path = os.path.join(app.root_path, "static", "texts", f"{selected_info} Stego.txt")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        try:
            with open(save_path, "w") as f:
                f.write(payload)
        except Exception as e:
            print("Failed to save payload:", e)

        return rendered_page

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
                    '_':'..--.-', '=':'.-.-', ';':'-.-.-.', 
                    ':':'---...', '"':'.-..-.', '—':'-....-', # — as stylistic equivalent to - in morse code
                    '\'':'.----.', '&':'.-...', '£':'·−·−···'} # for jane eyre}

def encrypt(message): 
    cipher = ''
    for letter in message: 
        if letter != ' ' and letter != "\n": 
            cipher += MORSE_CODE_DICT[letter] + " "
        elif letter == ' ': 
            cipher += '  ' # double space for actual spaces btw words
    return cipher

def stego_1(img, name, hashed_data): 
    morse_code = encrypt(hashed_data)
    print("stego 1 morese code: " + morse_code)
    # used chatgpt help to fix image path loading error
    if img.startswith("/"):
        img_path = os.path.join(app.root_path, img.lstrip("/"))
    else:
        img_path = os.path.join(app.root_path, img)

    original_img = open_image_fixed(img_path)
    width, height = original_img.size
    new_image = Image.new('RGB', (width, height))

    new_image.paste(original_img)

    pixels = new_image.load()

    width, height = new_image.size
    
    morse_len = len(morse_code)
    
    # chatGPT to space symbols evenly across image
    grid_w = int(math.sqrt(morse_len)) + 1
    grid_h = int(math.ceil(morse_len / grid_w))

    x_spacing = width / grid_w
    y_spacing = height / grid_h

    for i, symbol in enumerate(morse_code):
        row = i // grid_w
        col = i % grid_w

        x = int(col * x_spacing)
        y = int(row * y_spacing)

        # safety clamp
        x = min(x, width - 1)
        y = min(y, height - 1)
        r,g,b = pixels[x, y]

        if symbol == ".": 
            # sets least significant bit to 0
            r = 10*int(r/10)
            # sets other lowest bits to 1 if 0
            if g % 10 == 0: 
                g = 10*int(g/10) + 1
            if b % 10 == 0: 
                b = 10*int(b/10) + 1
        elif symbol == "-": 
            g = 10*int(g/10)
            if r % 10 == 0: 
                r = 10*int(r/10) + 1
            if b % 10 == 0: 
                b = 10*int(b/10) + 1
        else: # space
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
    # copilot so encrypted can be displayed: return the morse code payload so the caller can save/display it
    return morse_code

import base64

# random key for stego_2 encryption
key = "5fC2yW8aHAi4foiM"

# from https://algocademy.com/blog/how-to-implement-simple-encryption-and-decryption/
def xor_encrypt_decrypt(data, key):
    # Convert data and key to bytearray for byte-level operations
    data = bytearray(data)
    key = bytearray(key)
    
    # XOR each byte of data with the corresponding byte of the key
    for i in range(len(data)):
        data[i] ^= key[i % len(key)]
    
    return bytes(data)

def get_encrypted_len_for_stego_2(info_path): 
    with open(info_path, "r") as f:
        content = normalize_text(f.read())
    
    data_bytes = content.encode()
    
    # chatGPT: Base64 length formula
    b64_len = 4 * math.ceil(len(data_bytes) / 3)
    return b64_len

def stego_2(img, name, content): 
    # chatGPT advice for reconciling string v byte errors
    encrypted_bytes = xor_encrypt_decrypt(normalize_text(content).encode(), key.encode())
    encrypted = base64.b64encode(encrypted_bytes).decode()
    print("encrypted: " + encrypted)

    # used chatgpt help to fix image path loading error
    if img.startswith("/"):
        img_path = os.path.join(app.root_path, img.lstrip("/"))
    else:
        img_path = os.path.join(app.root_path, img)

    original_img = open_image_fixed(img_path)
    width, height = original_img.size
    new_image = Image.new('RGB', (width, height))

    new_image.paste(original_img)

    pixels = new_image.load()

    width, height = new_image.size

    length = len(encrypted)
    
    # chatGPT to space symbols evenly across image
    grid_w = int(math.sqrt(length)) + 1
    grid_h = int(math.ceil(length / grid_w))

    x_spacing = width / grid_w
    y_spacing = height / grid_h

    for i, symbol in enumerate(encrypted):
        row = i // grid_w
        col = i % grid_w

        x = int(col * x_spacing)
        y = int(row * y_spacing)

        # safety clamp
        x = min(x, width - 1)
        y = min(y, height - 1)
        r,g,b = pixels[x, y]

        ascii_value = ord(symbol)

        if i % 3 == 0: 
            r = ascii_value
        elif i % 3 == 1: 
            g = ascii_value
        elif i % 3 == 2: 
            b = ascii_value

        new_image.putpixel((x,y), (r, g, b))

    # save with a .png extension so browsers can load it
    output_path = os.path.join(app.root_path, "static", "images", f"stego_{name}.png")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    new_image.save(output_path)
    # copilot to display encrypted: return the base64-encrypted payload so the caller can save/display it
    return encrypted

def decrypt_morse(message):
    decipher = ""
    words = message.split("  ")
    for word in words: 
        letters = word.split(" ")
        for letter in letters: 
            if letter: 
                try: 
                    decipher += list(MORSE_CODE_DICT.keys())[list(MORSE_CODE_DICT.values()).index(letter)]
                except ValueError:
                    # if smth weird happens
                    pass
        decipher += " "
    return decipher.strip() # removes extra whitespace

def get_morse_len(info_path): 
    file = open(info_path, "r")
    morse_len = len(encrypt(normalize_text(file.read())))
    file.close()
    return morse_len

def normalize_text(text): 
    # chatGPT suggestion for removing accents  and diacritics
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # to fix key error in jane eyre, chatGPT sugggestion for characters to include
    replacements = {
        '\u2018': "'", '\u2019': "'", '\u201C': '"', '\u201D': '"',
        'Æ': 'AE', 'æ': 'ae', '—': '-', '…': '...', '–': '-', '“': '"', '”': '"'
    }
    for k,v in replacements.items():
        text = text.replace(k,v)
    return text.upper()

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
        return render_template('index.html', error="There was an error retreiving this image", image_names=image_names, method_names=method_names, info_names=info_names, output_image=img) 
    
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
        return render_template('index.html', error="There was an error retreiving this information", image_names=image_names, method_names=method_names, info_names=info_names, output_image=img) 

    decrypted = ""

    if selected_stego == "method 1": 
        # copilot help to fix filepath issues
        # resolve the '/static/...' info path to the filesystem before reading
        info_fs_path = os.path.join(app.root_path, info.lstrip('/'))
        decrypted = decrypt_stego_1(img, get_morse_len(info_fs_path))
    else: 
        info_fs_path = os.path.join(app.root_path, info.lstrip('/'))
        decrypted = decrypt_stego_2(img, get_encrypted_len_for_stego_2(info.lstrip('/')))
    
    # chatGPT help to save file at defined location
    save_path = os.path.join(app.root_path, "static", "texts", f"{selected_info} Stego.txt")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w") as file: 
        file.write(decrypted)

    return render_template('index.html', image_names=image_names, method_names=method_names, info_names=info_names, selection=[selected_img, selected_stego, selected_info], output_image=img)

def decrypt_stego_1(img, morse_len): 
    if img.startswith("/"):
        img_path = os.path.join(app.root_path, img.lstrip("/"))
    else:
        img_path = os.path.join(app.root_path, img)

    stego_img = Image.open(img_path).convert('RGB')
    width, height = stego_img.size

    pixels = stego_img.load()

    # chatGPT help for even spacing
    grid_w = int(math.sqrt(morse_len)) + 1
    grid_h = int(math.ceil(morse_len / grid_w))

    x_spacing = width / grid_w
    y_spacing = height / grid_h

    result = ""

    for i in range(morse_len):
        row = i // grid_w
        col = i % grid_w

        x = int(col * x_spacing)
        y = int(row * y_spacing)

        x = min(x, width - 1)
        y = min(y, height - 1)
        r,g,b = pixels[x, y]

        if r % 10 == 0: 
            result += "."
        elif g % 10 == 0: 
            result += "-"
        elif b % 10 == 0: 
            result += " "
        
    print(result)
    decrypted = decrypt_morse(result)
    print("decrypted: " + decrypted)
    return decrypted

def decrypt_stego_2(img, msg_len): 
    if img.startswith("/"):
        img_path = os.path.join(app.root_path, img.lstrip("/"))
    else:
        img_path = os.path.join(app.root_path, img)

    stego_img = Image.open(img_path).convert('RGB')
    width, height = stego_img.size

    pixels = stego_img.load()

    # chatGPT help for even spacing

    grid_w = int(math.sqrt(msg_len)) + 1
    grid_h = int(math.ceil(msg_len / grid_w))
    x_spacing = width / grid_w
    y_spacing = height / grid_h

    result = ""
    
    for i in range(msg_len):
        row = i // grid_w
        col = i % grid_w

        x = int(col * x_spacing)
        y = int(row * y_spacing)

        x = min(x, width - 1)
        y = min(y, height - 1)
        r,g,b = pixels[x, y]

        if i % 3 == 0: 
            ascii_value = r
            result += chr(ascii_value)
        elif i % 3 == 1: 
            ascii_value = g
            result += chr(ascii_value)
        elif i % 3 == 2: 
            ascii_value = b
            result += chr(ascii_value)
    
    print("Decrypted: " + result)
    # chatGPT to fix order of decryption
    cipher_bytes = base64.b64decode(result)
    plaintext_bytes = xor_encrypt_decrypt(cipher_bytes, key.encode())
    decrypted = plaintext_bytes.decode(errors="replace")
    print("decrypted: " + decrypted)
    return decrypted

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")