# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["ClientCreateTokenParams", "ConnectOptions"]


class ClientCreateTokenParams(TypedDict, total=False):
    connect_options: ConnectOptions

    validity_in_seconds: float
    """
    How long the publishable token and magic link url will be valid for (in seconds)
    before it expires. By default it will be valid for 30 days unless otherwise
    specified.
    """


class ConnectOptions(TypedDict, total=False):
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
    """The names of the connectors to show in the connect page.

    If not provided, all connectors will be shown
    """

    debug: bool
    """Whether to enable debug mode"""

    is_embedded: bool
    """Whether to enable embedded mode.

    Embedded mode hides the side bar with extra context for the end user (customer)
    on the organization
    """

    return_url: str
    """
    Optional URL to return customers after adding a connection or if they press the
    Return To Organization button
    """

    view: Literal["add", "manage"]
    """The default view to show when the magic link is opened.

    If omitted, by default it will smartly load the right view based on whether the
    user has connections or not
    """
