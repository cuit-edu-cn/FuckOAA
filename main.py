import json
import platform
import time
import os
from cuit import FC


'''
使用方法：https://www.jysafe.cn/4498.air
author: msojocs
'''

################### 入口 ###########################
if __name__ == "__main__":
    # 加载配置
    with open('config.json',encoding='utf-8') as f:
        config = json.load(f)
    cookie = config['cookie']
    profiledId = config['profiled_id']
    courseName = config['course_name']

    print("开始了呀")
    cuit = FC(cookie, config['ocr_server'])
    
    # 验证码
    cnt = 0
    while True:
        pic = cuit.getPic()
        ocrResult = cuit.postOCRPic(pic)
        print('OCR: ' + ocrResult['result'])

        # 按识别出来的验证码写入文件
        # with open('pic/' + ocrResult['result'] + '.jpg', 'wb') as file:
        #     file.write(pic)

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
    print('获取lessonId')
    lessonId = cuit.courseName2Id(profiledId, courseName)
    if lessonId == None:
        print('没有找到相关课程:' + courseName)
        exit(1)

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
        if cuit.fuckCourse(str(profiledId), str(lessonId)):
            break
        time.sleep(0.5)
        if i >= 20:
            i = 0
            if platform.system().lower() == 'linux':
                os.system("clear")
            elif platform.system().lower() == 'windows':
                os.system("cls")
            pass
        pass
    pass