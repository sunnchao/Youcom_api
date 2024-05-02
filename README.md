# Youcom_api
you.com的逆向api，支持Stream 流式传输

## 测试
拉取并安装模块后运行
```bash
python test.py
```
如正常返回对话内容即可正常使用

如果输出 盾 请尝试[http代理](https://github.com/len-ni/Youcom_api/?tab=readme-ov-file#cf%E7%9B%BE)

## 部署
```bash
git clone https://github.com/len-ni/Youcom_api
cd Youcom_api
pip install -r requirements.txt
python api.py
```
## 使用
请求头需携带Authorization 内容是you.com的cookie。使用以下代码在浏览器F12开发者模式-控制台输入获取,nextchat则设置为API KEY。
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
## 支持的模型
使用发送API格式内容的对话，可正常返回
> - gpt_4
> - gpt_4_turbo
> - claude_3_opus
> - claude_3_sonnet
> - claude_3_haiku
> - command_r_plus

不支持api格式消息，使用增加提示解决(可能会露馅，未测试)
> - command_r
> - zephyr
> - claude_2

不支持上下文
> - databricks_dbrx_instruct 
> - gemini_pro
> - gemini_1_5_pro

nextchat直接在自定义模型名添加以下内容即可使用
```text
gpt_4,gpt_4_turbo,claude_2,claude_3_opus,claude_3_sonnet,claude_3_haiku,gem_pro,gem_1_5_pro,databricks_dbrx_instruct,command_r,command_r_plus,zephyr
```
其中gem_pro与gem_1_5_pro是gemini_pro和gemini_1_5_pro。因为使用原名称会使用google参数进行请求

## 其他事项
目前实测ip干净情况下不需要过cf盾。请自测

gemini_pro与gemini_1_5_pro同样使用openai API，nextchat可使用名称gem_pro和gem_1_5_pro进行调用

报错 ImportError: cannot import name 'EVENT_TYPE_OPENED' from 'watchdog.events' 使用以下代码更新watchdog
```bash
pip install --upgrade watchdog
```

## cf盾
关于cf盾，遇见盾会返回状态码403，无消息内容。

目前测试的cf盾貌似有三种

1.浏览器和API均不跳盾
2.浏览器跳盾，API不跳盾
3.浏览器和API均跳盾

如果跳盾可以尝试http代理解决，更新后的test.py和api.py文件内都有proxy选项，填入http代理即可使用。

我测试的 socks5.io 的部分家宽代理可过盾，具体自测。如果需要后续可能会加上socks5.io自动更换IP

放一个带aff的地址，不喜自去 https://my.socks5.io#CNLRXXRU


