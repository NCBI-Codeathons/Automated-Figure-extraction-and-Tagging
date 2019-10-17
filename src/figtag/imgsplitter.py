import cv2
import numpy as np
import requests
import os

MAX_PIX = 255
NOISE_CUTOFF = 0.5


def imgsplitter(image_url: str, image_uid: str, output_folder: str):
    req = requests.get(image_url)
    img = cv2.imdecode(np.asarray(bytearray(req.content), dtype="uint8"), cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray_inverted = MAX_PIX - img_gray

    hcuts = HorizontalCutPoints(img_gray_inverted)

    vcuts = VerticalCutPoints(img_gray_inverted)

    if IsMultiPanel(hcuts, vcuts):
        Split(hcuts, vcuts, img, image_uid, output_folder)
    else:
        print("Not a multipanel")
        cv2.imwrite("{}.png".format(os.path.join(output_folder, image_uid)), img)


def _CutPoints(img, dim):
    row_means = cv2.reduce(img, dim, cv2.REDUCE_AVG, dtype=cv2.CV_32F).flatten()
    row_gaps = zero_runs(row_means)
    row_cutpoints = (row_gaps[:, 0] + row_gaps[:, 1] - 1) / 2
    return [int(a) for a in row_cutpoints]


def HorizontalCutPoints(img, dim=1):
    """
    Return available horizontal cut points
    """
    return _CutPoints(img, 1)


def VerticalCutPoints(img):
    """
    Return available vertical cut points
    """
    return _CutPoints(img, 0)


def IsMultiPanel(hcuts, vcuts):
    """
    Check if the image is multi-panle or not.
    Could have more logic.
    """
    if hcuts or vcuts:
        return True
    else:
        return False


def DeFrag(points, total_len):
    points.append(total_len)
    done = False
    while not done:
        for i in range(len(points)):
            if i == 0:
                width = points[i]
            else:
                width = points[i] - points[i - 1]
            if width < int(total_len/10):
                del points[i]
                done = False
                break
        done = True
    if points[-1] == total_len:
        del points[-1]


def Split(hcuts, vcuts, img, image_uid, output_folder):
    index = 0
    height, width = img.shape[:2]
    DeFrag(hcuts, height)
    DeFrag(vcuts, width)

    hcuts.append(height - 1)
    vcuts.append(width - 1)

    outf_prefix = os.path.join(output_folder, image_uid)

    for hi in range(len(hcuts)):
        if hi == 0:
            y = 0
        else:
            y = hcuts[hi - 1]
        roi_h = hcuts[hi]
        for vi in range(len(vcuts)):
            if vi == 0:
                x = 0
            else:
                x = vcuts[vi - 1]
            roi_w = vcuts[vi]
            roi = img[y:roi_h, x:roi_w]
            cv2.imwrite(f"{outf_prefix}_{index}.png", roi)
            index = index + 1

# From https://stackoverflow.com/a/24892274/3962537


def zero_runs(a):
    # A hack to remove noise from grayish background
    a[np.where(a < NOISE_CUTOFF)] = 0
    # Create an array that is 1 where a is 0, and pad each end with an extra 0.
    iszero = np.concatenate(([0], np.equal(a, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    # Runs start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges
