param name string
param location string
param tags object = {}

@description('Subdomains to bind with CNAME validation (e.g. www.keiwijs.be). Each CNAME must resolve publicly before deployment: the binding is a long-running operation that waits for validation. Apex domains need the TXT-token flow and are bound by CLI instead.')
param customDomains array = []

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

resource domains 'Microsoft.Web/staticSites/customDomains@2023-12-01' = [
  for domain in customDomains: {
    parent: swa
    name: domain
    properties: {
      validationMethod: 'cname-delegation'
    }
  }
]

output name string = swa.name
output defaultHostname string = swa.properties.defaultHostname
