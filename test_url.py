import requests
import slack
import yaml
from slackbot import slackbot

# test 1
url = 'https://files.slack.com/files-pri/T01LLQL4QQL-F030TUKAX1R/download/test.yaml'
token = 'xoxb-1700836160836-1858504494976-s8tJUt2oFGmi64yhT8JkASSH'
test = requests.get(url, headers={'Authorization': f'Bearer {token}'})
yaml_data = yaml.load(test.text, Loader=yaml.FullLoader)

# test 2
with open('test.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


result = slackbot.run_command(config)
