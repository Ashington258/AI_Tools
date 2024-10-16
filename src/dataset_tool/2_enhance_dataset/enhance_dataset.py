import cv2
import numpy as np
import random
import os


def augment_image(
    image,
    scale_factors,
    rotations,
    flip_modes,
    brightness_factors,
    translations,
    noise_types,
    num_augmentations,
    do_scale=True,
    do_rotate=True,
    do_flip=True,
    do_brightness=True,
    do_translate=True,
    do_noise=True,
):
    augmented_images = []

    rows, cols = image.shape[:2]

    for _ in range(num_augmentations):
        aug_img = image.copy()

        if do_scale:
            scale = random.choice(scale_factors)
            aug_img = cv2.resize(aug_img, None, fx=scale, fy=scale)

        if do_rotate:
            angle = random.choice(rotations)
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
            aug_img = cv2.warpAffine(aug_img, M, (cols, rows))

        if do_flip:
            flip = random.choice(flip_modes)
            aug_img = cv2.flip(aug_img, flip)

        if do_brightness:
            brightness = random.choice(brightness_factors)
            aug_img = cv2.convertScaleAbs(aug_img, alpha=1, beta=brightness)

        if do_translate:
            tx, ty = random.choice(translations)
            M = np.float32([[1, 0, tx], [0, 1, ty]])
            aug_img = cv2.warpAffine(
                aug_img,
                M,
                (cols, rows),
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0),
            )

        if do_noise:
            noise_type = random.choice(noise_types)
            noisy_image = aug_img.copy()
            if noise_type == "salt_pepper":
                prob = 0.05
                for i in range(noisy_image.shape[0]):
                    for j in range(noisy_image.shape[1]):
                        rdn = random.random()
                        if rdn < prob:
                            noisy_image[i, j] = 0
                        elif rdn > 1 - prob:
                            noisy_image[i, j] = 255
            elif noise_type == "gaussian":
                mean = 0
                var = 10
                sigma = var**0.5
                gauss = np.random.normal(mean, sigma, aug_img.shape)
                noisy_image = cv2.addWeighted(
                    aug_img, 0.75, gauss.astype("uint8"), 0.25, 0
                )
            aug_img = noisy_image

        augmented_images.append(aug_img)

    return augmented_images


def process_directory(
    input_dir,
    output_dir,
    scale_factors,
    rotations,
    flip_modes,
    brightness_factors,
    translations,
    noise_types,
    num_augmentations,
    do_scale=True,
    do_rotate=True,
    do_flip=True,
    do_brightness=True,
    do_translate=True,
    do_noise=True,
):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
            image_path = os.path.join(input_dir, filename)
            image = cv2.imread(image_path)

            augmented_images = augment_image(
                image,
                scale_factors,
                rotations,
                flip_modes,
                brightness_factors,
                translations,
                noise_types,
                num_augmentations,
                do_scale,
                do_rotate,
                do_flip,
                do_brightness,
                do_translate,
                do_noise,
            )
            base_filename = os.path.splitext(filename)[0]

            for idx, aug_img in enumerate(augmented_images):
                output_path = os.path.join(output_dir, f"{base_filename}_aug_{idx}.jpg")
                cv2.imwrite(output_path, aug_img)


# Parameters for augmentation
scale_factors = [0.5, 1.5]
rotations = [45, 90, 180, 270]
flip_modes = [0, 1]  # 0: vertical, 1: horizontal
brightness_factors = [50, -50]  # Increase and decrease brightness
translations = [(50, 0), (0, 50)]  # Translate x and y
noise_types = ["salt_pepper", "gaussian"]

# Directories
input_directory = "data"
output_directory = "output"

# Number of augmentations per image
num_augmentations = 3

# Flags to control which augmentations to perform
do_scale = True
do_rotate = False
do_flip = False
do_brightness = True
do_translate = True
do_noise = True

# Process the directory
process_directory(
    input_directory,
    output_directory,
    scale_factors,
    rotations,
    flip_modes,
    brightness_factors,
    translations,
    noise_types,
    num_augmentations,
    do_scale,
    do_rotate,
    do_flip,
    do_brightness,
    do_translate,
    do_noise,
)
