from typing import List, Callable
from types import SimpleNamespace
from collections import defaultdict
from functools import partial
from datetime import datetime

from klaviyo_mcp_server.utils.utils import (
    get_klaviyo_client,
    get_filter_string,
    clean_result,
)


FLOW_FIELDS = ["name", "status", "trigger_type"]
# KEEP SEND TIME AND AUDIENCES
CAMPAIGN_FIELDS = ["name", "status", "audiences", "send_time"]


def get_id_to_tag_name(included: dict) -> dict:
    """
    Get a relationship dict, return a dict of id to tag name
    """
    tag_names = {
        item["id"]: item["attributes"]["name"]
        for item in included
        if item["type"] == "tag" and "name" in item["attributes"]
    }

    return tag_names


class AudienceDetails:
    """
    Class to get the name of an audience from an audience ID.
    """

    def __init__(self):
        self.audience_id_to_details = defaultdict(type(None))
        self.client = get_klaviyo_client()

    def get_audience_details(self, audience_id: str) -> dict:
        """
        Returns a dict with the name and type of the audience.

        Args:
            audience_id: The ID of the audience to get the name of

        Returns:
            {id: {name: str, type: str}}
        """

        if audience_id not in self.audience_id_to_details:
            # Try to get the name of the list or segment
            self.audience_id_to_details[audience_id] = {
                "name": self._get_list_name(audience_id),
                "type": "list",
            }
            if self.audience_id_to_details[audience_id]["name"] is None:
                self.audience_id_to_details[audience_id] = {
                    "name": self._get_segment_name(audience_id),
                    "type": "segment",
                }

            # If we still don't have a name, set the output to None
            if self.audience_id_to_details[audience_id]["name"] is None:
                self.audience_id_to_details[audience_id] = None

        # None if no name found
        return self.audience_id_to_details[audience_id]

    def _get_list_name(self, list_id: str) -> str:
        try:
            response = self.client.Lists.get_list(list_id, fields_list=["name"])
            return response["data"]["attributes"]["name"]
        except Exception:
            return None

    def _get_segment_name(self, segment_id: str) -> str:
        try:
            response = self.client.Segments.get_segment(
                segment_id, fields_segment=["name"]
            )
            return response["data"]["attributes"]["name"]
        except Exception:
            return None


def batch_request(
    ids: List[str], request: Callable, extra_filters: list[SimpleNamespace] = None
):
    """
    Given a list of IDs, returns a dictionary that maps IDs to data, using the given function to request data for a batch of IDs.
    Processes in batches of 50 IDs sequentially.

    Args:
        ids: List of IDs to get details for
        request: Callable function that takes a filter parameter and returns the API response.
                Should be a partial of a Klaviyo API method with all other parameters pre-filled.
        extra_filters: List of SimpleNamespace objects that represent extra filters to apply to the request.

    Returns:
        {id: campaign or flow object}
    """
    if not extra_filters:
        extra_filters = []

    items = defaultdict(type(None))
    batch_size = 50

    # Process batches of 50 unique IDs sequentially
    unique_ids = list(set(ids))
    for i in range(0, len(unique_ids), batch_size):
        batch_ids = unique_ids[i : i + batch_size]

        # Create filter with format: any(id,['id1','id2','id3'])
        batch_id_filter = SimpleNamespace(
            field="id",
            operator="any",
            value=batch_ids,
        )
        # Make request with filter and extra filters
        batch_response = request(
            filter=get_filter_string([batch_id_filter] + extra_filters)
        )

        # Get id to tag name
        id_to_tag_name = get_id_to_tag_name(batch_response["included"])

        if batch_response.get("data", None):
            # Add results to items dict
            for item in batch_response["data"]:
                item["attributes"]["tags"] = []
                # Assign tag names to item
                for tag in item["relationships"]["tags"]["data"]:
                    item["attributes"]["tags"].append(id_to_tag_name[tag["id"]])

                # Remove relationships and links
                clean_result(item)
                items[item["id"]] = item

    # Return results in the same order as input IDs
    return items


def get_flow_details(flow_ids: List[str]):
    """
    Use the get_flows endpoint to get flow details from a list of flow_ids.
    Processes batches of 50 IDs sequentially.

    Args:
        flow_ids: List of flow IDs to get details for

    Returns:
        {id: flow object}
    """
    client = get_klaviyo_client()

    flow_request = partial(
        client.Flows.get_flows,
        include=["tags"],
        fields_flow=FLOW_FIELDS,
        fields_tag=["name"],
    )

    return batch_request(flow_ids, flow_request)


def get_campaign_details(channel_to_campaign_ids: dict[str, List[str]]):
    """
    Use the get_campaigns endpoint to get campaign details from a list of campaign_ids.
    Processes batches of 50 IDs sequentially.

    Args:
        channel_to_campaign_ids: dict of channel to list of campaign IDs to get details for

    Returns:
        {id: campaign object}
    """
    client = get_klaviyo_client()

    results = defaultdict(type(None))
    audience_id_to_details = AudienceDetails()
    for channel, ids in channel_to_campaign_ids.items():
        channel_filter = SimpleNamespace(
            field="messages.channel", operator="equals", value=channel
        )

        campaign_request = partial(
            client.Campaigns.get_campaigns,
            include=["tags"],
            fields_campaign=CAMPAIGN_FIELDS,
            fields_tag=["name"],
        )

        batch_results = batch_request(
            ids, campaign_request, extra_filters=[channel_filter]
        )

        # Add audience details and send time formatting to returned campaigns
        for campaign in batch_results.values():
            # Change send_time to year, month, day, hour, minute
            if campaign["attributes"].get("send_time", None):
                send_time = datetime.fromisoformat(campaign["attributes"]["send_time"])
                campaign["attributes"]["send_time"] = send_time.strftime(
                    "%Y %d %B %H:%M"
                )

            # Add audience details to item if it exists
            if campaign.get("attributes", {}).get("audiences", {}):
                # Add audience details to included audiences
                campaign["attributes"]["audiences"]["included"] = [
                    audience_id_to_details.get_audience_details(audience_id)
                    for audience_id in campaign["attributes"]["audiences"]["included"]
                ]

                # Add audience details to excluded audiences
                campaign["attributes"]["audiences"]["excluded"] = [
                    audience_id_to_details.get_audience_details(audience_id)
                    for audience_id in campaign["attributes"]["audiences"]["excluded"]
                ]

        results.update(batch_results)

    return results
