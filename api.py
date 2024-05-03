from flask import Flask, Response, request
import requests
import uuid
from datetime import datetime
import json
from flask_cors import CORS
import re
import random
import string
import os

proxy = os.getenv("PROXY", None)
print(f"Proxy is set to: {proxy}")
ua = 'Mozilla/5.0 (Windows NT 5.0) AppleWebKit/534.2 (KHTML, like Gecko) Chrome/59.0.865.0 Safari/534.2'
# 例: proxy = a:a@proxy.socks5.io:3005

if proxy:
    proxies = {'http':proxy,'https':proxy}
else:
    proxies = None

models = ['gpt_4', 'gpt_4_turbo', 'claude_2', 'claude_3_opus', 'claude_3_sonnet', 'claude_3_haiku', 'gemini_pro', 'gemini_1_5_pro', 'databricks_dbrx_instruct', 'command_r', 'command_r_plus', 'zephyr', 'claude_3_opus_2k', 'research', 'create']

headers = {
    'User-Agent': ua,
    'Accept': 'text/event-stream',
    'Referer': 'https://you.com/',
}



app = Flask(__name__)
CORS(app)

def update_files(content, cookies):
    response = requests.get('https://you.com/api/get_nonce', cookies=cookies, headers=headers, proxies=proxies)
    boundary = '----MyCustomBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    user_filename = f'{"".join(random.choices(string.ascii_letters + string.digits, k=5))}.txt'
    multipart_data = (
        '--' + boundary + '\r\n' +
        f'Content-Disposition: form-data; name="file"; filename={user_filename}\r\n' +
        'Content-Type: text/plain\r\n\r\n' +
        content
        +'\r\n'
        '--' + boundary + '--'
    )
    headers123 = {
        'User-Agent': ua,
        'Accept': 'text/event-stream',
        'Referer': 'https://you.com/',
        'accept': 'multipart/form-data',
        'accept-language': 'cmn',
        'content-type': 'multipart/form-data; boundary=' + boundary,
        'x-upload-nonce': response.text,
        'Content-Length': str(len(content.encode('utf-8'))),
    }
    response = requests.post('https://you.com/api/upload', headers=headers123, data=multipart_data.encode('utf-8'), cookies=cookies, proxies=proxies)
    filename = response.json()['filename']
    return filename, user_filename, str(len(content.encode('utf-8')))

def get_ck_parms(session, session_jwt, chat, chatid, model):
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
        'selectedChatMode':'custom',
        'selectedAIModel':model,
        'traceId':f'{chatid}|{uuid.uuid4()}|{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}'
    }
    return cookies,params
def get_research_and_creat_parms(session, session_jwt, chat, chatid, model):
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
        'selectedChatMode':model,
        'traceId':f'{chatid}|{uuid.uuid4()}|{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}'
    }
    return cookies,params

def parse_1(data):
    messages = data['messages']
    model = data['model']
    try:
        _stream = data['stream']
    except:
        _stream = False

    if '使用四到五个字直接返回这句话的简要主题，不要解释、不要标点、不要语气词、不要多余文本，不要加粗，如果没有主题，请直接返回“闲聊”' in str(messages):
        model = 'gpt_4_turbo'
    if model == 'gem_pro':
        model = 'gemini_pro'
    elif model == 'gem_1_5_pro':
        model = 'gemini_1_5_pro'
    elif model not in models:
        model = 'gpt_4_turbo'
    elif model == 'research':
        model = 'research'
    elif model == 'create':
        model = 'create'
    if model == 'command_r' or model == 'zephyr' or model == 'claude_2':
        add_t = "This is the api format of our previous conversation, please understand and reply to the user's last question"
        messages = add_t + str(messages)
    elif model == 'databricks_dbrx_instruct' or model == 'gemini_pro'or model == 'gemini_1_5_pro' or model == 'claude_3_opus_2k' or model == 'research' or model == 'create':
        for item in reversed(messages):
            if item['role'] == 'user':
                messages = item['content']
                break
    return str(messages),model,_stream

def chat_liu(chat, model, session, session_jwt):
    chatid = uuid.uuid4()
    if model == 'research' or model == 'create':
        cookies,params = get_research_and_creat_parms(session, session_jwt, chat, chatid, model)
    else:
        cookies,params = get_ck_parms(session, session_jwt, chat, chatid, model)
    response = requests.get(
        'https://you.com/api/streamingSearch',
        cookies=cookies,
        headers=headers,
        params=params,
        stream=True,
        proxies=proxies
    )
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                data = line.decode('utf-8')
                if 'event' in data:
                    continue
                else:
                    data = data[6:]  # Assumes first 6 characters need to be removed
                try:
                    json_data = json.loads(data)
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}, Data: {data}")
                    continue
                print(json_data)
                if 'youChatToken' in json_data or 't' in json_data:
                    content = 'Generating... '
                    id = str(uuid.uuid4())
                    if model == 'create':
                        if json_data.get('t') is None:
                            continue
                        content = json_data.get('t')
                    elif 'youChatToken' in json_data:
                        content = json_data['youChatToken']
                    elif model == 'research':
                        if json_data.get('t') is None:
                            continue
                        content = json_data.get('t')
                    try:
                        if 'Please log in to access GPT-4 mode.' in content and 'Answering your question without GPT-4 mode:' in content:
                            content = 'cookie失效或会员到期，将默认使用智障模型!\n\n'
                    except:
                        pass
                    if content == 'Generating... ':
                        continue
                    yield "data: {}\n\n".format(json.dumps({
                        "id": "chatcmpl-"+id,
                        "created": 0,
                        "model": model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": content,
                            }
                        }]
                    }))
        yield bytes(f"data: {['DONE']}", 'utf-8')
        yield bytes()
    else:
        if response.status_code == 403 and 'Just a moment...' in response.text:
            print('盾')
        return response.status_code
    
