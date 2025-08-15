import raster_geometry as rg
import numpy as np
from tnia.simulation.phantoms import add_small_to_large_2d
from random import seed, uniform
import matplotlib.pyplot as plt
import math
from tnia.deeplearning.augmentation import uber_augmenter_im

def test_augmentation():
    width = 512
    height = 512

    truth = np.zeros([height, width], dtype=np.float32)

    seed(354)

    for i in range(10):
        x = int(uniform(0, width))
        y = int(uniform(0, height))
        r = int(uniform(20, 30))
        size = [math.ceil(r*2), math.ceil(r*2)]
        temp=rg.circle(size, r)

        add_small_to_large_2d(truth, temp, x, y, mode='replace_non_zero')

    assert truth.sum() == 16355.0

    print(truth.sum())

    im = truth.copy()

    im_aug, truth_aug = uber_augmenter_im(im, truth, 256)

    print(im_aug.sum())

    #assert im_aug.sum() == 6049.3467
    assert math.isclose(im_aug.sum(), 6049.3467, rel_tol=1e-5)

    #plt.imshow(im)
    #plt.imshow(im_aug)
    #plt.show()
    #stop = 5

# make main
if __name__ == "__main__":
    test_augmentation()
    



