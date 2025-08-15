import albumentations as A
import cv2
import numpy as np

def apply_traditional_augmentations(image, aug_params):
    transform = A.Compose([
        A.HorizontalFlip(p=aug_params.get('horizontal_flip_p', 0.5)),
        A.VerticalFlip(p=aug_params.get('vertical_flip_p', 0.5)),
        A.Rotate(limit=aug_params.get('rotate_limit', 45), p=aug_params.get('rotate_p', 0.5)),
        A.RandomBrightnessContrast(brightness_limit=aug_params.get('brightness_limit', 0.2), 
                                   contrast_limit=aug_params.get('contrast_limit', 0.2), 
                                   p=aug_params.get('brightness_contrast_p', 0.5)),
        A.GaussNoise(p=aug_params.get('gauss_noise_p', 0.2)),
        A.ColorJitter(p=aug_params.get('color_jitter_p', 0.2)),
        A.ShiftScaleRotate(shift_limit=aug_params.get('shift_limit', 0.0625),
                           scale_limit=aug_params.get('scale_limit', 0.1),
                           rotate_limit=aug_params.get('rotate_limit_ssr', 45),
                           p=aug_params.get('shift_scale_rotate_p', 0.5))
    ])
    augmented_image = transform(image=image)['image']
    return augmented_image

if __name__ == '__main__':
    # Example usage
    # Create a dummy image (e.g., a black square)
    dummy_image = np.zeros((256, 256, 3), dtype=np.uint8)
    # Draw a white square in the middle
    cv2.rectangle(dummy_image, (64, 64), (192, 192), (255, 255, 255), -1)

    print("Original image shape:", dummy_image.shape)

    aug_params = {
        'horizontal_flip_p': 1.0,
        'rotate_limit': 90,
        'rotate_p': 1.0,
        'brightness_limit': 0.5,
        'contrast_limit': 0.5,
        'brightness_contrast_p': 1.0,
        'gauss_noise_p': 1.0,
        'color_jitter_p': 1.0,
        'shift_limit': 0.1,
        'scale_limit': 0.2,
        'rotate_limit_ssr': 90,
        'shift_scale_rotate_p': 1.0
    }

    augmented_image = apply_traditional_augmentations(dummy_image, aug_params)

    print("Augmented image shape:", augmented_image.shape)

    # You can save or display the image to verify
    # cv2.imwrite('original_dummy.png', dummy_image)
    # cv2.imwrite('augmented_dummy.png', augmented_image)
    print("Example traditional augmentation applied. Check comments for saving/displaying.")