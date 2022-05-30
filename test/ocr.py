import json
import requests


def getPic():
    url="http://jwgl.cuit.edu.cn/eams/captcha/image.action"
    picReq=requests.get(url=url)
    # print(picReq.content)
    with open('picture.jpg', 'wb') as file:
        file.write(picReq.content)
    return picReq.content
    pass

def postOCRPic(pic):
    url="http://127.0.0.1:4006/vercode"
    files = {'captcha': pic}
    data = {'enctype':'multipart/form-data','name':'captcha'}
    ocrReq=requests.post(url=url, data=data, files=files)
    print(ocrReq.content)
    return json.loads(ocrReq.content)
    pass

def checkCaptcha(captcha):
    url="http://jwgl.cuit.edu.cn/eams/stdElectCourse!defaultPage.action"
    requests.post(url=url)
    pass
if __name__ == "__main__":
    # 获取图片
    pic=getPic()
    # 识别图片
    ocr=postOCRPic(pic)
    print(ocr['result'])
    # 输出结果
    pass