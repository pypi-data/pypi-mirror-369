# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "ClientCreateConnectionParams",
    "Data",
    "DataConnectorAcceloDiscriminatedConnectionSettings",
    "DataConnectorAcceloDiscriminatedConnectionSettingsSettings",
    "DataConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAcmeApikeyDiscriminatedConnectionSettings",
    "DataConnectorAcmeApikeyDiscriminatedConnectionSettingsSettings",
    "DataConnectorAcmeOauth2DiscriminatedConnectionSettings",
    "DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings",
    "DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAdobeDiscriminatedConnectionSettings",
    "DataConnectorAdobeDiscriminatedConnectionSettingsSettings",
    "DataConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAdyenDiscriminatedConnectionSettings",
    "DataConnectorAdyenDiscriminatedConnectionSettingsSettings",
    "DataConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAircallDiscriminatedConnectionSettings",
    "DataConnectorAircallDiscriminatedConnectionSettingsSettings",
    "DataConnectorAircallDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAircallDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAmazonDiscriminatedConnectionSettings",
    "DataConnectorAmazonDiscriminatedConnectionSettingsSettings",
    "DataConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorApaleoDiscriminatedConnectionSettings",
    "DataConnectorApaleoDiscriminatedConnectionSettingsSettings",
    "DataConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAsanaDiscriminatedConnectionSettings",
    "DataConnectorAsanaDiscriminatedConnectionSettingsSettings",
    "DataConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAttioDiscriminatedConnectionSettings",
    "DataConnectorAttioDiscriminatedConnectionSettingsSettings",
    "DataConnectorAttioDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAttioDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAuth0DiscriminatedConnectionSettings",
    "DataConnectorAuth0DiscriminatedConnectionSettingsSettings",
    "DataConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAutodeskDiscriminatedConnectionSettings",
    "DataConnectorAutodeskDiscriminatedConnectionSettingsSettings",
    "DataConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAwsDiscriminatedConnectionSettings",
    "DataConnectorAwsDiscriminatedConnectionSettingsSettings",
    "DataConnectorAwsDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorAwsDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBamboohrDiscriminatedConnectionSettings",
    "DataConnectorBamboohrDiscriminatedConnectionSettingsSettings",
    "DataConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBasecampDiscriminatedConnectionSettings",
    "DataConnectorBasecampDiscriminatedConnectionSettingsSettings",
    "DataConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBattlenetDiscriminatedConnectionSettings",
    "DataConnectorBattlenetDiscriminatedConnectionSettingsSettings",
    "DataConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBigcommerceDiscriminatedConnectionSettings",
    "DataConnectorBigcommerceDiscriminatedConnectionSettingsSettings",
    "DataConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBitbucketDiscriminatedConnectionSettings",
    "DataConnectorBitbucketDiscriminatedConnectionSettingsSettings",
    "DataConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBitlyDiscriminatedConnectionSettings",
    "DataConnectorBitlyDiscriminatedConnectionSettingsSettings",
    "DataConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBlackbaudDiscriminatedConnectionSettings",
    "DataConnectorBlackbaudDiscriminatedConnectionSettingsSettings",
    "DataConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBoldsignDiscriminatedConnectionSettings",
    "DataConnectorBoldsignDiscriminatedConnectionSettingsSettings",
    "DataConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBoxDiscriminatedConnectionSettings",
    "DataConnectorBoxDiscriminatedConnectionSettingsSettings",
    "DataConnectorBoxDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBoxDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorBraintreeDiscriminatedConnectionSettings",
    "DataConnectorBraintreeDiscriminatedConnectionSettingsSettings",
    "DataConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorCalendlyDiscriminatedConnectionSettings",
    "DataConnectorCalendlyDiscriminatedConnectionSettingsSettings",
    "DataConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorClickupDiscriminatedConnectionSettings",
    "DataConnectorClickupDiscriminatedConnectionSettingsSettings",
    "DataConnectorClickupDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorClickupDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorCloseDiscriminatedConnectionSettings",
    "DataConnectorCloseDiscriminatedConnectionSettingsSettings",
    "DataConnectorCloseDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorCloseDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorConfluenceDiscriminatedConnectionSettings",
    "DataConnectorConfluenceDiscriminatedConnectionSettingsSettings",
    "DataConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorContentfulDiscriminatedConnectionSettings",
    "DataConnectorContentfulDiscriminatedConnectionSettingsSettings",
    "DataConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorContentstackDiscriminatedConnectionSettings",
    "DataConnectorContentstackDiscriminatedConnectionSettingsSettings",
    "DataConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorCopperDiscriminatedConnectionSettings",
    "DataConnectorCopperDiscriminatedConnectionSettingsSettings",
    "DataConnectorCopperDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorCopperDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorCorosDiscriminatedConnectionSettings",
    "DataConnectorCorosDiscriminatedConnectionSettingsSettings",
    "DataConnectorCorosDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorCorosDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorDatevDiscriminatedConnectionSettings",
    "DataConnectorDatevDiscriminatedConnectionSettingsSettings",
    "DataConnectorDatevDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorDatevDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorDeelDiscriminatedConnectionSettings",
    "DataConnectorDeelDiscriminatedConnectionSettingsSettings",
    "DataConnectorDeelDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorDeelDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorDialpadDiscriminatedConnectionSettings",
    "DataConnectorDialpadDiscriminatedConnectionSettingsSettings",
    "DataConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorDigitaloceanDiscriminatedConnectionSettings",
    "DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettings",
    "DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorDiscordDiscriminatedConnectionSettings",
    "DataConnectorDiscordDiscriminatedConnectionSettingsSettings",
    "DataConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorDocusignDiscriminatedConnectionSettings",
    "DataConnectorDocusignDiscriminatedConnectionSettingsSettings",
    "DataConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorDropboxDiscriminatedConnectionSettings",
    "DataConnectorDropboxDiscriminatedConnectionSettingsSettings",
    "DataConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorEbayDiscriminatedConnectionSettings",
    "DataConnectorEbayDiscriminatedConnectionSettingsSettings",
    "DataConnectorEbayDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorEbayDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorEgnyteDiscriminatedConnectionSettings",
    "DataConnectorEgnyteDiscriminatedConnectionSettingsSettings",
    "DataConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorEnvoyDiscriminatedConnectionSettings",
    "DataConnectorEnvoyDiscriminatedConnectionSettingsSettings",
    "DataConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorEventbriteDiscriminatedConnectionSettings",
    "DataConnectorEventbriteDiscriminatedConnectionSettingsSettings",
    "DataConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorExistDiscriminatedConnectionSettings",
    "DataConnectorExistDiscriminatedConnectionSettingsSettings",
    "DataConnectorExistDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorExistDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorFacebookDiscriminatedConnectionSettings",
    "DataConnectorFacebookDiscriminatedConnectionSettingsSettings",
    "DataConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorFactorialDiscriminatedConnectionSettings",
    "DataConnectorFactorialDiscriminatedConnectionSettingsSettings",
    "DataConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorFigmaDiscriminatedConnectionSettings",
    "DataConnectorFigmaDiscriminatedConnectionSettingsSettings",
    "DataConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorFitbitDiscriminatedConnectionSettings",
    "DataConnectorFitbitDiscriminatedConnectionSettingsSettings",
    "DataConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorFortnoxDiscriminatedConnectionSettings",
    "DataConnectorFortnoxDiscriminatedConnectionSettingsSettings",
    "DataConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorFreshbooksDiscriminatedConnectionSettings",
    "DataConnectorFreshbooksDiscriminatedConnectionSettingsSettings",
    "DataConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorFrontDiscriminatedConnectionSettings",
    "DataConnectorFrontDiscriminatedConnectionSettingsSettings",
    "DataConnectorFrontDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorFrontDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGitHubDiscriminatedConnectionSettings",
    "DataConnectorGitHubDiscriminatedConnectionSettingsSettings",
    "DataConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGitlabDiscriminatedConnectionSettings",
    "DataConnectorGitlabDiscriminatedConnectionSettingsSettings",
    "DataConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGongDiscriminatedConnectionSettings",
    "DataConnectorGongDiscriminatedConnectionSettingsSettings",
    "DataConnectorGongDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGongDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGoogleCalendarDiscriminatedConnectionSettings",
    "DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGoogleDocsDiscriminatedConnectionSettings",
    "DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGoogleDriveDiscriminatedConnectionSettings",
    "DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGoogleMailDiscriminatedConnectionSettings",
    "DataConnectorGoogleMailDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGoogleSheetDiscriminatedConnectionSettings",
    "DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettings",
    "DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGorgiasDiscriminatedConnectionSettings",
    "DataConnectorGorgiasDiscriminatedConnectionSettingsSettings",
    "DataConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGrainDiscriminatedConnectionSettings",
    "DataConnectorGrainDiscriminatedConnectionSettingsSettings",
    "DataConnectorGrainDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGrainDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGumroadDiscriminatedConnectionSettings",
    "DataConnectorGumroadDiscriminatedConnectionSettingsSettings",
    "DataConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorGustoDiscriminatedConnectionSettings",
    "DataConnectorGustoDiscriminatedConnectionSettingsSettings",
    "DataConnectorGustoDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorGustoDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorHarvestDiscriminatedConnectionSettings",
    "DataConnectorHarvestDiscriminatedConnectionSettingsSettings",
    "DataConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorHighlevelDiscriminatedConnectionSettings",
    "DataConnectorHighlevelDiscriminatedConnectionSettingsSettings",
    "DataConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorHubspotDiscriminatedConnectionSettings",
    "DataConnectorHubspotDiscriminatedConnectionSettingsSettings",
    "DataConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorInstagramDiscriminatedConnectionSettings",
    "DataConnectorInstagramDiscriminatedConnectionSettingsSettings",
    "DataConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorIntercomDiscriminatedConnectionSettings",
    "DataConnectorIntercomDiscriminatedConnectionSettingsSettings",
    "DataConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorJiraDiscriminatedConnectionSettings",
    "DataConnectorJiraDiscriminatedConnectionSettingsSettings",
    "DataConnectorJiraDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorJiraDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorKeapDiscriminatedConnectionSettings",
    "DataConnectorKeapDiscriminatedConnectionSettingsSettings",
    "DataConnectorKeapDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorKeapDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorLeverDiscriminatedConnectionSettings",
    "DataConnectorLeverDiscriminatedConnectionSettingsSettings",
    "DataConnectorLeverDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorLeverDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorLinearDiscriminatedConnectionSettings",
    "DataConnectorLinearDiscriminatedConnectionSettingsSettings",
    "DataConnectorLinearDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorLinearDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorLinkedinDiscriminatedConnectionSettings",
    "DataConnectorLinkedinDiscriminatedConnectionSettingsSettings",
    "DataConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorLinkhutDiscriminatedConnectionSettings",
    "DataConnectorLinkhutDiscriminatedConnectionSettingsSettings",
    "DataConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorMailchimpDiscriminatedConnectionSettings",
    "DataConnectorMailchimpDiscriminatedConnectionSettingsSettings",
    "DataConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorMiroDiscriminatedConnectionSettings",
    "DataConnectorMiroDiscriminatedConnectionSettingsSettings",
    "DataConnectorMiroDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorMiroDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorMondayDiscriminatedConnectionSettings",
    "DataConnectorMondayDiscriminatedConnectionSettingsSettings",
    "DataConnectorMondayDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorMondayDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorMuralDiscriminatedConnectionSettings",
    "DataConnectorMuralDiscriminatedConnectionSettingsSettings",
    "DataConnectorMuralDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorMuralDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorNamelyDiscriminatedConnectionSettings",
    "DataConnectorNamelyDiscriminatedConnectionSettingsSettings",
    "DataConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorNationbuilderDiscriminatedConnectionSettings",
    "DataConnectorNationbuilderDiscriminatedConnectionSettingsSettings",
    "DataConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorNetsuiteDiscriminatedConnectionSettings",
    "DataConnectorNetsuiteDiscriminatedConnectionSettingsSettings",
    "DataConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorNotionDiscriminatedConnectionSettings",
    "DataConnectorNotionDiscriminatedConnectionSettingsSettings",
    "DataConnectorNotionDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorNotionDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorOdooDiscriminatedConnectionSettings",
    "DataConnectorOdooDiscriminatedConnectionSettingsSettings",
    "DataConnectorOdooDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorOdooDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorOktaDiscriminatedConnectionSettings",
    "DataConnectorOktaDiscriminatedConnectionSettingsSettings",
    "DataConnectorOktaDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorOktaDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorOsuDiscriminatedConnectionSettings",
    "DataConnectorOsuDiscriminatedConnectionSettingsSettings",
    "DataConnectorOsuDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorOsuDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorOuraDiscriminatedConnectionSettings",
    "DataConnectorOuraDiscriminatedConnectionSettingsSettings",
    "DataConnectorOuraDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorOuraDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorOutreachDiscriminatedConnectionSettings",
    "DataConnectorOutreachDiscriminatedConnectionSettingsSettings",
    "DataConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorPagerdutyDiscriminatedConnectionSettings",
    "DataConnectorPagerdutyDiscriminatedConnectionSettingsSettings",
    "DataConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorPandadocDiscriminatedConnectionSettings",
    "DataConnectorPandadocDiscriminatedConnectionSettingsSettings",
    "DataConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorPayfitDiscriminatedConnectionSettings",
    "DataConnectorPayfitDiscriminatedConnectionSettingsSettings",
    "DataConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorPaypalDiscriminatedConnectionSettings",
    "DataConnectorPaypalDiscriminatedConnectionSettingsSettings",
    "DataConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorPennylaneDiscriminatedConnectionSettings",
    "DataConnectorPennylaneDiscriminatedConnectionSettingsSettings",
    "DataConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorPinterestDiscriminatedConnectionSettings",
    "DataConnectorPinterestDiscriminatedConnectionSettingsSettings",
    "DataConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorPipedriveDiscriminatedConnectionSettings",
    "DataConnectorPipedriveDiscriminatedConnectionSettingsSettings",
    "DataConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorPodiumDiscriminatedConnectionSettings",
    "DataConnectorPodiumDiscriminatedConnectionSettingsSettings",
    "DataConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorProductboardDiscriminatedConnectionSettings",
    "DataConnectorProductboardDiscriminatedConnectionSettingsSettings",
    "DataConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorQualtricsDiscriminatedConnectionSettings",
    "DataConnectorQualtricsDiscriminatedConnectionSettingsSettings",
    "DataConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorQuickbooksDiscriminatedConnectionSettings",
    "DataConnectorQuickbooksDiscriminatedConnectionSettingsSettings",
    "DataConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorRedditDiscriminatedConnectionSettings",
    "DataConnectorRedditDiscriminatedConnectionSettingsSettings",
    "DataConnectorRedditDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorRedditDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSageDiscriminatedConnectionSettings",
    "DataConnectorSageDiscriminatedConnectionSettingsSettings",
    "DataConnectorSageDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSageDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSalesforceDiscriminatedConnectionSettings",
    "DataConnectorSalesforceDiscriminatedConnectionSettingsSettings",
    "DataConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSalesloftDiscriminatedConnectionSettings",
    "DataConnectorSalesloftDiscriminatedConnectionSettingsSettings",
    "DataConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSegmentDiscriminatedConnectionSettings",
    "DataConnectorSegmentDiscriminatedConnectionSettingsSettings",
    "DataConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorServicem8DiscriminatedConnectionSettings",
    "DataConnectorServicem8DiscriminatedConnectionSettingsSettings",
    "DataConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorServicenowDiscriminatedConnectionSettings",
    "DataConnectorServicenowDiscriminatedConnectionSettingsSettings",
    "DataConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSharepointDiscriminatedConnectionSettings",
    "DataConnectorSharepointDiscriminatedConnectionSettingsSettings",
    "DataConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorShopifyDiscriminatedConnectionSettings",
    "DataConnectorShopifyDiscriminatedConnectionSettingsSettings",
    "DataConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSignnowDiscriminatedConnectionSettings",
    "DataConnectorSignnowDiscriminatedConnectionSettingsSettings",
    "DataConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSlackDiscriminatedConnectionSettings",
    "DataConnectorSlackDiscriminatedConnectionSettingsSettings",
    "DataConnectorSlackDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSlackDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSmartsheetDiscriminatedConnectionSettings",
    "DataConnectorSmartsheetDiscriminatedConnectionSettingsSettings",
    "DataConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSnowflakeDiscriminatedConnectionSettings",
    "DataConnectorSnowflakeDiscriminatedConnectionSettingsSettings",
    "DataConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSpotifyDiscriminatedConnectionSettings",
    "DataConnectorSpotifyDiscriminatedConnectionSettingsSettings",
    "DataConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSquarespaceDiscriminatedConnectionSettings",
    "DataConnectorSquarespaceDiscriminatedConnectionSettingsSettings",
    "DataConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorSquareupDiscriminatedConnectionSettings",
    "DataConnectorSquareupDiscriminatedConnectionSettingsSettings",
    "DataConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorStackexchangeDiscriminatedConnectionSettings",
    "DataConnectorStackexchangeDiscriminatedConnectionSettingsSettings",
    "DataConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorStravaDiscriminatedConnectionSettings",
    "DataConnectorStravaDiscriminatedConnectionSettingsSettings",
    "DataConnectorStravaDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorStravaDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTeamworkDiscriminatedConnectionSettings",
    "DataConnectorTeamworkDiscriminatedConnectionSettingsSettings",
    "DataConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTicktickDiscriminatedConnectionSettings",
    "DataConnectorTicktickDiscriminatedConnectionSettingsSettings",
    "DataConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTimelyDiscriminatedConnectionSettings",
    "DataConnectorTimelyDiscriminatedConnectionSettingsSettings",
    "DataConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTodoistDiscriminatedConnectionSettings",
    "DataConnectorTodoistDiscriminatedConnectionSettingsSettings",
    "DataConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTremendousDiscriminatedConnectionSettings",
    "DataConnectorTremendousDiscriminatedConnectionSettingsSettings",
    "DataConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTsheetsteamDiscriminatedConnectionSettings",
    "DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettings",
    "DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTumblrDiscriminatedConnectionSettings",
    "DataConnectorTumblrDiscriminatedConnectionSettingsSettings",
    "DataConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTwinfieldDiscriminatedConnectionSettings",
    "DataConnectorTwinfieldDiscriminatedConnectionSettingsSettings",
    "DataConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTwitchDiscriminatedConnectionSettings",
    "DataConnectorTwitchDiscriminatedConnectionSettingsSettings",
    "DataConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTwitterDiscriminatedConnectionSettings",
    "DataConnectorTwitterDiscriminatedConnectionSettingsSettings",
    "DataConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorTypeformDiscriminatedConnectionSettings",
    "DataConnectorTypeformDiscriminatedConnectionSettingsSettings",
    "DataConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorUberDiscriminatedConnectionSettings",
    "DataConnectorUberDiscriminatedConnectionSettingsSettings",
    "DataConnectorUberDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorUberDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorVimeoDiscriminatedConnectionSettings",
    "DataConnectorVimeoDiscriminatedConnectionSettingsSettings",
    "DataConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorWakatimeDiscriminatedConnectionSettings",
    "DataConnectorWakatimeDiscriminatedConnectionSettingsSettings",
    "DataConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorWealthboxDiscriminatedConnectionSettings",
    "DataConnectorWealthboxDiscriminatedConnectionSettingsSettings",
    "DataConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorWebflowDiscriminatedConnectionSettings",
    "DataConnectorWebflowDiscriminatedConnectionSettingsSettings",
    "DataConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorWhoopDiscriminatedConnectionSettings",
    "DataConnectorWhoopDiscriminatedConnectionSettingsSettings",
    "DataConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorWordpressDiscriminatedConnectionSettings",
    "DataConnectorWordpressDiscriminatedConnectionSettingsSettings",
    "DataConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorWrikeDiscriminatedConnectionSettings",
    "DataConnectorWrikeDiscriminatedConnectionSettingsSettings",
    "DataConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorXeroDiscriminatedConnectionSettings",
    "DataConnectorXeroDiscriminatedConnectionSettingsSettings",
    "DataConnectorXeroDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorXeroDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorYahooDiscriminatedConnectionSettings",
    "DataConnectorYahooDiscriminatedConnectionSettingsSettings",
    "DataConnectorYahooDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorYahooDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorYandexDiscriminatedConnectionSettings",
    "DataConnectorYandexDiscriminatedConnectionSettingsSettings",
    "DataConnectorYandexDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorYandexDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorZapierDiscriminatedConnectionSettings",
    "DataConnectorZapierDiscriminatedConnectionSettingsSettings",
    "DataConnectorZapierDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorZapierDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorZendeskDiscriminatedConnectionSettings",
    "DataConnectorZendeskDiscriminatedConnectionSettingsSettings",
    "DataConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorZenefitsDiscriminatedConnectionSettings",
    "DataConnectorZenefitsDiscriminatedConnectionSettingsSettings",
    "DataConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorZohoDeskDiscriminatedConnectionSettings",
    "DataConnectorZohoDeskDiscriminatedConnectionSettingsSettings",
    "DataConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorZohoDiscriminatedConnectionSettings",
    "DataConnectorZohoDiscriminatedConnectionSettingsSettings",
    "DataConnectorZohoDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorZohoDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorZoomDiscriminatedConnectionSettings",
    "DataConnectorZoomDiscriminatedConnectionSettingsSettings",
    "DataConnectorZoomDiscriminatedConnectionSettingsSettingsOAuth",
    "DataConnectorZoomDiscriminatedConnectionSettingsSettingsOAuthCredentials",
    "DataConnectorAirtableDiscriminatedConnectionSettings",
    "DataConnectorAirtableDiscriminatedConnectionSettingsSettings",
    "DataConnectorApolloDiscriminatedConnectionSettings",
    "DataConnectorApolloDiscriminatedConnectionSettingsSettings",
    "DataConnectorBrexDiscriminatedConnectionSettings",
    "DataConnectorBrexDiscriminatedConnectionSettingsSettings",
    "DataConnectorCodaDiscriminatedConnectionSettings",
    "DataConnectorCodaDiscriminatedConnectionSettingsSettings",
    "DataConnectorFinchDiscriminatedConnectionSettings",
    "DataConnectorFinchDiscriminatedConnectionSettingsSettings",
    "DataConnectorFirebaseDiscriminatedConnectionSettings",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettings",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2",
    "DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig",
    "DataConnectorForeceiptDiscriminatedConnectionSettings",
    "DataConnectorForeceiptDiscriminatedConnectionSettingsSettings",
    "DataConnectorGreenhouseDiscriminatedConnectionSettings",
    "DataConnectorGreenhouseDiscriminatedConnectionSettingsSettings",
    "DataConnectorHeronDiscriminatedConnectionSettings",
    "DataConnectorLunchmoneyDiscriminatedConnectionSettings",
    "DataConnectorMercuryDiscriminatedConnectionSettings",
    "DataConnectorMergeDiscriminatedConnectionSettings",
    "DataConnectorMergeDiscriminatedConnectionSettingsSettings",
    "DataConnectorMootaDiscriminatedConnectionSettings",
    "DataConnectorOnebrickDiscriminatedConnectionSettings",
    "DataConnectorOnebrickDiscriminatedConnectionSettingsSettings",
    "DataConnectorOpenledgerDiscriminatedConnectionSettings",
    "DataConnectorOpenledgerDiscriminatedConnectionSettingsSettings",
    "DataConnectorPlaidDiscriminatedConnectionSettings",
    "DataConnectorPlaidDiscriminatedConnectionSettingsSettings",
    "DataConnectorPostgresDiscriminatedConnectionSettings",
    "DataConnectorPostgresDiscriminatedConnectionSettingsSettings",
    "DataConnectorRampDiscriminatedConnectionSettings",
    "DataConnectorRampDiscriminatedConnectionSettingsSettings",
    "DataConnectorSaltedgeDiscriminatedConnectionSettings",
    "DataConnectorSharepointOnpremDiscriminatedConnectionSettings",
    "DataConnectorSharepointOnpremDiscriminatedConnectionSettingsSettings",
    "DataConnectorSplitwiseDiscriminatedConnectionSettings",
    "DataConnectorSplitwiseDiscriminatedConnectionSettingsSettings",
    "DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser",
    "DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications",
    "DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture",
    "DataConnectorStripeDiscriminatedConnectionSettings",
    "DataConnectorStripeDiscriminatedConnectionSettingsSettings",
    "DataConnectorTellerDiscriminatedConnectionSettings",
    "DataConnectorTellerDiscriminatedConnectionSettingsSettings",
    "DataConnectorTogglDiscriminatedConnectionSettings",
    "DataConnectorTogglDiscriminatedConnectionSettingsSettings",
    "DataConnectorTwentyDiscriminatedConnectionSettings",
    "DataConnectorTwentyDiscriminatedConnectionSettingsSettings",
    "DataConnectorVenmoDiscriminatedConnectionSettings",
    "DataConnectorVenmoDiscriminatedConnectionSettingsSettings",
    "DataConnectorWiseDiscriminatedConnectionSettings",
    "DataConnectorWiseDiscriminatedConnectionSettingsSettings",
    "DataConnectorYodleeDiscriminatedConnectionSettings",
    "DataConnectorYodleeDiscriminatedConnectionSettingsSettings",
    "DataConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken",
    "DataConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount",
]


