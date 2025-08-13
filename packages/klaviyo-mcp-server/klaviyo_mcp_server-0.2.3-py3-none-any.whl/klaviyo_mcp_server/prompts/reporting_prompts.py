from klaviyo_mcp_server.server import mcp
from pydantic import Field
from fastmcp.prompts.prompt import PromptMessage, TextContent
from typing import Annotated


@mcp.prompt
def analyze_campaign_or_flow_anomalies(
    report_type: Annotated[
        str,
        Field(description="Report types include: [campaign, flow]"),
    ],
    timeframe: Annotated[str, Field(description="The timeframe to analyze")],
    refine_prompt: Annotated[
        str,
        Field(
            description="Ask for specific channels, tags, or other details for analysis"
        ),
    ] = "",
) -> PromptMessage:
    """Prompt for analyzing spikes, dips, and other anomalies in campaign or flow performance data."""

    return PromptMessage(
        role="user",
        content=TextContent(
            type="text",
            text=f"""
    You are a marketing analytics expert analyzing Klaviyo {report_type} performance data.

    Analyze {report_type} data over the timeframe: {timeframe}.

    IMPORTANT EXTRA DETAILS:
    {refine_prompt}
    --------------------------------

    # Important Details
    - ALWAYS use {report_type} names in final output; IDs only for internal tool calls
    - Prioritize actionable insights over descriptive statistics
    - Include the timeframe in the request always, prioritize using preset timeframes over custom timeframes if possible.
    - Use emojis in headers to make the output more engaging

    # Tool calls
    - Start with get_metrics to identify available KPIs for the timeframe
    - Use get_campaign_report for campaign performance data, get_flow_report for flow performance data
        - Apply channel filters (email/SMS) only when user specifies channel preference

    # Analysis Structure
    ## 1. Performance Overview
    - Lead with delivery rate, open rate, click rate, conversion rate as baseline
    - Flag {report_type}s with >15 percent deviation from report average in any core metric
    - Identify top 3 performers and bottom 3 performers with specific percentage differences

    ## 2. Event Analysis
    - To identify spikes and dips, focus on >25 percent day-over-day changes in key metrics
    - Correlate spikes/dips with: send time, subject lines, audience segments, external factors
    - If there are no spikes or dips, say so.

    ## 3. Conclusion
    - Rank findings by revenue impact potential
    - Provide 2-3 immediately actionable recommendations with expected impact ranges
    - If there are no spikes or dips, say so.
    """,
        ),
    )
