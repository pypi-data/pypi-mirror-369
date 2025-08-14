# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "CreateConnnectorConfigResponse",
    "ConnectorAcceloDiscriminatedConnectorConfig",
    "ConnectorAcceloDiscriminatedConnectorConfigConfig",
    "ConnectorAcceloDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAcmeApikeyDiscriminatedConnectorConfig",
    "ConnectorAcmeOauth2DiscriminatedConnectorConfig",
    "ConnectorAcmeOauth2DiscriminatedConnectorConfigConfig",
    "ConnectorAcmeOauth2DiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAdobeDiscriminatedConnectorConfig",
    "ConnectorAdobeDiscriminatedConnectorConfigConfig",
    "ConnectorAdobeDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAdyenDiscriminatedConnectorConfig",
    "ConnectorAdyenDiscriminatedConnectorConfigConfig",
    "ConnectorAdyenDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAircallDiscriminatedConnectorConfig",
    "ConnectorAircallDiscriminatedConnectorConfigConfig",
    "ConnectorAircallDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAmazonDiscriminatedConnectorConfig",
    "ConnectorAmazonDiscriminatedConnectorConfigConfig",
    "ConnectorAmazonDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorApaleoDiscriminatedConnectorConfig",
    "ConnectorApaleoDiscriminatedConnectorConfigConfig",
    "ConnectorApaleoDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAsanaDiscriminatedConnectorConfig",
    "ConnectorAsanaDiscriminatedConnectorConfigConfig",
    "ConnectorAsanaDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAttioDiscriminatedConnectorConfig",
    "ConnectorAttioDiscriminatedConnectorConfigConfig",
    "ConnectorAttioDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAuth0DiscriminatedConnectorConfig",
    "ConnectorAuth0DiscriminatedConnectorConfigConfig",
    "ConnectorAuth0DiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAutodeskDiscriminatedConnectorConfig",
    "ConnectorAutodeskDiscriminatedConnectorConfigConfig",
    "ConnectorAutodeskDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAwsDiscriminatedConnectorConfig",
    "ConnectorAwsDiscriminatedConnectorConfigConfig",
    "ConnectorAwsDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBamboohrDiscriminatedConnectorConfig",
    "ConnectorBamboohrDiscriminatedConnectorConfigConfig",
    "ConnectorBamboohrDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBasecampDiscriminatedConnectorConfig",
    "ConnectorBasecampDiscriminatedConnectorConfigConfig",
    "ConnectorBasecampDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBattlenetDiscriminatedConnectorConfig",
    "ConnectorBattlenetDiscriminatedConnectorConfigConfig",
    "ConnectorBattlenetDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBigcommerceDiscriminatedConnectorConfig",
    "ConnectorBigcommerceDiscriminatedConnectorConfigConfig",
    "ConnectorBigcommerceDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBitbucketDiscriminatedConnectorConfig",
    "ConnectorBitbucketDiscriminatedConnectorConfigConfig",
    "ConnectorBitbucketDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBitlyDiscriminatedConnectorConfig",
    "ConnectorBitlyDiscriminatedConnectorConfigConfig",
    "ConnectorBitlyDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBlackbaudDiscriminatedConnectorConfig",
    "ConnectorBlackbaudDiscriminatedConnectorConfigConfig",
    "ConnectorBlackbaudDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBoldsignDiscriminatedConnectorConfig",
    "ConnectorBoldsignDiscriminatedConnectorConfigConfig",
    "ConnectorBoldsignDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBoxDiscriminatedConnectorConfig",
    "ConnectorBoxDiscriminatedConnectorConfigConfig",
    "ConnectorBoxDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorBraintreeDiscriminatedConnectorConfig",
    "ConnectorBraintreeDiscriminatedConnectorConfigConfig",
    "ConnectorBraintreeDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorCalendlyDiscriminatedConnectorConfig",
    "ConnectorCalendlyDiscriminatedConnectorConfigConfig",
    "ConnectorCalendlyDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorClickupDiscriminatedConnectorConfig",
    "ConnectorClickupDiscriminatedConnectorConfigConfig",
    "ConnectorClickupDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorCloseDiscriminatedConnectorConfig",
    "ConnectorCloseDiscriminatedConnectorConfigConfig",
    "ConnectorCloseDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorConfluenceDiscriminatedConnectorConfig",
    "ConnectorConfluenceDiscriminatedConnectorConfigConfig",
    "ConnectorConfluenceDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorContentfulDiscriminatedConnectorConfig",
    "ConnectorContentfulDiscriminatedConnectorConfigConfig",
    "ConnectorContentfulDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorContentstackDiscriminatedConnectorConfig",
    "ConnectorContentstackDiscriminatedConnectorConfigConfig",
    "ConnectorContentstackDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorCopperDiscriminatedConnectorConfig",
    "ConnectorCopperDiscriminatedConnectorConfigConfig",
    "ConnectorCopperDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorCorosDiscriminatedConnectorConfig",
    "ConnectorCorosDiscriminatedConnectorConfigConfig",
    "ConnectorCorosDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorDatevDiscriminatedConnectorConfig",
    "ConnectorDatevDiscriminatedConnectorConfigConfig",
    "ConnectorDatevDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorDeelDiscriminatedConnectorConfig",
    "ConnectorDeelDiscriminatedConnectorConfigConfig",
    "ConnectorDeelDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorDialpadDiscriminatedConnectorConfig",
    "ConnectorDialpadDiscriminatedConnectorConfigConfig",
    "ConnectorDialpadDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorDigitaloceanDiscriminatedConnectorConfig",
    "ConnectorDigitaloceanDiscriminatedConnectorConfigConfig",
    "ConnectorDigitaloceanDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorDiscordDiscriminatedConnectorConfig",
    "ConnectorDiscordDiscriminatedConnectorConfigConfig",
    "ConnectorDiscordDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorDocusignDiscriminatedConnectorConfig",
    "ConnectorDocusignDiscriminatedConnectorConfigConfig",
    "ConnectorDocusignDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorDropboxDiscriminatedConnectorConfig",
    "ConnectorDropboxDiscriminatedConnectorConfigConfig",
    "ConnectorDropboxDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorEbayDiscriminatedConnectorConfig",
    "ConnectorEbayDiscriminatedConnectorConfigConfig",
    "ConnectorEbayDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorEgnyteDiscriminatedConnectorConfig",
    "ConnectorEgnyteDiscriminatedConnectorConfigConfig",
    "ConnectorEgnyteDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorEnvoyDiscriminatedConnectorConfig",
    "ConnectorEnvoyDiscriminatedConnectorConfigConfig",
    "ConnectorEnvoyDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorEventbriteDiscriminatedConnectorConfig",
    "ConnectorEventbriteDiscriminatedConnectorConfigConfig",
    "ConnectorEventbriteDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorExistDiscriminatedConnectorConfig",
    "ConnectorExistDiscriminatedConnectorConfigConfig",
    "ConnectorExistDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorFacebookDiscriminatedConnectorConfig",
    "ConnectorFacebookDiscriminatedConnectorConfigConfig",
    "ConnectorFacebookDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorFactorialDiscriminatedConnectorConfig",
    "ConnectorFactorialDiscriminatedConnectorConfigConfig",
    "ConnectorFactorialDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorFigmaDiscriminatedConnectorConfig",
    "ConnectorFigmaDiscriminatedConnectorConfigConfig",
    "ConnectorFigmaDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorFitbitDiscriminatedConnectorConfig",
    "ConnectorFitbitDiscriminatedConnectorConfigConfig",
    "ConnectorFitbitDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorFortnoxDiscriminatedConnectorConfig",
    "ConnectorFortnoxDiscriminatedConnectorConfigConfig",
    "ConnectorFortnoxDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorFreshbooksDiscriminatedConnectorConfig",
    "ConnectorFreshbooksDiscriminatedConnectorConfigConfig",
    "ConnectorFreshbooksDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorFrontDiscriminatedConnectorConfig",
    "ConnectorFrontDiscriminatedConnectorConfigConfig",
    "ConnectorFrontDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGitHubDiscriminatedConnectorConfig",
    "ConnectorGitHubDiscriminatedConnectorConfigConfig",
    "ConnectorGitHubDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGitlabDiscriminatedConnectorConfig",
    "ConnectorGitlabDiscriminatedConnectorConfigConfig",
    "ConnectorGitlabDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGongDiscriminatedConnectorConfig",
    "ConnectorGongDiscriminatedConnectorConfigConfig",
    "ConnectorGongDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGoogleCalendarDiscriminatedConnectorConfig",
    "ConnectorGoogleCalendarDiscriminatedConnectorConfigConfig",
    "ConnectorGoogleCalendarDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGoogleDocsDiscriminatedConnectorConfig",
    "ConnectorGoogleDocsDiscriminatedConnectorConfigConfig",
    "ConnectorGoogleDocsDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGoogleDriveDiscriminatedConnectorConfig",
    "ConnectorGoogleDriveDiscriminatedConnectorConfigConfig",
    "ConnectorGoogleDriveDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGoogleMailDiscriminatedConnectorConfig",
    "ConnectorGoogleMailDiscriminatedConnectorConfigConfig",
    "ConnectorGoogleMailDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGoogleSheetDiscriminatedConnectorConfig",
    "ConnectorGoogleSheetDiscriminatedConnectorConfigConfig",
    "ConnectorGoogleSheetDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGorgiasDiscriminatedConnectorConfig",
    "ConnectorGorgiasDiscriminatedConnectorConfigConfig",
    "ConnectorGorgiasDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGrainDiscriminatedConnectorConfig",
    "ConnectorGrainDiscriminatedConnectorConfigConfig",
    "ConnectorGrainDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGumroadDiscriminatedConnectorConfig",
    "ConnectorGumroadDiscriminatedConnectorConfigConfig",
    "ConnectorGumroadDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorGustoDiscriminatedConnectorConfig",
    "ConnectorGustoDiscriminatedConnectorConfigConfig",
    "ConnectorGustoDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorHarvestDiscriminatedConnectorConfig",
    "ConnectorHarvestDiscriminatedConnectorConfigConfig",
    "ConnectorHarvestDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorHighlevelDiscriminatedConnectorConfig",
    "ConnectorHighlevelDiscriminatedConnectorConfigConfig",
    "ConnectorHighlevelDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorHubspotDiscriminatedConnectorConfig",
    "ConnectorHubspotDiscriminatedConnectorConfigConfig",
    "ConnectorHubspotDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorInstagramDiscriminatedConnectorConfig",
    "ConnectorInstagramDiscriminatedConnectorConfigConfig",
    "ConnectorInstagramDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorIntercomDiscriminatedConnectorConfig",
    "ConnectorIntercomDiscriminatedConnectorConfigConfig",
    "ConnectorIntercomDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorJiraDiscriminatedConnectorConfig",
    "ConnectorJiraDiscriminatedConnectorConfigConfig",
    "ConnectorJiraDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorKeapDiscriminatedConnectorConfig",
    "ConnectorKeapDiscriminatedConnectorConfigConfig",
    "ConnectorKeapDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorLeverDiscriminatedConnectorConfig",
    "ConnectorLeverDiscriminatedConnectorConfigConfig",
    "ConnectorLeverDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorLinearDiscriminatedConnectorConfig",
    "ConnectorLinearDiscriminatedConnectorConfigConfig",
    "ConnectorLinearDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorLinkedinDiscriminatedConnectorConfig",
    "ConnectorLinkedinDiscriminatedConnectorConfigConfig",
    "ConnectorLinkedinDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorLinkhutDiscriminatedConnectorConfig",
    "ConnectorLinkhutDiscriminatedConnectorConfigConfig",
    "ConnectorLinkhutDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorMailchimpDiscriminatedConnectorConfig",
    "ConnectorMailchimpDiscriminatedConnectorConfigConfig",
    "ConnectorMailchimpDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorMiroDiscriminatedConnectorConfig",
    "ConnectorMiroDiscriminatedConnectorConfigConfig",
    "ConnectorMiroDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorMondayDiscriminatedConnectorConfig",
    "ConnectorMondayDiscriminatedConnectorConfigConfig",
    "ConnectorMondayDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorMuralDiscriminatedConnectorConfig",
    "ConnectorMuralDiscriminatedConnectorConfigConfig",
    "ConnectorMuralDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorNamelyDiscriminatedConnectorConfig",
    "ConnectorNamelyDiscriminatedConnectorConfigConfig",
    "ConnectorNamelyDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorNationbuilderDiscriminatedConnectorConfig",
    "ConnectorNationbuilderDiscriminatedConnectorConfigConfig",
    "ConnectorNationbuilderDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorNetsuiteDiscriminatedConnectorConfig",
    "ConnectorNetsuiteDiscriminatedConnectorConfigConfig",
    "ConnectorNetsuiteDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorNotionDiscriminatedConnectorConfig",
    "ConnectorNotionDiscriminatedConnectorConfigConfig",
    "ConnectorNotionDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorOdooDiscriminatedConnectorConfig",
    "ConnectorOdooDiscriminatedConnectorConfigConfig",
    "ConnectorOdooDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorOktaDiscriminatedConnectorConfig",
    "ConnectorOktaDiscriminatedConnectorConfigConfig",
    "ConnectorOktaDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorOsuDiscriminatedConnectorConfig",
    "ConnectorOsuDiscriminatedConnectorConfigConfig",
    "ConnectorOsuDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorOuraDiscriminatedConnectorConfig",
    "ConnectorOuraDiscriminatedConnectorConfigConfig",
    "ConnectorOuraDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorOutreachDiscriminatedConnectorConfig",
    "ConnectorOutreachDiscriminatedConnectorConfigConfig",
    "ConnectorOutreachDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorPagerdutyDiscriminatedConnectorConfig",
    "ConnectorPagerdutyDiscriminatedConnectorConfigConfig",
    "ConnectorPagerdutyDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorPandadocDiscriminatedConnectorConfig",
    "ConnectorPandadocDiscriminatedConnectorConfigConfig",
    "ConnectorPandadocDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorPayfitDiscriminatedConnectorConfig",
    "ConnectorPayfitDiscriminatedConnectorConfigConfig",
    "ConnectorPayfitDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorPaypalDiscriminatedConnectorConfig",
    "ConnectorPaypalDiscriminatedConnectorConfigConfig",
    "ConnectorPaypalDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorPennylaneDiscriminatedConnectorConfig",
    "ConnectorPennylaneDiscriminatedConnectorConfigConfig",
    "ConnectorPennylaneDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorPinterestDiscriminatedConnectorConfig",
    "ConnectorPinterestDiscriminatedConnectorConfigConfig",
    "ConnectorPinterestDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorPipedriveDiscriminatedConnectorConfig",
    "ConnectorPipedriveDiscriminatedConnectorConfigConfig",
    "ConnectorPipedriveDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorPodiumDiscriminatedConnectorConfig",
    "ConnectorPodiumDiscriminatedConnectorConfigConfig",
    "ConnectorPodiumDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorProductboardDiscriminatedConnectorConfig",
    "ConnectorProductboardDiscriminatedConnectorConfigConfig",
    "ConnectorProductboardDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorQualtricsDiscriminatedConnectorConfig",
    "ConnectorQualtricsDiscriminatedConnectorConfigConfig",
    "ConnectorQualtricsDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorQuickbooksDiscriminatedConnectorConfig",
    "ConnectorQuickbooksDiscriminatedConnectorConfigConfig",
    "ConnectorQuickbooksDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorRedditDiscriminatedConnectorConfig",
    "ConnectorRedditDiscriminatedConnectorConfigConfig",
    "ConnectorRedditDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSageDiscriminatedConnectorConfig",
    "ConnectorSageDiscriminatedConnectorConfigConfig",
    "ConnectorSageDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSalesforceDiscriminatedConnectorConfig",
    "ConnectorSalesforceDiscriminatedConnectorConfigConfig",
    "ConnectorSalesforceDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSalesloftDiscriminatedConnectorConfig",
    "ConnectorSalesloftDiscriminatedConnectorConfigConfig",
    "ConnectorSalesloftDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSegmentDiscriminatedConnectorConfig",
    "ConnectorSegmentDiscriminatedConnectorConfigConfig",
    "ConnectorSegmentDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorServicem8DiscriminatedConnectorConfig",
    "ConnectorServicem8DiscriminatedConnectorConfigConfig",
    "ConnectorServicem8DiscriminatedConnectorConfigConfigOAuth",
    "ConnectorServicenowDiscriminatedConnectorConfig",
    "ConnectorServicenowDiscriminatedConnectorConfigConfig",
    "ConnectorServicenowDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSharepointDiscriminatedConnectorConfig",
    "ConnectorSharepointDiscriminatedConnectorConfigConfig",
    "ConnectorSharepointDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorShopifyDiscriminatedConnectorConfig",
    "ConnectorShopifyDiscriminatedConnectorConfigConfig",
    "ConnectorShopifyDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSignnowDiscriminatedConnectorConfig",
    "ConnectorSignnowDiscriminatedConnectorConfigConfig",
    "ConnectorSignnowDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSlackDiscriminatedConnectorConfig",
    "ConnectorSlackDiscriminatedConnectorConfigConfig",
    "ConnectorSlackDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSmartsheetDiscriminatedConnectorConfig",
    "ConnectorSmartsheetDiscriminatedConnectorConfigConfig",
    "ConnectorSmartsheetDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSnowflakeDiscriminatedConnectorConfig",
    "ConnectorSnowflakeDiscriminatedConnectorConfigConfig",
    "ConnectorSnowflakeDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSpotifyDiscriminatedConnectorConfig",
    "ConnectorSpotifyDiscriminatedConnectorConfigConfig",
    "ConnectorSpotifyDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSquarespaceDiscriminatedConnectorConfig",
    "ConnectorSquarespaceDiscriminatedConnectorConfigConfig",
    "ConnectorSquarespaceDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSquareupDiscriminatedConnectorConfig",
    "ConnectorSquareupDiscriminatedConnectorConfigConfig",
    "ConnectorSquareupDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorStackexchangeDiscriminatedConnectorConfig",
    "ConnectorStackexchangeDiscriminatedConnectorConfigConfig",
    "ConnectorStackexchangeDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorStravaDiscriminatedConnectorConfig",
    "ConnectorStravaDiscriminatedConnectorConfigConfig",
    "ConnectorStravaDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTeamworkDiscriminatedConnectorConfig",
    "ConnectorTeamworkDiscriminatedConnectorConfigConfig",
    "ConnectorTeamworkDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTicktickDiscriminatedConnectorConfig",
    "ConnectorTicktickDiscriminatedConnectorConfigConfig",
    "ConnectorTicktickDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTimelyDiscriminatedConnectorConfig",
    "ConnectorTimelyDiscriminatedConnectorConfigConfig",
    "ConnectorTimelyDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTodoistDiscriminatedConnectorConfig",
    "ConnectorTodoistDiscriminatedConnectorConfigConfig",
    "ConnectorTodoistDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTremendousDiscriminatedConnectorConfig",
    "ConnectorTremendousDiscriminatedConnectorConfigConfig",
    "ConnectorTremendousDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTsheetsteamDiscriminatedConnectorConfig",
    "ConnectorTsheetsteamDiscriminatedConnectorConfigConfig",
    "ConnectorTsheetsteamDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTumblrDiscriminatedConnectorConfig",
    "ConnectorTumblrDiscriminatedConnectorConfigConfig",
    "ConnectorTumblrDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTwinfieldDiscriminatedConnectorConfig",
    "ConnectorTwinfieldDiscriminatedConnectorConfigConfig",
    "ConnectorTwinfieldDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTwitchDiscriminatedConnectorConfig",
    "ConnectorTwitchDiscriminatedConnectorConfigConfig",
    "ConnectorTwitchDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTwitterDiscriminatedConnectorConfig",
    "ConnectorTwitterDiscriminatedConnectorConfigConfig",
    "ConnectorTwitterDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTypeformDiscriminatedConnectorConfig",
    "ConnectorTypeformDiscriminatedConnectorConfigConfig",
    "ConnectorTypeformDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorUberDiscriminatedConnectorConfig",
    "ConnectorUberDiscriminatedConnectorConfigConfig",
    "ConnectorUberDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorVimeoDiscriminatedConnectorConfig",
    "ConnectorVimeoDiscriminatedConnectorConfigConfig",
    "ConnectorVimeoDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorWakatimeDiscriminatedConnectorConfig",
    "ConnectorWakatimeDiscriminatedConnectorConfigConfig",
    "ConnectorWakatimeDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorWealthboxDiscriminatedConnectorConfig",
    "ConnectorWealthboxDiscriminatedConnectorConfigConfig",
    "ConnectorWealthboxDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorWebflowDiscriminatedConnectorConfig",
    "ConnectorWebflowDiscriminatedConnectorConfigConfig",
    "ConnectorWebflowDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorWhoopDiscriminatedConnectorConfig",
    "ConnectorWhoopDiscriminatedConnectorConfigConfig",
    "ConnectorWhoopDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorWordpressDiscriminatedConnectorConfig",
    "ConnectorWordpressDiscriminatedConnectorConfigConfig",
    "ConnectorWordpressDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorWrikeDiscriminatedConnectorConfig",
    "ConnectorWrikeDiscriminatedConnectorConfigConfig",
    "ConnectorWrikeDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorXeroDiscriminatedConnectorConfig",
    "ConnectorXeroDiscriminatedConnectorConfigConfig",
    "ConnectorXeroDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorYahooDiscriminatedConnectorConfig",
    "ConnectorYahooDiscriminatedConnectorConfigConfig",
    "ConnectorYahooDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorYandexDiscriminatedConnectorConfig",
    "ConnectorYandexDiscriminatedConnectorConfigConfig",
    "ConnectorYandexDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorZapierDiscriminatedConnectorConfig",
    "ConnectorZapierDiscriminatedConnectorConfigConfig",
    "ConnectorZapierDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorZendeskDiscriminatedConnectorConfig",
    "ConnectorZendeskDiscriminatedConnectorConfigConfig",
    "ConnectorZendeskDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorZenefitsDiscriminatedConnectorConfig",
    "ConnectorZenefitsDiscriminatedConnectorConfigConfig",
    "ConnectorZenefitsDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorZohoDeskDiscriminatedConnectorConfig",
    "ConnectorZohoDeskDiscriminatedConnectorConfigConfig",
    "ConnectorZohoDeskDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorZohoDiscriminatedConnectorConfig",
    "ConnectorZohoDiscriminatedConnectorConfigConfig",
    "ConnectorZohoDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorZoomDiscriminatedConnectorConfig",
    "ConnectorZoomDiscriminatedConnectorConfigConfig",
    "ConnectorZoomDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorAirtableDiscriminatedConnectorConfig",
    "ConnectorApolloDiscriminatedConnectorConfig",
    "ConnectorBrexDiscriminatedConnectorConfig",
    "ConnectorBrexDiscriminatedConnectorConfigConfig",
    "ConnectorBrexDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorCodaDiscriminatedConnectorConfig",
    "ConnectorFinchDiscriminatedConnectorConfig",
    "ConnectorFinchDiscriminatedConnectorConfigConfig",
    "ConnectorFirebaseDiscriminatedConnectorConfig",
    "ConnectorForeceiptDiscriminatedConnectorConfig",
    "ConnectorGreenhouseDiscriminatedConnectorConfig",
    "ConnectorHeronDiscriminatedConnectorConfig",
    "ConnectorHeronDiscriminatedConnectorConfigConfig",
    "ConnectorLunchmoneyDiscriminatedConnectorConfig",
    "ConnectorLunchmoneyDiscriminatedConnectorConfigConfig",
    "ConnectorMercuryDiscriminatedConnectorConfig",
    "ConnectorMercuryDiscriminatedConnectorConfigConfig",
    "ConnectorMercuryDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorMergeDiscriminatedConnectorConfig",
    "ConnectorMergeDiscriminatedConnectorConfigConfig",
    "ConnectorMootaDiscriminatedConnectorConfig",
    "ConnectorMootaDiscriminatedConnectorConfigConfig",
    "ConnectorOnebrickDiscriminatedConnectorConfig",
    "ConnectorOnebrickDiscriminatedConnectorConfigConfig",
    "ConnectorOpenledgerDiscriminatedConnectorConfig",
    "ConnectorOpenledgerDiscriminatedConnectorConfigConfig",
    "ConnectorPlaidDiscriminatedConnectorConfig",
    "ConnectorPlaidDiscriminatedConnectorConfigConfig",
    "ConnectorPlaidDiscriminatedConnectorConfigConfigCredentials",
    "ConnectorPostgresDiscriminatedConnectorConfig",
    "ConnectorRampDiscriminatedConnectorConfig",
    "ConnectorRampDiscriminatedConnectorConfigConfig",
    "ConnectorRampDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorSaltedgeDiscriminatedConnectorConfig",
    "ConnectorSaltedgeDiscriminatedConnectorConfigConfig",
    "ConnectorSharepointOnpremDiscriminatedConnectorConfig",
    "ConnectorSplitwiseDiscriminatedConnectorConfig",
    "ConnectorStripeDiscriminatedConnectorConfig",
    "ConnectorStripeDiscriminatedConnectorConfigConfig",
    "ConnectorStripeDiscriminatedConnectorConfigConfigOAuth",
    "ConnectorTellerDiscriminatedConnectorConfig",
    "ConnectorTellerDiscriminatedConnectorConfigConfig",
    "ConnectorTogglDiscriminatedConnectorConfig",
    "ConnectorTwentyDiscriminatedConnectorConfig",
    "ConnectorVenmoDiscriminatedConnectorConfig",
    "ConnectorVenmoDiscriminatedConnectorConfigConfig",
    "ConnectorVenmoDiscriminatedConnectorConfigConfigProxy",
    "ConnectorWiseDiscriminatedConnectorConfig",
    "ConnectorYodleeDiscriminatedConnectorConfig",
    "ConnectorYodleeDiscriminatedConnectorConfigConfig",
    "ConnectorYodleeDiscriminatedConnectorConfigConfigProxy",
]


class ConnectorAcceloDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAcceloDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAcceloDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAcceloDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAcceloDiscriminatedConnectorConfigConfig

    connector_name: Literal["accelo"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAcmeApikeyDiscriminatedConnectorConfig(BaseModel):
    config: object
    """Base configuration for api key connector"""

    connector_name: Literal["acme-apikey"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAcmeOauth2DiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAcmeOauth2DiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAcmeOauth2DiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAcmeOauth2DiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAcmeOauth2DiscriminatedConnectorConfigConfig

    connector_name: Literal["acme-oauth2"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAdobeDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAdobeDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAdobeDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAdobeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAdobeDiscriminatedConnectorConfigConfig

    connector_name: Literal["adobe"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAdyenDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAdyenDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAdyenDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAdyenDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAdyenDiscriminatedConnectorConfigConfig

    connector_name: Literal["adyen"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAircallDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAircallDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAircallDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAircallDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAircallDiscriminatedConnectorConfigConfig

    connector_name: Literal["aircall"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAmazonDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAmazonDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAmazonDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAmazonDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAmazonDiscriminatedConnectorConfigConfig

    connector_name: Literal["amazon"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorApaleoDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorApaleoDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorApaleoDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorApaleoDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorApaleoDiscriminatedConnectorConfigConfig

    connector_name: Literal["apaleo"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAsanaDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAsanaDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAsanaDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAsanaDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAsanaDiscriminatedConnectorConfigConfig

    connector_name: Literal["asana"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAttioDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAttioDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAttioDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAttioDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAttioDiscriminatedConnectorConfigConfig

    connector_name: Literal["attio"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAuth0DiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAuth0DiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAuth0DiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAuth0DiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAuth0DiscriminatedConnectorConfigConfig

    connector_name: Literal["auth0"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAutodeskDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAutodeskDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAutodeskDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAutodeskDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAutodeskDiscriminatedConnectorConfigConfig

    connector_name: Literal["autodesk"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAwsDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorAwsDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorAwsDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorAwsDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorAwsDiscriminatedConnectorConfigConfig

    connector_name: Literal["aws"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBamboohrDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBamboohrDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBamboohrDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBamboohrDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBamboohrDiscriminatedConnectorConfigConfig

    connector_name: Literal["bamboohr"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBasecampDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBasecampDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBasecampDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBasecampDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBasecampDiscriminatedConnectorConfigConfig

    connector_name: Literal["basecamp"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBattlenetDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBattlenetDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBattlenetDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBattlenetDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBattlenetDiscriminatedConnectorConfigConfig

    connector_name: Literal["battlenet"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBigcommerceDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBigcommerceDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBigcommerceDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBigcommerceDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBigcommerceDiscriminatedConnectorConfigConfig

    connector_name: Literal["bigcommerce"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBitbucketDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBitbucketDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBitbucketDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBitbucketDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBitbucketDiscriminatedConnectorConfigConfig

    connector_name: Literal["bitbucket"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBitlyDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBitlyDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBitlyDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBitlyDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBitlyDiscriminatedConnectorConfigConfig

    connector_name: Literal["bitly"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBlackbaudDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBlackbaudDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBlackbaudDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBlackbaudDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBlackbaudDiscriminatedConnectorConfigConfig

    connector_name: Literal["blackbaud"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBoldsignDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBoldsignDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBoldsignDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBoldsignDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBoldsignDiscriminatedConnectorConfigConfig

    connector_name: Literal["boldsign"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBoxDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBoxDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBoxDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBoxDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBoxDiscriminatedConnectorConfigConfig

    connector_name: Literal["box"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBraintreeDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorBraintreeDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorBraintreeDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorBraintreeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBraintreeDiscriminatedConnectorConfigConfig

    connector_name: Literal["braintree"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCalendlyDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorCalendlyDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorCalendlyDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorCalendlyDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorCalendlyDiscriminatedConnectorConfigConfig

    connector_name: Literal["calendly"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorClickupDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorClickupDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorClickupDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorClickupDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorClickupDiscriminatedConnectorConfigConfig

    connector_name: Literal["clickup"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCloseDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorCloseDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorCloseDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorCloseDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorCloseDiscriminatedConnectorConfigConfig

    connector_name: Literal["close"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorConfluenceDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorConfluenceDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorConfluenceDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorConfluenceDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorConfluenceDiscriminatedConnectorConfigConfig

    connector_name: Literal["confluence"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorContentfulDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorContentfulDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorContentfulDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorContentfulDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorContentfulDiscriminatedConnectorConfigConfig

    connector_name: Literal["contentful"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorContentstackDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorContentstackDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorContentstackDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorContentstackDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorContentstackDiscriminatedConnectorConfigConfig

    connector_name: Literal["contentstack"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCopperDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorCopperDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorCopperDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorCopperDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorCopperDiscriminatedConnectorConfigConfig

    connector_name: Literal["copper"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCorosDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorCorosDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorCorosDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorCorosDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorCorosDiscriminatedConnectorConfigConfig

    connector_name: Literal["coros"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDatevDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorDatevDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorDatevDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorDatevDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorDatevDiscriminatedConnectorConfigConfig

    connector_name: Literal["datev"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDeelDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorDeelDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorDeelDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorDeelDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorDeelDiscriminatedConnectorConfigConfig

    connector_name: Literal["deel"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDialpadDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorDialpadDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorDialpadDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorDialpadDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorDialpadDiscriminatedConnectorConfigConfig

    connector_name: Literal["dialpad"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDigitaloceanDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorDigitaloceanDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorDigitaloceanDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorDigitaloceanDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorDigitaloceanDiscriminatedConnectorConfigConfig

    connector_name: Literal["digitalocean"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDiscordDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorDiscordDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorDiscordDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorDiscordDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorDiscordDiscriminatedConnectorConfigConfig

    connector_name: Literal["discord"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDocusignDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorDocusignDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorDocusignDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorDocusignDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorDocusignDiscriminatedConnectorConfigConfig

    connector_name: Literal["docusign"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDropboxDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorDropboxDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorDropboxDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorDropboxDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorDropboxDiscriminatedConnectorConfigConfig

    connector_name: Literal["dropbox"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEbayDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorEbayDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorEbayDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorEbayDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorEbayDiscriminatedConnectorConfigConfig

    connector_name: Literal["ebay"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEgnyteDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorEgnyteDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorEgnyteDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorEgnyteDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorEgnyteDiscriminatedConnectorConfigConfig

    connector_name: Literal["egnyte"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEnvoyDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorEnvoyDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorEnvoyDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorEnvoyDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorEnvoyDiscriminatedConnectorConfigConfig

    connector_name: Literal["envoy"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEventbriteDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorEventbriteDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorEventbriteDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorEventbriteDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorEventbriteDiscriminatedConnectorConfigConfig

    connector_name: Literal["eventbrite"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorExistDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorExistDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorExistDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorExistDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorExistDiscriminatedConnectorConfigConfig

    connector_name: Literal["exist"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFacebookDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorFacebookDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorFacebookDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorFacebookDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorFacebookDiscriminatedConnectorConfigConfig

    connector_name: Literal["facebook"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFactorialDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorFactorialDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorFactorialDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorFactorialDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorFactorialDiscriminatedConnectorConfigConfig

    connector_name: Literal["factorial"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFigmaDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorFigmaDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorFigmaDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorFigmaDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorFigmaDiscriminatedConnectorConfigConfig

    connector_name: Literal["figma"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFitbitDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorFitbitDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorFitbitDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorFitbitDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorFitbitDiscriminatedConnectorConfigConfig

    connector_name: Literal["fitbit"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFortnoxDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorFortnoxDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorFortnoxDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorFortnoxDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorFortnoxDiscriminatedConnectorConfigConfig

    connector_name: Literal["fortnox"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFreshbooksDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorFreshbooksDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorFreshbooksDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorFreshbooksDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorFreshbooksDiscriminatedConnectorConfigConfig

    connector_name: Literal["freshbooks"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFrontDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorFrontDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorFrontDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorFrontDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorFrontDiscriminatedConnectorConfigConfig

    connector_name: Literal["front"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGitHubDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGitHubDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGitHubDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGitHubDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGitHubDiscriminatedConnectorConfigConfig

    connector_name: Literal["github"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGitlabDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGitlabDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGitlabDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGitlabDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGitlabDiscriminatedConnectorConfigConfig

    connector_name: Literal["gitlab"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGongDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGongDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGongDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGongDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGongDiscriminatedConnectorConfigConfig

    connector_name: Literal["gong"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleCalendarDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGoogleCalendarDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGoogleCalendarDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGoogleCalendarDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGoogleCalendarDiscriminatedConnectorConfigConfig

    connector_name: Literal["google-calendar"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleDocsDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGoogleDocsDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGoogleDocsDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGoogleDocsDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGoogleDocsDiscriminatedConnectorConfigConfig

    connector_name: Literal["google-docs"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleDriveDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGoogleDriveDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGoogleDriveDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGoogleDriveDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGoogleDriveDiscriminatedConnectorConfigConfig

    connector_name: Literal["google-drive"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleMailDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGoogleMailDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGoogleMailDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGoogleMailDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGoogleMailDiscriminatedConnectorConfigConfig

    connector_name: Literal["google-mail"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleSheetDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGoogleSheetDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGoogleSheetDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGoogleSheetDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGoogleSheetDiscriminatedConnectorConfigConfig

    connector_name: Literal["google-sheet"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGorgiasDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGorgiasDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGorgiasDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGorgiasDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGorgiasDiscriminatedConnectorConfigConfig

    connector_name: Literal["gorgias"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGrainDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGrainDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGrainDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGrainDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGrainDiscriminatedConnectorConfigConfig

    connector_name: Literal["grain"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGumroadDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGumroadDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGumroadDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGumroadDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGumroadDiscriminatedConnectorConfigConfig

    connector_name: Literal["gumroad"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGustoDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorGustoDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorGustoDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorGustoDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorGustoDiscriminatedConnectorConfigConfig

    connector_name: Literal["gusto"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHarvestDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorHarvestDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorHarvestDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorHarvestDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorHarvestDiscriminatedConnectorConfigConfig

    connector_name: Literal["harvest"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHighlevelDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorHighlevelDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorHighlevelDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorHighlevelDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorHighlevelDiscriminatedConnectorConfigConfig

    connector_name: Literal["highlevel"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHubspotDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorHubspotDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorHubspotDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorHubspotDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorHubspotDiscriminatedConnectorConfigConfig

    connector_name: Literal["hubspot"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorInstagramDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorInstagramDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorInstagramDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorInstagramDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorInstagramDiscriminatedConnectorConfigConfig

    connector_name: Literal["instagram"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorIntercomDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorIntercomDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorIntercomDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorIntercomDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorIntercomDiscriminatedConnectorConfigConfig

    connector_name: Literal["intercom"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorJiraDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorJiraDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorJiraDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorJiraDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorJiraDiscriminatedConnectorConfigConfig

    connector_name: Literal["jira"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorKeapDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorKeapDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorKeapDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorKeapDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorKeapDiscriminatedConnectorConfigConfig

    connector_name: Literal["keap"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLeverDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorLeverDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorLeverDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorLeverDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorLeverDiscriminatedConnectorConfigConfig

    connector_name: Literal["lever"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLinearDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorLinearDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorLinearDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorLinearDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorLinearDiscriminatedConnectorConfigConfig

    connector_name: Literal["linear"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLinkedinDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorLinkedinDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorLinkedinDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorLinkedinDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorLinkedinDiscriminatedConnectorConfigConfig

    connector_name: Literal["linkedin"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLinkhutDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorLinkhutDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorLinkhutDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorLinkhutDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorLinkhutDiscriminatedConnectorConfigConfig

    connector_name: Literal["linkhut"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMailchimpDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorMailchimpDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorMailchimpDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorMailchimpDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorMailchimpDiscriminatedConnectorConfigConfig

    connector_name: Literal["mailchimp"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMiroDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorMiroDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorMiroDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorMiroDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorMiroDiscriminatedConnectorConfigConfig

    connector_name: Literal["miro"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMondayDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorMondayDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorMondayDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorMondayDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorMondayDiscriminatedConnectorConfigConfig

    connector_name: Literal["monday"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMuralDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorMuralDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorMuralDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorMuralDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorMuralDiscriminatedConnectorConfigConfig

    connector_name: Literal["mural"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNamelyDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorNamelyDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorNamelyDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorNamelyDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorNamelyDiscriminatedConnectorConfigConfig

    connector_name: Literal["namely"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNationbuilderDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorNationbuilderDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorNationbuilderDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorNationbuilderDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorNationbuilderDiscriminatedConnectorConfigConfig

    connector_name: Literal["nationbuilder"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNetsuiteDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorNetsuiteDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorNetsuiteDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorNetsuiteDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorNetsuiteDiscriminatedConnectorConfigConfig

    connector_name: Literal["netsuite"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNotionDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorNotionDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorNotionDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorNotionDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorNotionDiscriminatedConnectorConfigConfig

    connector_name: Literal["notion"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOdooDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorOdooDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorOdooDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorOdooDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorOdooDiscriminatedConnectorConfigConfig

    connector_name: Literal["odoo"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOktaDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorOktaDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorOktaDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorOktaDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorOktaDiscriminatedConnectorConfigConfig

    connector_name: Literal["okta"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOsuDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorOsuDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorOsuDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorOsuDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorOsuDiscriminatedConnectorConfigConfig

    connector_name: Literal["osu"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOuraDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorOuraDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorOuraDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorOuraDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorOuraDiscriminatedConnectorConfigConfig

    connector_name: Literal["oura"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOutreachDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorOutreachDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorOutreachDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorOutreachDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorOutreachDiscriminatedConnectorConfigConfig

    connector_name: Literal["outreach"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPagerdutyDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorPagerdutyDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorPagerdutyDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorPagerdutyDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorPagerdutyDiscriminatedConnectorConfigConfig

    connector_name: Literal["pagerduty"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPandadocDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorPandadocDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorPandadocDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorPandadocDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorPandadocDiscriminatedConnectorConfigConfig

    connector_name: Literal["pandadoc"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPayfitDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorPayfitDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorPayfitDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorPayfitDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorPayfitDiscriminatedConnectorConfigConfig

    connector_name: Literal["payfit"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPaypalDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorPaypalDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorPaypalDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorPaypalDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorPaypalDiscriminatedConnectorConfigConfig

    connector_name: Literal["paypal"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPennylaneDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorPennylaneDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorPennylaneDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorPennylaneDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorPennylaneDiscriminatedConnectorConfigConfig

    connector_name: Literal["pennylane"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPinterestDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorPinterestDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorPinterestDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorPinterestDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorPinterestDiscriminatedConnectorConfigConfig

    connector_name: Literal["pinterest"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPipedriveDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorPipedriveDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorPipedriveDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorPipedriveDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorPipedriveDiscriminatedConnectorConfigConfig

    connector_name: Literal["pipedrive"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPodiumDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorPodiumDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorPodiumDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorPodiumDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorPodiumDiscriminatedConnectorConfigConfig

    connector_name: Literal["podium"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorProductboardDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorProductboardDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorProductboardDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorProductboardDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorProductboardDiscriminatedConnectorConfigConfig

    connector_name: Literal["productboard"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorQualtricsDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorQualtricsDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorQualtricsDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorQualtricsDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorQualtricsDiscriminatedConnectorConfigConfig

    connector_name: Literal["qualtrics"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorQuickbooksDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorQuickbooksDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorQuickbooksDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorQuickbooksDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorQuickbooksDiscriminatedConnectorConfigConfig

    connector_name: Literal["quickbooks"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorRedditDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorRedditDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorRedditDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorRedditDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorRedditDiscriminatedConnectorConfigConfig

    connector_name: Literal["reddit"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSageDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSageDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSageDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSageDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSageDiscriminatedConnectorConfigConfig

    connector_name: Literal["sage"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSalesforceDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSalesforceDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSalesforceDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSalesforceDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSalesforceDiscriminatedConnectorConfigConfig

    connector_name: Literal["salesforce"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSalesloftDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSalesloftDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSalesloftDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSalesloftDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSalesloftDiscriminatedConnectorConfigConfig

    connector_name: Literal["salesloft"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSegmentDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSegmentDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSegmentDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSegmentDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSegmentDiscriminatedConnectorConfigConfig

    connector_name: Literal["segment"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorServicem8DiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorServicem8DiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorServicem8DiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorServicem8DiscriminatedConnectorConfig(BaseModel):
    config: ConnectorServicem8DiscriminatedConnectorConfigConfig

    connector_name: Literal["servicem8"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorServicenowDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorServicenowDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorServicenowDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorServicenowDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorServicenowDiscriminatedConnectorConfigConfig

    connector_name: Literal["servicenow"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSharepointDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSharepointDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSharepointDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSharepointDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSharepointDiscriminatedConnectorConfigConfig

    connector_name: Literal["sharepoint"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorShopifyDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorShopifyDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorShopifyDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorShopifyDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorShopifyDiscriminatedConnectorConfigConfig

    connector_name: Literal["shopify"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSignnowDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSignnowDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSignnowDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSignnowDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSignnowDiscriminatedConnectorConfigConfig

    connector_name: Literal["signnow"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSlackDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSlackDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSlackDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSlackDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSlackDiscriminatedConnectorConfigConfig

    connector_name: Literal["slack"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSmartsheetDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSmartsheetDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSmartsheetDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSmartsheetDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSmartsheetDiscriminatedConnectorConfigConfig

    connector_name: Literal["smartsheet"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSnowflakeDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSnowflakeDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSnowflakeDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSnowflakeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSnowflakeDiscriminatedConnectorConfigConfig

    connector_name: Literal["snowflake"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSpotifyDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSpotifyDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSpotifyDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSpotifyDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSpotifyDiscriminatedConnectorConfigConfig

    connector_name: Literal["spotify"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSquarespaceDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSquarespaceDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSquarespaceDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSquarespaceDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSquarespaceDiscriminatedConnectorConfigConfig

    connector_name: Literal["squarespace"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSquareupDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorSquareupDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorSquareupDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorSquareupDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSquareupDiscriminatedConnectorConfigConfig

    connector_name: Literal["squareup"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorStackexchangeDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorStackexchangeDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorStackexchangeDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorStackexchangeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorStackexchangeDiscriminatedConnectorConfigConfig

    connector_name: Literal["stackexchange"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorStravaDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorStravaDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorStravaDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorStravaDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorStravaDiscriminatedConnectorConfigConfig

    connector_name: Literal["strava"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTeamworkDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTeamworkDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTeamworkDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTeamworkDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTeamworkDiscriminatedConnectorConfigConfig

    connector_name: Literal["teamwork"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTicktickDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTicktickDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTicktickDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTicktickDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTicktickDiscriminatedConnectorConfigConfig

    connector_name: Literal["ticktick"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTimelyDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTimelyDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTimelyDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTimelyDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTimelyDiscriminatedConnectorConfigConfig

    connector_name: Literal["timely"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTodoistDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTodoistDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTodoistDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTodoistDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTodoistDiscriminatedConnectorConfigConfig

    connector_name: Literal["todoist"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTremendousDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTremendousDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTremendousDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTremendousDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTremendousDiscriminatedConnectorConfigConfig

    connector_name: Literal["tremendous"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTsheetsteamDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTsheetsteamDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTsheetsteamDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTsheetsteamDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTsheetsteamDiscriminatedConnectorConfigConfig

    connector_name: Literal["tsheetsteam"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTumblrDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTumblrDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTumblrDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTumblrDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTumblrDiscriminatedConnectorConfigConfig

    connector_name: Literal["tumblr"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwinfieldDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTwinfieldDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTwinfieldDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTwinfieldDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTwinfieldDiscriminatedConnectorConfigConfig

    connector_name: Literal["twinfield"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwitchDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTwitchDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTwitchDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTwitchDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTwitchDiscriminatedConnectorConfigConfig

    connector_name: Literal["twitch"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwitterDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTwitterDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTwitterDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTwitterDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTwitterDiscriminatedConnectorConfigConfig

    connector_name: Literal["twitter"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTypeformDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorTypeformDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorTypeformDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorTypeformDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTypeformDiscriminatedConnectorConfigConfig

    connector_name: Literal["typeform"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorUberDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorUberDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorUberDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorUberDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorUberDiscriminatedConnectorConfigConfig

    connector_name: Literal["uber"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorVimeoDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorVimeoDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorVimeoDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorVimeoDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorVimeoDiscriminatedConnectorConfigConfig

    connector_name: Literal["vimeo"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWakatimeDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorWakatimeDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorWakatimeDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorWakatimeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorWakatimeDiscriminatedConnectorConfigConfig

    connector_name: Literal["wakatime"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWealthboxDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorWealthboxDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorWealthboxDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorWealthboxDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorWealthboxDiscriminatedConnectorConfigConfig

    connector_name: Literal["wealthbox"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWebflowDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorWebflowDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorWebflowDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorWebflowDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorWebflowDiscriminatedConnectorConfigConfig

    connector_name: Literal["webflow"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWhoopDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorWhoopDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorWhoopDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorWhoopDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorWhoopDiscriminatedConnectorConfigConfig

    connector_name: Literal["whoop"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWordpressDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorWordpressDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorWordpressDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorWordpressDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorWordpressDiscriminatedConnectorConfigConfig

    connector_name: Literal["wordpress"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWrikeDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorWrikeDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorWrikeDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorWrikeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorWrikeDiscriminatedConnectorConfigConfig

    connector_name: Literal["wrike"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorXeroDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorXeroDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorXeroDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorXeroDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorXeroDiscriminatedConnectorConfigConfig

    connector_name: Literal["xero"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorYahooDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorYahooDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorYahooDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorYahooDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorYahooDiscriminatedConnectorConfigConfig

    connector_name: Literal["yahoo"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorYandexDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorYandexDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorYandexDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorYandexDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorYandexDiscriminatedConnectorConfigConfig

    connector_name: Literal["yandex"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZapierDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorZapierDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorZapierDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorZapierDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorZapierDiscriminatedConnectorConfigConfig

    connector_name: Literal["zapier"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZendeskDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorZendeskDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorZendeskDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorZendeskDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorZendeskDiscriminatedConnectorConfigConfig

    connector_name: Literal["zendesk"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZenefitsDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorZenefitsDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorZenefitsDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorZenefitsDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorZenefitsDiscriminatedConnectorConfigConfig

    connector_name: Literal["zenefits"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZohoDeskDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorZohoDeskDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorZohoDeskDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorZohoDeskDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorZohoDeskDiscriminatedConnectorConfigConfig

    connector_name: Literal["zoho-desk"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZohoDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorZohoDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorZohoDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorZohoDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorZohoDiscriminatedConnectorConfigConfig

    connector_name: Literal["zoho"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZoomDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: Optional[str] = None

    client_secret: Optional[str] = None

    redirect_uri: Optional[str] = None
    """Custom redirect URI"""

    scopes: Optional[List[str]] = None


class ConnectorZoomDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: Optional[ConnectorZoomDiscriminatedConnectorConfigConfigOAuth] = None
    """Base oauth configuration for the connector"""


class ConnectorZoomDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorZoomDiscriminatedConnectorConfigConfig

    connector_name: Literal["zoom"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAirtableDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["airtable"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorApolloDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["apollo"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBrexDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorBrexDiscriminatedConnectorConfigConfig(BaseModel):
    apikey_auth: Optional[bool] = FieldInfo(alias="apikeyAuth", default=None)
    """API key auth support"""

    oauth: Optional[ConnectorBrexDiscriminatedConnectorConfigConfigOAuth] = None
    """Configure oauth"""


class ConnectorBrexDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorBrexDiscriminatedConnectorConfigConfig

    connector_name: Literal["brex"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCodaDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["coda"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFinchDiscriminatedConnectorConfigConfig(BaseModel):
    client_id: str

    client_secret: str

    products: List[
        Literal["company", "directory", "individual", "ssn", "employment", "payment", "pay_statement", "benefits"]
    ]
    """
    Finch products to access, @see
    https://developer.tryfinch.com/api-reference/development-guides/Permissions
    """

    api_version: Optional[str] = None
    """Finch API version"""


class ConnectorFinchDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorFinchDiscriminatedConnectorConfigConfig

    connector_name: Literal["finch"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFirebaseDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["firebase"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorForeceiptDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["foreceipt"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGreenhouseDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["greenhouse"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHeronDiscriminatedConnectorConfigConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorHeronDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorHeronDiscriminatedConnectorConfigConfig

    connector_name: Literal["heron"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLunchmoneyDiscriminatedConnectorConfigConfig(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ConnectorLunchmoneyDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorLunchmoneyDiscriminatedConnectorConfigConfig

    connector_name: Literal["lunchmoney"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMercuryDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorMercuryDiscriminatedConnectorConfigConfig(BaseModel):
    apikey_auth: Optional[bool] = FieldInfo(alias="apikeyAuth", default=None)
    """API key auth support"""

    oauth: Optional[ConnectorMercuryDiscriminatedConnectorConfigConfigOAuth] = None
    """Configure oauth"""


class ConnectorMercuryDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorMercuryDiscriminatedConnectorConfigConfig

    connector_name: Literal["mercury"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMergeDiscriminatedConnectorConfigConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorMergeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorMergeDiscriminatedConnectorConfigConfig

    connector_name: Literal["merge"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMootaDiscriminatedConnectorConfigConfig(BaseModel):
    token: str


class ConnectorMootaDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorMootaDiscriminatedConnectorConfigConfig

    connector_name: Literal["moota"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOnebrickDiscriminatedConnectorConfigConfig(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")

    env_name: Literal["sandbox", "production"] = FieldInfo(alias="envName")

    public_token: str = FieldInfo(alias="publicToken")

    access_token: Optional[str] = FieldInfo(alias="accessToken", default=None)

    redirect_url: Optional[str] = FieldInfo(alias="redirectUrl", default=None)


class ConnectorOnebrickDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorOnebrickDiscriminatedConnectorConfigConfig

    connector_name: Literal["onebrick"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOpenledgerDiscriminatedConnectorConfigConfig(BaseModel):
    api_url: str
    """API endpoint"""

    developer_id: str
    """Your developer ID for authentication"""

    developer_secret: str
    """Your developer secret"""

    environment: Literal["development", "production"]
    """Switch to "production" for live data"""


class ConnectorOpenledgerDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorOpenledgerDiscriminatedConnectorConfigConfig

    connector_name: Literal["openledger"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPlaidDiscriminatedConnectorConfigConfigCredentials(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorPlaidDiscriminatedConnectorConfigConfig(BaseModel):
    client_name: str = FieldInfo(alias="clientName")
    """
    The name of your application, as it should be displayed in Link. Maximum length
    of 30 characters. If a value longer than 30 characters is provided, Link will
    display "This Application" instead.
    """

    country_codes: List[
        Literal["US", "GB", "ES", "NL", "FR", "IE", "CA", "DE", "IT", "PL", "DK", "NO", "SE", "EE", "LT", "LV"]
    ] = FieldInfo(alias="countryCodes")

    env_name: Literal["sandbox", "development", "production"] = FieldInfo(alias="envName")

    language: Literal["en", "fr", "es", "nl", "de"]

    products: List[
        Literal[
            "assets",
            "auth",
            "balance",
            "identity",
            "investments",
            "liabilities",
            "payment_initiation",
            "identity_verification",
            "transactions",
            "credit_details",
            "income",
            "income_verification",
            "deposit_switch",
            "standing_orders",
            "transfer",
            "employment",
            "recurring_transactions",
        ]
    ]

    credentials: Optional[ConnectorPlaidDiscriminatedConnectorConfigConfigCredentials] = None


class ConnectorPlaidDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorPlaidDiscriminatedConnectorConfigConfig

    connector_name: Literal["plaid"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPostgresDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["postgres"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorRampDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorRampDiscriminatedConnectorConfigConfig(BaseModel):
    oauth: ConnectorRampDiscriminatedConnectorConfigConfigOAuth


class ConnectorRampDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorRampDiscriminatedConnectorConfigConfig

    connector_name: Literal["ramp"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSaltedgeDiscriminatedConnectorConfigConfig(BaseModel):
    app_id: str = FieldInfo(alias="appId")

    secret: str

    url: Optional[str] = None


class ConnectorSaltedgeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorSaltedgeDiscriminatedConnectorConfigConfig

    connector_name: Literal["saltedge"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSharepointOnpremDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["sharepoint-onprem"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSplitwiseDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["splitwise"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorStripeDiscriminatedConnectorConfigConfigOAuth(BaseModel):
    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")


class ConnectorStripeDiscriminatedConnectorConfigConfig(BaseModel):
    apikey_auth: Optional[bool] = FieldInfo(alias="apikeyAuth", default=None)
    """API key auth support"""

    oauth: Optional[ConnectorStripeDiscriminatedConnectorConfigConfigOAuth] = None
    """Configure oauth"""


class ConnectorStripeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorStripeDiscriminatedConnectorConfigConfig

    connector_name: Literal["stripe"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTellerDiscriminatedConnectorConfigConfig(BaseModel):
    application_id: str = FieldInfo(alias="applicationId")

    token: Optional[str] = None


class ConnectorTellerDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorTellerDiscriminatedConnectorConfigConfig

    connector_name: Literal["teller"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTogglDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["toggl"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwentyDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["twenty"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorVenmoDiscriminatedConnectorConfigConfigProxy(BaseModel):
    cert: str

    url: str


class ConnectorVenmoDiscriminatedConnectorConfigConfig(BaseModel):
    proxy: Optional[ConnectorVenmoDiscriminatedConnectorConfigConfigProxy] = None

    v1_base_url: Optional[str] = FieldInfo(alias="v1BaseURL", default=None)

    v5_base_url: Optional[str] = FieldInfo(alias="v5BaseURL", default=None)


class ConnectorVenmoDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorVenmoDiscriminatedConnectorConfigConfig

    connector_name: Literal["venmo"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWiseDiscriminatedConnectorConfig(BaseModel):
    config: object

    connector_name: Literal["wise"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorYodleeDiscriminatedConnectorConfigConfigProxy(BaseModel):
    cert: str

    url: str


class ConnectorYodleeDiscriminatedConnectorConfigConfig(BaseModel):
    admin_login_name: str = FieldInfo(alias="adminLoginName")

    client_id: str = FieldInfo(alias="clientId")

    client_secret: str = FieldInfo(alias="clientSecret")

    env_name: Literal["sandbox", "development", "production"] = FieldInfo(alias="envName")

    proxy: Optional[ConnectorYodleeDiscriminatedConnectorConfigConfigProxy] = None

    sandbox_login_name: Optional[str] = FieldInfo(alias="sandboxLoginName", default=None)


class ConnectorYodleeDiscriminatedConnectorConfig(BaseModel):
    config: ConnectorYodleeDiscriminatedConnectorConfigConfig

    connector_name: Literal["yodlee"]

    id: Optional[str] = None

    created_at: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    org_id: Optional[str] = None

    updated_at: Optional[str] = None


CreateConnnectorConfigResponse: TypeAlias = Union[
    ConnectorAcceloDiscriminatedConnectorConfig,
    ConnectorAcmeApikeyDiscriminatedConnectorConfig,
    ConnectorAcmeOauth2DiscriminatedConnectorConfig,
    ConnectorAdobeDiscriminatedConnectorConfig,
    ConnectorAdyenDiscriminatedConnectorConfig,
    ConnectorAircallDiscriminatedConnectorConfig,
    ConnectorAmazonDiscriminatedConnectorConfig,
    ConnectorApaleoDiscriminatedConnectorConfig,
    ConnectorAsanaDiscriminatedConnectorConfig,
    ConnectorAttioDiscriminatedConnectorConfig,
    ConnectorAuth0DiscriminatedConnectorConfig,
    ConnectorAutodeskDiscriminatedConnectorConfig,
    ConnectorAwsDiscriminatedConnectorConfig,
    ConnectorBamboohrDiscriminatedConnectorConfig,
    ConnectorBasecampDiscriminatedConnectorConfig,
    ConnectorBattlenetDiscriminatedConnectorConfig,
    ConnectorBigcommerceDiscriminatedConnectorConfig,
    ConnectorBitbucketDiscriminatedConnectorConfig,
    ConnectorBitlyDiscriminatedConnectorConfig,
    ConnectorBlackbaudDiscriminatedConnectorConfig,
    ConnectorBoldsignDiscriminatedConnectorConfig,
    ConnectorBoxDiscriminatedConnectorConfig,
    ConnectorBraintreeDiscriminatedConnectorConfig,
    ConnectorCalendlyDiscriminatedConnectorConfig,
    ConnectorClickupDiscriminatedConnectorConfig,
    ConnectorCloseDiscriminatedConnectorConfig,
    ConnectorConfluenceDiscriminatedConnectorConfig,
    ConnectorContentfulDiscriminatedConnectorConfig,
    ConnectorContentstackDiscriminatedConnectorConfig,
    ConnectorCopperDiscriminatedConnectorConfig,
    ConnectorCorosDiscriminatedConnectorConfig,
    ConnectorDatevDiscriminatedConnectorConfig,
    ConnectorDeelDiscriminatedConnectorConfig,
    ConnectorDialpadDiscriminatedConnectorConfig,
    ConnectorDigitaloceanDiscriminatedConnectorConfig,
    ConnectorDiscordDiscriminatedConnectorConfig,
    ConnectorDocusignDiscriminatedConnectorConfig,
    ConnectorDropboxDiscriminatedConnectorConfig,
    ConnectorEbayDiscriminatedConnectorConfig,
    ConnectorEgnyteDiscriminatedConnectorConfig,
    ConnectorEnvoyDiscriminatedConnectorConfig,
    ConnectorEventbriteDiscriminatedConnectorConfig,
    ConnectorExistDiscriminatedConnectorConfig,
    ConnectorFacebookDiscriminatedConnectorConfig,
    ConnectorFactorialDiscriminatedConnectorConfig,
    ConnectorFigmaDiscriminatedConnectorConfig,
    ConnectorFitbitDiscriminatedConnectorConfig,
    ConnectorFortnoxDiscriminatedConnectorConfig,
    ConnectorFreshbooksDiscriminatedConnectorConfig,
    ConnectorFrontDiscriminatedConnectorConfig,
    ConnectorGitHubDiscriminatedConnectorConfig,
    ConnectorGitlabDiscriminatedConnectorConfig,
    ConnectorGongDiscriminatedConnectorConfig,
    ConnectorGoogleCalendarDiscriminatedConnectorConfig,
    ConnectorGoogleDocsDiscriminatedConnectorConfig,
    ConnectorGoogleDriveDiscriminatedConnectorConfig,
    ConnectorGoogleMailDiscriminatedConnectorConfig,
    ConnectorGoogleSheetDiscriminatedConnectorConfig,
    ConnectorGorgiasDiscriminatedConnectorConfig,
    ConnectorGrainDiscriminatedConnectorConfig,
    ConnectorGumroadDiscriminatedConnectorConfig,
    ConnectorGustoDiscriminatedConnectorConfig,
    ConnectorHarvestDiscriminatedConnectorConfig,
    ConnectorHighlevelDiscriminatedConnectorConfig,
    ConnectorHubspotDiscriminatedConnectorConfig,
    ConnectorInstagramDiscriminatedConnectorConfig,
    ConnectorIntercomDiscriminatedConnectorConfig,
    ConnectorJiraDiscriminatedConnectorConfig,
    ConnectorKeapDiscriminatedConnectorConfig,
    ConnectorLeverDiscriminatedConnectorConfig,
    ConnectorLinearDiscriminatedConnectorConfig,
    ConnectorLinkedinDiscriminatedConnectorConfig,
    ConnectorLinkhutDiscriminatedConnectorConfig,
    ConnectorMailchimpDiscriminatedConnectorConfig,
    ConnectorMiroDiscriminatedConnectorConfig,
    ConnectorMondayDiscriminatedConnectorConfig,
    ConnectorMuralDiscriminatedConnectorConfig,
    ConnectorNamelyDiscriminatedConnectorConfig,
    ConnectorNationbuilderDiscriminatedConnectorConfig,
    ConnectorNetsuiteDiscriminatedConnectorConfig,
    ConnectorNotionDiscriminatedConnectorConfig,
    ConnectorOdooDiscriminatedConnectorConfig,
    ConnectorOktaDiscriminatedConnectorConfig,
    ConnectorOsuDiscriminatedConnectorConfig,
    ConnectorOuraDiscriminatedConnectorConfig,
    ConnectorOutreachDiscriminatedConnectorConfig,
    ConnectorPagerdutyDiscriminatedConnectorConfig,
    ConnectorPandadocDiscriminatedConnectorConfig,
    ConnectorPayfitDiscriminatedConnectorConfig,
    ConnectorPaypalDiscriminatedConnectorConfig,
    ConnectorPennylaneDiscriminatedConnectorConfig,
    ConnectorPinterestDiscriminatedConnectorConfig,
    ConnectorPipedriveDiscriminatedConnectorConfig,
    ConnectorPodiumDiscriminatedConnectorConfig,
    ConnectorProductboardDiscriminatedConnectorConfig,
    ConnectorQualtricsDiscriminatedConnectorConfig,
    ConnectorQuickbooksDiscriminatedConnectorConfig,
    ConnectorRedditDiscriminatedConnectorConfig,
    ConnectorSageDiscriminatedConnectorConfig,
    ConnectorSalesforceDiscriminatedConnectorConfig,
    ConnectorSalesloftDiscriminatedConnectorConfig,
    ConnectorSegmentDiscriminatedConnectorConfig,
    ConnectorServicem8DiscriminatedConnectorConfig,
    ConnectorServicenowDiscriminatedConnectorConfig,
    ConnectorSharepointDiscriminatedConnectorConfig,
    ConnectorShopifyDiscriminatedConnectorConfig,
    ConnectorSignnowDiscriminatedConnectorConfig,
    ConnectorSlackDiscriminatedConnectorConfig,
    ConnectorSmartsheetDiscriminatedConnectorConfig,
    ConnectorSnowflakeDiscriminatedConnectorConfig,
    ConnectorSpotifyDiscriminatedConnectorConfig,
    ConnectorSquarespaceDiscriminatedConnectorConfig,
    ConnectorSquareupDiscriminatedConnectorConfig,
    ConnectorStackexchangeDiscriminatedConnectorConfig,
    ConnectorStravaDiscriminatedConnectorConfig,
    ConnectorTeamworkDiscriminatedConnectorConfig,
    ConnectorTicktickDiscriminatedConnectorConfig,
    ConnectorTimelyDiscriminatedConnectorConfig,
    ConnectorTodoistDiscriminatedConnectorConfig,
    ConnectorTremendousDiscriminatedConnectorConfig,
    ConnectorTsheetsteamDiscriminatedConnectorConfig,
    ConnectorTumblrDiscriminatedConnectorConfig,
    ConnectorTwinfieldDiscriminatedConnectorConfig,
    ConnectorTwitchDiscriminatedConnectorConfig,
    ConnectorTwitterDiscriminatedConnectorConfig,
    ConnectorTypeformDiscriminatedConnectorConfig,
    ConnectorUberDiscriminatedConnectorConfig,
    ConnectorVimeoDiscriminatedConnectorConfig,
    ConnectorWakatimeDiscriminatedConnectorConfig,
    ConnectorWealthboxDiscriminatedConnectorConfig,
    ConnectorWebflowDiscriminatedConnectorConfig,
    ConnectorWhoopDiscriminatedConnectorConfig,
    ConnectorWordpressDiscriminatedConnectorConfig,
    ConnectorWrikeDiscriminatedConnectorConfig,
    ConnectorXeroDiscriminatedConnectorConfig,
    ConnectorYahooDiscriminatedConnectorConfig,
    ConnectorYandexDiscriminatedConnectorConfig,
    ConnectorZapierDiscriminatedConnectorConfig,
    ConnectorZendeskDiscriminatedConnectorConfig,
    ConnectorZenefitsDiscriminatedConnectorConfig,
    ConnectorZohoDeskDiscriminatedConnectorConfig,
    ConnectorZohoDiscriminatedConnectorConfig,
    ConnectorZoomDiscriminatedConnectorConfig,
    ConnectorAirtableDiscriminatedConnectorConfig,
    ConnectorApolloDiscriminatedConnectorConfig,
    ConnectorBrexDiscriminatedConnectorConfig,
    ConnectorCodaDiscriminatedConnectorConfig,
    ConnectorFinchDiscriminatedConnectorConfig,
    ConnectorFirebaseDiscriminatedConnectorConfig,
    ConnectorForeceiptDiscriminatedConnectorConfig,
    ConnectorGreenhouseDiscriminatedConnectorConfig,
    ConnectorHeronDiscriminatedConnectorConfig,
    ConnectorLunchmoneyDiscriminatedConnectorConfig,
    ConnectorMercuryDiscriminatedConnectorConfig,
    ConnectorMergeDiscriminatedConnectorConfig,
    ConnectorMootaDiscriminatedConnectorConfig,
    ConnectorOnebrickDiscriminatedConnectorConfig,
    ConnectorOpenledgerDiscriminatedConnectorConfig,
    ConnectorPlaidDiscriminatedConnectorConfig,
    ConnectorPostgresDiscriminatedConnectorConfig,
    ConnectorRampDiscriminatedConnectorConfig,
    ConnectorSaltedgeDiscriminatedConnectorConfig,
    ConnectorSharepointOnpremDiscriminatedConnectorConfig,
    ConnectorSplitwiseDiscriminatedConnectorConfig,
    ConnectorStripeDiscriminatedConnectorConfig,
    ConnectorTellerDiscriminatedConnectorConfig,
    ConnectorTogglDiscriminatedConnectorConfig,
    ConnectorTwentyDiscriminatedConnectorConfig,
    ConnectorVenmoDiscriminatedConnectorConfig,
    ConnectorWiseDiscriminatedConnectorConfig,
    ConnectorYodleeDiscriminatedConnectorConfig,
]
