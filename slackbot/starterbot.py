from __future__ import with_statement
from concurrent.futures import thread
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import string
from datetime import datetime, timedelta
import re

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)


slack_client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
BOT_ID = slack_client.api_call("auth.test")['user_id']

message_counts = {}
welcome_messages = {}

BAD_WORDS = ['hmm', 'no', 'tim']


SCHEDULED_MESSAGES = [
    {'text': 'First message 2 ', 'post_at': str((
        datetime.now() + timedelta(seconds=60)).timestamp()), 'channel': 'C03061D0C81'},
    {'text': 'Second Message! 2', 'post_at': str((
        datetime.now() + timedelta(seconds=70)).timestamp()), 'channel': 'C03061D0C81'}
]


class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                '돌팔이 채널에 오신 여러분들을 진심으로 환영합니다! \n\n'
                '--- < *지금 함께 하는 사람들* >---\n'
                '- *coolseaweed: 김은식 (바드 였던 사람)*\n'
                '- *cpark: 박창현 (템렙 1445)*\n'
                '- *charge: 차지훈 (로아 고인물)*\n'
                '- *hong: 최재홍 (칼바람 고인물)*\n'
                '- *du9172: 정동욱 (코딩배워서 들어올사람)*\n'
            )
        }
    }

    DIVIDER = {'type': 'divider'}

    def __init__(self, channel):
        self.channel = channel
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False

    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'Welcome Robot!',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':heart:'
        if not self.completed:
            checkmark = ':white_heart:'

        text = f'{checkmark} *React to this message!*'

        return {'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}


def send_welcome_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    if user in welcome_messages[channel]:
        return

    welcome = WelcomeMessage(channel)
    message = welcome.get_message()
    response = slack_client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    welcome_messages[channel][user] = welcome


def schedule_messages(messages):
    ids = []
    for msg in messages:
        post_at = re.sub('\.\d+', '', msg['post_at'])
        response = slack_client.chat_scheduleMessage(
            channel=msg['channel'], text=msg['text'], post_at=post_at).data

        id_ = response.get('scheduled_message_id')
        ids.append(id_)

    print(ids)
    return ids


def delete_scheduled_messages(ids, channel):
    for _id in ids:
        try:
            slack_client.chat_deleteScheduledMessage(
                channel=channel, scheduled_message_id=_id)
        except Exception as e:
            print(e)


def list_scheduled_messages(channel):
    response = slack_client.chat_scheduledMessages_list(channel=channel)
    messages = response.data.get('scheduled_messages')
    ids = []
    for msg in messages:
        ids.append(msg.get('id'))

    return ids


def check_if_bad_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    return any(word in msg for word in BAD_WORDS)


@slack_event_adapter.on('message')
def message(payload):

    print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if user_id != None and BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1

        if text.lower() == ';welcome':
            send_welcome_message(f'@{user_id}', user_id)
            # slack_client.chat_postMessage(channel=channel_id, text=text)
        elif check_if_bad_words(text):
            ts = event.get('ts')
            slack_client.chat_postMessage(
                channel=channel_id, thread_ts=ts, text="THAT IS BAD WORD! :(")

        if text.lower() == ';uk':
            slack_client.chat_postMessage(channel=channel_id, text='동욱이 바보')

        if text.lower() == ';img':
            response = slack_client.files_upload(
                channels=channel_id,
                file='./test.png',
                title='image upload test'
            )
            # print(f"[DEBUG] [CMD: '{text.lower()}'] response: {response}")
            # print(
            #     f"[DEBUG] [CMD: '{text.lower()}'] response['file'] : {response['file']}")
            # print(
            #     f"[DEBUG] [CMD: '{text.lower()}'] response['file']['groups']] : {response['file']['groups']}")

            # channel_id = response['file']['groups'][0]
            # ts = response['file']['shares']['private'][channel_id][0]['ts']
            # response = slack_client.chat_update(
            #     channel=channel_id,
            #     text="My Message",
            #     ts=ts,
            #     # blocks=blocks_list
            # )


@slack_event_adapter.on('reaction_added')
def reaction(payload):
    event = payload.get('event', {})
    channel_id = event.get('item', {}).get('channel')
    user_id = event.get('user')

    if f'@{user_id}' not in welcome_messages:
        return

    welcome = welcome_messages[f'@{user_id}'][user_id]
    welcome.completed = True
    welcome.channel = channel_id
    message = welcome.get_message()
    updated_message = slack_client.chat_update(**message)
    welcome.timestemp = updated_message['ts']


@app.route('/message-count', methods=['POST'])
def message_count():

    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = message_counts.get(user_id, 0)

    slack_client.chat_postMessage(
        channel=channel_id, text=f'Message: {message_count}')
    return Response(), 200


if __name__ == "__main__":

    # schedule_messages(SCHEDULED_MESSAGES)
    # ids = list_scheduled_messages('C03061D0C81')
    # delete_scheduled_messages(ids, 'C03061D0C81')

    app.run(debug=True, host="0.0.0.0", port=9000,)
    # app.run(threaded=True, host='0.0.0.0', port=9000)
