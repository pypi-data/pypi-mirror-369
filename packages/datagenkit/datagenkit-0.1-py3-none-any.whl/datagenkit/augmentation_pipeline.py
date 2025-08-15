import cv2
import numpy as np
from tri_breed.traditional_augmentations import apply_traditional_augmentations
from tri_breed.neural_style_transfer import apply_neural_style_transfer
from tri_breed.patch_mixing import cutmix, mixup

def apply_tri_breed_augmentations(image, style_image=None, selected_techniques=None, params=None, all_input_images=None, nst_steps=300):
    if selected_techniques is None:
        selected_techniques = []
    if params is None:
        params = {}

    augmented_image = image.copy()

    # Apply Traditional Augmentations
    if 'traditional' in selected_techniques:
        aug_params = params.get('traditional_aug_params', {})
        augmented_image = apply_traditional_augmentations(augmented_image, aug_params)

    # Apply Neural Style Transfer
    if 'nst' in selected_techniques and style_image is not None:
        style_strength = params.get('nst_style_strength', 1.0)
        augmented_image = apply_neural_style_transfer(augmented_image, style_image, steps=nst_steps, style_weight=params.get('nst_style_strength', 1.0) * 1e6)

    # Apply Patch Mixing
    if 'cutmix' in selected_techniques and all_input_images is not None:
        augmented_image = cutmix(augmented_image, all_input_images, alpha=params.get('cutmix_alpha', 1.0))
    elif 'mixup' in selected_techniques and all_input_images is not None:
        augmented_image = mixup(augmented_image, all_input_images, alpha=params.get('mixup_alpha', 1.0))

    return augmented_image

if __name__ == '__main__':
    # Example usage
    # Create a dummy content image
    content_img = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(content_img, (50, 50), (200, 200), (255, 255, 0), -1) # Yellow square

    # Create a dummy style image
    style_img = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.circle(style_img, (128, 128), 100, (0, 255, 255), -1) # Cyan circle

    print("Original content image shape:", content_img.shape)
    print("Original style image shape:", style_img.shape)

    # Test with Traditional Augmentations
    print("\n--- Testing Traditional Augmentations ---")
    aug_params_trad = {'horizontal_flip_p': 1.0, 'rotate_limit': 30, 'rotate_p': 1.0}
    augmented_trad = apply_tri_breed_augmentations(
        content_img, 
        selected_techniques=['traditional'], 
        params={'traditional_aug_params': aug_params_trad}
    )
    print("Augmented (Traditional) image shape:", augmented_trad.shape)

    # Test with Neural Style Transfer
    print("\n--- Testing Neural Style Transfer ---")
    augmented_nst = apply_tri_breed_augmentations(
        content_img, 
        style_image=style_img, 
        selected_techniques=['nst'], 
        params={'nst_style_strength': 0.7}
    )
    print("Augmented (NST) image shape:", augmented_nst.shape)

    # Test with CutMix
    print("\n--- Testing CutMix ---")
    augmented_cutmix = apply_tri_breed_augmentations(
        content_img, 
        style_image=style_img, 
        selected_techniques=['cutmix'], 
        params={'cutmix_alpha': 1.0}
    )
    print("Augmented (CutMix) image shape:", augmented_cutmix.shape)

    # Test with MixUp
    print("\n--- Testing MixUp ---")
    augmented_mixup = apply_tri_breed_augmentations(
        content_img, 
        style_image=style_img, 
        selected_techniques=['mixup'], 
        params={'mixup_alpha': 1.0}
    )
    print("Augmented (MixUp) image shape:", augmented_mixup.shape)

    print("\nAll augmentation types tested. Check comments in individual files for saving/displaying examples.")