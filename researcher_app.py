import os
import json
from slack_bolt import App
from slack_sdk.web import WebClient
from pathlib import Path
from dotenv import load_dotenv
import logging
from research_dialog import research_dialog
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import uuid

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

research_tracker = {}

signing_secret=os.environ['SLACK_SIGNING_SECRET']
slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")

app = App(
          signing_secret=signing_secret,
          token=slack_bot_token
          )

@app.message("")
def handle_message(event, say):
    say(f"Received your message: {event['text']}")


@app.message("research")
def research_request(message, say):
    logger.debug("="*40)
    logger.debug(f"{message=}")
    logger.debug("="*40)
    # Set a uuid for the submit button
    unique_id = str(uuid.uuid4())
    research_dialog['blocks'][6]['elements'][0]['value']=unique_id

    say(
        research_dialog
    )

def get_research_dialog_state(dialog_state):
    research_topic = ""
    level_of_analysis = ""
    dialog_state_values = dialog_state['values']
    for key in dialog_state_values:
        if "research_topic-action" in dialog_state_values[key]:
            research_topic_value = dialog_state_values[key]["research_topic-action"]["value"]
            if research_topic_value:
                research_topic = research_topic_value
        elif "level_of_analysis-action" in dialog_state_values[key]:
            selected_option = dialog_state_values[key]["level_of_analysis-action"]["selected_option"]
            if selected_option:
                level_of_analysis = selected_option["value"]
    return research_topic, level_of_analysis

    
@app.action("submit-research")
def handle_some_action(ack, action, body, client):
    logger.debug("body="*40)
    logger.info(body)
    logger.debug("action="*40)
    logger.info(action)
    logger.debug("="*40)
    
    research_topic, level_of_analysis = get_research_dialog_state(body['state'])
    reply = {'research_topic':research_topic, 
             'level_of_analysis':level_of_analysis,
             'action_value':action['value'],
             'action_ts':action['action_ts']}
    dict_as_string = json.dumps(reply, indent=4)
    client.chat_postMessage(channel='C077K7EFWUE',text=f"{dict_as_string}")
    ack()

    

if __name__ == "__main__":
    
    app.start(port=3000)