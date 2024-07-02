# Sytem level imports
import asyncio
import sys
import os
import io

from llm_analyst.core.config import Config, DataSource
from llm_analyst.core.research_analyst import LLMAnalyst
from llm_analyst.core.research_editor import LLMEditor
from llm_analyst.core.research_publisher import LLMPublisher


def process_research_request(
    client, user_id, channel_id, level_of_analysis, research_topic
):
    asyncio.run(
        async_process_research_request(
            client, user_id, channel_id, level_of_analysis, research_topic
        )
    )


async def async_process_research_request(
    client, user_id, channel_id, level_of_analysis, research_topic
):
    try:
        if level_of_analysis == "detailed-research":
            plublished_research_path = await detailed_internet_research(research_topic)
        else:
            plublished_research_path = await basic_internet_research(research_topic)
        file_name = os.path.basename(plublished_research_path)
        plublished_research_stream = None
        with open(plublished_research_path, "rb") as file:
            plublished_research_stream = io.BytesIO(file.read())

        if plublished_research_stream:
            response = client.files_upload_v2(
                channel=channel_id,
                file=plublished_research_stream,
                filename=file_name,
                title="Research Results",
            )
            if response["ok"]:
                result_status = "Your Research has been completed and uploaded."
            else:
                result_status = "Your Research has been completed unfortunately there was a problem uploading."

            # Notify the user and the channel
            client.chat_postMessage(
                channel=channel_id, text=f"Hello <@{user_id}>, {result_status}"
            )
    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"Hello <@{user_id}>, there was an error completing the process. Please try again later.",
        )


async def basic_internet_research(research_topic):
    llm_analyst = LLMAnalyst(active_research_topic=research_topic)

    await llm_analyst.conduct_research()
    research_state = await llm_analyst.write_report()

    # Once the report is written we can ask the LLMPublisher to make a pdf
    llm_publisher = LLMPublisher(**research_state.dump())
    plublished_research_path = await llm_publisher.publish_to_pdf_file()
    return plublished_research_path


async def detailed_internet_research(research_topic):
    llm_editor = LLMEditor(active_research_topic=research_topic)

    research_state = await llm_editor.create_detailed_report()

    llm_publisher = LLMPublisher(**research_state.dump())
    plublished_research_path = await llm_publisher.publish_to_pdf_file()

    return plublished_research_path
