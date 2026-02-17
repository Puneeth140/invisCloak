import cv2
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageTk

class CloakApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Aura Cloak v2.1 // Precision VFX")
        self.geometry("1300x850")
        ctk.set_appearance_mode("dark")
        self.main_font = "Playpen Sans" 

        # --- Grid Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="AURA CLOAK", 
                                font=ctk.CTkFont(family=self.main_font, size=26, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=(30, 10))

        # --- PRESET BUTTON ---
        self.btn_presets = ctk.CTkButton(self.sidebar, text="💡 COLOR PRESETS", 
                                        command=self.show_presets, 
                                        fg_color="#ff00ff", hover_color="#c000c0",
                                        font=ctk.CTkFont(family=self.main_font, size=13, weight="bold"))
        self.btn_presets.grid(row=1, column=0, padx=20, pady=10)

        self.btn_capture = ctk.CTkButton(self.sidebar, text="Capture Background", 
                                        command=self.capture_bg, 
                                        font=ctk.CTkFont(family=self.main_font, size=14))
        self.btn_capture.grid(row=2, column=0, padx=20, pady=10)

        # --- Dynamic Sliders with Live Numbers ---
        self.sliders = {}
        self.h_low = self.create_slider("Lower Hue", 35, 180, 3)
        self.h_high = self.create_slider("Upper Hue", 85, 180, 4)
        self.s_low = self.create_slider("Min Saturation", 100, 255, 5)
        self.v_low = self.create_slider("Min Brightness", 50, 255, 6)
        self.edge_grow = self.create_slider("Edge Growth", 3, 15, 7)
        self.blur_val = self.create_slider("Feathering", 25, 61, 8)

        # --- Viewport ---
        self.video_container = ctk.CTkFrame(self, fg_color="transparent")
        self.video_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.video_label = ctk.CTkLabel(self.video_container, text="")
        self.video_label.pack(expand=True)

        # --- Engine Logic ---
        self.cap = cv2.VideoCapture(0)
        self.background = None
        self.bg_v = None
        self.update_frame()

    def create_slider(self, name, default, to, row):
        container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        container.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
        
        # Header for Slider: Name + Live Number
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x")
        
        label = ctk.CTkLabel(header, text=name, font=ctk.CTkFont(family=self.main_font, size=12))
        label.pack(side="left")
        
        value_label = ctk.CTkLabel(header, text=str(default), font=ctk.CTkFont(family=self.main_font, size=12, weight="bold"), text_color="#00f3ff")
        value_label.pack(side="right")
        
        slider = ctk.CTkSlider(container, from_=0, to=to, number_of_steps=to,
                              command=lambda v, l=value_label: l.configure(text=str(int(v))))
        slider.set(default)
        slider.pack(side="top", fill="x", pady=(0, 5))
        return slider

    def show_presets(self):
        # A simple popup or text update to guide the user
        preset_msg = (
            "Recommended Settings:\n\n"
            "🟢 GREEN: Hue 35-85, Sat 100, Val 50\n"
            "🔴 RED: Hue 0-10 (or 170-180), Sat 120, Val 70\n"
            "🔵 BLUE: Hue 100-130, Sat 150, Val 50\n\n"
            "Adjust 'Feathering' to smooth edges!"
        )
        # We'll use a standard CTk Messagebox-style approach
        popup = ctk.CTkToplevel(self)
        popup.title("Calibration Guide")
        popup.geometry("400x250")
        popup.attributes("-topmost", True)
        
        msg_label = ctk.CTkLabel(popup, text=preset_msg, font=ctk.CTkFont(family=self.main_font, size=13), justify="left", padx=20, pady=20)
        msg_label.pack()

    def capture_bg(self):
        for _ in range(30): # Warm up for exposure
            ret, frame = self.cap.read()
        if ret:
            self.background = np.flip(frame, axis=1)
            bg_hsv = cv2.cvtColor(self.background, cv2.COLOR_BGR2HSV)
            self.bg_v = bg_hsv[:, :, 2].astype(float)
            self.btn_capture.configure(text="BG Captured", fg_color="#28a745")

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret: return
        frame = np.flip(frame, axis=1)
        
        if self.background is not None:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # 1. Capture current mask
            lower = np.array([int(self.h_low.get()), int(self.s_low.get()), int(self.v_low.get())])
            upper = np.array([int(self.h_high.get()), 255, 255])
            mask = cv2.inRange(hsv, lower, upper)
            
            # --- STABILIZER A: Median Blur (Kills the "sparkles") ---
            mask = cv2.medianBlur(mask, 7) 

            # --- STABILIZER B: Temporal Blending ---
            # We mix the current mask with the previous one to stop the "shimmer"
            if hasattr(self, 'prev_mask') and self.prev_mask is not None:
                mask = cv2.addWeighted(mask, 0.5, self.prev_mask, 0.5, 0)
            self.prev_mask = mask

            # Re-threshold to keep it sharp
            _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
            
            # Morphological Cleanup
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            grow = int(self.edge_grow.get())
            if grow > 0: mask = cv2.dilate(mask, kernel, iterations=grow)

            # Feathering for smooth edges
            f_val = int(self.blur_val.get())
            if f_val % 2 == 0: f_val += 1
            mask_soft = cv2.GaussianBlur(mask, (f_val, f_val), 0)
            alpha = cv2.merge([mask_soft/255.0] * 3)

            # Final Blend
            res1 = cv2.multiply(self.background.astype(float), alpha)
            res2 = cv2.multiply(frame.astype(float), 1.0 - alpha)
            display_frame = cv2.add(res1, res2).astype(np.uint8)
        else:
            display_frame = frame

        img = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(800, 600))
        self.video_label.configure(image=imgtk)
        self.after(10, self.update_frame)

    def on_closing(self):
        if self.cap.isOpened(): self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = CloakApp()
    app.mainloop()