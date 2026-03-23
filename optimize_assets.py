import os
import subprocess
from PIL import Image

# Path to ffmpeg from imageio-ffmpeg
FFMPEG_PATH = r"C:\Users\prash\Downloads\xj (3)\xj (2)\xj\venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"

def compress_image(image_path, quality=50):
    try:
        temp_path = image_path + ".tmp.jpg"
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(temp_path, "JPEG", quality=quality, optimize=True)
        
        # Replace original
        os.replace(temp_path, image_path)
        print(f"Compressed & Replaced Image: {image_path}")
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")

def compress_video(video_path, bitrate="500k"):
    try:
        temp_path = video_path + ".min.mp4"
        # Overwrite if exists
        cmd = [
            FFMPEG_PATH, "-y", "-i", video_path,
            "-b:v", bitrate, "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", "-b:a", "64k",
            temp_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Replace original
        os.replace(temp_path, video_path)
        print(f"Compressed & Replaced Video: {video_path}")
    except Exception as e:
        print(f"Error compressing video {video_path}: {e}")

if __name__ == "__main__":
    assets_to_optimize = [
        # Videos
        {"path": "static/videos/bg_devotional.mpeg", "type": "video", "bitrate": "50k"},
        {"path": "static/videos/karyasiddhi-logo-animation.mp4", "type": "video", "bitrate": "150k"},
        {"path": "static/videos/video.mp4", "type": "video", "bitrate": "150k"},
        {"path": "static/videos/snipping.mp4", "type": "video", "bitrate": "150k"},
        # Images
        {"path": "media/photos/karyasiddhi_logo.png", "type": "image"},
        {"path": "static/images/rangoli.png", "type": "image"},
        {"path": "static/images/sec1.png", "type": "image"},
        {"path": "static/images/blogtemple.png", "type": "image"},
    ]

    for asset in assets_to_optimize:
        abs_path = os.path.join(os.getcwd(), asset["path"].replace("/", os.sep))
        if not os.path.exists(abs_path):
            print(f"File not found: {abs_path}")
            continue

        if asset["type"] == "image":
            compress_image(abs_path)
        elif asset["type"] == "video":
            compress_video(abs_path, bitrate=asset.get("bitrate", "500k"))
