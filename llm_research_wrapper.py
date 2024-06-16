# Sytem level imports
import sys
import os
import json

from llm_analyst.core.config import Config, DataSource
from llm_analyst.core.research_analyst import LLMAnalyst
from llm_analyst.core.research_editor import LLMEditor
from llm_analyst.core.research_publisher import LLMPublisher

async def basic_internet_research(research_topic):
    llm_analyst = LLMAnalyst(active_research_topic = research_topic)

    await llm_analyst.conduct_research()
    research_state = await llm_analyst.write_report()
    
    # Once the report is written we can ask the LLMPublisher to make a pdf
    llm_publisher = LLMPublisher(**research_state.dump())
    plublished_research_path = await llm_publisher.publish_to_pdf_file()
    return plublished_research_path

async def detailed_internet_research(research_topic):
    llm_editor = LLMEditor(active_research_topic = research_topic)

    research_state = await llm_editor.create_detailed_report()

    llm_publisher = LLMPublisher(**research_state.dump())
    plublished_research_path = await llm_publisher.publish_to_pdf_file()
    
    return plublished_research_path