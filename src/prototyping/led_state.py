import collections
import time

import cv2

# blob detection params
params = cv2.SimpleBlobDetector_Params()
params.filterByColor = False
params.filterByConvexity = False
params.filterByArea = False
params.filterByInertia = True
params.filterByCircularity = True
params.minInertiaRatio = 0.1
params.minCircularity = 0.1
_detector = cv2.SimpleBlobDetector_create(params)


def avg(hist: [[int]]) -> int:
    """
    Returns the average in a histogram, returned by cv2.calcHist.
    :param hist: The histogram.
    :return: The average of the given histogram.
    """
    s = 0
    e = 0
    for i in range(len(hist)):
        e += hist[i, 0]
        s += i * hist[i, 0]
    return int(s / e)


def color(hist: [int]) -> (int, str):
    """
    Returns the maximum of area and the color range of the given histogram.
    The histogram should be over the hue values of the hsv color space.
    Note: OpenCV uses [0, 179] as the hue range instead of [0, 359].
    :param hist: A histogram of the hue values.
    :return: The maximum area and the color range.
    """
    return max([(sum(hist[-14:] + hist[0:16]), "red"),
                (sum(hist[16:46]), "yellow"),
                (sum(hist[46:76]), "green"),
                (sum(hist[76:106]), "blue"),
                (sum(hist[106:136]), "cyan"),
                (sum(hist[136:166]), "purple")
                ])


class LedStateDetector:
    _counter = 0

    def __init__(self, bbox):
        """
        Bounding box should be (left, top, right, bottom).
        Current LED state can be checked with is_on.
        Current LED color can be checked with color.
        The time since the last state change can be checked using passed_time.
        None is used as an undefined state for color, is_on and passed_time.
        :param bbox: the bounding box to define the LED's location.
        """
        self._bbox = bbox
        self._last_brightness = -1
        self._on_values = collections.deque(maxlen=20)
        self._last_state_time = None
        self._off_histogram = None
        self._on_histogram = None

        self.id = LedStateDetector._counter
        LedStateDetector._counter += 1
        self.is_on = None
        self.passed_time = None
        self.color = None

    def detect(self, img, imshow: bool = False):
        """
        Checks if the LED at the to be observed location is powered on in the given image.
        If the LED changed it's state, the color will be checked.
        Returns True if the LED has changed it's state i.e. from on to off.
        :param imshow: If set to True, an image with the given defined bbox will be displayed using cv2.imshow().
        :param img: The BGR image of the board that should be checked.
        :return: True if the led has changed it's state.
        """
        img = self.frame_cutout(img)
        on = self._detect_using_brightness(img, imshow)

        change = on is not None and (self.is_on is None or on is not self.is_on)
        if change:
            self._state_change(on)
            self._color_detection(img)
        elif self.is_on is None:
            self._color_detection(img)
        return change

    def _state_change(self, state: bool):
        self.is_on = state
        if self._last_state_time is None:
            self._last_state_time = time.time()
        else:
            current = time.time()
            self.passed_time = current - self._last_state_time
            self._last_state_time = current

    def _detect_using_brightness(self, img, imshow: bool = False):
        """
        True - LED is powered on.
        False - LED is powered off.
        None - LED is in an undefined state.
        :param img: The BGR image of this LED.
        :param imshow: Set to true, to display this LED in gray.
        :return: True if LED is powered on or None if undefined.
        """
        img = cv2.GaussianBlur(img, (3, 3), 0)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
        if imshow:
            cv2.imshow(str(self.id) + "Gray", gray_img)
        hist_avg = avg(hist)
        if len(self._on_values) == 0:
            if hist_avg in range(self._last_brightness - 10, self._last_brightness + 10) or self._last_brightness == -1:
                self._last_brightness = hist_avg
                return None
                # print("In range")
            elif hist_avg > self._last_brightness:
                self._on_values.append(hist_avg)
                return True
            else:
                self._on_values.append(self._last_brightness)
                return False
        else:
            on_avg = int(sum(self._on_values) / len(self._on_values))
            if hist_avg in range(on_avg - 10, 256):
                self._on_values.append(hist_avg)
                return True
            return False

    def _detect_using_blob(self, img, imshow: bool = False):
        img = cv2.GaussianBlur(img, (3, 3), 0)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh_img = cv2.threshold(gray_img, 215, 255, cv2.THRESH_BINARY)
        thresh_img = cv2.erode(thresh_img, None, iterations=2)
        thresh_img = cv2.dilate(thresh_img, None, iterations=2)
        if imshow:
            cv2.imshow(str(self.id) + "Threshold", thresh_img)
        keypoints = _detector.detect(thresh_img)
        return len(keypoints) > 0

    def frame_cutout(self, img):
        """
        Returns a cutout of the image of the defined bbox for this LED.
        :param img: The image of the board.
        :return: A cutout of the given image using this LED's defined bbox.
        """
        return img[self._bbox[1]:self._bbox[3], self._bbox[0]:self._bbox[2], :]

    def _color_detection(self, img):
        """
        Helper function using a naive attempt at detecting the LED's color by comparing the color changes
        from an off-state and an on-state. The difference in color should be the LED's color.
        :param img: The BGR image of this led.
        :return: None
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0], None, [360], [0, 259])
        if self.is_on is None:
            self._on_histogram = hist
            self._off_histogram = hist
        elif self.is_on:
            self._on_histogram = hist
            if self._off_histogram is not None:
                for i in range(len(self._on_histogram)):
                    self._on_histogram[i] = max(self._on_histogram[i] - self._off_histogram[i], 0)
                _, self.color = color([i for i in self._on_histogram[0]])
        else:
            self._off_histogram = hist


if __name__ == '__main__':
    led1 = LedStateDetector((980, 620, 1010, 660))
    led2 = LedStateDetector((980, 660, 1010, 700))
    vid = cv2.VideoCapture("resources/piOnOff.mp4")

    leds = [led1, led2]
    frame_exists, frame = vid.read()
    while frame_exists:
        for led in leds:
            if led.detect(frame, True):
                if led.is_on:
                    print("LED", led.id, "ON", "Time passed:", led.passed_time, "Color: ", led.color)
                else:
                    print("LED", led.id, "OFF", "Time passed:", led.passed_time)
        cv2.imshow("Raw", frame)
        if cv2.waitKey(10) == 27:
            break
        frame_exists, frame = vid.read()
    cv2.destroyAllWindows()
