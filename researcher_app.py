import os
import io
import json
import uuid
import time
import threading
import asyncio
import random
from flask import Flask, request, jsonify
from slack_bolt import App as BoltApp
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk.web import WebClient
from pathlib import Path
from dotenv import load_dotenv
import logging

from research_dialog import research_dialog, getting_started_responses
from llm_research_wrapper import basic_internet_research, detailed_internet_research

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

research_tracker = {}

signing_secret=os.environ['SLACK_SIGNING_SECRET']
slack_bot_token = os.environ.get("SLACK_BOT_TOKEN")

bolt_app = BoltApp(signing_secret=signing_secret, token=slack_bot_token)

flask_app = Flask(__name__)

handler = SlackRequestHandler(bolt_app)
client = WebClient(token=slack_bot_token)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@bolt_app.message("research")
def research_request(message, say):
    # Set a uuid for the submit button
    unique_id = str(uuid.uuid4())
    research_dialog['blocks'][6]['elements'][0]['value']=unique_id
    # Inject of the users name in the dialog response 
    position = 15
    intro = research_dialog['blocks'][1]['text']['text']
    intro = intro[:position] + f"<@{message['user']}>" + intro[position:]
    research_dialog['blocks'][1]['text']['text'] = intro

    say(research_dialog)

@bolt_app.action("submit-research")
def handle_submit_research_action(ack, action, body, client):
    research_topic, level_of_analysis = get_research_dialog_state(body['state'])
    action_value=action['value'] # UUID for this request
    action_ts=action['action_ts'] # Timestamp for this request
    channel_id=body['channel']['id']
    user_id=body['user']['id']
             
    getting_started_response = random.choice(getting_started_responses)
    level_of_analysis = "Basic Research" if level_of_analysis=='basic-research' else "Detailed Research"
    response_text = getting_started_response.format(user_id=user_id, level_of_analysis=level_of_analysis)
    client.chat_postMessage(channel=channel_id,text=response_text)
    threading.Thread(target=process_research_request, args=(user_id, channel_id, level_of_analysis, research_topic)).start()
    ack()


def get_research_dialog_state(dialog_state):
    """From the dialog_state pull the research topic and level of analysis"""
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

    

def process_research_request(user_id, channel_id, level_of_analysis, research_topic):
    asyncio.run(async_process_research_request(user_id, channel_id, level_of_analysis, research_topic))
    
async def async_process_research_request(user_id, channel_id, level_of_analysis, research_topic):
    try:
        if level_of_analysis =='detailed-research':
            plublished_research_path = await detailed_internet_research(research_topic)
        else:
            plublished_research_path = await basic_internet_research(research_topic)
        file_name = os.path.basename(plublished_research_path)
        plublished_research_stream = None
        with open(plublished_research_path, 'rb') as file:
            plublished_research_stream = io.BytesIO(file.read())
            
        if plublished_research_stream:
            response = client.files_upload_v2(
                channel=channel_id,
                file=plublished_research_stream,
                filename=file_name,
                title="Research Results"
            )
            if response["ok"]:
                result_status = "Your Research has been completed and uploaded."
            else:
                result_status = "Your Research has been completed unfortunately there was a problem uploading."

            # Notify the user and the channel
            client.chat_postMessage(
                channel=channel_id,
                text=f"Hello <@{user_id}>, {result_status}"
            )
    except Exception as e:
        logger.error(f"Error in background process: {e}")
        client.chat_postMessage(
            channel=channel_id,
            text=f"Hello <@{user_id}>, there was an error completing the process. Please try again later."
        )
        
@flask_app.route("/upload", methods=["POST"])
def upload_file():
    try:
        file = request.files['file']
        channel = request.form.get('channel')  
        
        file_stream = io.BytesIO(file.read())
        
        response = client.files_upload_v2(
            channel=channel,
            file=file_stream,
            filename=file.filename,
            title="Uploaded via Flask app"
        )
        if response["ok"]:
            return jsonify({"status": "success", "file": response["file"]}), 200
        else:
            return jsonify({"status": "error", "error": response["error"]}), 400
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)
    #bolt_app.start(port=5000)