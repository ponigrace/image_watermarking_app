import tkinter.colorchooser as colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageTk
from customtkinter import *


class Window(CTk):
    def __init__(self):
        super().__init__()
        self.initial_directory = "C:/Users/grace/Pictures"
        self.font_option = None
        self.start_y = None
        self.start_x = None
        self.text_align_option = None
        self.selected_color_label = None
        self.font_size_slider = None
        self.add_text_textbox = None
        self.text_transparency_slider = None
        self.text_image = None
        self.main_image = None
        self.display_text_on_image = None  # CTkCanvas variable for displaying the text and making it draggable
        self.canvas = None
        self.text_location = (0, 0)
        self.rotation_angle = 0

        self.center_window(width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        self.minsize(width=1000, height=800)
        self.set_theme()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tools_frame = CTkFrame(master=self, width=300, height=600)
        self.tools_frame.grid(padx=(10, 10), pady=(10, 10), row=0, column=1, sticky="nsew")

        import_button = CTkButton(master=self.tools_frame, text="Import Image", height=35,
                                  font=("Roboto", 16, "bold"), command=self.add_image_to_canvas)
        import_button.grid(padx=(20, 10), pady=(20, 20), row=0, sticky="nsew", columnspan=2, column=0)

        save_button = CTkButton(master=self.tools_frame, text="Save", height=35, font=("Roboto", 16, "bold"),
                                command=self.save_watermarked_image, width=50)
        save_button.grid(padx=(0, 20), pady=(20, 20), row=0, sticky="nsew", column=2)

        self.set_ui_add_text()
        self.set_ui_text_transparency()
        self.set_ui_font()
        self.set_ui_font_size()
        self.set_ui_font_color()
        self.set_ui_text_alignment()
        self.set_ui_rotation()
        self.set_canvas()

    def create_text_on_canvas(self, event):
        """Creates watermark on as an image and crops empty pixels"""
        text = self.add_text_textbox.get("1.0", "end-1c")
        rgba = self.hex_to_rgba()
        font = self.get_font()
        alignment = self.get_text_alignment()

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        image = Image.new(mode="RGBA", size=(canvas_width, canvas_height), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        text_bbox = draw.textbbox((20, 20), text, font=font)

        text_position = ((image.width - text_bbox[2]) // 2, (image.height - text_bbox[3]) // 2)
        draw.text(text_position, text=text, font=font, fill=rgba, align=alignment)

        img_rotated = image.rotate(angle=self.rotation_angle, expand=True, resample=Image.Resampling.BICUBIC)

        # Get the bounding box of the drawn text
        bbox = img_rotated.getbbox()

        if bbox:
            # Crop the image to include only the bounding box area
            cropped_image = img_rotated.crop(bbox)
        else:
            cropped_image = img_rotated  # If no bounding box, use the original image

        self.text_image = cropped_image
        self.text_location = (text_position[0], text_position[1])

        tk_image = ImageTk.PhotoImage(cropped_image)
        self.canvas.itemconfig(self.display_text_on_image, image=tk_image)
        self.canvas.image = tk_image

    def merge_images(self):
        """Merges the main image and the text image to create a watermarked image"""
        if self.main_image is None or self.text_image is None:
            return

        watermarked_img = self.main_image.copy()
        watermarked_img.paste(self.text_image, self.text_location, self.text_image)
        return watermarked_img

    def save_watermarked_image(self):
        """Saves the watermarked image to the destination folder"""
        watermarked_img = self.merge_images()

        if watermarked_img:
            file_path = filedialog.asksaveasfile(
                confirmoverwrite=True,
                initialdir=self.initial_directory,
                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("BITMAP", "*.bmp"), ("GIF", "*.gif")],
                defaultextension="*.*"
            ).name

            if file_path:
                selected_extension = os.path.splitext(file_path)[1]

                # Convert image mode if necessary (JPEG does not support alpha channel)
                if selected_extension.lower() in ['.jpg', '.jpeg']:
                    watermarked_img = watermarked_img.convert("RGB")

                # Save the watermarked image with the correct file extension
                watermarked_img.save(file_path)

    def rotate_left(self):
        """Rotates the watermark to the left by an increment of 5 degrees"""
        self.rotation_angle += 5
        self.create_text_on_canvas(self)

    def rotate_right(self):
        """Rotates the watermark to the right by a decrement of 5 degrees"""
        self.rotation_angle -= 5
        self.create_text_on_canvas(self)

    def get_text_alignment(self):
        """Sets the text alignment. It's useful for multi-line texts."""
        return self.text_align_option.get().lower()

    def get_font(self) -> ImageFont:
        """Retrieves the selected font from teh Fonts folder"""
        font_size = int(self.font_size_slider.get())
        current_dir = os.path.dirname(os.path.abspath(__file__))
        selected_font = self.font_option.get()

        font_path = os.path.join(current_dir, "Fonts", f"{selected_font}.ttf")

        try:
            font = ImageFont.truetype(font_path, size=font_size)
        except IOError:
            font = ImageFont.load_default()

        return font

    def hex_to_rgba(self):
        """Converts HEX color to RGBA"""
        hex_color = self.selected_color_label.cget("bg_color").lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        alpha = int(self.text_transparency_slider.get())

        return r, g, b, alpha

    def select_color(self, event=None):
        """Pops up a color palette to choose a color from"""
        current_color = self.selected_color_label.cget("bg_color")
        color = colorchooser.askcolor()
        if color[1]:  # Ensure a color was chosen
            self.selected_color_label.configure(fg_color=color[1], bg_color=color[1])
            if current_color != color[1]:
                self.create_text_on_canvas(self)

    def add_image_to_canvas(self):
        """Imports the main image and resizes the canvas based on the image's dimensions"""
        filename = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")]
        )

        if filename:
            self.add_text_textbox.configure(state=NORMAL)
            img_pil = Image.open(filename).convert("RGBA")
            img_resized = self.resize_image_to_fit_canvas(img_pil)

            new_canvas_width = img_resized.size[0]
            new_canvas_height = img_resized.size[1]

            self.canvas.configure(width=new_canvas_width, height=new_canvas_height)
            self.canvas.update()

            self.main_image = img_resized
            img_ctk = ImageTk.PhotoImage(img_resized)

            self.canvas.create_image(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                image=img_ctk
            )
            self.canvas.img_ctk = img_ctk
        self.canvas.tag_raise(self.display_text_on_image)

    def resize_image_to_fit_canvas(self, img_pil):
        """Resizes the image so that it fits the canvas while preserving the aspect ratio"""
        canvas_width = self.winfo_screenwidth() - self.tools_frame.winfo_width() - 10  # padding left
        canvas_height = self.winfo_screenheight() - 20  # padding top and bottom

        img_width, img_height = img_pil.size

        if img_width <= canvas_width or img_height <= canvas_height:
            # Resize canvas to image size if the image is smaller
            return img_pil
        else:
            # Resize image to fit the canvas while preserving the aspect ratio
            scale_factor = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)

            img_resized = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return img_resized

    def center_window(self, width=800, height=600):
        """Loads the window at the center of the screen and uses the screen's dimensions for its width and height"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    @staticmethod
    def set_theme(appearance="Dark", color="green"):
        set_appearance_mode(appearance)
        set_default_color_theme(color)

    def set_canvas(self):
        """Sets the canvas and initializes the starting position of the text"""
        screen_width = self.winfo_screenwidth() - self.tools_frame.winfo_width() - 10
        screen_height = self.winfo_screenheight() - 20
        x = screen_width // 2  # sets text_image at the center by default
        y = screen_height // 2  # sets text_image at the center by default

        self.canvas = CTkCanvas(master=self, highlightthickness=0, bg="#2b2b2b", width=screen_width,
                                height=screen_height)
        self.canvas.grid(row=0, column=0, padx=(10, 0), pady=(10, 10))

        self.display_text_on_image = self.canvas.create_image(x, y, image=None)
        self.canvas.tag_bind(self.display_text_on_image, "<Button-1>", self.on_start)
        self.canvas.tag_bind(self.display_text_on_image, "<B1-Motion>", self.on_drag)

    def set_ui_add_text(self):
        add_text_label = CTkLabel(master=self.tools_frame, text="Add Text:", width=250, font=("Roboto", 14, "bold"),
                                  anchor="w")
        add_text_label.grid(padx=(20, 20), pady=(20, 5), row=1, sticky="nsew", columnspan=3)

        self.add_text_textbox = CTkTextbox(master=self.tools_frame, font=("Roboto", 14), height=50)
        self.add_text_textbox.bind("<KeyRelease>", command=self.create_text_on_canvas)
        self.add_text_textbox.grid(padx=(20, 20), pady=(0, 5), row=2, sticky="nsew", columnspan=3)

    def set_ui_text_transparency(self):
        text_transparency_label = CTkLabel(master=self.tools_frame, text="Text transparency:", width=250,
                                           font=("Roboto", 14, "bold"), anchor="w")
        text_transparency_label.grid(padx=(20, 20), pady=(5, 5), row=3, sticky="nsew", columnspan=3)

        # It is used to set the transparency of the text
        self.text_transparency_slider = CTkSlider(master=self.tools_frame, width=250, from_=0, to=255,
                                                  command=self.create_text_on_canvas)
        self.text_transparency_slider.set(255)
        self.text_transparency_slider.grid(padx=(20, 20), pady=(5, 5), row=4, sticky="nsew", columnspan=3)

    def set_ui_font(self):
        directory = "Fonts/"
        ttf_files = [f for f in os.listdir(directory) if
                     f.endswith(".ttf") and os.path.isfile(os.path.join(directory, f))]
        font_name_list = [font.split(".")[0].title() for font in ttf_files]

        self.font_option = CTkOptionMenu(master=self.tools_frame, values=font_name_list, font=("Roboto", 14),
                                         command=self.create_text_on_canvas)
        self.font_option.grid(padx=(20, 20), pady=(5, 5), row=5, sticky="nsew", columnspan=3)

    def set_ui_font_size(self):
        font_size_label = CTkLabel(master=self.tools_frame, text="Font size (12 to 300 pt):", width=250,
                                   font=("Roboto", 14, "bold"), anchor="w")
        font_size_label.grid(padx=(20, 20), pady=(5, 5), row=6, sticky="nsew", columnspan=3)

        self.font_size_slider = CTkSlider(master=self.tools_frame, width=250, from_=12, to=300,
                                          command=self.create_text_on_canvas)
        self.font_size_slider.set(12)
        self.font_size_slider.grid(padx=(20, 20), pady=(5, 5), row=7, sticky="nsew", columnspan=3)

    def set_ui_font_color(self):
        font_color_label = CTkLabel(master=self.tools_frame, text="Select Font Color", anchor="w",
                                    font=("Roboto", 14, "bold"))
        font_color_label.grid(padx=(20, 0), pady=(5, 5), row=8, sticky="nsew", column=0)

        self.selected_color_label = CTkLabel(master=self.tools_frame, text="                        ",
                                             fg_color="#FFFFFF", bg_color="#FFFFFF", cursor="hand2")
        self.selected_color_label.bind("<Button-1>", self.select_color)
        self.selected_color_label.grid(padx=(0, 20), pady=(5, 5), row=8, sticky="nsew", columnspan=2, column=1)

    def set_ui_text_alignment(self):
        self.text_align_option = CTkOptionMenu(master=self.tools_frame, values=["Left", "Center", "Right"],
                                               font=("Roboto", 14), command=self.create_text_on_canvas)
        self.text_align_option.grid(padx=(20, 20), pady=(5, 5), row=9, sticky="nsew", columnspan=3)

    def set_ui_rotation(self):
        rotation_frame = CTkFrame(master=self.tools_frame, width=280)
        rotation_frame.grid(padx=(20, 20), pady=(10, 10), row=10, sticky="nsew", columnspan=3)

        rotate_left_button = CTkButton(master=rotation_frame, text="⟲ Rotate Left", height=20, font=("Roboto", 14),
                                       command=self.rotate_left)
        rotate_left_button.grid(padx=(0, 5), row=0, column=0, sticky="nsew")

        rotate_right_button = CTkButton(master=rotation_frame, text="⟳ Rotate Right", height=30, font=("Roboto", 14),
                                        command=self.rotate_right)
        rotate_right_button.grid(padx=(5, 0), row=0, column=1, sticky="nsew")

    def on_start(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        """Enables dragging the watermark"""
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        # Get current coordinates of the item
        x1, y1, x2, y2 = self.canvas.bbox(self.display_text_on_image)

        if self.main_image is None:
            boundary_width = self.winfo_screenwidth() - self.tools_frame.winfo_width() - 10  # padding left
            boundary_height = self.winfo_screenheight() - 20  # padding top and bottom
        else:
            boundary_width = self.canvas.winfo_width()
            boundary_height = self.canvas.winfo_height()

        # Check if moving the item will stay within the canvas boundaries
        if x1 + dx >= 0 and x2 + dx <= boundary_width and y1 + dy >= 0 and y2 + dy <= boundary_height:
            self.canvas.move(self.display_text_on_image, dx, dy)
            self.start_x = event.x
            self.start_y = event.y

            new_x1, new_y1, new_x2, new_y2 = self.canvas.bbox(self.display_text_on_image)
            self.text_location = (new_x1, new_y1)
