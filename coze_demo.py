from usr.coze import cozews
from usr import packet
import ujson
from machine import Pin
import request
import modem
import uhashlib
import ubinascii

from usr import Qth
import _thread
import dataCall
import utime
import log

Qth.setServer('mqtt://iot-south.quectelcn.com:1883')
PRODUCT_KEY = 'p11v3i'
PRODUCT_SECRET = 'TnVNa0dLS0JtS2RC'
AI_ACCESS_SECRET = '1b575890654447b39818de79ab33fbce'
AUTH_HEADER = 'af78e30677dd671fa5351017a299847'

# PRODUCT_KEY = 'p11vfz'
# PRODUCT_SECRET = 'c2dBTnF6M1FmUkE1'
# AI_ACCESS_SECRET = 'f29d65b22cd94ee4adcf2c2eda38e2b3'
# AUTH_HEADER = 'af78e30677dd671fa5351017a299847'

gpio1 = Pin(Pin.GPIO39, Pin.OUT, Pin.PULL_DISABLE, 1)
gpio1.write(1)

dev_volume = 8

def callback(coze, msg):
    start,end = ujson.search(msg, 'event_type')
    event = msg[start:end]
    if event == packet.EventType.CHAT_CREATED:
        coze.start_audio_stream()
        print('connect server success...')
    elif event == packet.EventType.DISCONNECTED:
        print('server disconnected...')
    elif event == packet.EventType.CONVERSATION_AUDIO_TRANSCRIPT_COMPLETED:
        start,end = ujson.search(msg, 'content')
        print('ASR {}'.format(msg[start:end]))
    elif event == packet.EventType.CONVERSATION_MESSAGE_COMPLETED:
        start,end = ujson.search(msg, 'content_type')
        content_type = msg[start:end]
        start,end = ujson.search(msg, 'type')
        type = msg[start:end]
        if content_type == 'text' and type == 'answer':
            start,end = ujson.search(msg, 'content')
            print('TTS {}'.format(msg[start:end]))
    elif event == packet.EventType.CONVERSATION_CHAT_FAILED:
        start,end = ujson.search(msg, 'last_error')
        print('failed {}'.format(msg[start:end]))
    elif event == packet.EventType.SERVER_ERROR:
        start,end = ujson.search(msg, 'msg')
        print('error {}'.format(msg[start:end]))
    else:
        print('unkown event_type: {}'.format(msg['event_type']))


logApp = log.getLogger("examp")

def http_post():
    try:
        dev_imei = modem.getDevImei()
        currenttime = utime.mktime(utime.localtime())

        signTemp = "{}{}{}{}".format(PRODUCT_KEY, dev_imei, currenttime, AI_ACCESS_SECRET)
        hash_obj  = uhashlib.sha256()  # 创建hash对象
        hash_obj.update(signTemp)
        sign = ubinascii.hexlify(hash_obj.digest())

        url = "https://aigc-api.iotomp.com/v2/aibiz/openapi/v1/coze/websocketConnectInfo/v1"
        data = {
            'productKey': PRODUCT_KEY, 
            'deviceKey': dev_imei, 
            'timestamp': currenttime, 
            'sign': sign
        }
        headers= {
            'Authorization': AUTH_HEADER, 
            'Content-Type': 'application/json'
        }
        # 发送请求
        logApp.info("发送WebSocket连接信息请求")
        logApp.info("请求参数：{}".format(data))
        response = request.post(url, data=ujson.dumps(data), headers=headers)
        # 检查响应是否为空
        if not response:
            logApp.error("请求无响应")
            return None, None, None

        logApp.info("响应状态码：{}".format(response.status_code))
        logApp.info("响应内容：{}".format(response.text))

        if response.status_code != 200:
            logApp.error("请求失败！状态码：{}，响应：{}".format(response.status_code, response.text))
            return None, None, None

        # 解析响应
        try:
            result = response.json()
        except ValueError as e:
            logApp.error("解析响应JSON失败：{}".format(str(e)))
            return None, None, None

        # 验证响应结构
        if 'data' not in result:
            logApp.error("响应中缺少data字段")
            return None, None, None

        required_fields = ['accessToken', 'botId', 'workflowId']
        for field in required_fields:
            if field not in result['data']:
                logApp.error("响应中缺少{}字段".format(field))
                return None, None, None

        return (
            result['data']['accessToken'],
            result['data']['botId'],
            result['data']['workflowId']
        )

    except Exception as e:
        logApp.error("http_post异常: {}".format(str(e)))
        return None, None, None  # 异常时返回三个None


# Qth.sendTsl(1, {"13": 1})
# # 上报设备的电量、接入方式以及音量大小等内容
# # my_dict = {}
# # my_dict.update({"4":8}) # 设备音量
# # my_dict.update({"8":100}) # 设备电量->根据实际采集的电量上报
# # my_dict.update({"9":0}) # 充电状态 1：未充电   2：充电中  3：充电完成
# # my_dict.update({"13":1}) # AI接入方式 0：RTC    1：WS
# # Qth.sendTsl(1, my_dict)

