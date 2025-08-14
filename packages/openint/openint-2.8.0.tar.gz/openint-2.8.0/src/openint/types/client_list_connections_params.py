# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["ClientListConnectionsParams"]


class ClientListConnectionsParams(TypedDict, total=False):
    connector_config_id: str
    """The id of the connector config, starts with `ccfg_`"""

    connector_names: List[
        Literal[
            "accelo",
            "acme-apikey",
            "acme-oauth2",
            "adobe",
            "adyen",
            "aircall",
            "airtable",
            "amazon",
            "apaleo",
            "apollo",
            "asana",
            "attio",
            "auth0",
            "autodesk",
            "aws",
            "bamboohr",
            "basecamp",
            "battlenet",
            "bigcommerce",
            "bitbucket",
            "bitly",
            "blackbaud",
            "boldsign",
            "box",
            "braintree",
            "brex",
            "calendly",
            "clickup",
            "close",
            "coda",
            "confluence",
            "contentful",
            "contentstack",
            "copper",
            "coros",
            "datev",
            "deel",
            "dialpad",
            "digitalocean",
            "discord",
            "docusign",
            "dropbox",
            "ebay",
            "egnyte",
            "envoy",
            "eventbrite",
            "exist",
            "facebook",
            "factorial",
            "figma",
            "finch",
            "firebase",
            "fitbit",
            "foreceipt",
            "fortnox",
            "freshbooks",
            "front",
            "github",
            "gitlab",
            "gong",
            "google-calendar",
            "google-docs",
            "google-drive",
            "google-mail",
            "google-sheet",
            "gorgias",
            "grain",
            "greenhouse",
            "gumroad",
            "gusto",
            "harvest",
            "heron",
            "highlevel",
            "hubspot",
            "instagram",
            "intercom",
            "jira",
            "keap",
            "lever",
            "linear",
            "linkedin",
            "linkhut",
            "lunchmoney",
            "mailchimp",
            "mercury",
            "merge",
            "miro",
            "monday",
            "moota",
            "mural",
            "namely",
            "nationbuilder",
            "netsuite",
            "notion",
            "odoo",
            "okta",
            "onebrick",
            "openledger",
            "osu",
            "oura",
            "outreach",
            "pagerduty",
            "pandadoc",
            "payfit",
            "paypal",
            "pennylane",
            "pinterest",
            "pipedrive",
            "plaid",
            "podium",
            "postgres",
            "productboard",
            "qualtrics",
            "quickbooks",
            "ramp",
            "reddit",
            "sage",
            "salesforce",
            "salesloft",
            "saltedge",
            "segment",
            "servicem8",
            "servicenow",
            "sharepoint",
            "sharepoint-onprem",
            "shopify",
            "signnow",
            "slack",
            "smartsheet",
            "snowflake",
            "splitwise",
            "spotify",
            "squarespace",
            "squareup",
            "stackexchange",
            "strava",
            "stripe",
            "teamwork",
            "teller",
            "ticktick",
            "timely",
            "todoist",
            "toggl",
            "tremendous",
            "tsheetsteam",
            "tumblr",
            "twenty",
            "twinfield",
            "twitch",
            "twitter",
            "typeform",
            "uber",
            "venmo",
            "vimeo",
            "wakatime",
            "wealthbox",
            "webflow",
            "whoop",
            "wise",
            "wordpress",
            "wrike",
            "xero",
            "yahoo",
            "yandex",
            "yodlee",
            "zapier",
            "zendesk",
            "zenefits",
            "zoho",
            "zoho-desk",
            "zoom",
        ]
    ]

    customer_id: str
    """The id of the customer in your application.

    Ensure it is unique for that customer.
    """

    expand: List[Literal["connector"]]
    """Expand the response with additional optionals"""

    include_secrets: bool

    limit: int
    """Limit the number of items returned"""

    offset: int
    """Offset the items returned"""

    refresh_policy: Literal["none", "force", "auto"]
    """
    Controls credential refresh: none (never), force (always), or auto (when
    expired, default)
    """

    search_query: str
