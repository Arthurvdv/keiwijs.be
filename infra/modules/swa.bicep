param name string
param location string
param tags object = {}

// Content is deployed from GitHub Actions with the deployment token (fetched at run time),
// so no repository link and no auto-generated workflow.
resource swa 'Microsoft.Web/staticSites@2023-12-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    stagingEnvironmentPolicy: 'Disabled'
    allowConfigFileUpdates: true
    buildProperties: {
      skipGithubActionWorkflowGeneration: true
    }
  }
}

output name string = swa.name
output defaultHostname string = swa.properties.defaultHostname
