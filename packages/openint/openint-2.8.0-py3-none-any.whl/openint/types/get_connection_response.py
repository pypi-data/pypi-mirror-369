# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .connector import Connector
from .integration import Integration

__all__ = [
    "GetConnectionResponse",
    "ConnectorAcceloDiscriminatedConnectionSettings",
    "ConnectorAcceloDiscriminatedConnectionSettingsSettings",
    "ConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAcmeApikeyDiscriminatedConnectionSettings",
    "ConnectorAcmeApikeyDiscriminatedConnectionSettingsSettings",
    "ConnectorAcmeOauth2DiscriminatedConnectionSettings",
    "ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings",
    "ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAdobeDiscriminatedConnectionSettings",
    "ConnectorAdobeDiscriminatedConnectionSettingsSettings",
    "ConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAdyenDiscriminatedConnectionSettings",
    "ConnectorAdyenDiscriminatedConnectionSettingsSettings",
    "ConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAircallDiscriminatedConnectionSettings",
    "ConnectorAircallDiscriminatedConnectionSettingsSettings",
    "ConnectorAircallDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAircallDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAmazonDiscriminatedConnectionSettings",
    "ConnectorAmazonDiscriminatedConnectionSettingsSettings",
    "ConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorApaleoDiscriminatedConnectionSettings",
    "ConnectorApaleoDiscriminatedConnectionSettingsSettings",
    "ConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAsanaDiscriminatedConnectionSettings",
    "ConnectorAsanaDiscriminatedConnectionSettingsSettings",
    "ConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAttioDiscriminatedConnectionSettings",
    "ConnectorAttioDiscriminatedConnectionSettingsSettings",
    "ConnectorAttioDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAttioDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAuth0DiscriminatedConnectionSettings",
    "ConnectorAuth0DiscriminatedConnectionSettingsSettings",
    "ConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAutodeskDiscriminatedConnectionSettings",
    "ConnectorAutodeskDiscriminatedConnectionSettingsSettings",
    "ConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAwsDiscriminatedConnectionSettings",
    "ConnectorAwsDiscriminatedConnectionSettingsSettings",
    "ConnectorAwsDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorAwsDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBamboohrDiscriminatedConnectionSettings",
    "ConnectorBamboohrDiscriminatedConnectionSettingsSettings",
    "ConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBasecampDiscriminatedConnectionSettings",
    "ConnectorBasecampDiscriminatedConnectionSettingsSettings",
    "ConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBattlenetDiscriminatedConnectionSettings",
    "ConnectorBattlenetDiscriminatedConnectionSettingsSettings",
    "ConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBigcommerceDiscriminatedConnectionSettings",
    "ConnectorBigcommerceDiscriminatedConnectionSettingsSettings",
    "ConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBitbucketDiscriminatedConnectionSettings",
    "ConnectorBitbucketDiscriminatedConnectionSettingsSettings",
    "ConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBitlyDiscriminatedConnectionSettings",
    "ConnectorBitlyDiscriminatedConnectionSettingsSettings",
    "ConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBlackbaudDiscriminatedConnectionSettings",
    "ConnectorBlackbaudDiscriminatedConnectionSettingsSettings",
    "ConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBoldsignDiscriminatedConnectionSettings",
    "ConnectorBoldsignDiscriminatedConnectionSettingsSettings",
    "ConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBoxDiscriminatedConnectionSettings",
    "ConnectorBoxDiscriminatedConnectionSettingsSettings",
    "ConnectorBoxDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBoxDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorBraintreeDiscriminatedConnectionSettings",
    "ConnectorBraintreeDiscriminatedConnectionSettingsSettings",
    "ConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorCalendlyDiscriminatedConnectionSettings",
    "ConnectorCalendlyDiscriminatedConnectionSettingsSettings",
    "ConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorClickupDiscriminatedConnectionSettings",
    "ConnectorClickupDiscriminatedConnectionSettingsSettings",
    "ConnectorClickupDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorClickupDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorCloseDiscriminatedConnectionSettings",
    "ConnectorCloseDiscriminatedConnectionSettingsSettings",
    "ConnectorCloseDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorCloseDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorConfluenceDiscriminatedConnectionSettings",
    "ConnectorConfluenceDiscriminatedConnectionSettingsSettings",
    "ConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorContentfulDiscriminatedConnectionSettings",
    "ConnectorContentfulDiscriminatedConnectionSettingsSettings",
    "ConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorContentstackDiscriminatedConnectionSettings",
    "ConnectorContentstackDiscriminatedConnectionSettingsSettings",
    "ConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorCopperDiscriminatedConnectionSettings",
    "ConnectorCopperDiscriminatedConnectionSettingsSettings",
    "ConnectorCopperDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorCopperDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorCorosDiscriminatedConnectionSettings",
    "ConnectorCorosDiscriminatedConnectionSettingsSettings",
    "ConnectorCorosDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorCorosDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorDatevDiscriminatedConnectionSettings",
    "ConnectorDatevDiscriminatedConnectionSettingsSettings",
    "ConnectorDatevDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorDatevDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorDeelDiscriminatedConnectionSettings",
    "ConnectorDeelDiscriminatedConnectionSettingsSettings",
    "ConnectorDeelDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorDeelDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorDialpadDiscriminatedConnectionSettings",
    "ConnectorDialpadDiscriminatedConnectionSettingsSettings",
    "ConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorDigitaloceanDiscriminatedConnectionSettings",
    "ConnectorDigitaloceanDiscriminatedConnectionSettingsSettings",
    "ConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorDiscordDiscriminatedConnectionSettings",
    "ConnectorDiscordDiscriminatedConnectionSettingsSettings",
    "ConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorDocusignDiscriminatedConnectionSettings",
    "ConnectorDocusignDiscriminatedConnectionSettingsSettings",
    "ConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorDropboxDiscriminatedConnectionSettings",
    "ConnectorDropboxDiscriminatedConnectionSettingsSettings",
    "ConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorEbayDiscriminatedConnectionSettings",
    "ConnectorEbayDiscriminatedConnectionSettingsSettings",
    "ConnectorEbayDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorEbayDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorEgnyteDiscriminatedConnectionSettings",
    "ConnectorEgnyteDiscriminatedConnectionSettingsSettings",
    "ConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorEnvoyDiscriminatedConnectionSettings",
    "ConnectorEnvoyDiscriminatedConnectionSettingsSettings",
    "ConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorEventbriteDiscriminatedConnectionSettings",
    "ConnectorEventbriteDiscriminatedConnectionSettingsSettings",
    "ConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorExistDiscriminatedConnectionSettings",
    "ConnectorExistDiscriminatedConnectionSettingsSettings",
    "ConnectorExistDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorExistDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorFacebookDiscriminatedConnectionSettings",
    "ConnectorFacebookDiscriminatedConnectionSettingsSettings",
    "ConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorFactorialDiscriminatedConnectionSettings",
    "ConnectorFactorialDiscriminatedConnectionSettingsSettings",
    "ConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorFigmaDiscriminatedConnectionSettings",
    "ConnectorFigmaDiscriminatedConnectionSettingsSettings",
    "ConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorFitbitDiscriminatedConnectionSettings",
    "ConnectorFitbitDiscriminatedConnectionSettingsSettings",
    "ConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorFortnoxDiscriminatedConnectionSettings",
    "ConnectorFortnoxDiscriminatedConnectionSettingsSettings",
    "ConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorFreshbooksDiscriminatedConnectionSettings",
    "ConnectorFreshbooksDiscriminatedConnectionSettingsSettings",
    "ConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorFrontDiscriminatedConnectionSettings",
    "ConnectorFrontDiscriminatedConnectionSettingsSettings",
    "ConnectorFrontDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorFrontDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGitHubDiscriminatedConnectionSettings",
    "ConnectorGitHubDiscriminatedConnectionSettingsSettings",
    "ConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGitlabDiscriminatedConnectionSettings",
    "ConnectorGitlabDiscriminatedConnectionSettingsSettings",
    "ConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGongDiscriminatedConnectionSettings",
    "ConnectorGongDiscriminatedConnectionSettingsSettings",
    "ConnectorGongDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGongDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGoogleCalendarDiscriminatedConnectionSettings",
    "ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGoogleDocsDiscriminatedConnectionSettings",
    "ConnectorGoogleDocsDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGoogleDriveDiscriminatedConnectionSettings",
    "ConnectorGoogleDriveDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGoogleMailDiscriminatedConnectionSettings",
    "ConnectorGoogleMailDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGoogleSheetDiscriminatedConnectionSettings",
    "ConnectorGoogleSheetDiscriminatedConnectionSettingsSettings",
    "ConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGorgiasDiscriminatedConnectionSettings",
    "ConnectorGorgiasDiscriminatedConnectionSettingsSettings",
    "ConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGrainDiscriminatedConnectionSettings",
    "ConnectorGrainDiscriminatedConnectionSettingsSettings",
    "ConnectorGrainDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGrainDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGumroadDiscriminatedConnectionSettings",
    "ConnectorGumroadDiscriminatedConnectionSettingsSettings",
    "ConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorGustoDiscriminatedConnectionSettings",
    "ConnectorGustoDiscriminatedConnectionSettingsSettings",
    "ConnectorGustoDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorGustoDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorHarvestDiscriminatedConnectionSettings",
    "ConnectorHarvestDiscriminatedConnectionSettingsSettings",
    "ConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorHighlevelDiscriminatedConnectionSettings",
    "ConnectorHighlevelDiscriminatedConnectionSettingsSettings",
    "ConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorHubspotDiscriminatedConnectionSettings",
    "ConnectorHubspotDiscriminatedConnectionSettingsSettings",
    "ConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorInstagramDiscriminatedConnectionSettings",
    "ConnectorInstagramDiscriminatedConnectionSettingsSettings",
    "ConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorIntercomDiscriminatedConnectionSettings",
    "ConnectorIntercomDiscriminatedConnectionSettingsSettings",
    "ConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorJiraDiscriminatedConnectionSettings",
    "ConnectorJiraDiscriminatedConnectionSettingsSettings",
    "ConnectorJiraDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorJiraDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorKeapDiscriminatedConnectionSettings",
    "ConnectorKeapDiscriminatedConnectionSettingsSettings",
    "ConnectorKeapDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorKeapDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorLeverDiscriminatedConnectionSettings",
    "ConnectorLeverDiscriminatedConnectionSettingsSettings",
    "ConnectorLeverDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorLeverDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorLinearDiscriminatedConnectionSettings",
    "ConnectorLinearDiscriminatedConnectionSettingsSettings",
    "ConnectorLinearDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorLinearDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorLinkedinDiscriminatedConnectionSettings",
    "ConnectorLinkedinDiscriminatedConnectionSettingsSettings",
    "ConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorLinkhutDiscriminatedConnectionSettings",
    "ConnectorLinkhutDiscriminatedConnectionSettingsSettings",
    "ConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorMailchimpDiscriminatedConnectionSettings",
    "ConnectorMailchimpDiscriminatedConnectionSettingsSettings",
    "ConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorMiroDiscriminatedConnectionSettings",
    "ConnectorMiroDiscriminatedConnectionSettingsSettings",
    "ConnectorMiroDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorMiroDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorMondayDiscriminatedConnectionSettings",
    "ConnectorMondayDiscriminatedConnectionSettingsSettings",
    "ConnectorMondayDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorMondayDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorMuralDiscriminatedConnectionSettings",
    "ConnectorMuralDiscriminatedConnectionSettingsSettings",
    "ConnectorMuralDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorMuralDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorNamelyDiscriminatedConnectionSettings",
    "ConnectorNamelyDiscriminatedConnectionSettingsSettings",
    "ConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorNationbuilderDiscriminatedConnectionSettings",
    "ConnectorNationbuilderDiscriminatedConnectionSettingsSettings",
    "ConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorNetsuiteDiscriminatedConnectionSettings",
    "ConnectorNetsuiteDiscriminatedConnectionSettingsSettings",
    "ConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorNotionDiscriminatedConnectionSettings",
    "ConnectorNotionDiscriminatedConnectionSettingsSettings",
    "ConnectorNotionDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorNotionDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorOdooDiscriminatedConnectionSettings",
    "ConnectorOdooDiscriminatedConnectionSettingsSettings",
    "ConnectorOdooDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorOdooDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorOktaDiscriminatedConnectionSettings",
    "ConnectorOktaDiscriminatedConnectionSettingsSettings",
    "ConnectorOktaDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorOktaDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorOsuDiscriminatedConnectionSettings",
    "ConnectorOsuDiscriminatedConnectionSettingsSettings",
    "ConnectorOsuDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorOsuDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorOuraDiscriminatedConnectionSettings",
    "ConnectorOuraDiscriminatedConnectionSettingsSettings",
    "ConnectorOuraDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorOuraDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorOutreachDiscriminatedConnectionSettings",
    "ConnectorOutreachDiscriminatedConnectionSettingsSettings",
    "ConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorPagerdutyDiscriminatedConnectionSettings",
    "ConnectorPagerdutyDiscriminatedConnectionSettingsSettings",
    "ConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorPandadocDiscriminatedConnectionSettings",
    "ConnectorPandadocDiscriminatedConnectionSettingsSettings",
    "ConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorPayfitDiscriminatedConnectionSettings",
    "ConnectorPayfitDiscriminatedConnectionSettingsSettings",
    "ConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorPaypalDiscriminatedConnectionSettings",
    "ConnectorPaypalDiscriminatedConnectionSettingsSettings",
    "ConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorPennylaneDiscriminatedConnectionSettings",
    "ConnectorPennylaneDiscriminatedConnectionSettingsSettings",
    "ConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorPinterestDiscriminatedConnectionSettings",
    "ConnectorPinterestDiscriminatedConnectionSettingsSettings",
    "ConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorPipedriveDiscriminatedConnectionSettings",
    "ConnectorPipedriveDiscriminatedConnectionSettingsSettings",
    "ConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorPodiumDiscriminatedConnectionSettings",
    "ConnectorPodiumDiscriminatedConnectionSettingsSettings",
    "ConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorProductboardDiscriminatedConnectionSettings",
    "ConnectorProductboardDiscriminatedConnectionSettingsSettings",
    "ConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorQualtricsDiscriminatedConnectionSettings",
    "ConnectorQualtricsDiscriminatedConnectionSettingsSettings",
    "ConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorQuickbooksDiscriminatedConnectionSettings",
    "ConnectorQuickbooksDiscriminatedConnectionSettingsSettings",
    "ConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorRedditDiscriminatedConnectionSettings",
    "ConnectorRedditDiscriminatedConnectionSettingsSettings",
    "ConnectorRedditDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorRedditDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSageDiscriminatedConnectionSettings",
    "ConnectorSageDiscriminatedConnectionSettingsSettings",
    "ConnectorSageDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSageDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSalesforceDiscriminatedConnectionSettings",
    "ConnectorSalesforceDiscriminatedConnectionSettingsSettings",
    "ConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSalesloftDiscriminatedConnectionSettings",
    "ConnectorSalesloftDiscriminatedConnectionSettingsSettings",
    "ConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSegmentDiscriminatedConnectionSettings",
    "ConnectorSegmentDiscriminatedConnectionSettingsSettings",
    "ConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorServicem8DiscriminatedConnectionSettings",
    "ConnectorServicem8DiscriminatedConnectionSettingsSettings",
    "ConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorServicenowDiscriminatedConnectionSettings",
    "ConnectorServicenowDiscriminatedConnectionSettingsSettings",
    "ConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSharepointDiscriminatedConnectionSettings",
    "ConnectorSharepointDiscriminatedConnectionSettingsSettings",
    "ConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorShopifyDiscriminatedConnectionSettings",
    "ConnectorShopifyDiscriminatedConnectionSettingsSettings",
    "ConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSignnowDiscriminatedConnectionSettings",
    "ConnectorSignnowDiscriminatedConnectionSettingsSettings",
    "ConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSlackDiscriminatedConnectionSettings",
    "ConnectorSlackDiscriminatedConnectionSettingsSettings",
    "ConnectorSlackDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSlackDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSmartsheetDiscriminatedConnectionSettings",
    "ConnectorSmartsheetDiscriminatedConnectionSettingsSettings",
    "ConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSnowflakeDiscriminatedConnectionSettings",
    "ConnectorSnowflakeDiscriminatedConnectionSettingsSettings",
    "ConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSpotifyDiscriminatedConnectionSettings",
    "ConnectorSpotifyDiscriminatedConnectionSettingsSettings",
    "ConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSquarespaceDiscriminatedConnectionSettings",
    "ConnectorSquarespaceDiscriminatedConnectionSettingsSettings",
    "ConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorSquareupDiscriminatedConnectionSettings",
    "ConnectorSquareupDiscriminatedConnectionSettingsSettings",
    "ConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorStackexchangeDiscriminatedConnectionSettings",
    "ConnectorStackexchangeDiscriminatedConnectionSettingsSettings",
    "ConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorStravaDiscriminatedConnectionSettings",
    "ConnectorStravaDiscriminatedConnectionSettingsSettings",
    "ConnectorStravaDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorStravaDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTeamworkDiscriminatedConnectionSettings",
    "ConnectorTeamworkDiscriminatedConnectionSettingsSettings",
    "ConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTicktickDiscriminatedConnectionSettings",
    "ConnectorTicktickDiscriminatedConnectionSettingsSettings",
    "ConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTimelyDiscriminatedConnectionSettings",
    "ConnectorTimelyDiscriminatedConnectionSettingsSettings",
    "ConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTodoistDiscriminatedConnectionSettings",
    "ConnectorTodoistDiscriminatedConnectionSettingsSettings",
    "ConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTremendousDiscriminatedConnectionSettings",
    "ConnectorTremendousDiscriminatedConnectionSettingsSettings",
    "ConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTsheetsteamDiscriminatedConnectionSettings",
    "ConnectorTsheetsteamDiscriminatedConnectionSettingsSettings",
    "ConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTumblrDiscriminatedConnectionSettings",
    "ConnectorTumblrDiscriminatedConnectionSettingsSettings",
    "ConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTwinfieldDiscriminatedConnectionSettings",
    "ConnectorTwinfieldDiscriminatedConnectionSettingsSettings",
    "ConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTwitchDiscriminatedConnectionSettings",
    "ConnectorTwitchDiscriminatedConnectionSettingsSettings",
    "ConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTwitterDiscriminatedConnectionSettings",
    "ConnectorTwitterDiscriminatedConnectionSettingsSettings",
    "ConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorTypeformDiscriminatedConnectionSettings",
    "ConnectorTypeformDiscriminatedConnectionSettingsSettings",
    "ConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorUberDiscriminatedConnectionSettings",
    "ConnectorUberDiscriminatedConnectionSettingsSettings",
    "ConnectorUberDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorUberDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorVimeoDiscriminatedConnectionSettings",
    "ConnectorVimeoDiscriminatedConnectionSettingsSettings",
    "ConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorWakatimeDiscriminatedConnectionSettings",
    "ConnectorWakatimeDiscriminatedConnectionSettingsSettings",
    "ConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorWealthboxDiscriminatedConnectionSettings",
    "ConnectorWealthboxDiscriminatedConnectionSettingsSettings",
    "ConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorWebflowDiscriminatedConnectionSettings",
    "ConnectorWebflowDiscriminatedConnectionSettingsSettings",
    "ConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorWhoopDiscriminatedConnectionSettings",
    "ConnectorWhoopDiscriminatedConnectionSettingsSettings",
    "ConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorWordpressDiscriminatedConnectionSettings",
    "ConnectorWordpressDiscriminatedConnectionSettingsSettings",
    "ConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorWrikeDiscriminatedConnectionSettings",
    "ConnectorWrikeDiscriminatedConnectionSettingsSettings",
    "ConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorXeroDiscriminatedConnectionSettings",
    "ConnectorXeroDiscriminatedConnectionSettingsSettings",
    "ConnectorXeroDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorXeroDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorYahooDiscriminatedConnectionSettings",
    "ConnectorYahooDiscriminatedConnectionSettingsSettings",
    "ConnectorYahooDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorYahooDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorYandexDiscriminatedConnectionSettings",
    "ConnectorYandexDiscriminatedConnectionSettingsSettings",
    "ConnectorYandexDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorYandexDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorZapierDiscriminatedConnectionSettings",
    "ConnectorZapierDiscriminatedConnectionSettingsSettings",
    "ConnectorZapierDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorZapierDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorZendeskDiscriminatedConnectionSettings",
    "ConnectorZendeskDiscriminatedConnectionSettingsSettings",
    "ConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorZenefitsDiscriminatedConnectionSettings",
    "ConnectorZenefitsDiscriminatedConnectionSettingsSettings",
    "ConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorZohoDeskDiscriminatedConnectionSettings",
    "ConnectorZohoDeskDiscriminatedConnectionSettingsSettings",
    "ConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorZohoDiscriminatedConnectionSettings",
    "ConnectorZohoDiscriminatedConnectionSettingsSettings",
    "ConnectorZohoDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorZohoDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorZoomDiscriminatedConnectionSettings",
    "ConnectorZoomDiscriminatedConnectionSettingsSettings",
    "ConnectorZoomDiscriminatedConnectionSettingsSettingsOAuth",
    "ConnectorZoomDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "ConnectorAirtableDiscriminatedConnectionSettings",
    "ConnectorAirtableDiscriminatedConnectionSettingsSettings",
    "ConnectorApolloDiscriminatedConnectionSettings",
    "ConnectorApolloDiscriminatedConnectionSettingsSettings",
    "ConnectorBrexDiscriminatedConnectionSettings",
    "ConnectorBrexDiscriminatedConnectionSettingsSettings",
    "ConnectorCodaDiscriminatedConnectionSettings",
    "ConnectorCodaDiscriminatedConnectionSettingsSettings",
    "ConnectorFinchDiscriminatedConnectionSettings",
    "ConnectorFinchDiscriminatedConnectionSettingsSettings",
    "ConnectorFirebaseDiscriminatedConnectionSettings",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettings",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2",
    "ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig",
    "ConnectorForeceiptDiscriminatedConnectionSettings",
    "ConnectorForeceiptDiscriminatedConnectionSettingsSettings",
    "ConnectorGreenhouseDiscriminatedConnectionSettings",
    "ConnectorGreenhouseDiscriminatedConnectionSettingsSettings",
    "ConnectorHeronDiscriminatedConnectionSettings",
    "ConnectorLunchmoneyDiscriminatedConnectionSettings",
    "ConnectorMercuryDiscriminatedConnectionSettings",
    "ConnectorMergeDiscriminatedConnectionSettings",
    "ConnectorMergeDiscriminatedConnectionSettingsSettings",
    "ConnectorMootaDiscriminatedConnectionSettings",
    "ConnectorOnebrickDiscriminatedConnectionSettings",
    "ConnectorOnebrickDiscriminatedConnectionSettingsSettings",
    "ConnectorOpenledgerDiscriminatedConnectionSettings",
    "ConnectorOpenledgerDiscriminatedConnectionSettingsSettings",
    "ConnectorPlaidDiscriminatedConnectionSettings",
    "ConnectorPlaidDiscriminatedConnectionSettingsSettings",
    "ConnectorPostgresDiscriminatedConnectionSettings",
    "ConnectorPostgresDiscriminatedConnectionSettingsSettings",
    "ConnectorRampDiscriminatedConnectionSettings",
    "ConnectorRampDiscriminatedConnectionSettingsSettings",
    "ConnectorSaltedgeDiscriminatedConnectionSettings",
    "ConnectorSharepointOnpremDiscriminatedConnectionSettings",
    "ConnectorSharepointOnpremDiscriminatedConnectionSettingsSettings",
    "ConnectorSplitwiseDiscriminatedConnectionSettings",
    "ConnectorSplitwiseDiscriminatedConnectionSettingsSettings",
    "ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser",
    "ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications",
    "ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture",
    "ConnectorStripeDiscriminatedConnectionSettings",
    "ConnectorStripeDiscriminatedConnectionSettingsSettings",
    "ConnectorTellerDiscriminatedConnectionSettings",
    "ConnectorTellerDiscriminatedConnectionSettingsSettings",
    "ConnectorTogglDiscriminatedConnectionSettings",
    "ConnectorTogglDiscriminatedConnectionSettingsSettings",
    "ConnectorTwentyDiscriminatedConnectionSettings",
    "ConnectorTwentyDiscriminatedConnectionSettingsSettings",
    "ConnectorVenmoDiscriminatedConnectionSettings",
    "ConnectorVenmoDiscriminatedConnectionSettingsSettings",
    "ConnectorWiseDiscriminatedConnectionSettings",
    "ConnectorWiseDiscriminatedConnectionSettingsSettings",
    "ConnectorYodleeDiscriminatedConnectionSettings",
    "ConnectorYodleeDiscriminatedConnectionSettingsSettings",
    "ConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken",
    "ConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount",
]


class ConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAcceloDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your Accelo account (e.g., https://domain.api.accelo.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAcceloDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["accelo"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAcceloDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAcmeApikeyDiscriminatedConnectionSettingsSettings(BaseModel):
    api_key: str


class ConnectorAcmeApikeyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["acme-apikey"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAcmeApikeyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAcmeOauth2DiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["acme-oauth2"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAdobeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAdobeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["adobe"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAdobeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAdyenDiscriminatedConnectionSettingsSettings(BaseModel):
    environment: str
    """The environment to use (e.g., live|test)"""

    oauth: ConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuth

    resource: str
    """
    The resource to use for your various requests (e.g.,
    https://kyc-(live|test).adyen.com)
    """

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAdyenDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["adyen"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAdyenDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAircallDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAircallDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAircallDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAircallDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorAircallDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAircallDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["aircall"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAircallDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAmazonDiscriminatedConnectionSettingsSettings(BaseModel):
    extension: str
    """The domain extension for your Amazon account (e.g., com)"""

    oauth: ConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAmazonDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["amazon"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAmazonDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorApaleoDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorApaleoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["apaleo"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorApaleoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAsanaDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAsanaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["asana"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAsanaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAttioDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAttioDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAttioDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAttioDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorAttioDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAttioDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["attio"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAttioDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAuth0DiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your Auth0 account (e.g., https://domain.auth0.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAuth0DiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["auth0"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAuth0DiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAutodeskDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAutodeskDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["autodesk"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAutodeskDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAwsDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorAwsDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorAwsDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorAwsDiscriminatedConnectionSettingsSettings(BaseModel):
    api_subdomain: str = FieldInfo(alias="apiSubdomain")
    """
    The API subdomain to the API you want to connect to (e.g.,
    https://cognito-idp.us-east-2.amazonaws.com)
    """

    extension: str
    """The domain extension of your AWS account (e.g., com)"""

    oauth: ConnectorAwsDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your AWS account (e.g., https://domain.amazoncognito.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorAwsDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["aws"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAwsDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBamboohrDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your BambooHR account (e.g., https://domain.bamboohr.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBamboohrDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["bamboohr"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBamboohrDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBasecampDiscriminatedConnectionSettingsSettings(BaseModel):
    account_id: str = FieldInfo(alias="accountId")
    """Your Account ID (e.g., 5899981)"""

    app_details: str = FieldInfo(alias="appDetails")
    """The details of your app (e.g., example-subdomain)"""

    oauth: ConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBasecampDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["basecamp"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBasecampDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBattlenetDiscriminatedConnectionSettingsSettings(BaseModel):
    api_domain: str = FieldInfo(alias="apiDomain")
    """
    The domain to where you will access your API (e.g., https://us.api.blizzard.com)
    """

    extension: str
    """The domain extension of your Battle.net account (e.g., com)"""

    oauth: ConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBattlenetDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["battlenet"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBattlenetDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBigcommerceDiscriminatedConnectionSettingsSettings(BaseModel):
    account_uuid: str = FieldInfo(alias="accountUuid")
    """
    The account UUID of your BigCommerce account (e.g.,
    123e4567-e89b-12d3-a456-426614174000)
    """

    oauth: ConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuth

    store_hash: str = FieldInfo(alias="storeHash")
    """The store hash of your BigCommerce account (e.g., Example123)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBigcommerceDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["bigcommerce"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBigcommerceDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBitbucketDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBitbucketDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["bitbucket"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBitbucketDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBitlyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBitlyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["bitly"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBitlyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBlackbaudDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBlackbaudDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["blackbaud"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBlackbaudDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBoldsignDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBoldsignDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["boldsign"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBoldsignDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBoxDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBoxDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBoxDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBoxDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorBoxDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBoxDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["box"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBoxDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorBraintreeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorBraintreeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["braintree"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBraintreeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorCalendlyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorCalendlyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["calendly"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCalendlyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorClickupDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorClickupDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorClickupDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorClickupDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorClickupDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorClickupDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["clickup"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorClickupDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCloseDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorCloseDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorCloseDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorCloseDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorCloseDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorCloseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["close"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCloseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorConfluenceDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorConfluenceDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["confluence"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorConfluenceDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorContentfulDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your Contentful account (e.g., https://domain.contentful.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorContentfulDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["contentful"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorContentfulDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorContentstackDiscriminatedConnectionSettingsSettings(BaseModel):
    api_domain: str = FieldInfo(alias="apiDomain")
    """
    The domain to where you will access your API (e.g.,
    https://eu-api.contentstack.com)
    """

    app_id: str = FieldInfo(alias="appId")
    """The app ID of your Contentstack account (e.g., example-subdomain)"""

    oauth: ConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """
    The subdomain of your Contentstack account (e.g.,
    https://domain.contentstack.com)
    """

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorContentstackDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["contentstack"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorContentstackDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCopperDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorCopperDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorCopperDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorCopperDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorCopperDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorCopperDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["copper"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCopperDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCorosDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorCorosDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorCorosDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorCorosDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorCorosDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorCorosDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["coros"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCorosDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDatevDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorDatevDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorDatevDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorDatevDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorDatevDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDatevDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["datev"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDatevDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDeelDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorDeelDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorDeelDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorDeelDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorDeelDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDeelDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["deel"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDeelDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorDialpadDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDialpadDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["dialpad"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDialpadDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorDigitaloceanDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDigitaloceanDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["digitalocean"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDigitaloceanDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorDiscordDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDiscordDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["discord"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDiscordDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorDocusignDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDocusignDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["docusign"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDocusignDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorDropboxDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorDropboxDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["dropbox"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorDropboxDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEbayDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorEbayDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorEbayDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorEbayDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorEbayDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorEbayDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["ebay"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorEbayDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorEgnyteDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your Egnyte account (e.g., https://domain.egnyte.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorEgnyteDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["egnyte"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorEgnyteDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorEnvoyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorEnvoyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["envoy"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorEnvoyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorEventbriteDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorEventbriteDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["eventbrite"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorEventbriteDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorExistDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorExistDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorExistDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorExistDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorExistDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorExistDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["exist"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorExistDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorFacebookDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFacebookDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["facebook"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFacebookDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorFactorialDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFactorialDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["factorial"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFactorialDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorFigmaDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFigmaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["figma"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFigmaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorFitbitDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFitbitDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["fitbit"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFitbitDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorFortnoxDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFortnoxDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["fortnox"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFortnoxDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorFreshbooksDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFreshbooksDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["freshbooks"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFreshbooksDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFrontDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorFrontDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorFrontDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorFrontDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorFrontDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorFrontDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["front"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFrontDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGitHubDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGitHubDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["github"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGitHubDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGitlabDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGitlabDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gitlab"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGitlabDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGongDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGongDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGongDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGongDiscriminatedConnectionSettingsSettings(BaseModel):
    api_base_url_for_customer: str
    """The base URL of your Gong account (e.g., example)"""

    oauth: ConnectorGongDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGongDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gong"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGongDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleCalendarDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-calendar"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGoogleDocsDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleDocsDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-docs"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleDocsDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGoogleDriveDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleDriveDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-drive"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleDriveDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGoogleMailDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleMailDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-mail"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleMailDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGoogleSheetDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGoogleSheetDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["google-sheet"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGoogleSheetDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGorgiasDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your Gorgias account (e.g., https://domain.gorgias.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGorgiasDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gorgias"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGorgiasDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGrainDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGrainDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGrainDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGrainDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGrainDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGrainDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["grain"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGrainDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGumroadDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGumroadDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gumroad"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGumroadDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGustoDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorGustoDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorGustoDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorGustoDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorGustoDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorGustoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["gusto"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGustoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorHarvestDiscriminatedConnectionSettingsSettings(BaseModel):
    app_details: str = FieldInfo(alias="appDetails")
    """The details of your app (e.g., example-subdomain)"""

    oauth: ConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorHarvestDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["harvest"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorHarvestDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorHighlevelDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorHighlevelDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["highlevel"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorHighlevelDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorHubspotDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorHubspotDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["hubspot"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorHubspotDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorInstagramDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorInstagramDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["instagram"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorInstagramDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorIntercomDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorIntercomDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["intercom"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorIntercomDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorJiraDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorJiraDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorJiraDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorJiraDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorJiraDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorJiraDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["jira"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorJiraDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorKeapDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorKeapDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorKeapDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorKeapDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorKeapDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorKeapDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["keap"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorKeapDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLeverDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorLeverDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorLeverDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorLeverDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorLeverDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorLeverDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["lever"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorLeverDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLinearDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorLinearDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorLinearDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorLinearDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorLinearDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorLinearDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["linear"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorLinearDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorLinkedinDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorLinkedinDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["linkedin"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorLinkedinDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorLinkhutDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorLinkhutDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["linkhut"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorLinkhutDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorMailchimpDiscriminatedConnectionSettingsSettings(BaseModel):
    dc: str
    """The data center for your account (e.g., us6)"""

    oauth: ConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorMailchimpDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["mailchimp"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMailchimpDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMiroDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorMiroDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorMiroDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorMiroDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorMiroDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorMiroDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["miro"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMiroDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMondayDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorMondayDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorMondayDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorMondayDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorMondayDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorMondayDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["monday"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMondayDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMuralDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorMuralDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorMuralDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorMuralDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorMuralDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorMuralDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["mural"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMuralDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorNamelyDiscriminatedConnectionSettingsSettings(BaseModel):
    company: str
    """The name of your Namely company (e.g., example)"""

    oauth: ConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorNamelyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["namely"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorNamelyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorNationbuilderDiscriminatedConnectionSettingsSettings(BaseModel):
    account_id: str = FieldInfo(alias="accountId")
    """The account ID of your NationBuilder account (e.g., example-subdomain)"""

    oauth: ConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorNationbuilderDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["nationbuilder"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorNationbuilderDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorNetsuiteDiscriminatedConnectionSettingsSettings(BaseModel):
    account_id: str = FieldInfo(alias="accountId")
    """The account ID of your NetSuite account (e.g., tstdrv231585)"""

    oauth: ConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorNetsuiteDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["netsuite"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorNetsuiteDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorNotionDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorNotionDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorNotionDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorNotionDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorNotionDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorNotionDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["notion"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorNotionDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOdooDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorOdooDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorOdooDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorOdooDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorOdooDiscriminatedConnectionSettingsSettingsOAuth

    server_url: str = FieldInfo(alias="serverUrl")
    """The domain of your Odoo account (e.g., https://example-subdomain)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOdooDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["odoo"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOdooDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOktaDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorOktaDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorOktaDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorOktaDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorOktaDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your Okta account (e.g., https://domain.okta.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOktaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["okta"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOktaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOsuDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorOsuDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorOsuDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorOsuDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorOsuDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOsuDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["osu"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOsuDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOuraDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorOuraDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorOuraDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorOuraDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorOuraDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOuraDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["oura"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOuraDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorOutreachDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorOutreachDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["outreach"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOutreachDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorPagerdutyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPagerdutyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pagerduty"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPagerdutyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorPandadocDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPandadocDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pandadoc"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPandadocDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorPayfitDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPayfitDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["payfit"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPayfitDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorPaypalDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPaypalDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["paypal"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPaypalDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorPennylaneDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPennylaneDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pennylane"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPennylaneDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorPinterestDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPinterestDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pinterest"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPinterestDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorPipedriveDiscriminatedConnectionSettingsSettings(BaseModel):
    api_domain: str
    """The API URL of your Pipedrive account (e.g., example)"""

    oauth: ConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPipedriveDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["pipedrive"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPipedriveDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorPodiumDiscriminatedConnectionSettingsSettings(BaseModel):
    api_version: str = FieldInfo(alias="apiVersion")
    """The API version of your Podium account (e.g., example-subdomain)"""

    oauth: ConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorPodiumDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["podium"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPodiumDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorProductboardDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorProductboardDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["productboard"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorProductboardDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorQualtricsDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your Qualtrics account (e.g., https://domain.qualtrics.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorQualtricsDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["qualtrics"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorQualtricsDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorQuickbooksDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorQuickbooksDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["quickbooks"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorQuickbooksDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorRedditDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorRedditDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorRedditDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorRedditDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorRedditDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorRedditDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["reddit"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorRedditDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSageDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSageDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSageDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSageDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSageDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSageDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["sage"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSageDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSalesforceDiscriminatedConnectionSettingsSettings(BaseModel):
    instance_url: str
    """The instance URL of your Salesforce account (e.g., example)"""

    oauth: ConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSalesforceDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["salesforce"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSalesforceDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSalesloftDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSalesloftDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["salesloft"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSalesloftDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSegmentDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSegmentDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["segment"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSegmentDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorServicem8DiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorServicem8DiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["servicem8"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorServicem8DiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorServicenowDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your ServiceNow account (e.g., https://domain.service-now.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorServicenowDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["servicenow"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorServicenowDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSharepointDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSharepointDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["sharepoint"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSharepointDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorShopifyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your Shopify account (e.g., https://domain.myshopify.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorShopifyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["shopify"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorShopifyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSignnowDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSignnowDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["signnow"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSignnowDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSlackDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSlackDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSlackDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSlackDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSlackDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSlackDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["slack"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSlackDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSmartsheetDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSmartsheetDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["smartsheet"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSmartsheetDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSnowflakeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuth

    snowflake_account_url: str
    """The domain of your Snowflake account (e.g., https://example-subdomain)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSnowflakeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["snowflake"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSnowflakeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSpotifyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSpotifyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["spotify"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSpotifyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSquarespaceDiscriminatedConnectionSettingsSettings(BaseModel):
    customapp_description: str = FieldInfo(alias="customappDescription")
    """The user agent of your custom app (e.g., example-subdomain)"""

    oauth: ConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSquarespaceDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["squarespace"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSquarespaceDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorSquareupDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorSquareupDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["squareup"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSquareupDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorStackexchangeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorStackexchangeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["stackexchange"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorStackexchangeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorStravaDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorStravaDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorStravaDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorStravaDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorStravaDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorStravaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["strava"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorStravaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTeamworkDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTeamworkDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["teamwork"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTeamworkDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTicktickDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTicktickDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["ticktick"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTicktickDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTimelyDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTimelyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["timely"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTimelyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTodoistDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTodoistDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["todoist"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTodoistDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTremendousDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTremendousDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["tremendous"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTremendousDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTsheetsteamDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTsheetsteamDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["tsheetsteam"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTsheetsteamDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTumblrDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTumblrDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["tumblr"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTumblrDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTwinfieldDiscriminatedConnectionSettingsSettings(BaseModel):
    cluster: str
    """The cluster to your Twinfield instance (e.g., https://accounting.twinfield.com)"""

    oauth: ConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTwinfieldDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["twinfield"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTwinfieldDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTwitchDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTwitchDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["twitch"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTwitchDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTwitterDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTwitterDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["twitter"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTwitterDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorTypeformDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorTypeformDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["typeform"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTypeformDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorUberDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorUberDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorUberDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorUberDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorUberDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorUberDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["uber"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorUberDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorVimeoDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorVimeoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["vimeo"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorVimeoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorWakatimeDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWakatimeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wakatime"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWakatimeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorWealthboxDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWealthboxDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wealthbox"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWealthboxDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorWebflowDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWebflowDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["webflow"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWebflowDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorWhoopDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWhoopDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["whoop"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWhoopDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorWordpressDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWordpressDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wordpress"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWordpressDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorWrikeDiscriminatedConnectionSettingsSettings(BaseModel):
    host: str
    """The domain of your Wrike account (e.g., https://example-subdomain)"""

    oauth: ConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorWrikeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wrike"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWrikeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorXeroDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorXeroDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorXeroDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorXeroDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorXeroDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorXeroDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["xero"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorXeroDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorYahooDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorYahooDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorYahooDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorYahooDiscriminatedConnectionSettingsSettings(BaseModel):
    api_domain: str = FieldInfo(alias="apiDomain")
    """
    The domain to the API you want to connect to (e.g.,
    https://fantasysports.yahooapis.com)
    """

    oauth: ConnectorYahooDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorYahooDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["yahoo"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorYahooDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorYandexDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorYandexDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorYandexDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorYandexDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorYandexDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorYandexDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["yandex"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorYandexDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZapierDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorZapierDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorZapierDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorZapierDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorZapierDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZapierDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zapier"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZapierDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorZendeskDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuth

    subdomain: str
    """The subdomain of your Zendesk account (e.g., https://domain.zendesk.com)"""

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZendeskDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zendesk"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZendeskDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorZenefitsDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZenefitsDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zenefits"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZenefitsDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorZohoDeskDiscriminatedConnectionSettingsSettings(BaseModel):
    extension: str
    """The domain extension of your Zoho account (e.g., https://accounts.zoho.com/)"""

    oauth: ConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZohoDeskDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zoho-desk"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZohoDeskDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZohoDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorZohoDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorZohoDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorZohoDiscriminatedConnectionSettingsSettings(BaseModel):
    extension: str
    """The domain extension of your Zoho account (e.g., https://accounts.zoho.com/)"""

    oauth: ConnectorZohoDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZohoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zoho"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZohoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorZoomDiscriminatedConnectionSettingsSettingsOAuthCredentials(BaseModel):
    access_token: str

    client_id: Optional[str] = None
    """Client ID used for the connection"""

    expires_at: Optional[str] = None

    expires_in: Optional[float] = None

    raw: Optional[Dict[str, object]] = None

    refresh_token: Optional[str] = None

    scope: Optional[str] = None

    token_type: Optional[str] = None


class ConnectorZoomDiscriminatedConnectionSettingsSettingsOAuth(BaseModel):
    created_at: Optional[str] = None

    credentials: Optional[ConnectorZoomDiscriminatedConnectionSettingsSettingsOAuthCredentials] = None
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None

    updated_at: Optional[str] = None


class ConnectorZoomDiscriminatedConnectionSettingsSettings(BaseModel):
    oauth: ConnectorZoomDiscriminatedConnectionSettingsSettingsOAuth

    access_token: Optional[str] = None
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class ConnectorZoomDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["zoom"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorZoomDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorAirtableDiscriminatedConnectionSettingsSettings(BaseModel):
    airtable_base: str = FieldInfo(alias="airtableBase")

    api_key: str = FieldInfo(alias="apiKey")


class ConnectorAirtableDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["airtable"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorAirtableDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorApolloDiscriminatedConnectionSettingsSettings(BaseModel):
    api_key: str


class ConnectorApolloDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["apollo"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorApolloDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorBrexDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ConnectorBrexDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["brex"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorBrexDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorCodaDiscriminatedConnectionSettingsSettings(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorCodaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["coda"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorCodaDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFinchDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str


class ConnectorFinchDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["finch"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFinchDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount(BaseModel):
    project_id: str

    __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]
    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0(BaseModel):
    role: Literal["admin"]

    service_account: ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount = FieldInfo(
        alias="serviceAccount"
    )


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson(BaseModel):
    app_name: str = FieldInfo(alias="appName")

    sts_token_manager: Dict[str, object] = FieldInfo(alias="stsTokenManager")

    uid: str

    __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]
    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0(BaseModel):
    method: Literal["userJson"]

    user_json: ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson = (
        FieldInfo(alias="userJson")
    )


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1(BaseModel):
    custom_token: str = FieldInfo(alias="customToken")

    method: Literal["customToken"]


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2(BaseModel):
    email: str

    method: Literal["emailPassword"]

    password: str


ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData: TypeAlias = Union[
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0,
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1,
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2,
]


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")

    app_id: str = FieldInfo(alias="appId")

    auth_domain: str = FieldInfo(alias="authDomain")

    database_url: str = FieldInfo(alias="databaseURL")

    project_id: str = FieldInfo(alias="projectId")

    measurement_id: Optional[str] = FieldInfo(alias="measurementId", default=None)

    messaging_sender_id: Optional[str] = FieldInfo(alias="messagingSenderId", default=None)

    storage_bucket: Optional[str] = FieldInfo(alias="storageBucket", default=None)


class ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1(BaseModel):
    auth_data: ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData = FieldInfo(
        alias="authData"
    )

    firebase_config: ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig = FieldInfo(
        alias="firebaseConfig"
    )

    role: Literal["user"]


ConnectorFirebaseDiscriminatedConnectionSettingsSettings: TypeAlias = Union[
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0,
    ConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1,
]


class ConnectorFirebaseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["firebase"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorFirebaseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorForeceiptDiscriminatedConnectionSettingsSettings(BaseModel):
    env_name: Literal["staging", "production"] = FieldInfo(alias="envName")

    api_id: Optional[object] = FieldInfo(alias="_id", default=None)

    credentials: Optional[object] = None


class ConnectorForeceiptDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["foreceipt"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorForeceiptDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorGreenhouseDiscriminatedConnectionSettingsSettings(BaseModel):
    api_key: str = FieldInfo(alias="apiKey")


class ConnectorGreenhouseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["greenhouse"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorGreenhouseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorHeronDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["heron"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorLunchmoneyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["lunchmoney"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMercuryDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["mercury"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMergeDiscriminatedConnectionSettingsSettings(BaseModel):
    account_token: str = FieldInfo(alias="accountToken")

    account_details: Optional[object] = FieldInfo(alias="accountDetails", default=None)


class ConnectorMergeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["merge"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorMergeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorMootaDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["moota"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOnebrickDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")


class ConnectorOnebrickDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["onebrick"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOnebrickDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorOpenledgerDiscriminatedConnectionSettingsSettings(BaseModel):
    entity_id: str
    """Your entity's identifier, aka customer ID"""


class ConnectorOpenledgerDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["openledger"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorOpenledgerDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPlaidDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    institution: Optional[object] = None

    item: Optional[object] = None

    item_id: Optional[str] = FieldInfo(alias="itemId", default=None)

    status: Optional[object] = None

    webhook_item_error: None = FieldInfo(alias="webhookItemError", default=None)


class ConnectorPlaidDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["plaid"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPlaidDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorPostgresDiscriminatedConnectionSettingsSettings(BaseModel):
    database_url: Optional[str] = FieldInfo(alias="databaseURL", default=None)


class ConnectorPostgresDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["postgres"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorPostgresDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorRampDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: Optional[str] = FieldInfo(alias="accessToken", default=None)

    start_after_transaction_id: Optional[str] = FieldInfo(alias="startAfterTransactionId", default=None)


class ConnectorRampDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["ramp"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorRampDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSaltedgeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["saltedge"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[object] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSharepointOnpremDiscriminatedConnectionSettingsSettings(BaseModel):
    password: str

    site_url: str

    username: str


class ConnectorSharepointOnpremDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["sharepoint-onprem"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSharepointOnpremDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications(BaseModel):
    added_as_friend: bool

    added_to_group: bool

    announcements: bool

    bills: bool

    expense_added: bool

    expense_updated: bool

    monthly_summary: bool

    payments: bool


class ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture(BaseModel):
    large: Optional[str] = None

    medium: Optional[str] = None

    original: Optional[str] = None

    small: Optional[str] = None

    xlarge: Optional[str] = None

    xxlarge: Optional[str] = None


class ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser(BaseModel):
    id: float

    country_code: str

    custom_picture: bool

    date_format: str

    default_currency: str

    default_group_id: float

    email: str

    first_name: str

    force_refresh_at: str

    last_name: str

    locale: str

    notifications: ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications

    notifications_count: float

    notifications_read: str

    picture: ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture

    registration_status: str


class ConnectorSplitwiseDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    current_user: Optional[ConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser] = FieldInfo(
        alias="currentUser", default=None
    )


class ConnectorSplitwiseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["splitwise"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorSplitwiseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorStripeDiscriminatedConnectionSettingsSettings(BaseModel):
    secret_key: str = FieldInfo(alias="secretKey")


class ConnectorStripeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["stripe"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorStripeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTellerDiscriminatedConnectionSettingsSettings(BaseModel):
    token: str


class ConnectorTellerDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["teller"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTellerDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTogglDiscriminatedConnectionSettingsSettings(BaseModel):
    api_token: str = FieldInfo(alias="apiToken")

    email: Optional[str] = None

    password: Optional[str] = None


class ConnectorTogglDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["toggl"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTogglDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorTwentyDiscriminatedConnectionSettingsSettings(BaseModel):
    access_token: str


class ConnectorTwentyDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["twenty"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorTwentyDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorVenmoDiscriminatedConnectionSettingsSettings(BaseModel):
    credentials: Optional[object] = None

    me: Optional[object] = None


class ConnectorVenmoDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["venmo"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorVenmoDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorWiseDiscriminatedConnectionSettingsSettings(BaseModel):
    env_name: Literal["sandbox", "live"] = FieldInfo(alias="envName")

    api_token: Optional[str] = FieldInfo(alias="apiToken", default=None)


class ConnectorWiseDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["wise"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorWiseDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


class ConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken(BaseModel):
    access_token: str = FieldInfo(alias="accessToken")

    expires_in: float = FieldInfo(alias="expiresIn")

    issued_at: str = FieldInfo(alias="issuedAt")


class ConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount(BaseModel):
    id: float

    aggregation_source: str = FieldInfo(alias="aggregationSource")

    created_date: str = FieldInfo(alias="createdDate")

    dataset: List[object]

    is_manual: bool = FieldInfo(alias="isManual")

    provider_id: float = FieldInfo(alias="providerId")

    status: Literal["LOGIN_IN_PROGRESS", "USER_INPUT_REQUIRED", "IN_PROGRESS", "PARTIAL_SUCCESS", "SUCCESS", "FAILED"]

    is_deleted: Optional[bool] = FieldInfo(alias="isDeleted", default=None)


class ConnectorYodleeDiscriminatedConnectionSettingsSettings(BaseModel):
    login_name: str = FieldInfo(alias="loginName")

    provider_account_id: Union[float, str] = FieldInfo(alias="providerAccountId")

    access_token: Optional[ConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken] = FieldInfo(
        alias="accessToken", default=None
    )

    provider: None = None

    provider_account: Optional[ConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount] = FieldInfo(
        alias="providerAccount", default=None
    )

    user: None = None


class ConnectorYodleeDiscriminatedConnectionSettings(BaseModel):
    connector_name: Literal["yodlee"]

    id: Optional[str] = None

    connector: Optional[Connector] = None

    connector_config_id: Optional[str] = None

    created_at: Optional[str] = None

    customer_id: Optional[str] = None

    disabled: Optional[bool] = None

    display_name: Optional[str] = None

    integration: Optional[Integration] = None

    integration_id: Optional[str] = None

    metadata: Optional[Dict[str, object]] = None
    """
    JSON object can can be used to associate arbitrary metadata to avoid needing a
    separate 1-1 table just for simple key values in your application. During
    updates this object will be shallowly merged
    """

    settings: Optional[ConnectorYodleeDiscriminatedConnectionSettingsSettings] = None

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None

    updated_at: Optional[str] = None


GetConnectionResponse: TypeAlias = Union[
    ConnectorAcceloDiscriminatedConnectionSettings,
    ConnectorAcmeApikeyDiscriminatedConnectionSettings,
    ConnectorAcmeOauth2DiscriminatedConnectionSettings,
    ConnectorAdobeDiscriminatedConnectionSettings,
    ConnectorAdyenDiscriminatedConnectionSettings,
    ConnectorAircallDiscriminatedConnectionSettings,
    ConnectorAmazonDiscriminatedConnectionSettings,
    ConnectorApaleoDiscriminatedConnectionSettings,
    ConnectorAsanaDiscriminatedConnectionSettings,
    ConnectorAttioDiscriminatedConnectionSettings,
    ConnectorAuth0DiscriminatedConnectionSettings,
    ConnectorAutodeskDiscriminatedConnectionSettings,
    ConnectorAwsDiscriminatedConnectionSettings,
    ConnectorBamboohrDiscriminatedConnectionSettings,
    ConnectorBasecampDiscriminatedConnectionSettings,
    ConnectorBattlenetDiscriminatedConnectionSettings,
    ConnectorBigcommerceDiscriminatedConnectionSettings,
    ConnectorBitbucketDiscriminatedConnectionSettings,
    ConnectorBitlyDiscriminatedConnectionSettings,
    ConnectorBlackbaudDiscriminatedConnectionSettings,
    ConnectorBoldsignDiscriminatedConnectionSettings,
    ConnectorBoxDiscriminatedConnectionSettings,
    ConnectorBraintreeDiscriminatedConnectionSettings,
    ConnectorCalendlyDiscriminatedConnectionSettings,
    ConnectorClickupDiscriminatedConnectionSettings,
    ConnectorCloseDiscriminatedConnectionSettings,
    ConnectorConfluenceDiscriminatedConnectionSettings,
    ConnectorContentfulDiscriminatedConnectionSettings,
    ConnectorContentstackDiscriminatedConnectionSettings,
    ConnectorCopperDiscriminatedConnectionSettings,
    ConnectorCorosDiscriminatedConnectionSettings,
    ConnectorDatevDiscriminatedConnectionSettings,
    ConnectorDeelDiscriminatedConnectionSettings,
    ConnectorDialpadDiscriminatedConnectionSettings,
    ConnectorDigitaloceanDiscriminatedConnectionSettings,
    ConnectorDiscordDiscriminatedConnectionSettings,
    ConnectorDocusignDiscriminatedConnectionSettings,
    ConnectorDropboxDiscriminatedConnectionSettings,
    ConnectorEbayDiscriminatedConnectionSettings,
    ConnectorEgnyteDiscriminatedConnectionSettings,
    ConnectorEnvoyDiscriminatedConnectionSettings,
    ConnectorEventbriteDiscriminatedConnectionSettings,
    ConnectorExistDiscriminatedConnectionSettings,
    ConnectorFacebookDiscriminatedConnectionSettings,
    ConnectorFactorialDiscriminatedConnectionSettings,
    ConnectorFigmaDiscriminatedConnectionSettings,
    ConnectorFitbitDiscriminatedConnectionSettings,
    ConnectorFortnoxDiscriminatedConnectionSettings,
    ConnectorFreshbooksDiscriminatedConnectionSettings,
    ConnectorFrontDiscriminatedConnectionSettings,
    ConnectorGitHubDiscriminatedConnectionSettings,
    ConnectorGitlabDiscriminatedConnectionSettings,
    ConnectorGongDiscriminatedConnectionSettings,
    ConnectorGoogleCalendarDiscriminatedConnectionSettings,
    ConnectorGoogleDocsDiscriminatedConnectionSettings,
    ConnectorGoogleDriveDiscriminatedConnectionSettings,
    ConnectorGoogleMailDiscriminatedConnectionSettings,
    ConnectorGoogleSheetDiscriminatedConnectionSettings,
    ConnectorGorgiasDiscriminatedConnectionSettings,
    ConnectorGrainDiscriminatedConnectionSettings,
    ConnectorGumroadDiscriminatedConnectionSettings,
    ConnectorGustoDiscriminatedConnectionSettings,
    ConnectorHarvestDiscriminatedConnectionSettings,
    ConnectorHighlevelDiscriminatedConnectionSettings,
    ConnectorHubspotDiscriminatedConnectionSettings,
    ConnectorInstagramDiscriminatedConnectionSettings,
    ConnectorIntercomDiscriminatedConnectionSettings,
    ConnectorJiraDiscriminatedConnectionSettings,
    ConnectorKeapDiscriminatedConnectionSettings,
    ConnectorLeverDiscriminatedConnectionSettings,
    ConnectorLinearDiscriminatedConnectionSettings,
    ConnectorLinkedinDiscriminatedConnectionSettings,
    ConnectorLinkhutDiscriminatedConnectionSettings,
    ConnectorMailchimpDiscriminatedConnectionSettings,
    ConnectorMiroDiscriminatedConnectionSettings,
    ConnectorMondayDiscriminatedConnectionSettings,
    ConnectorMuralDiscriminatedConnectionSettings,
    ConnectorNamelyDiscriminatedConnectionSettings,
    ConnectorNationbuilderDiscriminatedConnectionSettings,
    ConnectorNetsuiteDiscriminatedConnectionSettings,
    ConnectorNotionDiscriminatedConnectionSettings,
    ConnectorOdooDiscriminatedConnectionSettings,
    ConnectorOktaDiscriminatedConnectionSettings,
    ConnectorOsuDiscriminatedConnectionSettings,
    ConnectorOuraDiscriminatedConnectionSettings,
    ConnectorOutreachDiscriminatedConnectionSettings,
    ConnectorPagerdutyDiscriminatedConnectionSettings,
    ConnectorPandadocDiscriminatedConnectionSettings,
    ConnectorPayfitDiscriminatedConnectionSettings,
    ConnectorPaypalDiscriminatedConnectionSettings,
    ConnectorPennylaneDiscriminatedConnectionSettings,
    ConnectorPinterestDiscriminatedConnectionSettings,
    ConnectorPipedriveDiscriminatedConnectionSettings,
    ConnectorPodiumDiscriminatedConnectionSettings,
    ConnectorProductboardDiscriminatedConnectionSettings,
    ConnectorQualtricsDiscriminatedConnectionSettings,
    ConnectorQuickbooksDiscriminatedConnectionSettings,
    ConnectorRedditDiscriminatedConnectionSettings,
    ConnectorSageDiscriminatedConnectionSettings,
    ConnectorSalesforceDiscriminatedConnectionSettings,
    ConnectorSalesloftDiscriminatedConnectionSettings,
    ConnectorSegmentDiscriminatedConnectionSettings,
    ConnectorServicem8DiscriminatedConnectionSettings,
    ConnectorServicenowDiscriminatedConnectionSettings,
    ConnectorSharepointDiscriminatedConnectionSettings,
    ConnectorShopifyDiscriminatedConnectionSettings,
    ConnectorSignnowDiscriminatedConnectionSettings,
    ConnectorSlackDiscriminatedConnectionSettings,
    ConnectorSmartsheetDiscriminatedConnectionSettings,
    ConnectorSnowflakeDiscriminatedConnectionSettings,
    ConnectorSpotifyDiscriminatedConnectionSettings,
    ConnectorSquarespaceDiscriminatedConnectionSettings,
    ConnectorSquareupDiscriminatedConnectionSettings,
    ConnectorStackexchangeDiscriminatedConnectionSettings,
    ConnectorStravaDiscriminatedConnectionSettings,
    ConnectorTeamworkDiscriminatedConnectionSettings,
    ConnectorTicktickDiscriminatedConnectionSettings,
    ConnectorTimelyDiscriminatedConnectionSettings,
    ConnectorTodoistDiscriminatedConnectionSettings,
    ConnectorTremendousDiscriminatedConnectionSettings,
    ConnectorTsheetsteamDiscriminatedConnectionSettings,
    ConnectorTumblrDiscriminatedConnectionSettings,
    ConnectorTwinfieldDiscriminatedConnectionSettings,
    ConnectorTwitchDiscriminatedConnectionSettings,
    ConnectorTwitterDiscriminatedConnectionSettings,
    ConnectorTypeformDiscriminatedConnectionSettings,
    ConnectorUberDiscriminatedConnectionSettings,
    ConnectorVimeoDiscriminatedConnectionSettings,
    ConnectorWakatimeDiscriminatedConnectionSettings,
    ConnectorWealthboxDiscriminatedConnectionSettings,
    ConnectorWebflowDiscriminatedConnectionSettings,
    ConnectorWhoopDiscriminatedConnectionSettings,
    ConnectorWordpressDiscriminatedConnectionSettings,
    ConnectorWrikeDiscriminatedConnectionSettings,
    ConnectorXeroDiscriminatedConnectionSettings,
    ConnectorYahooDiscriminatedConnectionSettings,
    ConnectorYandexDiscriminatedConnectionSettings,
    ConnectorZapierDiscriminatedConnectionSettings,
    ConnectorZendeskDiscriminatedConnectionSettings,
    ConnectorZenefitsDiscriminatedConnectionSettings,
    ConnectorZohoDeskDiscriminatedConnectionSettings,
    ConnectorZohoDiscriminatedConnectionSettings,
    ConnectorZoomDiscriminatedConnectionSettings,
    ConnectorAirtableDiscriminatedConnectionSettings,
    ConnectorApolloDiscriminatedConnectionSettings,
    ConnectorBrexDiscriminatedConnectionSettings,
    ConnectorCodaDiscriminatedConnectionSettings,
    ConnectorFinchDiscriminatedConnectionSettings,
    ConnectorFirebaseDiscriminatedConnectionSettings,
    ConnectorForeceiptDiscriminatedConnectionSettings,
    ConnectorGreenhouseDiscriminatedConnectionSettings,
    ConnectorHeronDiscriminatedConnectionSettings,
    ConnectorLunchmoneyDiscriminatedConnectionSettings,
    ConnectorMercuryDiscriminatedConnectionSettings,
    ConnectorMergeDiscriminatedConnectionSettings,
    ConnectorMootaDiscriminatedConnectionSettings,
    ConnectorOnebrickDiscriminatedConnectionSettings,
    ConnectorOpenledgerDiscriminatedConnectionSettings,
    ConnectorPlaidDiscriminatedConnectionSettings,
    ConnectorPostgresDiscriminatedConnectionSettings,
    ConnectorRampDiscriminatedConnectionSettings,
    ConnectorSaltedgeDiscriminatedConnectionSettings,
    ConnectorSharepointOnpremDiscriminatedConnectionSettings,
    ConnectorSplitwiseDiscriminatedConnectionSettings,
    ConnectorStripeDiscriminatedConnectionSettings,
    ConnectorTellerDiscriminatedConnectionSettings,
    ConnectorTogglDiscriminatedConnectionSettings,
    ConnectorTwentyDiscriminatedConnectionSettings,
    ConnectorVenmoDiscriminatedConnectionSettings,
    ConnectorWiseDiscriminatedConnectionSettings,
    ConnectorYodleeDiscriminatedConnectionSettings,
]