class ClientCreateConnectionParams(TypedDict, total=False):
    connector_config_id: Required[str]
    """The id of the connector config, starts with `ccfg_`"""

    customer_id: Required[str]
    """The id of the customer in your application.

    Ensure it is unique for that customer.
    """

    data: Required[Data]
    """Connector specific data"""

    check_connection: bool
    """Perform a synchronous connection check before creating it."""

    metadata: Dict[str, object]


class DataConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAcceloDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorAcceloDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your Accelo account (e.g., https://domain.api.accelo.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAcceloDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["accelo"]]

    settings: DataConnectorAcceloDiscriminatedConnectionSettingsSettings


class DataConnectorAcmeApikeyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_key: Required[str]


class DataConnectorAcmeApikeyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["acme-apikey"]]

    settings: DataConnectorAcmeApikeyDiscriminatedConnectionSettingsSettings


class DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAcmeOauth2DiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["acme-oauth2"]]

    settings: DataConnectorAcmeOauth2DiscriminatedConnectionSettingsSettings


class DataConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAdobeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorAdobeDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAdobeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["adobe"]]

    settings: DataConnectorAdobeDiscriminatedConnectionSettingsSettings


class DataConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAdyenDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    environment: Required[str]
    """The environment to use (e.g., live|test)"""

    oauth: Required[DataConnectorAdyenDiscriminatedConnectionSettingsSettingsOAuth]

    resource: Required[str]
    """
    The resource to use for your various requests (e.g.,
    https://kyc-(live|test).adyen.com)
    """

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAdyenDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["adyen"]]

    settings: DataConnectorAdyenDiscriminatedConnectionSettingsSettings


class DataConnectorAircallDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAircallDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAircallDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAircallDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorAircallDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAircallDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["aircall"]]

    settings: DataConnectorAircallDiscriminatedConnectionSettingsSettings


class DataConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAmazonDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    extension: Required[str]
    """The domain extension for your Amazon account (e.g., com)"""

    oauth: Required[DataConnectorAmazonDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAmazonDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["amazon"]]

    settings: DataConnectorAmazonDiscriminatedConnectionSettingsSettings


class DataConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorApaleoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorApaleoDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorApaleoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["apaleo"]]

    settings: DataConnectorApaleoDiscriminatedConnectionSettingsSettings


class DataConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAsanaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorAsanaDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAsanaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["asana"]]

    settings: DataConnectorAsanaDiscriminatedConnectionSettingsSettings


class DataConnectorAttioDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAttioDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAttioDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAttioDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorAttioDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAttioDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["attio"]]

    settings: DataConnectorAttioDiscriminatedConnectionSettingsSettings


class DataConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAuth0DiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorAuth0DiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your Auth0 account (e.g., https://domain.auth0.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAuth0DiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["auth0"]]

    settings: DataConnectorAuth0DiscriminatedConnectionSettingsSettings


class DataConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAutodeskDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorAutodeskDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAutodeskDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["autodesk"]]

    settings: DataConnectorAutodeskDiscriminatedConnectionSettingsSettings


class DataConnectorAwsDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorAwsDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorAwsDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorAwsDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_subdomain: Required[Annotated[str, PropertyInfo(alias="apiSubdomain")]]
    """
    The API subdomain to the API you want to connect to (e.g.,
    https://cognito-idp.us-east-2.amazonaws.com)
    """

    extension: Required[str]
    """The domain extension of your AWS account (e.g., com)"""

    oauth: Required[DataConnectorAwsDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your AWS account (e.g., https://domain.amazoncognito.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorAwsDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["aws"]]

    settings: DataConnectorAwsDiscriminatedConnectionSettingsSettings


class DataConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBamboohrDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorBamboohrDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your BambooHR account (e.g., https://domain.bamboohr.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBamboohrDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["bamboohr"]]

    settings: DataConnectorBamboohrDiscriminatedConnectionSettingsSettings


class DataConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBasecampDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_id: Required[Annotated[str, PropertyInfo(alias="accountId")]]
    """Your Account ID (e.g., 5899981)"""

    app_details: Required[Annotated[str, PropertyInfo(alias="appDetails")]]
    """The details of your app (e.g., example-subdomain)"""

    oauth: Required[DataConnectorBasecampDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBasecampDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["basecamp"]]

    settings: DataConnectorBasecampDiscriminatedConnectionSettingsSettings


class DataConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBattlenetDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_domain: Required[Annotated[str, PropertyInfo(alias="apiDomain")]]
    """
    The domain to where you will access your API (e.g., https://us.api.blizzard.com)
    """

    extension: Required[str]
    """The domain extension of your Battle.net account (e.g., com)"""

    oauth: Required[DataConnectorBattlenetDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBattlenetDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["battlenet"]]

    settings: DataConnectorBattlenetDiscriminatedConnectionSettingsSettings


class DataConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBigcommerceDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_uuid: Required[Annotated[str, PropertyInfo(alias="accountUuid")]]
    """
    The account UUID of your BigCommerce account (e.g.,
    123e4567-e89b-12d3-a456-426614174000)
    """

    oauth: Required[DataConnectorBigcommerceDiscriminatedConnectionSettingsSettingsOAuth]

    store_hash: Required[Annotated[str, PropertyInfo(alias="storeHash")]]
    """The store hash of your BigCommerce account (e.g., Example123)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBigcommerceDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["bigcommerce"]]

    settings: DataConnectorBigcommerceDiscriminatedConnectionSettingsSettings


class DataConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBitbucketDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorBitbucketDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBitbucketDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["bitbucket"]]

    settings: DataConnectorBitbucketDiscriminatedConnectionSettingsSettings


class DataConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBitlyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorBitlyDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBitlyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["bitly"]]

    settings: DataConnectorBitlyDiscriminatedConnectionSettingsSettings


class DataConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBlackbaudDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorBlackbaudDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBlackbaudDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["blackbaud"]]

    settings: DataConnectorBlackbaudDiscriminatedConnectionSettingsSettings


class DataConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBoldsignDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorBoldsignDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBoldsignDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["boldsign"]]

    settings: DataConnectorBoldsignDiscriminatedConnectionSettingsSettings


class DataConnectorBoxDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBoxDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBoxDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBoxDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorBoxDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBoxDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["box"]]

    settings: DataConnectorBoxDiscriminatedConnectionSettingsSettings


class DataConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorBraintreeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorBraintreeDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorBraintreeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["braintree"]]

    settings: DataConnectorBraintreeDiscriminatedConnectionSettingsSettings


class DataConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorCalendlyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorCalendlyDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorCalendlyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["calendly"]]

    settings: DataConnectorCalendlyDiscriminatedConnectionSettingsSettings


class DataConnectorClickupDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorClickupDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorClickupDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorClickupDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorClickupDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorClickupDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["clickup"]]

    settings: DataConnectorClickupDiscriminatedConnectionSettingsSettings


class DataConnectorCloseDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorCloseDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorCloseDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorCloseDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorCloseDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorCloseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["close"]]

    settings: DataConnectorCloseDiscriminatedConnectionSettingsSettings


class DataConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorConfluenceDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorConfluenceDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorConfluenceDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["confluence"]]

    settings: DataConnectorConfluenceDiscriminatedConnectionSettingsSettings


class DataConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorContentfulDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorContentfulDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your Contentful account (e.g., https://domain.contentful.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorContentfulDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["contentful"]]

    settings: DataConnectorContentfulDiscriminatedConnectionSettingsSettings


class DataConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorContentstackDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_domain: Required[Annotated[str, PropertyInfo(alias="apiDomain")]]
    """
    The domain to where you will access your API (e.g.,
    https://eu-api.contentstack.com)
    """

    app_id: Required[Annotated[str, PropertyInfo(alias="appId")]]
    """The app ID of your Contentstack account (e.g., example-subdomain)"""

    oauth: Required[DataConnectorContentstackDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """
    The subdomain of your Contentstack account (e.g.,
    https://domain.contentstack.com)
    """

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorContentstackDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["contentstack"]]

    settings: DataConnectorContentstackDiscriminatedConnectionSettingsSettings


class DataConnectorCopperDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorCopperDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorCopperDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorCopperDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorCopperDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorCopperDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["copper"]]

    settings: DataConnectorCopperDiscriminatedConnectionSettingsSettings


class DataConnectorCorosDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorCorosDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorCorosDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorCorosDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorCorosDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorCorosDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["coros"]]

    settings: DataConnectorCorosDiscriminatedConnectionSettingsSettings


class DataConnectorDatevDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorDatevDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorDatevDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorDatevDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorDatevDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDatevDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["datev"]]

    settings: DataConnectorDatevDiscriminatedConnectionSettingsSettings


class DataConnectorDeelDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorDeelDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorDeelDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorDeelDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorDeelDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDeelDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["deel"]]

    settings: DataConnectorDeelDiscriminatedConnectionSettingsSettings


class DataConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorDialpadDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorDialpadDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDialpadDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["dialpad"]]

    settings: DataConnectorDialpadDiscriminatedConnectionSettingsSettings


class DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDigitaloceanDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["digitalocean"]]

    settings: DataConnectorDigitaloceanDiscriminatedConnectionSettingsSettings


class DataConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorDiscordDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorDiscordDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDiscordDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["discord"]]

    settings: DataConnectorDiscordDiscriminatedConnectionSettingsSettings


class DataConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorDocusignDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorDocusignDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDocusignDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["docusign"]]

    settings: DataConnectorDocusignDiscriminatedConnectionSettingsSettings


class DataConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorDropboxDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorDropboxDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorDropboxDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["dropbox"]]

    settings: DataConnectorDropboxDiscriminatedConnectionSettingsSettings


class DataConnectorEbayDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorEbayDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorEbayDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorEbayDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorEbayDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorEbayDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["ebay"]]

    settings: DataConnectorEbayDiscriminatedConnectionSettingsSettings


class DataConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorEgnyteDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorEgnyteDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your Egnyte account (e.g., https://domain.egnyte.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorEgnyteDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["egnyte"]]

    settings: DataConnectorEgnyteDiscriminatedConnectionSettingsSettings


class DataConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorEnvoyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorEnvoyDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorEnvoyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["envoy"]]

    settings: DataConnectorEnvoyDiscriminatedConnectionSettingsSettings


class DataConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorEventbriteDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorEventbriteDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorEventbriteDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["eventbrite"]]

    settings: DataConnectorEventbriteDiscriminatedConnectionSettingsSettings


class DataConnectorExistDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorExistDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorExistDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorExistDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorExistDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorExistDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["exist"]]

    settings: DataConnectorExistDiscriminatedConnectionSettingsSettings


class DataConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorFacebookDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorFacebookDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFacebookDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["facebook"]]

    settings: DataConnectorFacebookDiscriminatedConnectionSettingsSettings


class DataConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorFactorialDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorFactorialDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFactorialDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["factorial"]]

    settings: DataConnectorFactorialDiscriminatedConnectionSettingsSettings


class DataConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorFigmaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorFigmaDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFigmaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["figma"]]

    settings: DataConnectorFigmaDiscriminatedConnectionSettingsSettings


class DataConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorFitbitDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorFitbitDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFitbitDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["fitbit"]]

    settings: DataConnectorFitbitDiscriminatedConnectionSettingsSettings


class DataConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorFortnoxDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorFortnoxDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFortnoxDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["fortnox"]]

    settings: DataConnectorFortnoxDiscriminatedConnectionSettingsSettings


class DataConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorFreshbooksDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorFreshbooksDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFreshbooksDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["freshbooks"]]

    settings: DataConnectorFreshbooksDiscriminatedConnectionSettingsSettings


class DataConnectorFrontDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorFrontDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorFrontDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorFrontDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorFrontDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorFrontDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["front"]]

    settings: DataConnectorFrontDiscriminatedConnectionSettingsSettings


class DataConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGitHubDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGitHubDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGitHubDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["github"]]

    settings: DataConnectorGitHubDiscriminatedConnectionSettingsSettings


class DataConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGitlabDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGitlabDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGitlabDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gitlab"]]

    settings: DataConnectorGitlabDiscriminatedConnectionSettingsSettings


class DataConnectorGongDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGongDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGongDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGongDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_base_url_for_customer: Required[str]
    """The base URL of your Gong account (e.g., example)"""

    oauth: Required[DataConnectorGongDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGongDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gong"]]

    settings: DataConnectorGongDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleCalendarDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-calendar"]]

    settings: DataConnectorGoogleCalendarDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleDocsDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-docs"]]

    settings: DataConnectorGoogleDocsDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleDriveDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-drive"]]

    settings: DataConnectorGoogleDriveDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGoogleMailDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGoogleMailDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleMailDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-mail"]]

    settings: DataConnectorGoogleMailDiscriminatedConnectionSettingsSettings


class DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGoogleSheetDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["google-sheet"]]

    settings: DataConnectorGoogleSheetDiscriminatedConnectionSettingsSettings


class DataConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGorgiasDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGorgiasDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your Gorgias account (e.g., https://domain.gorgias.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGorgiasDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gorgias"]]

    settings: DataConnectorGorgiasDiscriminatedConnectionSettingsSettings


class DataConnectorGrainDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGrainDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGrainDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGrainDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGrainDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGrainDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["grain"]]

    settings: DataConnectorGrainDiscriminatedConnectionSettingsSettings


class DataConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGumroadDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGumroadDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGumroadDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gumroad"]]

    settings: DataConnectorGumroadDiscriminatedConnectionSettingsSettings


class DataConnectorGustoDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorGustoDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorGustoDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorGustoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorGustoDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorGustoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["gusto"]]

    settings: DataConnectorGustoDiscriminatedConnectionSettingsSettings


class DataConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorHarvestDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    app_details: Required[Annotated[str, PropertyInfo(alias="appDetails")]]
    """The details of your app (e.g., example-subdomain)"""

    oauth: Required[DataConnectorHarvestDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorHarvestDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["harvest"]]

    settings: DataConnectorHarvestDiscriminatedConnectionSettingsSettings


class DataConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorHighlevelDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorHighlevelDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorHighlevelDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["highlevel"]]

    settings: DataConnectorHighlevelDiscriminatedConnectionSettingsSettings


class DataConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorHubspotDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorHubspotDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorHubspotDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["hubspot"]]

    settings: DataConnectorHubspotDiscriminatedConnectionSettingsSettings


class DataConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorInstagramDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorInstagramDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorInstagramDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["instagram"]]

    settings: DataConnectorInstagramDiscriminatedConnectionSettingsSettings


class DataConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorIntercomDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorIntercomDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorIntercomDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["intercom"]]

    settings: DataConnectorIntercomDiscriminatedConnectionSettingsSettings


class DataConnectorJiraDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorJiraDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorJiraDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorJiraDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorJiraDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorJiraDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["jira"]]

    settings: DataConnectorJiraDiscriminatedConnectionSettingsSettings


class DataConnectorKeapDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorKeapDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorKeapDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorKeapDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorKeapDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorKeapDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["keap"]]

    settings: DataConnectorKeapDiscriminatedConnectionSettingsSettings


class DataConnectorLeverDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorLeverDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorLeverDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorLeverDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorLeverDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorLeverDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["lever"]]

    settings: DataConnectorLeverDiscriminatedConnectionSettingsSettings


class DataConnectorLinearDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorLinearDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorLinearDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorLinearDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorLinearDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorLinearDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["linear"]]

    settings: DataConnectorLinearDiscriminatedConnectionSettingsSettings


class DataConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorLinkedinDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorLinkedinDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorLinkedinDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["linkedin"]]

    settings: DataConnectorLinkedinDiscriminatedConnectionSettingsSettings


class DataConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorLinkhutDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorLinkhutDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorLinkhutDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["linkhut"]]

    settings: DataConnectorLinkhutDiscriminatedConnectionSettingsSettings


class DataConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorMailchimpDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    dc: Required[str]
    """The data center for your account (e.g., us6)"""

    oauth: Required[DataConnectorMailchimpDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorMailchimpDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["mailchimp"]]

    settings: DataConnectorMailchimpDiscriminatedConnectionSettingsSettings


class DataConnectorMiroDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorMiroDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorMiroDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorMiroDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorMiroDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorMiroDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["miro"]]

    settings: DataConnectorMiroDiscriminatedConnectionSettingsSettings


class DataConnectorMondayDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorMondayDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorMondayDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorMondayDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorMondayDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorMondayDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["monday"]]

    settings: DataConnectorMondayDiscriminatedConnectionSettingsSettings


class DataConnectorMuralDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorMuralDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorMuralDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorMuralDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorMuralDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorMuralDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["mural"]]

    settings: DataConnectorMuralDiscriminatedConnectionSettingsSettings


class DataConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorNamelyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    company: Required[str]
    """The name of your Namely company (e.g., example)"""

    oauth: Required[DataConnectorNamelyDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorNamelyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["namely"]]

    settings: DataConnectorNamelyDiscriminatedConnectionSettingsSettings


class DataConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorNationbuilderDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_id: Required[Annotated[str, PropertyInfo(alias="accountId")]]
    """The account ID of your NationBuilder account (e.g., example-subdomain)"""

    oauth: Required[DataConnectorNationbuilderDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorNationbuilderDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["nationbuilder"]]

    settings: DataConnectorNationbuilderDiscriminatedConnectionSettingsSettings


class DataConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorNetsuiteDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_id: Required[Annotated[str, PropertyInfo(alias="accountId")]]
    """The account ID of your NetSuite account (e.g., tstdrv231585)"""

    oauth: Required[DataConnectorNetsuiteDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorNetsuiteDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["netsuite"]]

    settings: DataConnectorNetsuiteDiscriminatedConnectionSettingsSettings


class DataConnectorNotionDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorNotionDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorNotionDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorNotionDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorNotionDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorNotionDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["notion"]]

    settings: DataConnectorNotionDiscriminatedConnectionSettingsSettings


class DataConnectorOdooDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorOdooDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorOdooDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorOdooDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorOdooDiscriminatedConnectionSettingsSettingsOAuth]

    server_url: Required[Annotated[str, PropertyInfo(alias="serverUrl")]]
    """The domain of your Odoo account (e.g., https://example-subdomain)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOdooDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["odoo"]]

    settings: DataConnectorOdooDiscriminatedConnectionSettingsSettings


class DataConnectorOktaDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorOktaDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorOktaDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorOktaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorOktaDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your Okta account (e.g., https://domain.okta.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOktaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["okta"]]

    settings: DataConnectorOktaDiscriminatedConnectionSettingsSettings


class DataConnectorOsuDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorOsuDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorOsuDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorOsuDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorOsuDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOsuDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["osu"]]

    settings: DataConnectorOsuDiscriminatedConnectionSettingsSettings


class DataConnectorOuraDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorOuraDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorOuraDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorOuraDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorOuraDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOuraDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["oura"]]

    settings: DataConnectorOuraDiscriminatedConnectionSettingsSettings


class DataConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorOutreachDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorOutreachDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorOutreachDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["outreach"]]

    settings: DataConnectorOutreachDiscriminatedConnectionSettingsSettings


class DataConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorPagerdutyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorPagerdutyDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPagerdutyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pagerduty"]]

    settings: DataConnectorPagerdutyDiscriminatedConnectionSettingsSettings


class DataConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorPandadocDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorPandadocDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPandadocDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pandadoc"]]

    settings: DataConnectorPandadocDiscriminatedConnectionSettingsSettings


class DataConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorPayfitDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorPayfitDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPayfitDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["payfit"]]

    settings: DataConnectorPayfitDiscriminatedConnectionSettingsSettings


class DataConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorPaypalDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorPaypalDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPaypalDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["paypal"]]

    settings: DataConnectorPaypalDiscriminatedConnectionSettingsSettings


class DataConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorPennylaneDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorPennylaneDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPennylaneDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pennylane"]]

    settings: DataConnectorPennylaneDiscriminatedConnectionSettingsSettings


class DataConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorPinterestDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorPinterestDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPinterestDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pinterest"]]

    settings: DataConnectorPinterestDiscriminatedConnectionSettingsSettings


class DataConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorPipedriveDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_domain: Required[str]
    """The API URL of your Pipedrive account (e.g., example)"""

    oauth: Required[DataConnectorPipedriveDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPipedriveDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["pipedrive"]]

    settings: DataConnectorPipedriveDiscriminatedConnectionSettingsSettings


class DataConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorPodiumDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_version: Required[Annotated[str, PropertyInfo(alias="apiVersion")]]
    """The API version of your Podium account (e.g., example-subdomain)"""

    oauth: Required[DataConnectorPodiumDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorPodiumDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["podium"]]

    settings: DataConnectorPodiumDiscriminatedConnectionSettingsSettings


class DataConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorProductboardDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorProductboardDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorProductboardDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["productboard"]]

    settings: DataConnectorProductboardDiscriminatedConnectionSettingsSettings


class DataConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorQualtricsDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorQualtricsDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your Qualtrics account (e.g., https://domain.qualtrics.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorQualtricsDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["qualtrics"]]

    settings: DataConnectorQualtricsDiscriminatedConnectionSettingsSettings


class DataConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorQuickbooksDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorQuickbooksDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorQuickbooksDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["quickbooks"]]

    settings: DataConnectorQuickbooksDiscriminatedConnectionSettingsSettings


class DataConnectorRedditDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorRedditDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorRedditDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorRedditDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorRedditDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorRedditDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["reddit"]]

    settings: DataConnectorRedditDiscriminatedConnectionSettingsSettings


class DataConnectorSageDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSageDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSageDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSageDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSageDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSageDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["sage"]]

    settings: DataConnectorSageDiscriminatedConnectionSettingsSettings


class DataConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSalesforceDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    instance_url: Required[str]
    """The instance URL of your Salesforce account (e.g., example)"""

    oauth: Required[DataConnectorSalesforceDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSalesforceDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["salesforce"]]

    settings: DataConnectorSalesforceDiscriminatedConnectionSettingsSettings


class DataConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSalesloftDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSalesloftDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSalesloftDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["salesloft"]]

    settings: DataConnectorSalesloftDiscriminatedConnectionSettingsSettings


class DataConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSegmentDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSegmentDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSegmentDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["segment"]]

    settings: DataConnectorSegmentDiscriminatedConnectionSettingsSettings


class DataConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorServicem8DiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorServicem8DiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorServicem8DiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["servicem8"]]

    settings: DataConnectorServicem8DiscriminatedConnectionSettingsSettings


class DataConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorServicenowDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorServicenowDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your ServiceNow account (e.g., https://domain.service-now.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorServicenowDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["servicenow"]]

    settings: DataConnectorServicenowDiscriminatedConnectionSettingsSettings


class DataConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSharepointDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSharepointDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSharepointDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["sharepoint"]]

    settings: DataConnectorSharepointDiscriminatedConnectionSettingsSettings


class DataConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorShopifyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorShopifyDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your Shopify account (e.g., https://domain.myshopify.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorShopifyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["shopify"]]

    settings: DataConnectorShopifyDiscriminatedConnectionSettingsSettings


class DataConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSignnowDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSignnowDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSignnowDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["signnow"]]

    settings: DataConnectorSignnowDiscriminatedConnectionSettingsSettings


class DataConnectorSlackDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSlackDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSlackDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSlackDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSlackDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSlackDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["slack"]]

    settings: DataConnectorSlackDiscriminatedConnectionSettingsSettings


class DataConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSmartsheetDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSmartsheetDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSmartsheetDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["smartsheet"]]

    settings: DataConnectorSmartsheetDiscriminatedConnectionSettingsSettings


class DataConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSnowflakeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSnowflakeDiscriminatedConnectionSettingsSettingsOAuth]

    snowflake_account_url: Required[str]
    """The domain of your Snowflake account (e.g., https://example-subdomain)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSnowflakeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["snowflake"]]

    settings: DataConnectorSnowflakeDiscriminatedConnectionSettingsSettings


class DataConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSpotifyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSpotifyDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSpotifyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["spotify"]]

    settings: DataConnectorSpotifyDiscriminatedConnectionSettingsSettings


class DataConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSquarespaceDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    customapp_description: Required[Annotated[str, PropertyInfo(alias="customappDescription")]]
    """The user agent of your custom app (e.g., example-subdomain)"""

    oauth: Required[DataConnectorSquarespaceDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSquarespaceDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["squarespace"]]

    settings: DataConnectorSquarespaceDiscriminatedConnectionSettingsSettings


class DataConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorSquareupDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorSquareupDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorSquareupDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["squareup"]]

    settings: DataConnectorSquareupDiscriminatedConnectionSettingsSettings


class DataConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorStackexchangeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorStackexchangeDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorStackexchangeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["stackexchange"]]

    settings: DataConnectorStackexchangeDiscriminatedConnectionSettingsSettings


class DataConnectorStravaDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorStravaDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorStravaDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorStravaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorStravaDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorStravaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["strava"]]

    settings: DataConnectorStravaDiscriminatedConnectionSettingsSettings


class DataConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTeamworkDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTeamworkDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTeamworkDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["teamwork"]]

    settings: DataConnectorTeamworkDiscriminatedConnectionSettingsSettings


class DataConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTicktickDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTicktickDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTicktickDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["ticktick"]]

    settings: DataConnectorTicktickDiscriminatedConnectionSettingsSettings


class DataConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTimelyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTimelyDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTimelyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["timely"]]

    settings: DataConnectorTimelyDiscriminatedConnectionSettingsSettings


class DataConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTodoistDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTodoistDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTodoistDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["todoist"]]

    settings: DataConnectorTodoistDiscriminatedConnectionSettingsSettings


class DataConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTremendousDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTremendousDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTremendousDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["tremendous"]]

    settings: DataConnectorTremendousDiscriminatedConnectionSettingsSettings


class DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTsheetsteamDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["tsheetsteam"]]

    settings: DataConnectorTsheetsteamDiscriminatedConnectionSettingsSettings


class DataConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTumblrDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTumblrDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTumblrDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["tumblr"]]

    settings: DataConnectorTumblrDiscriminatedConnectionSettingsSettings


class DataConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTwinfieldDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    cluster: Required[str]
    """The cluster to your Twinfield instance (e.g., https://accounting.twinfield.com)"""

    oauth: Required[DataConnectorTwinfieldDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTwinfieldDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["twinfield"]]

    settings: DataConnectorTwinfieldDiscriminatedConnectionSettingsSettings


class DataConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTwitchDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTwitchDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTwitchDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["twitch"]]

    settings: DataConnectorTwitchDiscriminatedConnectionSettingsSettings


class DataConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTwitterDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTwitterDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTwitterDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["twitter"]]

    settings: DataConnectorTwitterDiscriminatedConnectionSettingsSettings


class DataConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorTypeformDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorTypeformDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorTypeformDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["typeform"]]

    settings: DataConnectorTypeformDiscriminatedConnectionSettingsSettings


class DataConnectorUberDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorUberDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorUberDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorUberDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorUberDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorUberDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["uber"]]

    settings: DataConnectorUberDiscriminatedConnectionSettingsSettings


class DataConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorVimeoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorVimeoDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorVimeoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["vimeo"]]

    settings: DataConnectorVimeoDiscriminatedConnectionSettingsSettings


class DataConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorWakatimeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorWakatimeDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWakatimeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wakatime"]]

    settings: DataConnectorWakatimeDiscriminatedConnectionSettingsSettings


class DataConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorWealthboxDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorWealthboxDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWealthboxDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wealthbox"]]

    settings: DataConnectorWealthboxDiscriminatedConnectionSettingsSettings


class DataConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorWebflowDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorWebflowDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWebflowDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["webflow"]]

    settings: DataConnectorWebflowDiscriminatedConnectionSettingsSettings


class DataConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorWhoopDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorWhoopDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWhoopDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["whoop"]]

    settings: DataConnectorWhoopDiscriminatedConnectionSettingsSettings


class DataConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorWordpressDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorWordpressDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWordpressDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wordpress"]]

    settings: DataConnectorWordpressDiscriminatedConnectionSettingsSettings


class DataConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorWrikeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    host: Required[str]
    """The domain of your Wrike account (e.g., https://example-subdomain)"""

    oauth: Required[DataConnectorWrikeDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorWrikeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wrike"]]

    settings: DataConnectorWrikeDiscriminatedConnectionSettingsSettings


class DataConnectorXeroDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorXeroDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorXeroDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorXeroDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorXeroDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorXeroDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["xero"]]

    settings: DataConnectorXeroDiscriminatedConnectionSettingsSettings


class DataConnectorYahooDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorYahooDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorYahooDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorYahooDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_domain: Required[Annotated[str, PropertyInfo(alias="apiDomain")]]
    """
    The domain to the API you want to connect to (e.g.,
    https://fantasysports.yahooapis.com)
    """

    oauth: Required[DataConnectorYahooDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorYahooDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["yahoo"]]

    settings: DataConnectorYahooDiscriminatedConnectionSettingsSettings


class DataConnectorYandexDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorYandexDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorYandexDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorYandexDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorYandexDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorYandexDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["yandex"]]

    settings: DataConnectorYandexDiscriminatedConnectionSettingsSettings


class DataConnectorZapierDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorZapierDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorZapierDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorZapierDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorZapierDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZapierDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zapier"]]

    settings: DataConnectorZapierDiscriminatedConnectionSettingsSettings


class DataConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorZendeskDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorZendeskDiscriminatedConnectionSettingsSettingsOAuth]

    subdomain: Required[str]
    """The subdomain of your Zendesk account (e.g., https://domain.zendesk.com)"""

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZendeskDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zendesk"]]

    settings: DataConnectorZendeskDiscriminatedConnectionSettingsSettings


class DataConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorZenefitsDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorZenefitsDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZenefitsDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zenefits"]]

    settings: DataConnectorZenefitsDiscriminatedConnectionSettingsSettings


class DataConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorZohoDeskDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    extension: Required[str]
    """The domain extension of your Zoho account (e.g., https://accounts.zoho.com/)"""

    oauth: Required[DataConnectorZohoDeskDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZohoDeskDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zoho-desk"]]

    settings: DataConnectorZohoDeskDiscriminatedConnectionSettingsSettings


class DataConnectorZohoDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorZohoDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorZohoDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorZohoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    extension: Required[str]
    """The domain extension of your Zoho account (e.g., https://accounts.zoho.com/)"""

    oauth: Required[DataConnectorZohoDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZohoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zoho"]]

    settings: DataConnectorZohoDiscriminatedConnectionSettingsSettings


class DataConnectorZoomDiscriminatedConnectionSettingsSettingsOAuthCredentials(TypedDict, total=False):
    access_token: Required[str]

    client_id: str
    """Client ID used for the connection"""

    expires_at: str

    expires_in: float

    raw: Dict[str, object]

    refresh_token: str

    scope: str

    token_type: str


class DataConnectorZoomDiscriminatedConnectionSettingsSettingsOAuth(TypedDict, total=False):
    created_at: str

    credentials: DataConnectorZoomDiscriminatedConnectionSettingsSettingsOAuthCredentials
    """Output of the postConnect hook for oauth2 connectors"""

    last_fetched_at: str

    metadata: Optional[Dict[str, object]]

    updated_at: str


class DataConnectorZoomDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    oauth: Required[DataConnectorZoomDiscriminatedConnectionSettingsSettingsOAuth]

    access_token: str
    """Same as oauth.credentials.access_token, but more convenient to access.

    Optional for backward compatibility until we remove the oauth field
    """


class DataConnectorZoomDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["zoom"]]

    settings: DataConnectorZoomDiscriminatedConnectionSettingsSettings


class DataConnectorAirtableDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    airtable_base: Required[Annotated[str, PropertyInfo(alias="airtableBase")]]

    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]


class DataConnectorAirtableDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["airtable"]]

    settings: DataConnectorAirtableDiscriminatedConnectionSettingsSettings


class DataConnectorApolloDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_key: Required[str]


class DataConnectorApolloDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["apollo"]]

    settings: DataConnectorApolloDiscriminatedConnectionSettingsSettings


class DataConnectorBrexDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]


class DataConnectorBrexDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["brex"]]

    settings: DataConnectorBrexDiscriminatedConnectionSettingsSettings


class DataConnectorCodaDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]


class DataConnectorCodaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["coda"]]

    settings: DataConnectorCodaDiscriminatedConnectionSettingsSettings


class DataConnectorFinchDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[str]


class DataConnectorFinchDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["finch"]]

    settings: DataConnectorFinchDiscriminatedConnectionSettingsSettings


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccountTyped(
    TypedDict, total=False
):
    project_id: Required[str]


DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount: TypeAlias = Union[
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccountTyped, Dict[str, object]
]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0(TypedDict, total=False):
    role: Required[Literal["admin"]]

    service_account: Required[
        Annotated[
            DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0ServiceAccount,
            PropertyInfo(alias="serviceAccount"),
        ]
    ]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJsonTyped(
    TypedDict, total=False
):
    app_name: Required[Annotated[str, PropertyInfo(alias="appName")]]

    sts_token_manager: Required[Annotated[Dict[str, object], PropertyInfo(alias="stsTokenManager")]]

    uid: Required[str]


DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson: TypeAlias = Union[
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJsonTyped,
    Dict[str, object],
]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0(
    TypedDict, total=False
):
    method: Required[Literal["userJson"]]

    user_json: Required[
        Annotated[
            DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0UserJson,
            PropertyInfo(alias="userJson"),
        ]
    ]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1(
    TypedDict, total=False
):
    custom_token: Required[Annotated[str, PropertyInfo(alias="customToken")]]

    method: Required[Literal["customToken"]]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2(
    TypedDict, total=False
):
    email: Required[str]

    method: Required[Literal["emailPassword"]]

    password: Required[str]


DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData: TypeAlias = Union[
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember0,
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember1,
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthDataUnionMember2,
]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig(TypedDict, total=False):
    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]

    app_id: Required[Annotated[str, PropertyInfo(alias="appId")]]

    auth_domain: Required[Annotated[str, PropertyInfo(alias="authDomain")]]

    database_url: Required[Annotated[str, PropertyInfo(alias="databaseURL")]]

    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]

    measurement_id: Annotated[str, PropertyInfo(alias="measurementId")]

    messaging_sender_id: Annotated[str, PropertyInfo(alias="messagingSenderId")]

    storage_bucket: Annotated[str, PropertyInfo(alias="storageBucket")]


class DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1(TypedDict, total=False):
    auth_data: Required[
        Annotated[
            DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1AuthData,
            PropertyInfo(alias="authData"),
        ]
    ]

    firebase_config: Required[
        Annotated[
            DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1FirebaseConfig,
            PropertyInfo(alias="firebaseConfig"),
        ]
    ]

    role: Required[Literal["user"]]


DataConnectorFirebaseDiscriminatedConnectionSettingsSettings: TypeAlias = Union[
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember0,
    DataConnectorFirebaseDiscriminatedConnectionSettingsSettingsUnionMember1,
]


class DataConnectorFirebaseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["firebase"]]

    settings: DataConnectorFirebaseDiscriminatedConnectionSettingsSettings


class DataConnectorForeceiptDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    env_name: Required[Annotated[Literal["staging", "production"], PropertyInfo(alias="envName")]]

    _id: object

    credentials: object


class DataConnectorForeceiptDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["foreceipt"]]

    settings: DataConnectorForeceiptDiscriminatedConnectionSettingsSettings


class DataConnectorGreenhouseDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]


class DataConnectorGreenhouseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["greenhouse"]]

    settings: DataConnectorGreenhouseDiscriminatedConnectionSettingsSettings


class DataConnectorHeronDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["heron"]]

    settings: object


class DataConnectorLunchmoneyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["lunchmoney"]]

    settings: object


class DataConnectorMercuryDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["mercury"]]

    settings: object


class DataConnectorMergeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    account_token: Required[Annotated[str, PropertyInfo(alias="accountToken")]]

    account_details: Annotated[object, PropertyInfo(alias="accountDetails")]


class DataConnectorMergeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["merge"]]

    settings: DataConnectorMergeDiscriminatedConnectionSettingsSettings


class DataConnectorMootaDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["moota"]]

    settings: object


class DataConnectorOnebrickDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]


class DataConnectorOnebrickDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["onebrick"]]

    settings: DataConnectorOnebrickDiscriminatedConnectionSettingsSettings


class DataConnectorOpenledgerDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    entity_id: Required[str]
    """Your entity's identifier, aka customer ID"""


class DataConnectorOpenledgerDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["openledger"]]

    settings: DataConnectorOpenledgerDiscriminatedConnectionSettingsSettings


class DataConnectorPlaidDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]

    institution: object

    item: object

    item_id: Annotated[Optional[str], PropertyInfo(alias="itemId")]

    status: object

    webhook_item_error: Annotated[None, PropertyInfo(alias="webhookItemError")]


class DataConnectorPlaidDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["plaid"]]

    settings: DataConnectorPlaidDiscriminatedConnectionSettingsSettings


class DataConnectorPostgresDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    database_url: Annotated[str, PropertyInfo(alias="databaseURL")]


class DataConnectorPostgresDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["postgres"]]

    settings: DataConnectorPostgresDiscriminatedConnectionSettingsSettings


class DataConnectorRampDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Annotated[Optional[str], PropertyInfo(alias="accessToken")]

    start_after_transaction_id: Annotated[Optional[str], PropertyInfo(alias="startAfterTransactionId")]


class DataConnectorRampDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["ramp"]]

    settings: DataConnectorRampDiscriminatedConnectionSettingsSettings


class DataConnectorSaltedgeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["saltedge"]]

    settings: object


class DataConnectorSharepointOnpremDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    password: Required[str]

    site_url: Required[str]

    username: Required[str]


class DataConnectorSharepointOnpremDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["sharepoint-onprem"]]

    settings: DataConnectorSharepointOnpremDiscriminatedConnectionSettingsSettings


class DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications(TypedDict, total=False):
    added_as_friend: Required[bool]

    added_to_group: Required[bool]

    announcements: Required[bool]

    bills: Required[bool]

    expense_added: Required[bool]

    expense_updated: Required[bool]

    monthly_summary: Required[bool]

    payments: Required[bool]


class DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture(TypedDict, total=False):
    large: Optional[str]

    medium: Optional[str]

    original: Optional[str]

    small: Optional[str]

    xlarge: Optional[str]

    xxlarge: Optional[str]


class DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser(TypedDict, total=False):
    id: Required[float]

    country_code: Required[str]

    custom_picture: Required[bool]

    date_format: Required[str]

    default_currency: Required[str]

    default_group_id: Required[float]

    email: Required[str]

    first_name: Required[str]

    force_refresh_at: Required[str]

    last_name: Required[str]

    locale: Required[str]

    notifications: Required[DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserNotifications]

    notifications_count: Required[float]

    notifications_read: Required[str]

    picture: Required[DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUserPicture]

    registration_status: Required[str]


class DataConnectorSplitwiseDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]

    current_user: Annotated[
        Optional[DataConnectorSplitwiseDiscriminatedConnectionSettingsSettingsCurrentUser],
        PropertyInfo(alias="currentUser"),
    ]


class DataConnectorSplitwiseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["splitwise"]]

    settings: DataConnectorSplitwiseDiscriminatedConnectionSettingsSettings


class DataConnectorStripeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    secret_key: Required[Annotated[str, PropertyInfo(alias="secretKey")]]


class DataConnectorStripeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["stripe"]]

    settings: DataConnectorStripeDiscriminatedConnectionSettingsSettings


class DataConnectorTellerDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    token: Required[str]


class DataConnectorTellerDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["teller"]]

    settings: DataConnectorTellerDiscriminatedConnectionSettingsSettings


class DataConnectorTogglDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    api_token: Required[Annotated[str, PropertyInfo(alias="apiToken")]]

    email: Optional[str]

    password: Optional[str]


class DataConnectorTogglDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["toggl"]]

    settings: DataConnectorTogglDiscriminatedConnectionSettingsSettings


class DataConnectorTwentyDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    access_token: Required[str]


class DataConnectorTwentyDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["twenty"]]

    settings: DataConnectorTwentyDiscriminatedConnectionSettingsSettings


class DataConnectorVenmoDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    credentials: object

    me: object


class DataConnectorVenmoDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["venmo"]]

    settings: DataConnectorVenmoDiscriminatedConnectionSettingsSettings


class DataConnectorWiseDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    env_name: Required[Annotated[Literal["sandbox", "live"], PropertyInfo(alias="envName")]]

    api_token: Annotated[Optional[str], PropertyInfo(alias="apiToken")]


class DataConnectorWiseDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["wise"]]

    settings: DataConnectorWiseDiscriminatedConnectionSettingsSettings


class DataConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken(TypedDict, total=False):
    access_token: Required[Annotated[str, PropertyInfo(alias="accessToken")]]

    expires_in: Required[Annotated[float, PropertyInfo(alias="expiresIn")]]

    issued_at: Required[Annotated[str, PropertyInfo(alias="issuedAt")]]


class DataConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount(TypedDict, total=False):
    id: Required[float]

    aggregation_source: Required[Annotated[str, PropertyInfo(alias="aggregationSource")]]

    created_date: Required[Annotated[str, PropertyInfo(alias="createdDate")]]

    dataset: Required[Iterable[object]]

    is_manual: Required[Annotated[bool, PropertyInfo(alias="isManual")]]

    provider_id: Required[Annotated[float, PropertyInfo(alias="providerId")]]

    status: Required[
        Literal["LOGIN_IN_PROGRESS", "USER_INPUT_REQUIRED", "IN_PROGRESS", "PARTIAL_SUCCESS", "SUCCESS", "FAILED"]
    ]

    is_deleted: Annotated[Optional[bool], PropertyInfo(alias="isDeleted")]


class DataConnectorYodleeDiscriminatedConnectionSettingsSettings(TypedDict, total=False):
    login_name: Required[Annotated[str, PropertyInfo(alias="loginName")]]

    provider_account_id: Required[Annotated[Union[float, str], PropertyInfo(alias="providerAccountId")]]

    access_token: Annotated[
        Optional[DataConnectorYodleeDiscriminatedConnectionSettingsSettingsAccessToken],
        PropertyInfo(alias="accessToken"),
    ]

    provider: None

    provider_account: Annotated[
        Optional[DataConnectorYodleeDiscriminatedConnectionSettingsSettingsProviderAccount],
        PropertyInfo(alias="providerAccount"),
    ]

    user: None


class DataConnectorYodleeDiscriminatedConnectionSettings(TypedDict, total=False):
    connector_name: Required[Literal["yodlee"]]

    settings: DataConnectorYodleeDiscriminatedConnectionSettingsSettings


