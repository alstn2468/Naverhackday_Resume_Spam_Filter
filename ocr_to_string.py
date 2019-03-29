from PIL import Image
from pytesseract import *
import configparser
import os

# Config parser 초기화
config = configparser.ConfigParser()
# Config File 읽기
config.read(os.path.dirname(os.path.realpath(__file__))
            + os.sep + 'envs' + os.sep + 'property.ini')

def ocr_to_str(fullPath, outTxtPath, fileName, lang="eng"):
    # Image path
    image_path = Image.open(fullPath)
    textName = os.path.join(outTxtPath, fileName.split('.')[0])

    '''추출(이미지파일, 추출언어, 옵션)
    preserve_interword_spaces : 단어 간격 옵션 조절
    psm(페이지 세그먼트 모드) : 이미지 영역안에서 텍스트 추출 범위 모드
    '''
    outputText = image_to_string(
        image_path, lang=lang, config='--psm 1 -c preserve_interword_spaces=1'
    )


    print("+++ OCT Extract Result +++")
    print("Extract File Name :", fileName)
    print("\n")

    print(outputText)

    str_to_text(textName, outputText)

def str_to_text(textName, outputText):
    textName += ".txt"

    with open(textName, "w", encoding="utf-8") as f:
        f.write(outputText)

if __name__ == "__main__":

    outTxtPath = os.path.dirname(os.path.realpath(__file__)
                                 + config["Path"]["OcrTxtPath"])

    print(outTxtPath)

    for root, dirs, files in os.walk(
        os.path.dirname(os.path.realpath(__file__)) + config["Path"]["OriImgPath"]):

        for fileName in files:
            fullName = os.path.join(root, fileName)

            print("fileName :", fileName)
            print("fullName :", fullName)

            ocr_to_str(fullName, outTxtPath, fileName, "kor+eng")
