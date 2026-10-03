@description('Globally unique storage account name (3-24 lowercase alphanumerics).')
param name string
param location string
param tags object = {}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    // Identity-based access only: no account keys / SAS.
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    // The static website ($web) endpoint is always served anonymously, independent of this
    // setting (see "Static website hosting in Azure Storage"), so anonymous access to the
    // regular blob endpoint can stay disabled.
    allowBlobPublicAccess: false
    publicNetworkAccess: 'Enabled'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

// Flex Consumption deployment package container.
resource deployments 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'deployments'
  properties: {
    publicAccess: 'None'
  }
}

output id string = storage.id
output name string = storage.name
output blobEndpoint string = storage.properties.primaryEndpoints.blob
output queueEndpoint string = storage.properties.primaryEndpoints.queue
output tableEndpoint string = storage.properties.primaryEndpoints.table
output webEndpoint string = storage.properties.primaryEndpoints.web
output deploymentContainerName string = deployments.name
