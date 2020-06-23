from chalice import Chalice
import logging
import os

app = Chalice(app_name='teckup-notification')

# logging setting
# refer: https://aws.github.io/chalice/topics/logging
app.log.setLevel(logging.INFO)

@app.route('/')
def index():
    return {'health_check': 'ok'}


@app.route('/broadcast_tweet_by_user', methods=['POST'], name='UserTweet')
def broadcast_tweet_by_user():
    json_body = app.current_request.json_body
    app.log.info('received: %s' % json_body)

    user_name = json_body.get('user_name')
    text = json_body.get('text')
    link_to_tweet = json_body.get('link_to_tweet')
    created_at = convert_japan_tweet_time(json_body.get('created_at'))

    values = {
        'content': f'ハッシュタグ #TeckUp の新規投稿がありました',
        'embeds': [
            {
                'author': {
                    'name': user_name,
                    'url': link_to_tweet,
                },
                'description': f'{text}\n{link_to_tweet}',
                'timestamp': created_at,
            },
        ],
    }
    return send_post(values)


@app.route('/broadcast_tweet_by_search', methods=['POST'], name='UserTweet')
def broadcast_tweet_by_search():
    import urllib.request
    import json

    json_body = app.current_request.json_body
    app.log.info('received: %s' % json_body)

    # TODO: まだユーザーのものをコピペしただけ
    user_name = json_body.get('user_name')
    text = json_body.get('text')
    link_to_tweet = json_body.get('link_to_tweet')
    created_at = convert_japan_tweet_time(json_body.get('created_at'))

    values = {
        'content': f'ハッシュタグ #TeckUp の新規投稿がありました',
        'embeds': [
            {
                'author': {
                    'name': user_name,
                    'url': link_to_tweet,
                },
                'description': f'{text}\n{link_to_tweet}',
                'timestamp': created_at,
            },
        ],
    }

    return send_post(values)

def convert_japan_tweet_time(created_at):
    import datetime
    from dateutil.tz import gettz
    from dateutil.parser import parse

    if not created_at:
        return None

    # TODO: バグってはいなさそうだが、無駄が多い気がする（変換が一回多い気がしている）
    date_str = datetime.datetime.strptime(created_at, '%B %d, %Y at %H:%M%p')
    tzinfos = {'JST' : gettz('Asia/Tokyo')}
    str_to_dt = parse(date_str.isoformat() + ' JST', tzinfos=tzinfos)
    return str_to_dt.isoformat()

def send_post(values):
    import json
    import urllib.request

    webhook_url = os.environ.get('WEBHOOK_URL')
    method = 'POST'
    headers = {
        'Content-Type' : 'application/json',
        # User-Agent 指定なしだと怒られるため
        'User-Agent': 'Yumechi WebHook/1.0',
    }

    json_data = json.dumps(values).encode('utf-8')
    request = urllib.request.Request(webhook_url, data=json_data, headers=headers)
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode('utf-8')
        return {
            'status': 'ok',
            'res': response.read().decode('utf-8'),
        }

