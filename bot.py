import slack
import os
import locale
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter


# initial settings
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
locale.setlocale(locale.LC_TIME, '')
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
xlsx_file = 'Dailys_ Equipo TI Reservo_20220720.xlsx'
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)
BOT_ID = client.api_call('auth.test')['user_id']

today = datetime.now()
today_str = today.isoformat().split('T')[0]
df_dailies = pd.read_excel(xlsx_file, sheet_name='Table 2')
# pa probar usar un dia que tenga daily
# today = today + timedelta(days=3)
# today_str = today.isoformat().split('T')[0]

@slack_events_adapter.on('message')
def message(payload):
    # print(payload)
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id, text=text)

@app.route('/daily', methods=['POST'])
def daily():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')

    members = client.api_call('users.list').get('members')
    for member in members:
        print(member['name'], member['team_id'])

    list_lider_daily = df_dailies[df_dailies['Día'] == today_str].index.values
    if len(list_lider_daily):
        lider_daily = df_dailies.loc[list_lider_daily[0], 'Responsable']
        # print(lider_daily)
        # print(today.strftime('%d/%m/%Y'))
        if lider_daily != 'FERIADO':
            msg = f"Hoy lidera {lider_daily} ({today.strftime('%A %d')})"
            client.chat_postMessage(channel='#test', text=msg)
        # TODO: 3 casos segun hora: 
    return Response(), 200
    

if __name__ == '__main__':
    app.run(debug=True)





