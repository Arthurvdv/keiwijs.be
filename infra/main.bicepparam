using 'main.bicep'

param baseName = 'ssplanner'
param secondaryLocation = 'westeurope'
// Passed by the Deploy workflow from the BUDGET_CONTACT_EMAIL repository secret.
param budgetContactEmail = 'REPLACE-ME@example.org'
param siteCustomDomain = ''
param budgetAmount = 2
