import numpy as np
import cv2
import numpy as np
import random

def cutmix(image1, all_input_images, alpha=1.0):
    # Ensure images are of the same shape
    # Randomly select a second image from all_input_images, ensuring it's not the same as image1
    other_images = [img for img in all_input_images if img.shape == image1.shape and not np.array_equal(img, image1)]
    if not other_images:
        # If no other suitable images, return original image (or handle as error)
        return image1
    image2 = random.choice(other_images)
    if image2 is None:
        raise ValueError("No suitable second image found for CutMix with matching dimensions.")

    lam = np.random.beta(alpha, alpha)
    bbx1, bby1, bbx2, bby2 = rand_bbox(image1.shape, lam)

    mixed_image = image1.copy()
    mixed_image[bby1:bby2, bbx1:bbx2] = image2[bby1:bby2, bbx1:bbx2]
    return mixed_image

def mixup(image1, all_input_images, alpha=1.0):
    # Ensure images are of the same shape
    # Randomly select a second image from all_input_images, ensuring it's not the same as image1
    other_images = [img for img in all_input_images if img.shape == image1.shape and not np.array_equal(img, image1)]
    if not other_images:
        # If no other suitable images, return original image (or handle as error)
        return image1
    image2 = random.choice(other_images)
    if image2 is None:
        raise ValueError("No suitable second image found for MixUp with matching dimensions.")

    lam = np.random.beta(alpha, alpha)
    mixed_image = lam * image1 + (1 - lam) * image2
    return mixed_image.astype(np.uint8)

def rand_bbox(img_shape, lam):
    W = img_shape[1]
    H = img_shape[0]
    cut_rat = np.sqrt(1. - lam)
    cut_w = int(W * cut_rat)
    cut_h = int(H * cut_rat)

    # uniform
    cx = np.random.randint(W)
    cy = np.random.randint(H)

    bbx1 = np.clip(cx - cut_w // 2, 0, W)
    bby1 = np.clip(cy - cut_h // 2, 0, H)
    bbx2 = np.clip(cx + cut_w // 2, 0, W)
    bby2 = np.clip(cy + cut_h // 2, 0, H)

    return bbx1, bby1, bbx2, bby2

if __name__ == '__main__':
    # Example usage
    # Create two dummy images
    img1 = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.rectangle(img1, (50, 50), (200, 200), (255, 0, 0), -1) # Red square

    img2 = np.zeros((256, 256, 3), dtype=np.uint8)
    cv2.circle(img2, (128, 128), 100, (0, 255, 0), -1) # Green circle

    print("Image 1 shape:", img1.shape)
    print("Image 2 shape:", img2.shape)

    # Apply CutMix
    cutmixed_img = cutmix(img1, img2)
    print("CutMixed image shape:", cutmixed_img.shape)

    # Apply MixUp
    mixedup_img = mixup(img1, img2)
    print("MixUp image shape:", mixedup_img.shape)

    # You can save or display the images to verify
    # cv2.imwrite('img1.png', img1)
    # cv2.imwrite('img2.png', img2)
    # cv2.imwrite('cutmixed_img.png', cutmixed_img)
    # cv2.imwrite('mixedup_img.png', mixedup_img)
    print("Example patch mixing applied. Check comments for saving/displaying.")