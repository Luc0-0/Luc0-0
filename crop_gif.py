from PIL import Image

gif_path = r"c:\Users\NIPUN\OneDrive\Desktop\Projects 100\Luc0-0\header\anb (1).gif"

# Open the GIF
img = Image.open(gif_path)

# Crop dimensions: remove 200px from top and 200px from bottom
crop_box = (0, 280, 1920, 800)

# Process all frames
frames = []
durations = []

for frame_idx in range(img.n_frames):
    img.seek(frame_idx)
    frame = img.convert('RGB')
    cropped_frame = frame.crop(crop_box)
    frames.append(cropped_frame)
    durations.append(img.info.get('duration', 100))

# Save the cropped GIF
frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0
)

print(f"Cropped successfully!")
print(f"New dimensions: 1920x680 pixels")
print(f"Frames processed: {len(frames)}")
