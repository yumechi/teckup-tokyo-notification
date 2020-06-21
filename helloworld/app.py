from chalice import Chalice
import logging
import os

app = Chalice(app_name='helloworld')
# logging setting
# refer: https://aws.github.io/chalice/topics/logging
app.log.setLevel(logging.INFO)

@app.route('/')
def index():
    return {
        'jinrui': 'shosinsha_pri',
    }

@app.route('/idol/{idol_name}')
def echo_idol_name(idol_name):
    return {'idol_name': idol_name}

@app.route('/test', methods=['POST'], name='TweetTest')
def send_tweet_test():
    import urllib.request
    import json

    json_body = app.current_request.json_body
    app.log.info("received: %s" % json_body)

    webhook_url = os.environ.get('WEBHOOK_URL')
    method = "POST"
    headers = {
        "Content-Type" : "application/json",
        # User-Agent 指定なしだと怒られるため
        "User-Agent": "Yumechi WebHook/1.0",
    }

    # TODO: コンテンツはこの辺を見て増やしたい
    # https://birdie0.github.io/discord-webhooks-guide/discord_webhook.html
    values = {'content' : str(json_body)}


    # 典型的なリクエスト処理
    # refer: https://qiita.com/neko_the_shadow/items/324976c7b54623e82b26
    # refer: https://qiita.com/hoto17296/items/8fcf55cc6cd823a18217
    json_data = json.dumps(values).encode("utf-8")
    request = urllib.request.Request(webhook_url, data=json_data, headers=headers)
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8")
        return {
            'status': 'ok',
            'res': response.read().decode("utf-8"),
        }
