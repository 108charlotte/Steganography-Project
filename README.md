# Steganography-Project
My final project for my data structures and algorithms semester-long elective. 

## Project Description
Develop 2+ algorithms for hiding information in images and/or audio files. For my project, I chose to create 2 steganography algorithms to hide textual information in images. My code is heavily commented in the areas which alter the pixels of the original image to create a new one, so please check those out and my final presentation if you want descriptions of each algorithm and how they work. The images available on the website are taken from my iPhone! It also generates a difference map from each original --> new image. 

## Development Process
Originally, I had planned to distribute my message across the image using a sinusoidal function. After trying (and failing) several times to get this function to always map inside the image and keep information dense without overlapping, I switched to a grid distribution approach. I ended up using this grid approach for both of my algorithms. In my first working attempt, you had to pass the length of the encrypted message to the functions, which meant that information had to be exchanged outside of the image by the two parties. Since this wasn't practical, I chose to add a header to both images. The header would set the ones digit of the r channel for the first 8 channels to encode the length of the encrypted message, so that it could later be read and used to calculate grid spacing. This means that before sending these images, all that would have to be exchanged between the two parties would be information on how to read the length, or reading the r channel of the first 8 pixels in the top left corner of the image. 

## Tools
This project permitted the use of generative AI tools for code generation, so long as the final presentation and analyses were our own work. My final presentation can be found here: [Stego Final Presentation](https://docs.google.com/presentation/d/1-Rx_rbjpMvD-OFHWwh2PjQiTHubhFUvbNpUu3T6BHK4/edit?usp=sharing), which includes analyses of my two algorithms. However, it notably doesn't include any description of the Flask and Javascript components, since those were outside the scope of the course. 

For generating code, I used: 
- github copilot
- chatGPT
- and experimented with Claude

Github Copilot generated a lot of the Javascript code by elaborating on what I had already written to make it more robust, since I had issues with images not displaying, taking too long to display, or incorrect images displaying. I did not use ChatGPT as frequently, but cited it when I did use it as with Github Copilot. Primarily, it was when I wanted a minimal fix or an explanation since I could show it parts of my code in isolation. Finally, near the end of the project I experimented with Claude to help me debug. Although I didn't use any Claude-generated code in my final product, it helped me create useful debugging logs. 
