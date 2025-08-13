"""Constants for the API.

Authors:
    Ryan Ignatius Hadiwijaya (ryan.i.hadiwijaya@gdplabs.id)

References:
    None
"""

from enum import StrEnum


class SearchType(StrEnum):
    """The type of search to perform.

    Attributes:
        NORMAL: Get answer from chatbot knowledge.
        WEB: Get more relevant information from the web.
            Web Search uses real-time data. Agent selection isn't available in this mode.
        DEEP_RESEARCH: Get answer from Deep Research Agent.
    """

    NORMAL = "normal"
    WEB = "web"
    DEEP_RESEARCH = "deep_research"
