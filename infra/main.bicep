targetScope = 'resourceGroup'

@description('Primary Azure region (function app, plan, storage).')
param location string = resourceGroup().location

@description('Region for resources not offered in the primary region: Static Web Apps (Central US, East US 2, West US 2, West Europe, East Asia only) and Application Insights components.')
param secondaryLocation string = 'westeurope'

@description('Custom domain of the website (bound to the Static Web App via CNAME).')
param siteDomain string = 'www.keiwijs.be'

@description('Phase 2 switch: create the custom-domain binding on the Static Web App. The CNAME for siteDomain must resolve publicly first, because the binding waits for DNS validation. The apex domain is bound by the Deploy infra workflow (TXT token flow), not here.')
param bindCustomDomains bool = false

// Explicit resource names (no hash suffix). Function app and storage account names are global.
param functionAppName string = 'planner-keiwijs-be'
param planName string = 'planner-keiwijs-be-plan'
param storageAccountName string = 'plannerkeiwijsbe'
param staticWebAppName string = 'keiwijs-be-swa'
param logAnalyticsName string = 'keiwijs-be-log'
param appInsightsName string = 'keiwijs-be-appi'
param budgetName string = 'keiwijs-be-budget'

@description('E-mail address that receives budget alerts.')
param budgetContactEmail string

@description('Monthly budget (subscription currency).')
param budgetAmount int = 2

@description('Budget start date (yyyy-MM-01). Leave empty to use the current month at first deployment.')
param budgetStartDate string = ''

param tags object = {
  app: 'keiwijs'
}

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    logAnalyticsName: logAnalyticsName
    appInsightsName: appInsightsName
    location: secondaryLocation
    tags: union(tags, { component: 'shared' })
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: storageAccountName
    location: location
    tags: union(tags, { component: 'planner' })
  }
}

module swa 'modules/swa.bicep' = {
  name: 'swa'
  params: {
    name: staticWebAppName
    // Static Web Apps are only available in a handful of regions; location is metadata only.
    location: secondaryLocation
    tags: union(tags, { component: 'site' })
    customDomains: bindCustomDomains ? [siteDomain] : []
  }
}

var swaUrl = 'https://${swa.outputs.defaultHostname}'
var siteUrl = 'https://${siteDomain}'
// The default hostname stays allowed so the site also works before DNS is live.
var allowedOrigins = '${siteUrl},${swaUrl}'

module functionApp 'modules/functionapp.bicep' = {
  name: 'functionapp'
  params: {
    planName: planName
    functionAppName: functionAppName
    location: location
    tags: union(tags, { component: 'planner' })
    storageAccountName: storage.outputs.name
    blobEndpoint: storage.outputs.blobEndpoint
    queueEndpoint: storage.outputs.queueEndpoint
    tableEndpoint: storage.outputs.tableEndpoint
    deploymentContainerName: storage.outputs.deploymentContainerName
    staticWebsiteEndpoint: storage.outputs.webEndpoint
    appInsightsConnectionString: monitoring.outputs.connectionString
    siteUrl: siteUrl
    allowedOrigins: allowedOrigins
  }
}

module rbac 'modules/rbac.bicep' = {
  name: 'rbac'
  params: {
    storageAccountName: storage.outputs.name
    appInsightsName: monitoring.outputs.appInsightsName
    principalId: functionApp.outputs.principalId
  }
}

module budget 'modules/budget.bicep' = {
  name: 'budget'
  params: {
    name: budgetName
    amount: budgetAmount
    contactEmail: budgetContactEmail
    startDate: budgetStartDate
  }
}

output functionAppName string = functionApp.outputs.name
output functionAppHostName string = functionApp.outputs.hostName
output storageAccountName string = storage.outputs.name
output staticWebsiteEndpoint string = storage.outputs.webEndpoint
output staticWebAppName string = swa.outputs.name
output staticWebAppDefaultHostname string = swa.outputs.defaultHostname
output siteUrl string = siteUrl
