import requests
import uuid
from datetime import datetime
import json

proxy = None
# 例: proxy = 'a:a@proxy.socks5.io:3005'

if proxy:
    proxies = {'http':proxy,'https':proxy}
else:
    proxies = None
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.0) AppleWebKit/534.2 (KHTML, like Gecko) Chrome/59.0.865.0 Safari/534.2',
    'Accept': 'text/event-stream',
    'Referer': 'https://you.com/',
}
def get_ck_parms(session, session_jwt, chat, chatid, model):
    cookies = {
        'youpro_subscription': 'true',
        'stytch_session': session,
        'stytch_session_jwt': session_jwt,
        'ydc_stytch_session': session,
        'ydc_stytch_session_jwt': session_jwt,
    }
    cookies = {
        'youpro_subscription': 'true',
        'stytch_session': session,
        'stytch_session_jwt': session_jwt,
        'ydc_stytch_session': session,
        'ydc_stytch_session_jwt': session_jwt,
    }
    params = {
        'q':chat,
        'page':1,
        'count':10,
        'safeSearch':'Off',
        'responseFilter':'WebPages,TimeZone,Computation,RelatedSearches',
        'domain':'youchat',
        'use_personalization_extraction':'true',
        'queryTraceId':chatid,
        'chatId':chatid,
        'conversationTurnId':uuid.uuid4(),
        'pastChatLength':0,
        'isSmallMediumDevice':'true',
        'selectedChatMode':'custom',
        'selectedAIModel':model,
        'traceId':f'{chatid}|{uuid.uuid4()}|{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}'
    }
    return cookies,params

session_jwt = ''
session = ''
chat = '你好'
chatid = uuid.uuid4()
model = ''
cookies,params = get_ck_parms(session, session_jwt, chat, chatid, model)
response = requests.get(
        'https://you.com/api/streamingSearch',
        cookies=cookies,
        headers=headers,
        params=params,
        stream=True,
        proxies=proxies
    )

if response.status_code == 403 and 'Just a moment...' in response.text:
    print('盾')
else:
    print(f'返回状态码: {response.status_code}')
    chat_text = ''
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                if 'event' in data:
                    continue
                else:
                    data = data[6:]
                if 'youChatToken' in data:
                    id = str(uuid.uuid4())
                    content = json.loads(data)['youChatToken']
                    if 'Please log in to access GPT-4 mode.' in content and 'Answering your question without GPT-4 mode:' in content:
                        content = 'cookie失效或会员到期，将默认使用智障模型!\n\n'
                    chat_text = chat_text + content
    print(f'返回内容 {chat_text}')