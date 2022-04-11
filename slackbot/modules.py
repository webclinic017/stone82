import re


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
        self.client =
        self.welcome_messages = {}

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

    def send_welcome_message(self, channel, user):
        if channel not in self.welcome_messages:
            self.welcome_messages[channel] = {}

        if user in self.welcome_messages[channel]:
            return

        welcome = WelcomeMessage(channel)
        message = welcome.get_message()
        response = client.chat_postMessage(**message)
        welcome.timestamp = response['ts']

        self.welcome_messages[channel][user] = welcome

    def schedule_messages(messages):
        ids = []
        for msg in messages:
            post_at = re.sub('\.\d+', '', msg['post_at'])
            response = client.chat_scheduleMessage(
                channel=msg['channel'], text=msg['text'], post_at=post_at).data

            id_ = response.get('scheduled_message_id')
            ids.append(id_)

        print(ids)
        return ids
