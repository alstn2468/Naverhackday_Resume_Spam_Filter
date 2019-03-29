from PIL import Image
from pytesseract import *
from pymongo import MongoClient
import configparser
import os
import sys
import csv
import re

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
        image_path,
        lang=lang,
        config='--psm 1 -c preserve_interword_spaces=1',
    )

    print("+++ OCT Extract Result +++")

    print(outputText + "\n")

    str_to_text(textName, outputText)


'''이미지에서 추출한 문자열을 파일로 저장하는 함수
textName   : 저장할 파일 이름
outputText : 저장할 텍스트
return     : 없음
'''


def str_to_text(textName, outputText):
    # 이미지 이름과 같은 이름의 텍스트 파일
    textName += ".txt"

    print("Output Text File Path :", textName, "\n")

    with open(textName, "w", encoding="utf-8") as f:
        f.write(outputText)


'''텍스트파일을 CSV파일로 만들어주는 함수
textName   : 저장된 텍스트 파일 이름
csvName    : 저장할 CSV 파일 이름
outTxtPath : 저장된 텍스트 파일 경로
outCsvPath : 저장할 CSV 파일 경로
return     : 없음
'''


def text_to_csv(textName, csvName, outTxtPath, outCsvPath):
    # 파일의 사이즈가 0이면 미추출 파일
    if os.path.getsize(os.path.join(outTxtPath, textName)) != 0:
        with open(os.path.join(outTxtPath, textName), "r", encoding="utf-8") as r:
            with open(os.path.join(outCsvPath, config["FileName"]["CsvFileName"]),
                      "a", encoding="utf-8", newline='') as w:
                writer = csv.writer(w, delimiter=',')
                text = cleanText(r.read())
                writer.writerow([csvName, text])


'''OCR한 텍스트를 전처리하는 함수
data   : 전처리할 데이터
return : 전처리된 데이터
'''


def cleanText(data):
    # 특수문자 제거
    text = re.sub('[-=,#/\?:^$.@*\"※~&%・!\\′|\(\)\[\]\<\>`\'...⟫]', '', data)
    # 줄바꿈 제거
    text = text.strip('\n')

    return text


if __name__ == "__main__":

    # 이미지파일 경로
    imagePath = os.path.dirname(os.path.realpath(__file__)) \
        + config["Path"]["OriImgPath"]

    # 텍스트파일 저장 경로
    outTxtPath = os.path.dirname(os.path.realpath(__file__)) \
        + config["Path"]["OcrTxtPath"]

    # CSV파일 저장 경로
    outCsvPath = os.path.dirname(os.path.realpath(__file__)) \
        + config["Path"]["TxtCsvPath"]

    # OCR 데이터 추출 작업
    for root, dirs, files in os.walk(imagePath):
        for fileName in files:
            fullPath = os.path.join(root, fileName)

            print("Input Image File Name :", fileName)
            print("Input Image Path :", fullPath, "\n")

            ocr_to_str(fullPath, outTxtPath, fileName, "kor+eng")

    # CSV 변환 작업
    for fileName in os.listdir(outTxtPath):
        csvName = ''.join([i for i in fileName if not i.isdigit()]) \
                    .split('.')[0] \
                    .strip()

        text_to_csv(fileName, csvName, outTxtPath, outCsvPath)

    print("OCR Image --> Text --> CSV Convert Complete")
