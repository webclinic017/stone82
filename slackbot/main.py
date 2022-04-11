import slack
import os

KEY = os.environ.get('SLACK_BOT_TOKEN')

assert KEY != None, f"There are no 'SLACK_BOT_TOKEN' run '. .env' first"

client = slack.WebClient(token=KEY)

markdown_text = '''
This message is plain.
*This message is bold.*
`This message is code.`
_This message is italic._
~This message is strike.~
'''

attach_dict = {
    'color': '#ff0000',
    'author_name': '돌팔이',
    "author_link": 'github.com/coolseaweed',
    'title': '오늘의 증시 KOSPI',
    'title_link': 'http://finance.naver.com/sise/sise_index.nhn?code=KOSPI',
    'text': '2,326.13 △11.89 (+0.51%)',
    'image_url': 'ssl.pstatic.net/imgstock/chart3/day/KOSPI.png'
}

attach_list = [attach_dict]
# client.chat_postMessage(channel="#general", text=markdown_text, attachments=attach_list)

client.chat_postMessage(channel="#general", text='슬랙봇 테스트중')
