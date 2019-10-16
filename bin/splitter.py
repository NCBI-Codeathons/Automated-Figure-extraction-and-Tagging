import cv2
import numpy as np

def HorizontalCutPoints(img_gray_inverted, dim=1):
    """
    Return available horizontal cut points
    """
    row_means = cv2.reduce(img_gray_inverted, dim, cv2.REDUCE_AVG, dtype=cv2.CV_32F).flatten()
    # print (row_means)
    row_gaps = zero_runs(row_means)

    # print (row_gaps)

    row_cutpoints = (row_gaps[:,0] + row_gaps[:,1] - 1) / 2
    return [int(a) for a in row_cutpoints]

def VerticalCutPoints(img_gray_inverted):
    """
    Return available vertical cut points
    """
    return HorizontalCutPoints(img_gray_inverted, 0)

def IsMultiPanel(hcuts, vcuts):
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
            print (f'=== {i}, {width}')
            if width < int(total_len/10):
                print (f'del at {i}: {points[i]}')
                del points[i]
                done = False
                break
        done = True
    if points[-1] == total_len:
        del points[-1]


def Split(hcuts, vcuts, img):
    index=0
    height, width = img.shape[:2]
    print (f"{height}, {width}")
    DeFrag(hcuts, height)
    DeFrag (vcuts, width)

    hcuts.append(height - 1)
    vcuts.append(width - 1)
    print (hcuts)
    print (vcuts)
    hi = 0
    hi_prev = 0
    vi = 0
    vi_prev = 0
    while hi < len(hcuts):
        if hi == 0:
            y = 0
            roi_h = hcuts[hi]
        else:
            y = hcuts[hi_prev]
            roi_h = hcuts[hi] - hcuts[hi_prev]
        if roi_h < int(height/10):
            hi = hi + 1
            continue
        while vi < len(vcuts):
            print (f' *** {hi}, {hi_prev}, {vi}, {vi_prev}')
            if vi == 0:
                x = 0
                roi_w = vcuts[vi]
            else:
                x = vcuts[vi_prev]
                roi_w = vcuts[vi] - vcuts[vi_prev]

            if roi_w < int(width/10):
                vi = vi + 1
                continue
            print (f"y: {y}, height: {hcuts[hi]}, x: {x}, width: {vcuts[vi]}")
            print (f'  ==> {roi_h}, {roi_w}')

            roi = img[y:hcuts[hi], x:vcuts[vi]]
            cv2.imwrite(f"test9_{index}.png", roi)
            index = index + 1
            vi_prev = vi
            vi = vi + 1
        hi_prev = hi
        hi = hi + 1



# From https://stackoverflow.com/a/24892274/3962537
def zero_runs(a):
    # Create an array that is 1 where a is 0, and pad each end with an extra 0.
    iszero = np.concatenate(([0], np.equal(a, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    # Runs start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges

img = cv2.imread('s9.png', cv2.IMREAD_COLOR)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# ret, img_thr = cv2.threshold( img_gray, 100,255,cv2.THRESH_BINARY )
img_gray_inverted = 255 - img_gray

hcuts = HorizontalCutPoints(img_gray_inverted)
# cut_line = hcuts[0]

vcuts = VerticalCutPoints(img_gray_inverted)


print (hcuts)
print (vcuts)

if IsMultiPanel(hcuts, vcuts):
    Split(hcuts, vcuts, img)
else:
    print ("Not a multipanel")