using 'main.bicep'

param secondaryLocation = 'westeurope'
param siteDomain = 'www.keiwijs.be'
// Phase 2 (after the www CNAME resolves): the Deploy infra workflow passes bindCustomDomains=true
// explicitly. Flip this default to true once the cutover is done so a re-provision reproduces the binding.
param bindCustomDomains = false
// Passed by the Deploy infra workflow from the BUDGET_CONTACT_EMAIL repository secret.
param budgetContactEmail = 'REPLACE-ME@example.org'
param budgetAmount = 2
