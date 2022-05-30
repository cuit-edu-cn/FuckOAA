import requests
import re
import json
import execjs

class FC(object):
    cookie = ""
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
                "lesson0": lessonId,
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
        while True:
            try:
                picReq=requests.get(url=url, headers=headers, timeout=5)
                break
            except Exception as err:
                continue
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
        while True:
            try:
                checkReq = requests.post(url=url, headers=headers, data=data, allow_redirects=False, timeout=5)
                break
            except Exception as err:
                continue

        # print(checkReq.text)
        # 未登录与验证码错误都是302,但Location去向不同
        if checkReq.status_code == 200 :
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
        while True:
            try:
                checkReq = requests.post(url=url, headers=headers, data=data, allow_redirects=False, timeout=5)
                break
            except Exception as err:
                continue
        # print(checkReq.text)
        # 未登录与验证码错误都是302,但Location去向不同
        if checkReq.status_code == 200 :
            return '不在选课时间内' not in checkReq.text
        elif 'sso' in checkReq.headers['Location']:
            # 转到统一登录中心
            print('cookie失效！！！')
            self.cookie = input("请输入新的cookie:")
            False
        return False
        pass

    def courseName2Id(self, profileId, courseName):
        url="http://jwgl.cuit.edu.cn/eams/stdElectCourse!data.action?profileId=" + str(profileId)
        headers = {
            'cookie': self.cookie
            }
        while True:
            try:
                courseListReq = requests.get(url=url, headers=headers, allow_redirects=False, timeout=5)
                break
            except Exception as err:
                continue
        courseList = courseListReq.text
        # with open('test/html/courseList.html',encoding='utf-8') as f:
        #     courseList = f.read()
        # print(courseList)
        jsData = execjs.compile(courseList)
        lessonJSONs = jsData.eval('lessonJSONs')
        # print(lessonJSONs)
        for lesson in lessonJSONs:
            if courseName in lesson['name']:
                return lesson['id']
        return None
        pass