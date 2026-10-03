targetScope = 'resourceGroup'

@description('Primary Azure region (function app, plan, storage).')
param location string = resourceGroup().location

@description('Region for resources not offered in the primary region: Static Web Apps (Central US, East US 2, West US 2, West Europe, East Asia only) and Application Insights components.')
param secondaryLocation string = 'westeurope'

@description('Base name used as prefix for all resources.')
@minLength(3)
@maxLength(12)
param baseName string = 'ssplanner'

@description('E-mail address that receives budget alerts.')
param budgetContactEmail string

@description('Optional custom domain (e.g. planner.example.org) of the Static Web App; added to SITE_URL/CORS allow-list. Leave empty for none.')
param siteCustomDomain string = ''

@description('Monthly budget (subscription currency).')
param budgetAmount int = 2

@description('Budget start date (yyyy-MM-01). Leave empty to use the current month at first deployment.')
param budgetStartDate string = ''

param tags object = {
  app: 'smartschool-planner-filter'
}

var suffix = take(uniqueString(resourceGroup().id), 6)
var storageName = toLower(take(replace('${baseName}st${suffix}', '-', ''), 24))
var functionAppName = '${baseName}-func-${suffix}'

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    logAnalyticsName: '${baseName}-log-${suffix}'
    appInsightsName: '${baseName}-appi-${suffix}'
    location: secondaryLocation
    tags: tags
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: storageName
    location: location
    tags: tags
  }
}

module swa 'modules/swa.bicep' = {
  name: 'swa'
  params: {
    name: '${baseName}-swa-${suffix}'
    // Static Web Apps are only available in a handful of regions; location is metadata only.
    location: secondaryLocation
    tags: tags
  }
}

var swaUrl = 'https://${swa.outputs.defaultHostname}'
var customUrl = empty(siteCustomDomain) ? '' : 'https://${siteCustomDomain}'
var siteUrl = empty(customUrl) ? swaUrl : customUrl
var allowedOrigins = empty(customUrl) ? swaUrl : '${swaUrl},${customUrl}'

module functionApp 'modules/functionapp.bicep' = {
  name: 'functionapp'
  params: {
    planName: '${baseName}-plan-${suffix}'
    functionAppName: functionAppName
    location: location
    tags: tags
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
    name: '${baseName}-budget'
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
