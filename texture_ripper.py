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

        # Create canvas for displaying the image
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        # Buttons
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT)

        self.extract_button = tk.Button(root, text="Extract Texture", command=self.extract_texture)
        self.extract_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(root, text="Clear Points", command=self.clear_points)
        self.clear_button.pack(side=tk.LEFT)

        # Bind mouse click to add points, and dragging events
        self.canvas.bind("<Button-1>", self.add_or_select_point)
        self.canvas.bind("<B1-Motion>", self.drag_point)
        self.canvas.bind("<ButtonRelease-1>", self.release_point)

    def load_image(self):
        """Load an image file."""
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not self.image_path:
            return
        self.image = Image.open(self.image_path)
        self.display_image()

    def display_image(self):
        """Display the image on the canvas."""
        if self.image:
            self.canvas_image = ImageTk.PhotoImage(self.image.resize((800, 600), Image.LANCZOS))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
            self.draw_grid()

    def draw_grid(self):
        """Draw the quadrilateral grid and secondary points."""
        self.canvas.delete("grid")
        if len(self.points) == 4:
            # Draw curves between primary points
            for i in range(4):
                p1 = self.points[i]
                p2 = self.points[(i+1) % 4]

                # Get the secondary point or calculate a default midpoint if not set
                if i in self.secondary_points:
                    sec_point = self.secondary_points[i]
                else:
                    sec_point = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
                    self.secondary_points[i] = sec_point

                # Draw Bézier curve using the primary and secondary points
                self.draw_bezier_curve(p1, sec_point, p2)

                # Draw primary and secondary points
                self.canvas.create_oval(p1[0]-5, p1[1]-5, p1[0]+5, p1[1]+5, outline='red', width=2, tags="grid")
                self.canvas.create_oval(sec_point[0]-5, sec_point[1]-5, sec_point[0]+5, sec_point[1]+5, outline='blue', width=2, tags="grid")

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
            self.canvas.create_line(x, y, next_x, next_y, fill='green', width=2, tags="grid")

    def add_or_select_point(self, event):
        """Add a point or select a point (primary or secondary) to drag."""
        x, y = event.x, event.y

        # If there are less than 4 points, add new points
        if len(self.points) < 4:
            self.points.append((x, y))
            if len(self.points) == 4:
                self.draw_grid()
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
            x, y = event.x, event.y
            if point_type == 'primary':
                self.points[index] = (x, y)
            elif point_type == 'secondary':
                # Constrain secondary point to the line between primary points
                p1 = self.points[index]
                p2 = self.points[(index + 1) % 4]
                x, y = self.constrain_to_line(x, y, p1, p2)
                self.secondary_points[index] = (x, y)
            self.draw_grid()

    def constrain_to_line(self, x, y, p1, p2):
        """Constrain a point to the line between p1 and p2."""
        line_vec = np.array([p2[0] - p1[0], p2[1] - p1[1]])
        point_vec = np.array([x - p1[0], y - p1[1]])
        line_len = np.dot(line_vec, line_vec)
        projection = np.dot(point_vec, line_vec) / line_len
        projection = max(0, min(1, projection))  # Clamp to [0, 1]
        return (p1[0] + projection * line_vec[0], p1[1] + projection * line_vec[1])

    def release_point(self, event):
        """Release the dragged point."""
        self.selected_point = None

    def clear_points(self):
        """Clear the selected points."""
        self.points = []
        self.secondary_points = {}
        self.canvas.delete("grid")
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

        # Perform perspective transform (currently, still based on primary points)
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        extracted_texture = cv2.warpPerspective(src_img, matrix, (width, height))

        # Save and display the extracted texture
        extracted_image = Image.fromarray(cv2.cvtColor(extracted_texture, cv2.COLOR_BGR2RGB))
        extracted_image.show()
        extracted_image.save("extracted_texture.png")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextureRipperApp(root)
    root.mainloop()
