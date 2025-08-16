from PIL import Image, ImageTk
import tkinter as tk
import platform
from datetime import date
def age():

    # Enter your birth year
    birth_year = 2004  # change this to your year of        birth

    # Get the current year
    current_year = date.today().year

    # Calculate age
    age = current_year - birth_year

    print(age)
    
def show_image_fit_screen(image_path):
    # Detect OS
    system = platform.system()

    if system in ["Windows", "Linux", "Darwin"]:  
        # Works on PC (Windows/Linux/Mac) using Tkinter
        root = tk.Tk()
        root.title("Image Viewer")

        # Get screen size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Open and resize image
        img = Image.open(image_path)
        img = img.resize((screen_width, screen_height), Image.LANCZOS)

        # Convert for Tkinter
        tk_img = ImageTk.PhotoImage(img)

        # Display
        label = tk.Label(root, image=tk_img)
        label.pack()
        root.mainloop()

    else:  
        # If running on Android (Pydroid 3), use matplotlib instead
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg

        img = mpimg.imread(image_path)
        plt.figure(figsize=(8, 6))  # auto-scale for mobile
        plt.imshow(img)
        plt.axis("off")
        plt.show()


# 🔹 Call function
show_image_fit_screen("sarathii.jpg")
def full_name():
	print("VIJAYASARATHI.A")
def dob():
	print("02/MAY/2004")
def degree():
	print("B.tech-AI&DS")
