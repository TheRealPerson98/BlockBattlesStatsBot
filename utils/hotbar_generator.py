from PIL import Image
import os

def create_hotbar(item_string, image_name):
    # Convert the entire string to lowercase and then split into items
    items = item_string.lower().split(',')

    # Load the hotbar background image
    hotbar_bg = Image.open('hotbar_background.png')

    # Initial x-offset for the first item
    x_offset = 33

    # Loop through the items and place them on the hotbar
    for item in items:
        # Load the item image
        try:
            item_img = Image.open(os.path.join('BlockPics', f'{item}.png'))
        except FileNotFoundError:
            print(f"Image for '{item}' not found. Skipping this item.")
            continue

        # Calculate the position for this item
        position = (x_offset, 24)  # 24 pixels from top and bottom

        # Paste the item image onto the hotbar
        hotbar_bg.paste(item_img, position, item_img)

        # Update the x-offset for the next item
        x_offset += 128 + 16  # width of the item plus additional space

    # Save the final hotbar image
    hotbar_bg.save(image_name)
