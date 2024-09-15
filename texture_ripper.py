import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

class TextureRipperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Texture Ripper")

        # Initialize variables
        self.image = None
        self.image_path = None
        self.canvas_image = None
        self.points = []  # Primary points
        self.secondary_points = {}  # Secondary points, between primary points
        self.selected_point = None
        self.curve_mode = False  # Default to straight lines
        self.zoom_level = 1.0  # Default zoom level (1.0 = no zoom)
        self.canvas_offset_x = 0  # For tracking canvas movement during zoom/pan
        self.canvas_offset_y = 0
        self.pan_start_x = 0  # For tracking the starting point of the pan
        self.pan_start_y = 0
        self.is_panning = False  # Whether we are currently panning
        self.extracted_image = None  # Holds the current extracted image

        # Layout setup
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(side=tk.TOP, padx=10, pady=10)

        # Canvas dimensions (assuming 800x600 for now)
        self.canvas_width = 800
        self.canvas_height = 600

        # Create canvas for displaying the main image
        self.canvas = tk.Canvas(self.main_frame, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.LEFT)

        # Create area for displaying the extracted texture (larger canvas)
        self.extracted_canvas = tk.Canvas(self.main_frame, width=400, height=400, bg="gray")
        self.extracted_canvas.pack(side=tk.LEFT, padx=10)

        # Button frame to hold buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side=tk.TOP, pady=10)

        # Buttons
        self.load_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.extract_button = tk.Button(self.button_frame, text="Extract Texture", command=self.extract_texture)
        self.extract_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save As", command=self.save_extracted_texture)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.toggle_curve_button = tk.Button(self.button_frame, text="Toggle Curves", command=self.toggle_curves)
        self.toggle_curve_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(self.button_frame, text="Reset View", command=self.reset_view)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.button_frame, text="Clear Points", command=self.clear_points)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Bind mouse events for adding points, panning, zooming, and dragging
        self.canvas.bind("<Button-1>", self.add_or_select_point)
        self.canvas.bind("<B1-Motion>", self.drag_point)
        self.canvas.bind("<ButtonRelease-1>", self.release_point)
        self.canvas.bind("<MouseWheel>", self.zoom_image)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)  # Middle mouse button press
        self.canvas.bind("<B2-Motion>", self.pan_image)  # Middle mouse button drag
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)  # Middle mouse button release
        self.root.bind("<Control_L>", self.enable_zoom_mode)
        self.root.bind("<Control_R>", self.enable_zoom_mode)
        self.root.bind("<KeyRelease-Control_L>", self.disable_zoom_mode)
        self.root.bind("<KeyRelease-Control_R>", self.disable_zoom_mode)

        self.zoom_active = False  # Whether zoom mode is active

    def load_image(self):
        """Load an image file."""
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not self.image_path:
            return
        self.image = Image.open(self.image_path)
        self.zoom_level = 1.0  # Reset zoom when loading a new image
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.display_image()

    def display_image(self):
        """Display the image on the canvas, accounting for zoom and panning."""
        if self.image:
            zoomed_width = int(self.canvas_width * self.zoom_level)
            zoomed_height = int(self.canvas_height * self.zoom_level)
            resized_image = self.image.resize((zoomed_width, zoomed_height), Image.LANCZOS)
            self.canvas_image = ImageTk.PhotoImage(resized_image)
            self.canvas.create_image(self.canvas_offset_x, self.canvas_offset_y, anchor=tk.NW, image=self.canvas_image)
            self.draw_grid()

    def draw_grid(self):
        """Draw the quadrilateral grid with either straight lines or curves."""
        self.canvas.delete("grid")
        for i, point in enumerate(self.points):
            # Scale points according to zoom level
            zoomed_x = point[0] * self.zoom_level + self.canvas_offset_x
            zoomed_y = point[1] * self.zoom_level + self.canvas_offset_y

            # Draw primary points immediately after they are added
            self.canvas.create_oval(zoomed_x-5, zoomed_y-5, zoomed_x+5, zoomed_y+5, outline='red', width=2, tags="grid")

        if len(self.points) == 4:
            # Draw straight lines or curves based on the toggle state
            for i in range(4):
                p1 = self.points[i]
                p2 = self.points[(i+1) % 4]

                if self.curve_mode:
                    # If curve mode is on, use quadratic Bézier curves
                    if i in self.secondary_points:
                        sec_point = self.secondary_points[i]
                    else:
                        sec_point = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
                        self.secondary_points[i] = sec_point

                    # Draw the Bézier curve
                    self.draw_bezier_curve(p1, sec_point, p2)

                    # Draw secondary points
                    zoomed_sec_x = sec_point[0] * self.zoom_level + self.canvas_offset_x
                    zoomed_sec_y = sec_point[1] * self.zoom_level + self.canvas_offset_y
                    self.canvas.create_oval(zoomed_sec_x-5, zoomed_sec_y-5, zoomed_sec_x+5, zoomed_sec_y+5, outline='blue', width=2, tags="grid")
                else:
                    # If curve mode is off, draw straight lines
                    zoomed_x1 = p1[0] * self.zoom_level + self.canvas_offset_x
                    zoomed_y1 = p1[1] * self.zoom_level + self.canvas_offset_y
                    zoomed_x2 = p2[0] * self.zoom_level + self.canvas_offset_x
                    zoomed_y2 = p2[1] * self.zoom_level + self.canvas_offset_y
                    self.canvas.create_line(zoomed_x1, zoomed_y1, zoomed_x2, zoomed_y2, fill='green', width=2, tags="grid")

    def draw_bezier_curve(self, p1, p2, p3):
        """Draw a quadratic Bézier curve between three points."""
        steps = 50  # Number of points to calculate for the curve
        for t in range(steps):
            t /= steps
            x = (1 - t)**2 * p1[0] + 2 * (1 - t) * t * p2[0] + t**2 * p3[0]
            y = (1 - t)**2 * p1[1] + 2 * (1 - t) * t * p2[1] + t**2 * p3[1]
            next_t = (t + 1/steps)
            next_x = (1 - next_t)**2 * p1[0] + 2 * (1 - next_t) * next_t * p2[0] + next_t**2 * p3[0]
            next_y = (1 - next_t)**2 * p1[1] + 2 * (1 - next_t) * next_t * p2[1] + next_t**2 * p3[1]

            # Apply zoom to Bézier curve points
            zoomed_x = x * self.zoom_level + self.canvas_offset_x
            zoomed_y = y * self.zoom_level + self.canvas_offset_y
            zoomed_next_x = next_x * self.zoom_level + self.canvas_offset_x
            zoomed_next_y = next_y * self.zoom_level + self.canvas_offset_y

            self.canvas.create_line(zoomed_x, zoomed_y, zoomed_next_x, zoomed_next_y, fill='green', width=2, tags="grid")

    def toggle_curves(self):
        """Toggle between straight lines and curves."""
        self.curve_mode = not self.curve_mode
        self.draw_grid()

    def add_or_select_point(self, event):
        """Add a point or select a point (primary or secondary) to drag."""
        x = (event.x - self.canvas_offset_x) / self.zoom_level
        y = (event.y - self.canvas_offset_y) / self.zoom_level

        # If there are less than 4 points, add new points
        if len(self.points) < 4:
            self.points.append((x, y))
            self.draw_grid()  # Draw point immediately
        else:
            # Otherwise, check if a primary or secondary point is selected for dragging
            for i, point in enumerate(self.points):
                if abs(point[0] - x) < 10 and abs(point[1] - y) < 10:
                    self.selected_point = ('primary', i)
                    return
            for i, sec_point in self.secondary_points.items():
                if abs(sec_point[0] - x) < 10 and abs(sec_point[1] - y) < 10:
                    self.selected_point = ('secondary', i)
                    return

    def drag_point(self, event):
        """Drag the selected point."""
        if self.selected_point is not None:
            point_type, index = self.selected_point
            x = (event.x - self.canvas_offset_x) / self.zoom_level
            y = (event.y - self.canvas_offset_y) / self.zoom_level

            # Constrain the point within the canvas (image) boundaries
            x = max(0, min(x, self.canvas_width))
            y = max(0, min(y, self.canvas_height))

            if point_type == 'primary':
                self.points[index] = (x, y)
            elif point_type == 'secondary':
                # Secondary points are free to move and adjust the curve
                self.secondary_points[index] = (x, y)
            self.draw_grid()

    def release_point(self, event):
        """Release the dragged point."""
        self.selected_point = None

    def clear_points(self):
        """Clear the selected points."""
        self.points = []
        self.secondary_points = {}
        self.canvas.delete("grid")
        self.display_image()

    def zoom_image(self, event):
        """Zoom in or out based on the mouse wheel while Control is held."""
        if self.zoom_active:
            # Calculate the zoom factor
            zoom_factor = 1.1 if event.delta > 0 else 0.9

            # Prevent zooming out past the original size
            if zoom_factor * self.zoom_level < 1.0:
                zoom_factor = 1.0 / self.zoom_level  # Reset to original size

            # Zoom relative to the current mouse position
            mouse_x = self.canvas.canvasx(event.x)
            mouse_y = self.canvas.canvasy(event.y)

            # Adjust zoom level and offsets
            self.zoom_level *= zoom_factor
            self.canvas_offset_x = mouse_x - zoom_factor * (mouse_x - self.canvas_offset_x)
            self.canvas_offset_y = mouse_y - zoom_factor * (mouse_y - self.canvas_offset_y)

            # Redraw the image and points
            self.display_image()

    def enable_zoom_mode(self, event):
        """Enable zoom mode when Control is pressed."""
        self.zoom_active = True

    def disable_zoom_mode(self, event):
        """Disable zoom mode when Control is released."""
        self.zoom_active = False

    def start_pan(self, event):
        """Start panning when the middle mouse button is pressed."""
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.is_panning = True

    def pan_image(self, event):
        """Pan the image by dragging with the middle mouse button."""
        if self.is_panning:
            delta_x = event.x - self.pan_start_x
            delta_y = event.y - self.pan_start_y
            self.canvas_offset_x += delta_x
            self.canvas_offset_y += delta_y
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.display_image()

    def end_pan(self, event):
        """End panning when the middle mouse button is released."""
        self.is_panning = False

    def reset_view(self):
        """Reset the zoom and panning to the default view."""
        self.zoom_level = 1.0
        self.canvas_offset_x = 0
        self.canvas_offset_y = 0
        self.display_image()

    def extract_texture(self):
        """Extract the texture using the selected quadrilateral points."""
        if len(self.points) != 4:
            print("Please select exactly 4 points.")
            return

        # Convert canvas coordinates back to original image coordinates
        src_img = cv2.imread(self.image_path)
        h_ratio, w_ratio = src_img.shape[0] / 600, src_img.shape[1] / 800
        src_points = np.array([[x * w_ratio, y * h_ratio] for x, y in self.points], dtype='float32')

        # Define destination points for perspective transform (a rectangle)
        width = int(np.linalg.norm(src_points[0] - src_points[1]))  # Approximate width of the texture
        height = int(np.linalg.norm(src_points[0] - src_points[3]))  # Approximate height of the texture
        dst_points = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype='float32')

        # Perform perspective transform (based on selected points)
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        extracted_texture = cv2.warpPerspective(src_img, matrix, (width, height))

        # Convert to a PIL Image and display it on the extracted canvas
        self.extracted_image = Image.fromarray(cv2.cvtColor(extracted_texture, cv2.COLOR_BGR2RGB))
        self.display_extracted_image(self.extracted_image)

    def display_extracted_image(self, img):
        """Display the extracted image while maintaining its aspect ratio."""
        # Calculate aspect ratio and fit the image to the extracted canvas (400x400)
        canvas_width, canvas_height = 400, 400
        img_width, img_height = img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        # Resize while preserving aspect ratio
        img_resized = img.resize((new_width, new_height), Image.LANCZOS)
        extracted_image_tk = ImageTk.PhotoImage(img_resized)

        # Clear the canvas and display the resized image
        self.extracted_canvas.delete("all")
        self.extracted_canvas.create_image((canvas_width - new_width) // 2, (canvas_height - new_height) // 2, anchor=tk.NW, image=extracted_image_tk)
        self.extracted_canvas.image = extracted_image_tk  # Keep reference

    def save_extracted_texture(self):
        """Save the currently displayed extracted texture to a user-specified location."""
        if self.extracted_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg;*.jpeg")])
            if file_path:
                self.extracted_image.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextureRipperApp(root)
    root.mainloop()
