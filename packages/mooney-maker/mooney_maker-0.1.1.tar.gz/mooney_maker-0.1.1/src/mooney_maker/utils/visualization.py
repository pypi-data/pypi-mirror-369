import cv2
from matplotlib import pyplot as plt

__all__ = ["visualize_template_and_mooney"]


def visualize_template_and_mooney(img_color, img_mooney):
    fig, ax = plt.subplots(1, 2)
    img_rgb = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB)
    ax[0].imshow(img_rgb)
    ax[0].axis("off")
    ax[1].imshow(img_mooney, cmap="gray")
    ax[1].axis("off")
    plt.axis("off")
    plt.show()