Data: TypeAlias = Union[
    DataConnectorAcceloDiscriminatedConnectionSettings,
    DataConnectorAcmeApikeyDiscriminatedConnectionSettings,
    DataConnectorAcmeOauth2DiscriminatedConnectionSettings,
    DataConnectorAdobeDiscriminatedConnectionSettings,
    DataConnectorAdyenDiscriminatedConnectionSettings,
    DataConnectorAircallDiscriminatedConnectionSettings,
    DataConnectorAmazonDiscriminatedConnectionSettings,
    DataConnectorApaleoDiscriminatedConnectionSettings,
    DataConnectorAsanaDiscriminatedConnectionSettings,
    DataConnectorAttioDiscriminatedConnectionSettings,
    DataConnectorAuth0DiscriminatedConnectionSettings,
    DataConnectorAutodeskDiscriminatedConnectionSettings,
    DataConnectorAwsDiscriminatedConnectionSettings,
    DataConnectorBamboohrDiscriminatedConnectionSettings,
    DataConnectorBasecampDiscriminatedConnectionSettings,
    DataConnectorBattlenetDiscriminatedConnectionSettings,
    DataConnectorBigcommerceDiscriminatedConnectionSettings,
    DataConnectorBitbucketDiscriminatedConnectionSettings,
    DataConnectorBitlyDiscriminatedConnectionSettings,
    DataConnectorBlackbaudDiscriminatedConnectionSettings,
    DataConnectorBoldsignDiscriminatedConnectionSettings,
    DataConnectorBoxDiscriminatedConnectionSettings,
    DataConnectorBraintreeDiscriminatedConnectionSettings,
    DataConnectorCalendlyDiscriminatedConnectionSettings,
    DataConnectorClickupDiscriminatedConnectionSettings,
    DataConnectorCloseDiscriminatedConnectionSettings,
    DataConnectorConfluenceDiscriminatedConnectionSettings,
    DataConnectorContentfulDiscriminatedConnectionSettings,
    DataConnectorContentstackDiscriminatedConnectionSettings,
    DataConnectorCopperDiscriminatedConnectionSettings,
    DataConnectorCorosDiscriminatedConnectionSettings,
    DataConnectorDatevDiscriminatedConnectionSettings,
    DataConnectorDeelDiscriminatedConnectionSettings,
    DataConnectorDialpadDiscriminatedConnectionSettings,
    DataConnectorDigitaloceanDiscriminatedConnectionSettings,
    DataConnectorDiscordDiscriminatedConnectionSettings,
    DataConnectorDocusignDiscriminatedConnectionSettings,
    DataConnectorDropboxDiscriminatedConnectionSettings,
    DataConnectorEbayDiscriminatedConnectionSettings,
    DataConnectorEgnyteDiscriminatedConnectionSettings,
    DataConnectorEnvoyDiscriminatedConnectionSettings,
    DataConnectorEventbriteDiscriminatedConnectionSettings,
    DataConnectorExistDiscriminatedConnectionSettings,
    DataConnectorFacebookDiscriminatedConnectionSettings,
    DataConnectorFactorialDiscriminatedConnectionSettings,
    DataConnectorFigmaDiscriminatedConnectionSettings,
    DataConnectorFitbitDiscriminatedConnectionSettings,
    DataConnectorFortnoxDiscriminatedConnectionSettings,
    DataConnectorFreshbooksDiscriminatedConnectionSettings,
    DataConnectorFrontDiscriminatedConnectionSettings,
    DataConnectorGitHubDiscriminatedConnectionSettings,
    DataConnectorGitlabDiscriminatedConnectionSettings,
    DataConnectorGongDiscriminatedConnectionSettings,
    DataConnectorGoogleCalendarDiscriminatedConnectionSettings,
    DataConnectorGoogleDocsDiscriminatedConnectionSettings,
    DataConnectorGoogleDriveDiscriminatedConnectionSettings,
    DataConnectorGoogleMailDiscriminatedConnectionSettings,
    DataConnectorGoogleSheetDiscriminatedConnectionSettings,
    DataConnectorGorgiasDiscriminatedConnectionSettings,
    DataConnectorGrainDiscriminatedConnectionSettings,
    DataConnectorGumroadDiscriminatedConnectionSettings,
    DataConnectorGustoDiscriminatedConnectionSettings,
    DataConnectorHarvestDiscriminatedConnectionSettings,
    DataConnectorHighlevelDiscriminatedConnectionSettings,
    DataConnectorHubspotDiscriminatedConnectionSettings,
    DataConnectorInstagramDiscriminatedConnectionSettings,
    DataConnectorIntercomDiscriminatedConnectionSettings,
    DataConnectorJiraDiscriminatedConnectionSettings,
    DataConnectorKeapDiscriminatedConnectionSettings,
    DataConnectorLeverDiscriminatedConnectionSettings,
    DataConnectorLinearDiscriminatedConnectionSettings,
    DataConnectorLinkedinDiscriminatedConnectionSettings,
    DataConnectorLinkhutDiscriminatedConnectionSettings,
    DataConnectorMailchimpDiscriminatedConnectionSettings,
    DataConnectorMiroDiscriminatedConnectionSettings,
    DataConnectorMondayDiscriminatedConnectionSettings,
    DataConnectorMuralDiscriminatedConnectionSettings,
    DataConnectorNamelyDiscriminatedConnectionSettings,
    DataConnectorNationbuilderDiscriminatedConnectionSettings,
    DataConnectorNetsuiteDiscriminatedConnectionSettings,
    DataConnectorNotionDiscriminatedConnectionSettings,
    DataConnectorOdooDiscriminatedConnectionSettings,
    DataConnectorOktaDiscriminatedConnectionSettings,
    DataConnectorOsuDiscriminatedConnectionSettings,
    DataConnectorOuraDiscriminatedConnectionSettings,
    DataConnectorOutreachDiscriminatedConnectionSettings,
    DataConnectorPagerdutyDiscriminatedConnectionSettings,
    DataConnectorPandadocDiscriminatedConnectionSettings,
    DataConnectorPayfitDiscriminatedConnectionSettings,
    DataConnectorPaypalDiscriminatedConnectionSettings,
    DataConnectorPennylaneDiscriminatedConnectionSettings,
    DataConnectorPinterestDiscriminatedConnectionSettings,
    DataConnectorPipedriveDiscriminatedConnectionSettings,
    DataConnectorPodiumDiscriminatedConnectionSettings,
    DataConnectorProductboardDiscriminatedConnectionSettings,
    DataConnectorQualtricsDiscriminatedConnectionSettings,
    DataConnectorQuickbooksDiscriminatedConnectionSettings,
    DataConnectorRedditDiscriminatedConnectionSettings,
    DataConnectorSageDiscriminatedConnectionSettings,
    DataConnectorSalesforceDiscriminatedConnectionSettings,
    DataConnectorSalesloftDiscriminatedConnectionSettings,
    DataConnectorSegmentDiscriminatedConnectionSettings,
    DataConnectorServicem8DiscriminatedConnectionSettings,
    DataConnectorServicenowDiscriminatedConnectionSettings,
    DataConnectorSharepointDiscriminatedConnectionSettings,
    DataConnectorShopifyDiscriminatedConnectionSettings,
    DataConnectorSignnowDiscriminatedConnectionSettings,
    DataConnectorSlackDiscriminatedConnectionSettings,
    DataConnectorSmartsheetDiscriminatedConnectionSettings,
    DataConnectorSnowflakeDiscriminatedConnectionSettings,
    DataConnectorSpotifyDiscriminatedConnectionSettings,
    DataConnectorSquarespaceDiscriminatedConnectionSettings,
    DataConnectorSquareupDiscriminatedConnectionSettings,
    DataConnectorStackexchangeDiscriminatedConnectionSettings,
    DataConnectorStravaDiscriminatedConnectionSettings,
    DataConnectorTeamworkDiscriminatedConnectionSettings,
    DataConnectorTicktickDiscriminatedConnectionSettings,
    DataConnectorTimelyDiscriminatedConnectionSettings,
    DataConnectorTodoistDiscriminatedConnectionSettings,
    DataConnectorTremendousDiscriminatedConnectionSettings,
    DataConnectorTsheetsteamDiscriminatedConnectionSettings,
    DataConnectorTumblrDiscriminatedConnectionSettings,
    DataConnectorTwinfieldDiscriminatedConnectionSettings,
    DataConnectorTwitchDiscriminatedConnectionSettings,
    DataConnectorTwitterDiscriminatedConnectionSettings,
    DataConnectorTypeformDiscriminatedConnectionSettings,
    DataConnectorUberDiscriminatedConnectionSettings,
    DataConnectorVimeoDiscriminatedConnectionSettings,
    DataConnectorWakatimeDiscriminatedConnectionSettings,
    DataConnectorWealthboxDiscriminatedConnectionSettings,
    DataConnectorWebflowDiscriminatedConnectionSettings,
    DataConnectorWhoopDiscriminatedConnectionSettings,
    DataConnectorWordpressDiscriminatedConnectionSettings,
    DataConnectorWrikeDiscriminatedConnectionSettings,
    DataConnectorXeroDiscriminatedConnectionSettings,
    DataConnectorYahooDiscriminatedConnectionSettings,
    DataConnectorYandexDiscriminatedConnectionSettings,
    DataConnectorZapierDiscriminatedConnectionSettings,
    DataConnectorZendeskDiscriminatedConnectionSettings,
    DataConnectorZenefitsDiscriminatedConnectionSettings,
    DataConnectorZohoDeskDiscriminatedConnectionSettings,
    DataConnectorZohoDiscriminatedConnectionSettings,
    DataConnectorZoomDiscriminatedConnectionSettings,
    DataConnectorAirtableDiscriminatedConnectionSettings,
    DataConnectorApolloDiscriminatedConnectionSettings,
    DataConnectorBrexDiscriminatedConnectionSettings,
    DataConnectorCodaDiscriminatedConnectionSettings,
    DataConnectorFinchDiscriminatedConnectionSettings,
    DataConnectorFirebaseDiscriminatedConnectionSettings,
    DataConnectorForeceiptDiscriminatedConnectionSettings,
    DataConnectorGreenhouseDiscriminatedConnectionSettings,
    DataConnectorHeronDiscriminatedConnectionSettings,
    DataConnectorLunchmoneyDiscriminatedConnectionSettings,
    DataConnectorMercuryDiscriminatedConnectionSettings,
    DataConnectorMergeDiscriminatedConnectionSettings,
    DataConnectorMootaDiscriminatedConnectionSettings,
    DataConnectorOnebrickDiscriminatedConnectionSettings,
    DataConnectorOpenledgerDiscriminatedConnectionSettings,
    DataConnectorPlaidDiscriminatedConnectionSettings,
    DataConnectorPostgresDiscriminatedConnectionSettings,
    DataConnectorRampDiscriminatedConnectionSettings,
    DataConnectorSaltedgeDiscriminatedConnectionSettings,
    DataConnectorSharepointOnpremDiscriminatedConnectionSettings,
    DataConnectorSplitwiseDiscriminatedConnectionSettings,
    DataConnectorStripeDiscriminatedConnectionSettings,
    DataConnectorTellerDiscriminatedConnectionSettings,
    DataConnectorTogglDiscriminatedConnectionSettings,
    DataConnectorTwentyDiscriminatedConnectionSettings,
    DataConnectorVenmoDiscriminatedConnectionSettings,
    DataConnectorWiseDiscriminatedConnectionSettings,
    DataConnectorYodleeDiscriminatedConnectionSettings,
]
