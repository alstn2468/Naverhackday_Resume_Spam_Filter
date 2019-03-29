from PIL import Image
from pytesseract import *
import configparser
import os

# Config parser 초기화
config = configparser.ConfigParser()
# Config File 읽기
config.read(os.path.dirname(os.path.realpath(__file__))
            + os.sep + 'envs' + os.sep + 'property.ini')

'''이미지에서 문자열을 추출하는 함수
fullPath   : 이미지 파일 경로
outTxtPath : 문자열 반환 경로
fileName   : 이미지 파일 이름
lang       : OCR언어 설정 default는 영어
return     : 없음
'''
def ocr_to_str(fullPath, outTxtPath, fileName, lang="eng"):
    # 이미지 경로
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

    print(outputText + "\n")

    str_to_text(textName, outputText)

'''이미지에서 추출한 문자열을 파일로 저장하는 함수
textName   : 저장할 파일 이름
outputText : 저장할 텍스트
'''
def str_to_text(textName, outputText):
    # 이미지 이름과 같은 이름의 텍스트 파일
    textName += ".txt"

    print("Output Text File Path :", textName, "\n")

    with open(textName, "w", encoding="utf-8") as f:
        f.write(outputText)


if __name__ == "__main__":

    outTxtPath = os.path.dirname(os.path.realpath(__file__))
    outTxtPath += config["Path"]["OcrTxtPath"]

    print("outTxtPath :", outTxtPath)

    for root, dirs, files in os.walk(
        os.path.dirname(
            os.path.realpath(__file__)) + config["Path"]["OriImgPath"]
    ):

        for fileName in files:
            fullPath = os.path.join(root, fileName)

            print("Input Image File Name :", fileName)
            print("Input Image Path :", fullPath, "\n")

            ocr_to_str(fullPath, outTxtPath, fileName, "kor+eng")
