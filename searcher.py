import numpy as np
import torch
from effnetv2_pure import effnetv2_s
from PIL import Image
import os
import time
from torchsummary import summary
# Global memory and adjustment counter
memory = []
adjustments = 0

def search(model, processed_image, max_adjustments=10, min_value=40, max_multiplier=5, num_classes=5, dead_zone=0.5):
    global memory, adjustments, last_adjustment
    with torch.no_grad():
        prediction = np.argmax(model(processed_image).cpu().detach().numpy())
    memory.append(prediction)
    adjustments += 1

    # Check for maximum adjustments
    if adjustments > max_adjustments:
        return -1, -1  # Signal to stop if max adjustments exceeded

    # Determine adjustment based on the severity of the focus issue
    if len(memory) >= 2:
        current, previous = prediction, memory[-2]
        
        # Calculate the base adjustment factor
        base_adjustment = (num_classes - 1 - current) * min_value

        if current == 4:  # No adjustment needed if focused
            adjustment = 0
        elif abs(current - 4) <= dead_zone:  # If within dead zone, adjust less aggressively
            adjustment = base_adjustment / 2
        elif current > previous:  # Image is getting more focused, adjust less aggressively
            adjustment = base_adjustment
            last_adjustment = adjustment
        elif current < previous:  # Image is getting less focused, adjust more aggressively
            adjustment = -base_adjustment
            last_adjustment = adjustment
        else:  # No change in prediction
            # If the image is not focused, continue adjusting in the same direction
            # try 7 times before changing direction
            if adjustments % 7 == 0:
                adjustment = -last_adjustment
                last_adjustment = adjustment    
            else:
                adjustment = last_adjustment
            #adjustment = last_adjustment
    else:
        # Initial adjustment based on first prediction
        adjustment = (num_classes - 1 - prediction) * min_value
        last_adjustment = adjustment

    # Ensure adjustment is within allowed range
    adjustment = max(-min_value * max_multiplier, min(min_value * max_multiplier, adjustment))
    return adjustment, prediction if type(prediction) == np.int64 else 10


def process(image_path, target_size=(384, 384), load_image=False):
    if load_image:
        image = Image.open(image_path)
    else:
        image = image_path
    image = image.resize(target_size)
    image = image.convert("RGB")
    image = np.array(image) / 255.0
    image = np.transpose(image, (2, 0, 1))
    image = np.expand_dims(image, axis=0)
    image = torch.tensor(image, dtype=torch.float32)
    return image

""" def test_search(test_folder, model):
    for file in os.listdir(test_folder):
        image_path = os.path.join(test_folder, file)
        processed_image = process_image(image_path, load_image=True)
        adjustment = search(model, processed_image, max_adjustments=100, min_value=400, max_multiplier=5)
        print(f"File: {file}, Adjustment: {adjustment}") """




if __name__ == "__main__":
    """
    model = effnetv2_s(num_classes=5)
    model.load_state_dict(torch.load("53_28.02.pth", map_location="cuda"))
    model.eval()
    test_folder = "test_folder"
    start = time.time()
    test_search(test_folder, model, max_adjustments=10, min_value=40, max_multiplier=5)
    end = time.time()
    print("Took:", end - start )
    """
    pass
