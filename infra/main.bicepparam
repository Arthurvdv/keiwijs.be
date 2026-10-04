using 'main.bicep'

param secondaryLocation = 'westeurope'
param siteDomain = 'www.keiwijs.be'
// Both custom domains (www.keiwijs.be, keiwijs.be) were bound once on 2026-10-04 and stay in place
// across deployments (incremental mode). Keep this false: the Bicep binding works but the deployment
// then hangs for 20+ minutes polling the operation. See docs/DEPLOY.md, "Custom domains".
param bindCustomDomains = false
// Passed by the Deploy infra workflow from the BUDGET_CONTACT_EMAIL repository secret.
param budgetContactEmail = 'REPLACE-ME@example.org'
param budgetAmount = 2
