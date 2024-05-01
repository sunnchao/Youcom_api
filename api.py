from flask import Flask, Response, request
import requests
import uuid
from datetime import datetime
import json
from flask_cors import CORS
import re

models = ['gpt_4', 'gpt_4_turbo', 'claude_2', 'claude_3_opus', 'claude_3_sonnet', 'claude_3_haiku', 'gemini_pro', 'gemini_1_5_pro', 'databricks_dbrx_instruct', 'command_r', 'command_r_plus', 'zephyr']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.0) AppleWebKit/534.2 (KHTML, like Gecko) Chrome/59.0.865.0 Safari/534.2',
    'Accept': 'text/event-stream',
    'Referer': 'https://you.com/',
}

app = Flask(__name__)
CORS(app)

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
        'isSmallMediumDevice':'true',
        'selectedChatMode':'custom',
        'selectedAIModel':model,
        'traceId':f'{chatid}|{uuid.uuid4()}|{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")}'
    }
    return cookies,params

def parse_1(data):
    messages = data['messages']
    model = data['model']
    _stream = data['stream']
    if model == 'gem_pro':
        model = 'gemini_pro'
    elif model == 'gem_1_5_pro':
        model = 'gemini_1_5_pro'
    elif model not in models:
        model = 'gpt_4_turbo'
    if model == 'command_r' or model == 'zephyr':
        add_t = "This is the api format of our previous conversation, please understand and reply to the user's last question"
        messages = add_t + str(messages)
    elif model == 'databricks_dbrx_instruct' or model == 'gemini_pro'or model == 'gemini_1_5_pro':
        for item in reversed(messages):
            if item['role'] == 'user':
                messages = item['content']
                break
    return messages,model,_stream

def chat_liu(chat, model, session, session_jwt):
    chatid = uuid.uuid4()
    cookies,params = get_ck_parms(session, session_jwt, chat, chatid, model)
    response = requests.get(
        'https://you.com/api/streamingSearch',
        cookies=cookies,
        headers=headers,
        params=params,
        stream=True
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
                    chat_text = chat_text + content
        yield bytes(f"data: {['DONE']}", 'utf-8')
        yield bytes()
    else:
        return response.status_code

def chat_feiliu(chat, model, session, session_jwt):
    chatid = uuid.uuid4()
    cookies,params = get_ck_parms(session, session_jwt, chat, chatid, model)
    response = requests.get(
        'https://you.com/api/streamingSearch',
        cookies=cookies,
        headers=headers,
        params=params,
        stream=True
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
                    chat_text = chat_text + json.loads(data)['youChatToken']
    else:
        return {"error": f'返回错误|{str(response.status_code)}'}, response.status_code
    return chat_text


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
        messages,model,_stream = parse_1(request.get_json())
        if _stream == True:
            return Response(chat_liu(str(messages), model, session, session_jwt), mimetype='text/event-stream')
        else:
            return chat_feiliu(messages, model, session, session_jwt)
    except:
        return {"error": "Invalid JSON body"}, 404

if __name__ == '__main__':
    app.run(debug=True, port=5060, host='0.0.0.0')
