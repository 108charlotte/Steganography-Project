# Steganography-Project
My final project for my data structures and algorithms semester-long elective. Come back soon for a more updated README! 

Observations in development
- small images result in garbled results for large texts like jane eyre, because x values start to overlap
- formula for mapping spreads things out too much even though it scales, leading to corrupted messages
- original function :    # function to follow for y values to mess with
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
        # getting y value, used chatGPT to generate function which will utilize more of the image than my original
        y_func = ((x - width/2)**2) * math.sin(k * (x - width/2))