def claude_3_opus_2k(chat, model, session, session_jwt):
    model = 'claude_3_opus'
    cookies = {
        'youpro_subscription': 'true',
        'stytch_session': session,
        'stytch_session_jwt': session_jwt,
        'ydc_stytch_session': session,
        'ydc_stytch_session_jwt': session_jwt,
    }

    with open('wb.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    filename, user_filename, size = update_files(content.replace('{tihuan1145141919810}', chat), cookies)
    chatid = str(uuid.uuid4())
    params = {'q': 'Please review the attached prompt', 'page': '1', 'count': '10', 'safeSearch': 'Moderate', 'mkt': 'zh-HK', 'responseFilter': 'WebPages,TimeZone,Computation,RelatedSearches', 'domain': 'youchat', 'use_personalization_extraction': 'true', 
         'queryTraceId': chatid, 
         'chatId': chatid, 
         'conversationTurnId': str(uuid.uuid4()), 
         'pastChatLength': '0', 'isSmallMediumDevice': 'true', 'selectedChatMode': 'custom', 
         'userFiles': '[{"user_filename":"' + user_filename + '","filename":"' + filename + '","size":"' + size + '"}]', 
         'selectedAIModel': 'claude_3_opus', 
         'traceId': f'{chatid}|{uuid.uuid4()}|{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}',
         'chat': '[]'}
    response = requests.get(
        'https://you.com/api/streamingSearch',
        cookies=cookies,
        headers=headers,
        params=params,
        stream=True,
        proxies=proxies,
        timeout=500
    )
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
                    yield "data: {}\n\n".format(json.dumps({
                        "id": "chatcmpl-"+id,
                        "created": 0,
                        "model": model,
                        "choices": [{
                            "index": 0,
                            "delta": {
                                "content": content,
                            }
                        }]
                    }))
        yield bytes(f"data: {['DONE']}", 'utf-8')
        yield bytes()
    else:
        if response.status_code == 403 and 'Just a moment...' in response.text:
            print('盾')
        return response.status_code

def chat_feiliu(chat, model, session, session_jwt):
    chatid = uuid.uuid4()
    cookies,params = get_ck_parms(session, session_jwt, chat, chatid, model)
    response = requests.get(
        'https://you.com/api/streamingSearch',
        cookies=cookies,
        headers=headers,
        params=params,
        stream=True,
        proxies=proxies
    )
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
    else:
        return {"error": f'返回错误|{str(response.status_code)}'}, response.status_code
    return {"id":f"chatcmpl-{str(uuid.uuid4())}",
     "OAI-Device-Id":str(uuid.uuid4()),
     "conversation_id":str(uuid.uuid4()),
     "created":123,
     "model":"gpt-3.5-turbo",
     "choices":[{"index":0,"message":{"role":"assistant","content":chat_text},"finish_reason":"stop"}],
     "usage":{"prompt_tokens":0,"completion_tokens":0,"total_tokens":0}}


@app.route('/')
def stream():
    return 'ok'
    
@app.route('/v1/chat/completions', methods=['POST', 'OPTIONS'])
def chatv1_1():
    if request.method == 'OPTIONS':
        return '', 204
    try:
        try:
            session_jwt = re.search(r'stytch_session_jwt=([^;]+)', request.headers.get('Authorization')).group(1)
            session = re.search(r'ydc_stytch_session=([^;]+)', request.headers.get('Authorization')).group(1)
        except:
            return {"error": "请确保传入的Authorization正确"}, 401
        try:
            messages,model,_stream = parse_1(request.get_json())
        except Exception as e:
            print(e)
            return {"error": "Invalid JSON body1"}, 404
        try:
            if model == 'claude_3_opus_2k':
                if _stream == False:
                    return {"error": "Only supports stream mode"}, 404
                return Response(claude_3_opus_2k(str(messages), model, session, session_jwt), mimetype='text/event-stream')
        except:
            return {"error": "Upload error or membership expiration"}, 404

        if _stream == True:
            return Response(chat_liu(str(messages), model, session, session_jwt), mimetype='text/event-stream')
        else:
            return chat_feiliu(messages, model, session, session_jwt)
    except Exception as e:
        print('error')
        print(e)
        return {"error": "Invalid JSON body"}, 404

if __name__ == '__main__':
    app.run(debug=True, port=50600, host='0.0.0.0')