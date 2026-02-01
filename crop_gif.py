from PIL import Image

gif_path = r"c:\Users\NIPUN\OneDrive\Desktop\Projects 100\Luc0-0\header\anb (1).gif"

img = Image.open(gif_path)

crop_box = (0, 290, 1920, 790)


durations = []

for frame_idx in range(img.n_frames):
    img.seek(frame_idx)
    frame = img.convert('RGB')
    cropped_frame = frame.crop(crop_box)
    frames.append(cropped_frame)
    durations.append(img.info.get('duration', 100))


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
