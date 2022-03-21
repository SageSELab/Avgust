from PIL import Image
import pytesseract

def OCR(self):
    ocrResult=pytesseract.image_to_string(self)
    proc_ocr_text = ocrResult.replace('\r', ' ').replace('\n', ' ').replace('\"', '\'').replace('<', '').replace('>',
                                                                                                                 '')
    return ocrResult

if __name__=="__main__":
    print("Test OCR...")
    OCR("UsageTesting-Artifacts/8-Menu/abc-menu-2/ir_data_auto/abc-menu-2-bbox-0342-widget.jpg")