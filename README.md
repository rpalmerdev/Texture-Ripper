# Texture-Ripper
A misguided attempt to recreate the Texture Ripper tool from [ShoeBox](https://renderhjs.net/shoebox/) with the power of ChatGPT.

No, that doesn't mean AI assisted texture extraction. It means **I don't know how to code.**

If I could still use ShoeBox, I would. It is/was an amazing program, it just doesn't really work on my computer anymore.

This is **not** an amazing program, but it gets the job done, more-or-less. 

![2024-09-18 10_17_20-Settings](https://github.com/user-attachments/assets/17da90ec-4a2d-43b1-bd3f-53facecc2e92)

# How to Use:

- **Load an Image:**
    - Click the **"Load Image"** button and select the image file.
- **Add a Selection Set:**
    - Click the **"Add Selection Set"** button to start defining a new texture area.
- **Select Points:**
    - Click on the image to select four points outlining the area to extract.
    - Adjust points by clicking and dragging them.
- **Extract Texture:**
    - Click **"Extract Texture"** to extract the selected area.
    - The points remain on the image, allowing further adjustments if needed.
    - If you modify the points and click **"Extract Texture"** again, the texture in the map is updated.
- **Add More Selection Sets:**
    - Click **"Add Selection Set"** to define additional textures.
    - Use **"Previous Set"** and **"Next Set"** to navigate between selection sets.
- **View the Texture Map:**
    - The right canvas displays the composite texture map, updated with each extraction.
- **Save the Texture Map:**
    - Once all textures are extracted and adjusted, click **"Save As"** to save the map.
- **Clear Points or Map:**
    - Use **"Clear Points"** to reset points in the current selection set.
    - Use **"Clear Map"** to clear all extracted textures and start over.
- **Zoom and Pan:**
    - Hold the Control key and use the mouse wheel to zoom.
    - Use the middle or right mouse button to pan.

# Installation:

**Python:**

**1: Clone the repository in the desired location:**
`git clone https://github.com/rpalmerdev/Texture-Ripper.git`

**2: Create a Virtual Environment (Optional but Recommended):**

- **Open a terminal or command prompt.**
    
- **Navigate** to the directory where you saved `texture_ripper.py`.
    
- **Create** a virtual environment by running:
  `python -m venv venv`
  
- **Activate** the virtual environment:
  On **Windows**:
  `venv\Scripts\activate`
  On **macOS/Linux**:
  `source venv/bin/activate`

**3: Install the Required Dependencies:**
- Using Pip:
  `pip install -r requirements.txt`

**4: Run the Application:**
`python texture_ripper.py`

**OR** download the binary from the [Releases](https://github.com/rpalmerdev/Texture-Ripper/releases/tag/v1.0.0) page. (Windows)

# Limitations:

- Currently does not support using curved lines for texture extraction like ShoeBox does.
- Texture packing method is pretty simple/unoptimized. 
- I should have implemented a dark/light mode toggle, but I didn't. Coming soon™
