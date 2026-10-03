param planName string
param functionAppName string
param location string
param tags object = {}

param storageAccountName string
param blobEndpoint string
param queueEndpoint string
param tableEndpoint string
param deploymentContainerName string
@description('Static website primary endpoint (with or without trailing slash).')
param staticWebsiteEndpoint string
param appInsightsConnectionString string
@description('https URL of the Static Web App (or custom domain) serving the UI.')
param siteUrl string
@description('Comma separated list of allowed CORS origins.')
param allowedOrigins string

param instanceMemoryMB int = 512
param maximumInstanceCount int = 40

var blobBase = endsWith(blobEndpoint, '/') ? substring(blobEndpoint, 0, length(blobEndpoint) - 1) : blobEndpoint
var queueBase = endsWith(queueEndpoint, '/') ? substring(queueEndpoint, 0, length(queueEndpoint) - 1) : queueEndpoint
var tableBase = endsWith(tableEndpoint, '/') ? substring(tableEndpoint, 0, length(tableEndpoint) - 1) : tableEndpoint
var feedBase = endsWith(staticWebsiteEndpoint, '/') ? substring(staticWebsiteEndpoint, 0, length(staticWebsiteEndpoint) - 1) : staticWebsiteEndpoint

resource plan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: planName
  location: location
  tags: tags
  kind: 'functionapp'
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
  }
  properties: {
    reserved: true
  }
}

resource functionApp 'Microsoft.Web/sites@2024-04-01' = {
  name: functionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: '${blobBase}/${deploymentContainerName}'
          authentication: {
            type: 'SystemAssignedIdentity'
          }
        }
      }
      runtime: {
        name: 'python'
        version: '3.13'
      }
      scaleAndConcurrency: {
        instanceMemoryMB: instanceMemoryMB
        maximumInstanceCount: maximumInstanceCount
      }
    }
    siteConfig: {
      http20Enabled: true
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      // The Functions platform answers CORS preflight (OPTIONS) requests itself and only adds
      // Access-Control-* headers for origins listed here; the in-code CORS handling alone is not
      // enough in Azure (it is sufficient under `func start`).
      cors: {
        allowedOrigins: split(allowedOrigins, ',')
        supportCredentials: false
      }
      appSettings: [
        { name: 'AzureWebJobsStorage__accountName', value: storageAccountName }
        { name: 'AzureWebJobsStorage__blobServiceUri', value: blobBase }
        { name: 'AzureWebJobsStorage__queueServiceUri', value: queueBase }
        { name: 'AzureWebJobsStorage__tableServiceUri', value: tableBase }
        { name: 'AzureWebJobsStorage__credential', value: 'managedidentity' }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
        { name: 'STORAGE_ACCOUNT_BLOB_URL', value: blobBase }
        { name: 'FEED_BASE_URL', value: feedBase }
        { name: 'SITE_URL', value: siteUrl }
        { name: 'ALLOWED_ORIGINS', value: allowedOrigins }
      ]
    }
  }
}

output name string = functionApp.name
output hostName string = functionApp.properties.defaultHostName
output principalId string = functionApp.identity.principalId
