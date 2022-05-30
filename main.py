import json
import requests
import re
import time
import os

'''
使用方法：https://www.jysafe.cn/4498.air
author: msojocs
'''
class FC(object):
    cookie = ""
    available = False
    ocrServer = ""
    def __init__(self, cookie, ocrServer):
        self.cookie = cookie
        self.ocrServer = ocrServer
        pass
    
    def fuckCourse(self, profiledId, lessonId):
        try:
            body = {
                "optype": "true",
                "operator0": lessonId + ":true:0",
                "lesson0":lessonId,
                "schLessonGroup_" + lessonId:"undefined"
            }
            req = requests.post("http://jwgl.cuit.edu.cn/eams/stdElectCourse!batchOperator.action?profileId=" + profiledId,
                headers={
                    "cookie": self.cookie,
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer" : "http://jwgl.cuit.edu.cn/eams/stdElectCourse!batchOperator.action?profileId=" + profiledId,
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.0 Safari/537.36 Edg/84.0.521.0"
                }, data=body, timeout=5, allow_redirects=False)
            req.encoding = 'utf-8'
            
            html = req.text
            ret = re.search(r"margin:auto;\">\n\t\t\t\t(.*)<\/br>", html)
            if ret == None:
                print("cookie过期")
                exit(-1)
                pass
            print(ret.group(1))
            req.close()
            if '成功' in ret.group(1):
                print('get')
                return True
        except Exception as err:
            print("出错")
            print(err)
            return False
        pass
    pass

    def getPic(self):
        url="http://jwgl.cuit.edu.cn/eams/captcha/image.action"
        headers = {
            'cookie': self.cookie
            }
        picReq=requests.get(url=url, headers=headers)
        # print(picReq.content)
        return picReq.content
        pass

    def postOCRPic(self, pic):
        url = self.ocrServer
        files = {'captcha': pic}
        data = {
            'enctype':'multipart/form-data',
            'name':'captcha'
            }
        ocrReq=requests.post(url=url, data=data, files=files)
        # print(ocrReq.content)
        return json.loads(ocrReq.content)
        pass

    '''
    '''
    def checkCaptcha(self, captcha, profiledId):
        url="http://jwgl.cuit.edu.cn/eams/stdElectCourse!defaultPage.action"
        headers = {
            'cookie': self.cookie
            }
        data = {
            'captcha_response': captcha,
            'electionProfile.id': profiledId
        }
        checkReq = requests.post(url=url, headers=headers, data=data, allow_redirects=False)
        # print(checkReq.text)
        # 未登录与验证码错误都是302,但Location去向不同
        if checkReq.status_code == 200 :
            self.available = '操作 失败:不在选课时间内' not in checkReq.text
            return True
        elif 'sso' in checkReq.headers['Location']:
            # 转到统一登录中心
            print('cookie失效！！！')
            exit(1)
        return False
        pass
    
    def isAvailable(self, captcha, profiledId):
        url="http://jwgl.cuit.edu.cn/eams/stdElectCourse!defaultPage.action"
        headers = {
            'cookie': self.cookie
            }
        data = {
            'captcha_response': captcha,
            'electionProfile.id': profiledId
        }
        checkReq = requests.post(url=url, headers=headers, data=data, allow_redirects=False)
        # print(checkReq.text)
        # 未登录与验证码错误都是302,但Location去向不同
        if checkReq.status_code == 200 :
            return '操作 失败:不在选课时间内' not in checkReq.text
        elif 'sso' in checkReq.headers['Location']:
            # 转到统一登录中心
            print('cookie失效！！！')
            self.cookie = input("请输入新的cookie:")
            False
        return False
        pass


################### 入口 ###########################
if __name__ == "__main__":
    # 加载配置
    with open('config.json',encoding='utf-8') as f:
        config = json.load(f)
    cookie = config['cookie']
    profiledId = config['profiled_id']
    lessonId = config['lesson_id']

    print("开始了呀")
    cuit = FC(cookie, config['ocr_server'])
    
    # 验证码
    cnt = 0
    while True:
        pic = cuit.getPic()
        ocrResult = cuit.postOCRPic(pic)
        print('OCR: ' + ocrResult['result'])

        # 按识别出来的验证码写入文件
        with open('pic/' + ocrResult['result'] + '.jpg', 'wb') as file:
            file.write(pic)

        checkResult = cuit.checkCaptcha(ocrResult['result'], profiledId)
        if checkResult:
            break
        cnt += 1
        time.sleep(0.5)
        if cnt % 5 == 0:
            print('验证码错误次数过多, 等待5秒')
            time.sleep(5)

    print('验证码检测通过,等待1秒')
    time.sleep(1)
    # 检测开放状态
    print('检测选课开放状态')
    cnt = 0
    while True:
        if cuit.isAvailable(ocrResult['result'], profiledId):
            break
            pass
        cnt += 1
        print('没有到选课时间,等待5秒 - ' + str(cnt))
        time.sleep(5)

    # 抢课
    print('开始抢课')

    i= 0
    while True:
        i += 1
        print(i)
        if cuit.fuckCourse(profiledId, lessonId):
            break
        time.sleep(0.5)
        if i >= 20:
            i = 0
            os.system("cls")
            pass
        pass
    pass