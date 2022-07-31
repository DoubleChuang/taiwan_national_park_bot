from io import BytesIO
import cv2
import numpy as np
import pytesseract
from PIL import Image
from paddleocr import PaddleOCR


class SingleTonPaddleOCR:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._ocr = PaddleOCR(use_angle_cls=True, lang='en',
                              use_gpu=False, show_log=False)
        self._initialized = True

    def __call__(self, *args, **kwargs):
        return self._ocr.ocr(*args, **kwargs)


def get_verify_code(verify_image: bytes, method: str = 'paddleocr', default_code: str = "1234"):
    """
    Use tesseract or paddleocr to get the verify code from image,
    if ocr can not recognitition any characters then return default code
    :param verify_image bytes: The verify image
    :param method str: OCR method [paddleocr/pytesseract]
    :return: The verify code
    :rtype: str
    """

    img = Image.open(BytesIO(verify_image))
    img = img.convert("RGB")
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.medianBlur(img, 3)

    if method == 'paddleocr':
        ocr = SingleTonPaddleOCR()
        result = ocr(np.array(img))
        verify_code = "".join((line[1][0] for line in result))
    else:
        verify_code = pytesseract.image_to_string(img)

    # Exclude special characters
    verify_code = ''.join(filter(str.isalnum, verify_code))
    # Can not recognitition any characters
    if len(verify_code) == 0:
        verify_code = default_code

    return verify_code
