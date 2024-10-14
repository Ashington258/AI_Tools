import os
import cv2
import numpy as np
import random


def augment_image(image, operations):
    augmented_images = []

    if "scale" in operations:
        scales = [0.8, 1.2]
        for scale in scales:
            h, w = image.shape[:2]
            new_h, new_w = int(h * scale), int(w * scale)
            scaled_image = cv2.resize(image, (new_w, new_h))
            augmented_images.append(scaled_image)

    if "rotate" in operations:
        angles = [45, 90, 180, 270]
        for angle in angles:
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated_image = cv2.warpAffine(image, M, (w, h))
            augmented_images.append(rotated_image)

    if "flip" in operations:
        flipped_h = cv2.flip(image, 1)
        flipped_v = cv2.flip(image, 0)
        augmented_images.append(flipped_h)
        augmented_images.append(flipped_v)

    if "brightness" in operations:
        brightness_values = [50, -50]
        for value in brightness_values:
            bright_image = cv2.convertScaleAbs(image, alpha=1, beta=value)
            augmented_images.append(bright_image)

    if "translate" in operations:
        translations = [(10, 0), (0, 10)]
        for tx, ty in translations:
            M = np.float32([[1, 0, tx], [0, 1, ty]])
            translated_image = cv2.warpAffine(
                image,
                M,
                (image.shape[1], image.shape[0]),
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0),
            )
            augmented_images.append(translated_image)

    if "noise" in operations:
        salt_pepper_ratio = 0.02
        noisy_image_sp = image.copy()
        num_salt = np.ceil(salt_pepper_ratio * image.size * 0.5)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
        noisy_image_sp[coords[0], coords[1], :] = 255

        num_pepper = np.ceil(salt_pepper_ratio * image.size * 0.5)
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
        noisy_image_sp[coords[0], coords[1], :] = 0
        augmented_images.append(noisy_image_sp)

        mean = 0
        var = 1
        sigma = var**0.5
        gauss = np.random.normal(mean, sigma, image.shape).astype("uint8")
        noisy_image_gauss = cv2.add(image, gauss)
        augmented_images.append(noisy_image_gauss)

    return augmented_images


def enhance_dataset(input_dir, output_dir, operations, times):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith((".png", ".jpg", ".jpeg", ".bmp")):
            image_path = os.path.join(input_dir, filename)
            image = cv2.imread(image_path)

            for i in range(times):
                augmented_images = augment_image(image, operations)
                for j, augmented_image in enumerate(augmented_images):
                    output_path = os.path.join(
                        output_dir, f"{os.path.splitext(filename)[0]}_aug_{i}_{j}.png"
                    )
                    cv2.imwrite(output_path, augmented_image)


if __name__ == "__main__":
    input_dir = "F:/15_Train_data/lanedetection/data"
    output_dir = "output"
    operations = [
        "scale",
        # "rotate",
        # "flip",
        "brightness",
        "translate",
        "noise",
    ]  # Specify desired operations
    times = 1  # Specify the number of times to augment each image

    enhance_dataset(input_dir, output_dir, operations, times)
