from flask import Flask, render_template, request
from PIL import Image
import os

app = Flask(__name__)

image_names = ["trees", "sky", "city", "low saturation", "high saturation"]
method_names = ["method 1", "method 2"]
info_names = ["Hello world", "Jane Eyre", "Macbeth", "In Search of Lost Time (longest novel)"]

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
        if not selected_info in info_names: 
            return render_template('index.html', error="There was an error retreiving this information", image_names=image_names, method_names=method_names, info_names=info_names) 

        selected_stego = request.form.get('stego_dropdown')
        new_img = "placeholder"
        match selected_stego: 
            case "method 1": 
                new_img = stego_1(img, selected_img)
            case "method 2": 
                new_img = stego_2(img, selected_img)
        
        if new_img == "placeholder": 
            return render_template('index.html', error="There was an error generating the new image", image_names=image_names, method_names=method_names, info_names=info_names)
        
        return render_template('index.html', error="There was an error generating the new image", image_names=image_names, method_names=method_names, info_names=info_names, selection=[selected_img, selected_stego, selected_info])
    
# both funcs return a path to the new image they've generated
def stego_1(img, name): 
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