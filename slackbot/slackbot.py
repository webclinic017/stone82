import re
import slack
import logging
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import requests

from analyzer.analyzer import Analyzer
from DB.korDB_manager import KoreaDB_manager
from DB.database import DataBase
from utils.visualizer import Visualizer
import yaml
import os


SIGNING_SECRET = os.environ['SIGNING_SECRET']
SLACK_TOKEN = os.environ['SLACK_TOKEN']


app = Flask(__name__)
event_adapter = SlackEventAdapter(
    SIGNING_SECRET, '/slack/events', app)
client = slack.WebClient(token=SLACK_TOKEN)
BOT_ID = client.api_call("auth.test")['user_id']
logger = logging.getLogger(__name__)

# extra modules
visualizer = Visualizer()
manager = KoreaDB_manager(
    host=os.environ.get('MYSQL_HOST'),
    db_name='KOR_DB',
    pwd=os.environ.get('MYSQL_ROOT_PASSWORD'),
    user=os.environ.get('MYSQL_USER'),
)
db = DataBase(
    host=os.environ.get('MYSQL_HOST'),
    db_name='KOR_DB',
    pwd=os.environ.get('MYSQL_ROOT_PASSWORD'),
    user=os.environ.get('MYSQL_USER'),
)


# global variables
message_counts = {}
welcome_messages = {}


def run(mode="debug", host="0.0.0.0", port=9000):

    if mode == "debug":
        app.run(debug=True, host=host, port=port)

    elif mode == "prod":
        app.run(threaded=True, host=host, port=port)

# ------------------------------


def draw_candle_chart(company, cfg, start, end, img_base):
    target_dir = os.path.join(img_base, company)
    os.makedirs(target_dir, exist_ok=True)

    data = db.getDailyPrice(
        company, start_date=start, end_date=end)
    visualizer.drawCandleStick(
        data,
        ma_list=cfg['moving_average'],
        title=f"{company} candle chart",
    )
    visualizer.save(target_dir+'/candle.png')
    visualizer.clear()

    return target_dir+'/candle.png'


def run_command(cfg, img_base="imgs"):
    title = cfg['TITLE']
    start, end = cfg['PERIOD'].split("~")
    company_list = cfg['company_list']

    results = []

    for company in company_list:
        try:
            if "candle" in cfg:
                result = draw_candle_chart(
                    company, cfg['candle'], start, end, img_base=img_base)
                results.append(result)

        except Exception as e:
            print(e)

    return results


@event_adapter.on('message')
def message(payload):

    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    files = event.get('files')

    if user_id != None and BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1

        if 'cmd;' in text.lower():

            # test scripts:
            # with open('./test.yaml', 'r') as f:
            #     config = yaml.load(f, Loader=yaml.FullLoader)

            if files != None:
                for file in files:
                    yaml_url = file['url_private_download']
                    content = requests.get(
                        yaml_url,
                        headers={'Authorization': f'Bearer {SLACK_TOKEN}'})
                    config = yaml.load(
                        content.text, Loader=yaml.FullLoader)
                    results = run_command(config)
                    for result in results:
                        response = client.files_upload(
                            channels=channel_id,
                            file=result,
                            title='image upload test'
                        )

            else:
                client.chat_postMessage(
                    channel=channel_id,
                    text="yaml 파일이 없습니다 :("
                )
