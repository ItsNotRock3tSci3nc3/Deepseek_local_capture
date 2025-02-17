import pygetwindow as gw
import pyautogui
from PIL import Image, ImageTk
import tkinter as tk
import subprocess
import os
import io
import base64
import cv2
import numpy as np

#import ollama
import ollama
print("ollama is installed:", hasattr(ollama, '__version__'))

import deepseek as deepseek
print("DeepSeek-R1 is installed:", hasattr(deepseek, '__version__'))

def get_window_list():
    return gw.getAllTitles()


def take_screenshot(window_title):
    try:
        win = gw.getWindowsWithTitle(window_title)[0]
        x, y, width, height = win.left, win.top, win.width, win.height

        # Ensure directory exists
        screenshot_dir = "C:/Users/fcb4d/OneDrive/Documents/coding projects/AI/Deepseek/image_reader/data/screenshots_png/"
        os.makedirs(screenshot_dir, exist_ok=True)

        screenshot_path = os.path.join(screenshot_dir, "sc_pysc.png")

        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot.save(screenshot_path)

        return screenshot_path
    except IndexError:
        return None

def analyze_with_deepseek(image_path):
    print(image_path)

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image from {image_path}")  # Handle missing image error

    encodedImg = encode_image(image_path)

    prompt = f"Analyze the screenshot located at {image_path} and provide a detailed description of its content. If there are questions, answer them. If there are any issues, flag them and offer solutions."

    try:
        response = ollama.chat(
            model = "deepseek-r1",
            messages = [{"role": "user", "content": prompt, "images": [encodedImg], "Image path" : image_path}], 
            stream = False,           
        )

        for chunk in response:
            print(chunk["message"]["content"], end = '', flush = True)

        return response["message"]["content"]

    except Exception as e:
        print(f"Error analyzing image: {e}")
        return None


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    

def show_results(image_path, analysis):
    window = tk.Toplevel()
    window.title("Screenshot and Analysis")
    
    img = Image.open(image_path)
    img = img.resize((700, 500))  # Resize for display
    photo = ImageTk.PhotoImage(img)
    
    label_img = tk.Label(window, image=photo)
    label_img.image = photo  # Keep a reference to avoid garbage collection
    label_img.pack()

    text_area = tk.Text(window, wrap=tk.WORD, height=10, width=50)
    text_area.pack()

    if isinstance(analysis, bytes):  # If analysis is bytes, convert to string
        analysis = analysis.decode('utf-8')

    text_area.insert(tk.END, str(analysis))  # Ensure it's a string

def main():
    root = tk.Tk()
    root.title("Select a Window")
    
    window_list = get_window_list()
    
    var = tk.StringVar(root)
    var.set(window_list[0] if window_list else "No windows available")
    
    dropdown = tk.OptionMenu(root, var, *window_list)
    dropdown.pack()
    
    def capture_and_analyze():
        window_title = var.get()
        img_path = take_screenshot(window_title)
        if img_path:
            analysis = analyze_with_deepseek(img_path)
            show_results(img_path, analysis)
        else:
            tk.Label(root, text="Failed to capture screenshot").pack()
    
    btn = tk.Button(root, text="Capture & Analyze", command=capture_and_analyze)
    btn.pack()
    
    root.mainloop()

if __name__ == "__main__":
    main()
