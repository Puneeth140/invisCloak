🌌 Aura Cloak: Real-Time VFX & CV Engine

Aura Cloak is a high-fidelity Computer Vision application that simulates an "Invisibility Cloak" effect using real-time image segmentation and advanced blending techniques. Unlike basic color-replacement scripts, this engine focuses on temporal stability, shadow preservation, and seamless alpha blending to create a cinematic experience.


🚀 Key Technical Features

1. Dynamic Shadow Preservation:
    The engine utilizes Ratio-based Intensity Mapping to extract shadows from the live frame and project them onto the background replacement. This ensures the "invisible" subject remains grounded in the physical lighting environment.

2. Temporal Mask Smoothing:
    To eliminate "salt-and-pepper" noise and sensor flicker, the system implements a Weighted Temporal Filter. By blending the current mask with previous frames, the segmentation remains stable even in low-light conditions.

3. Morphological Edge Refinement:
    Using Dilation and Closing operations, the engine swallows "color bleeding" at the edges of the subject and fills internal holes caused by fabric folds and shadows.

4. Adaptive Contrast (CLAHE)
    The pipeline includes Contrast Limited Adaptive Histogram Equalization in the LAB color space to normalize lighting across the subject, improving segmentation accuracy for dark-colored fabrics.


🛠️ Tech Stack
    Language: Python 3.10+
    Computer Vision: OpenCV (cv2)
    UI/UX: CustomTkinter (Modern Dark Mode UI)
    Image Processing: NumPy, Pillow (PIL)


📖 How It Works

Background Calibration: 
    The user captures a reference frame of the empty environment.

HSV Segmentation:
    The system isolates the target color (default: Dark Blue) using an adjustable Hue-Saturation-Value range.

Advanced Blending:
    Mask Feathering: 
        A Gaussian blur is applied to the binary mask to create a soft Alpha channel.
    Linear Interpolation: 
        The final output is rendered using the formula:
        $$Final = (Background \times \alpha) + (LiveFrame \times (1 - \alpha))$$


📥 Installation & Usage

Clone the repository:
    Bash
    git clone https://github.com/Puneeth140/invisCloak.git
    cd invisCloak

Install dependencies:
    Bash
    pip install opencv-python numpy Pillow customtkinter

Run the application:
    Bash
    python main.py


👨‍🔬 AuthorPuneeth Master’s Student | Aspiring AI & CV Engineer
