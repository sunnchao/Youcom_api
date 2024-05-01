# Youcom_api
you.com的逆向api，支持Stream 流式传输

## 部署
```bash
git clone https://github.com/len-ni/Youcom_api
cd Youcom_api
pip install -r requirements.txt
python api.py
```
## 使用
请求头需携带Authorization 内容是you.com的cookie。使用以下代码在浏览器F12开发者模式-控制台输入获取
```bash
var cookie = document.cookie;
var stytch_session_jwt = cookie.match(/stytch_session_jwt=([^;]+)/);
var ydc_stytch_session = cookie.match(/stytch_session=([^;]+)/);

if (stytch_session_jwt && ydc_stytch_session) {
    var combined_cookie = 'stytch_session_jwt=' + stytch_session_jwt[1] + '; ' + 'ydc_stytch_session=' + ydc_stytch_session[1];
    var ask = confirm('Cookie: ' + combined_cookie + '\n\n按下确定写入剪切板?');
    if (ask == true) {
        copy(combined_cookie);
        msg = combined_cookie;
    } else {
        msg = 'Cancel';
    }
} else {
    msg = '请登录后重试';
}
```

调用参数为openai API所需的参数
```request body
{"messages":[,{"role":"user","content":"你好"}],"stream":true,"model":"gpt-4"}
```
## 模型支持

## 其他事项
目前实测ip干净情况下不需要过cf盾。请自测
