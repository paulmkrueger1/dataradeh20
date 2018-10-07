from PIL import Image
import requests
import numpy as np

def image_url_to_vector(img_url):
    """
    s/o to https://stackoverflow.com/questions/15612373/convert-image-png-to-matrix-and-then-to-1d-array
    """
    response = requests.get(img_url, stream=True)
    response.raw.decode_content = True
    original_image = Image.open(response.raw)
    rgba_image = original_image.convert('RGBA')
    arr = np.array(rgba_image)

    # record the original shape
    shape = arr.shape

    # make a 1-dimensional view of arr
    flat_arr = arr.ravel()

    # convert it to a matrix
    vector = np.matrix(flat_arr)

    # do something to the vector
    vector[:,::10] = 128

    # reform a numpy array of the original shape
    arr2 = np.asarray(vector).reshape(shape)

    # make a PIL image
    img2 = Image.fromarray(arr2, 'RGBA')
    return arr2