def App_devEventCb(event, result):
    logApp.info('dev event:{} result:{}'.format(event, result))
    if(2== event and 0 == result):
        Qth.otaRequest()
        # Qth.sendTsl(1, {"13": 1})
        # # 上报设备的电量、接入方式以及音量大小等内容
        my_dict = {}
        my_dict.update({4: 8}) # 设备音量
        my_dict.update({8: 100}) # 设备电量->根据实际采集的电量上报
        my_dict.update({9: 0}) # 充电状态 1：未充电   2：充电中  3：充电完成
        my_dict.update({13: 1}) # AI接入方式 0：RTC    1：WS
        Qth.sendTsl(1, my_dict)


def App_cmdRecvTransCb(value):
    ret = Qth.sendTrans(1, value)
    logApp.info('recvTrans value:{} ret:{}'.format(value, ret))

def merge_dict(original, update_data):
    """递归合并字典：用update_data更新original，新增不存在的键，保留原始未覆盖的键"""
    for key, value in update_data.items():
        if isinstance(value, dict) and key in original and isinstance(original[key], dict):
            # 若子节点是字典，则递归合并
            merge_dict(original[key], value)
        else:
            # 否则直接覆盖或新增键
            original[key] = value
    return original


def App_cmdRecvTslCb(value):
    logApp.info('recvTsl:{}'.format(value))
    for cmdId, val in value.items():
        if cmdId == 11:
            for subId, subVal in val.items():
                if subId == 1:
                    logApp.info('{}:{}'.format(subId, subVal))
                elif subId == 2:
                    subVal = ujson.loads(subVal)
                    updated_result = merge_dict(packet.update, subVal)
                    coze.update(updated_result)

def App_cmdReadTslCb(ids, pkgId):
    logApp.info('readTsl ids:{} pkgId:{}'.format(ids, pkgId))
    value=dict()
    for id in ids:
        if 7 == id:
            value[7]=2
    Qth.ackTsl(1, value, pkgId)

def App_cmdRecvTslServerCb(serverId, value, pkgId):
    logApp.info('recvTslServer serverId:{} value:{} pkgId:{}'.format(serverId, value, pkgId))
    Qth.ackTslServer(1, serverId, value, pkgId)

def App_otaPlanCb(plans):
    logApp.info('otaPlan:{}'.format(plans))
    Qth.otaAction(1)

def App_fotaResultCb(comp_no, result):
    logApp.info('fotaResult comp_no:{} result:{}'.format(comp_no, result))

def App_sotaInfoCb(comp_no, version, url,fileSize, md5, crc):   # fileSize是可选参数
    logApp.info('sotaInfo comp_no:{} version:{} url:{} fileSize:{} md5:{} crc:{}'.format(comp_no, version, url,fileSize, md5, crc))
    # 当使用url下载固件完成，且MCU更新完毕后，需要获取MCU最新的版本信息，并通过setMcuVer进行更新
    Qth.setMcuVer('MCU1', 'V1.0.0', App_sotaInfoCb, App_sotaResultCb)

def App_sotaResultCb(comp_no, result):
    logApp.info('sotaResult comp_no:{} result:{}'.format(comp_no, result))

def Qth_tslSend():
    static_var = 0
    while True:       
        # 先判断连接云平台状态
        if Qth.state():
            Qth.sendTsl(1, {1: static_var})   #用户任务，每30秒上报精油剩余容量     
            static_var+=1
        utime.sleep(30)

if __name__ == '__main__':
    dataCall.setAutoActivate(1, 1)
    dataCall.setAutoConnect(1, 1)
    Qth.setServer('mqtt://iot-south.quectelcn.com:1883')
    # 获取WebSocket连接信息
    access_token, bot_id, workflow_id = http_post()
    logApp.info("获取连接信息: bot_id={}".format(bot_id))

    # 连接Coze服务
    url = "wss://ws.coze.cn/v1/chat?bot_id={}".format(bot_id)
    coze = cozews(url, access_token, callback)  # 修复原代码中auth参数未定义的问题
    coze.config(volume=dev_volume)
    coze.start()
    logApp.info("Coze服务启动")

    Qth.init()
    Qth.setProductInfo(PRODUCT_KEY, PRODUCT_SECRET)
    Qth.setBsEt('tls')

    eventOtaCb={
            'otaPlan':App_otaPlanCb,
            'fotaResult':App_fotaResultCb
            }
    eventCb={
        'devEvent':App_devEventCb, 
        'recvTrans':App_cmdRecvTransCb, 
        'recvTsl':App_cmdRecvTslCb, 
        'readTsl':App_cmdReadTslCb, 
        'readTslServer':App_cmdRecvTslServerCb,
        'ota':eventOtaCb
        }
    Qth.setEventCb(eventCb)
    Qth.setAppVer('V1.0.1', App_sotaResultCb)
    Qth.start()


