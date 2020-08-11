# -*- coding : UTF-8 -*-

import pyocr
from pyocr.builders import TextBuilder
from PIL import Image

DEFAULT_LANG = "pol"

class OCRConverterNotFoundException(Exception): pass

class OCRConverter(object):
    def __init__(self, language = DEFAULT_LANG):
        self.lang = language
        ocr_tools = pyocr.get_available_tools()
        
        if len(ocr_tools) == 0:
            raise OCRConverterNotFoundException("Cannot Find OCR tool")

        self.ocr_tool = ocr_tools[0]
        
    def parseImageFile(self, filename):
        image = Image.open(filename)
        
        converted = self.ocr_tool.image_to_string(
                            image,
                            lang = self.lang,
                            builder = TextBuilder()
        )

        return converted

