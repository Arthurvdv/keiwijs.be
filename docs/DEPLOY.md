# Deploying to Azure

Three workflows deploy from `main`, each filtered on its own path and also available as `Run workflow`:

| Workflow | Triggers on | Does |
|---|---|---|
| `deploy-infra.yml` | `infra/**` | `az deployment group create` (deployment name `keiwijs-infra`), enables static website hosting, optional domain binding steps |
| `deploy-planner-api.yml` | `planner/**` | zip deploy of `planner/` to the function app (remote build) |
| `deploy-site.yml` | `site/**` | Hugo build, CSP substitution, upload to the Static Web App |

The api and site workflows wait until the `keiwijs-infra` deployment is `Succeeded` before reading its
outputs, so a push that touches several folders at once is safe. GitHub authenticates to Azure with
**OIDC** (a federated credential on an Entra app registration); the only values stored in GitHub are
identifiers, no passwords.

Resources (one resource group, `rg-keiwijs-prod`):

| Resource | Name | Region | Why |
|---|---|---|---|
| Function App (Flex Consumption, Python 3.13, 512 MB) + plan | `planner-keiwijs-be`, `planner-keiwijs-be-plan` | `belgiumcentral` | API, hourly renderer |
| Storage account (LRS, shared keys disabled) | `plannerkeiwijsbe` | `belgiumcentral` | deployment package, WebJobs host, Tables `FeedConfig`/`RolloverLog`, static website `$web` serving `feeds/*.ics` |
| Static Web App (Free) | `keiwijs-be-swa` | `westeurope` | the website (landing + planner); SWA only exists in Central US, East US 2, West US 2, West Europe, East Asia (location is metadata, content is global) |
| Log Analytics + Application Insights | `keiwijs-be-log`, `keiwijs-be-appi` | `westeurope` | App Insights components are not offered in Belgium Central |
| Budget (2/month, e-mail at 50 % and 100 %) | `keiwijs-be-budget` | n/a | cost guard |

Bicep: `infra/main.bicep` with `infra/main.bicepparam` (`location` = primary region, `secondaryLocation` =
`westeurope` for SWA and monitoring). Names are explicit parameters; there is no hash suffix.

## GitHub configuration

Repository **secrets** (Settings → Secrets and variables → Actions → Secrets):

| Secret | Value |
|---|---|
| `AZURE_CLIENT_ID` | client id of the `keiwijs-github-deploy` app registration |
| `AZURE_TENANT_ID` | tenant id |
| `AZURE_SUBSCRIPTION_ID` | subscription id |
| `BUDGET_CONTACT_EMAIL` | address for budget alerts |

Repository **variables**:

| Variable | Value |
|---|---|
| `AZURE_RESOURCE_GROUP` | `rg-keiwijs-prod` |
| `AZURE_LOCATION` | `belgiumcentral` |
| `SITE_DOMAIN` | `www.keiwijs.be` |
| `APEX_DOMAIN` | `keiwijs.be` |

Environment `prod` must exist (no reviewers required). All deploy jobs run in it, which is what the
federated credential subject matches.

## One-time Azure setup

Run with `az` logged in to the right tenant; all steps are idempotent.

```bash
SUB=<subscription-id>
az account set --subscription $SUB
TENANT=$(az account show --query tenantId -o tsv)

for p in Microsoft.Web Microsoft.Storage Microsoft.Insights Microsoft.OperationalInsights \
         Microsoft.Consumption Microsoft.AlertsManagement; do az provider register -n $p; done

az group create -n rg-keiwijs-prod -l belgiumcentral

APP_ID=$(az ad app create --display-name keiwijs-github-deploy --sign-in-audience AzureADMyOrg --query appId -o tsv)
SP_OID=$(az ad sp create --id $APP_ID --query id -o tsv)

# GitHub presents the OIDC subject in the immutable, id-qualified form
# repo:<owner>@<owner-id>/<repo>@<repo-id>:environment:prod. The repository *name* is part of
# that string, so a repository rename needs a new federated credential. The plain form is kept
# as well in case the format changes back.
OWNER_ID=$(gh api users/Arthurvdv -q .id); REPO_ID=$(gh api repos/Arthurvdv/keiwijs.be -q .id)
cat > fc.json <<EOF
{"name":"github-prod-keiwijs","issuer":"https://token.actions.githubusercontent.com",
 "subject":"repo:Arthurvdv@${OWNER_ID}/keiwijs.be@${REPO_ID}:environment:prod",
 "audiences":["api://AzureADTokenExchange"]}
EOF
az ad app federated-credential create --id $APP_ID --parameters @fc.json
sed -e 's/github-prod-keiwijs/github-prod-keiwijs-plain/' -e "s/Arthurvdv@${OWNER_ID}/Arthurvdv/" -e "s/keiwijs.be@${REPO_ID}/keiwijs.be/" fc.json > fc-plain.json
az ad app federated-credential create --id $APP_ID --parameters @fc-plain.json

SCOPE=$(az group show -n rg-keiwijs-prod --query id -o tsv)
for r in "Contributor" "Role Based Access Control Administrator" "Storage Blob Data Contributor"; do
  az role assignment create --assignee-object-id $SP_OID --assignee-principal-type ServicePrincipal \
    --role "$r" --scope "$SCOPE"
done

echo "AZURE_CLIENT_ID=$APP_ID AZURE_TENANT_ID=$TENANT AZURE_SUBSCRIPTION_ID=$SUB"
```

| Role | Why |
|---|---|
| `Contributor` | create/update the resources |
| `Role Based Access Control Administrator` | `infra/modules/rbac.bicep` assigns storage/monitoring roles to the function's managed identity |
| `Storage Blob Data Contributor` | enabling static website hosting is a data-plane call; shared keys are disabled so the workflow uses `--auth-mode login` |

Then in GitHub (`gh` examples):

```bash
gh api -X PUT repos/Arthurvdv/keiwijs.be/environments/prod
gh secret set AZURE_CLIENT_ID -b "$APP_ID"
gh secret set AZURE_TENANT_ID -b "$TENANT"
gh secret set AZURE_SUBSCRIPTION_ID -b "$SUB"
gh secret set BUDGET_CONTACT_EMAIL -b "you@example.org"
gh variable set AZURE_RESOURCE_GROUP -b rg-keiwijs-prod
gh variable set AZURE_LOCATION -b belgiumcentral
gh variable set SITE_DOMAIN -b www.keiwijs.be
gh variable set APEX_DOMAIN -b keiwijs.be
```

If `azure/login` fails with `AADSTS700213`, the error message contains the exact subject GitHub
presented; register that string verbatim as a federated credential.

## What the workflows do

1. **Deploy infra**: `az deployment group create` with `infra/main.bicep` + `main.bicepparam`, then enables
   static website hosting (`az storage blob service-properties update --static-website --auth-mode login`;
   a data-plane property that Bicep cannot set; also creates `$web`). Outputs (function host, storage
   account, static website endpoint, SWA name and hostname) are printed in the job summary.
2. **Deploy planner API**: `Azure/functions-action@v1` zip deploy of `planner/` with remote build
   (`planner/.funcignore` trims the package).
3. **Deploy site**: Hugo build with `--baseURL https://www.keiwijs.be/` (the API base is set in
   `site/config/production/hugo.toml`), substitutes the feed host into the CSP of
   `site/staticwebapp.config.json`, fetches the SWA deployment token at run time (masked, never stored)
   and uploads with `Azure/static-web-apps-deploy@v1`.

Notes:

- `primaryEndpoints.web` is available from ARM as soon as the storage account exists, so `FEED_BASE_URL`
  is set from the Bicep output. The zone label (`z??`) in that host is assigned by Azure at creation.
- The budget `startDate` defaults to the current month at first deployment; if a later run in another
  month is rejected, pin `budgetStartDate` (`yyyy-MM-01`) in `infra/main.bicepparam`.
- An infra change that alters outputs does not re-trigger the api or site workflows; run them by hand.

## Custom domains (DNS at the registrar, mijn.host)

Both domains are bound (done 2026-10-04); this section documents how, for a re-provision.

mijn.host supports A, AAAA, CNAME, SPF, SRV and TXT records (no ALIAS/ANAME, no URL forwarding), so the
apex uses the TXT-token validation plus an A record to the Static Web App's stable inbound IP, as in the
[Azure docs for external DNS providers](https://learn.microsoft.com/azure/static-web-apps/apex-domain-external).

| Step | Who | What |
|---|---|---|
| 1 | workflow | `Deploy infra` with default inputs creates everything. Read `staticWebAppDefaultHostname` from the job summary. |
| 2 | you | Registrar: `CNAME www -> <staticWebAppDefaultHostname>.` (TTL 300). Delete the registrar's parking A/AAAA records (apex and `*`). Check with `nslookup -type=CNAME www.keiwijs.be 1.1.1.1`. |
| 3 | you | Portal → `keiwijs-be-swa` → Custom domains → Add `www.keiwijs.be` (CNAME validation). Or `Deploy infra` with **bindCustomDomains = true**: that works too, but the deployment then hangs for 20+ minutes polling the operation (status "Forbidden" on the poll) and has to be cancelled, so the portal is the better route. |
| 4 | you | Portal → Custom domains → Add `keiwijs.be` → TXT → Generate code. Or `Deploy infra` with **bindApex = true**, which prints the token and IP in the job summary. The stable inbound IP is also in the JSON view of the Static Web App (`stableInboundIP`, currently `20.82.12.44`). |
| 5 | you | Registrar: `TXT @ = <token>` and `A @ = <stableInboundIP>`. Validation took about 7 minutes; if it stays `Validating` for more than 30 minutes, add the same TXT at `_dnsauth.www.keiwijs.be` as well. |
| 6 | you | Portal → Custom domains → `www.keiwijs.be` → **Set default**. Azure then 301s `keiwijs.be` and the `*.azurestaticapps.net` hostname to `www.keiwijs.be`. This setting has no CLI or Bicep equivalent. |

Check: `az staticwebapp hostname list -n keiwijs-be-swa -g rg-keiwijs-prod -o table` shows both `Ready`.
The Static Web App Free tier allows two custom domains, which `www.keiwijs.be` and `keiwijs.be` use up.
Keep the validation TXT record; it is harmless and saves a step if the binding ever needs re-validation.

## Finding the URLs

```bash
az deployment group show -g rg-keiwijs-prod -n keiwijs-infra --query properties.outputs
az storage account show -n plannerkeiwijsbe -g rg-keiwijs-prod --query primaryEndpoints.web -o tsv   # feeds
az staticwebapp show -n keiwijs-be-swa -g rg-keiwijs-prod --query defaultHostname -o tsv            # site
az functionapp show -n planner-keiwijs-be -g rg-keiwijs-prod --query defaultHostName -o tsv         # API
```

## Secrets and rotation

No long-lived secrets exist: GitHub uses OIDC, the function uses its managed identity, the storage account
has shared keys disabled, and the SWA deployment token is fetched per run. Nothing to rotate. To revoke
GitHub's access, delete the federated credential or the app registration.

## Operations

Ops routes need a function key (`host.json` has an empty route prefix, so there is no `/api` in front):

```bash
KEY=$(az functionapp keys list -n planner-keiwijs-be -g rg-keiwijs-prod --query functionKeys.default -o tsv)
H=https://planner-keiwijs-be.azurewebsites.net
curl -X POST "$H/ops/render" -H "x-functions-key: $KEY"                 # render all feeds now
curl -X POST "$H/ops/render?rowKey=<hash>" -H "x-functions-key: $KEY"   # one feed
curl -X POST "$H/ops/rollover?dryRun=1" -H "x-functions-key: $KEY"      # show due rollovers
```

`GET /healthz` reports `failingFeeds` (feeds with 30+ consecutive upstream failures).

## Cost

Expected: well under the 2/month budget.

- Flex Consumption: monthly free grant of 250,000 executions and 100,000 GB-s per subscription. An hourly
  render of all feeds plus light interactive traffic stays inside it (feeds are served by Blob Storage, not
  by the function). No always-ready instances.
- Static Web Apps Free: 0.
- Storage (LRS, Hot): small files and tables, cents per month.
- Log Analytics capped at 0.1 GB/day, 30-day retention; Application Insights is workspace-based.
- The budget alerts at 50 % and 100 % of actual spend by e-mail; it does not stop anything.

## History

- 2026-10-03: first deployment as `smartschool-planner-filter` in `rg-ssplanner-prod` (default Azure hostnames).
- 2026-10-04: moved to keiwijs.be: repository renamed, resources re-provisioned in `rg-keiwijs-prod` with
  explicit names, planner served at `www.keiwijs.be/planner/`, both custom domains bound. The old resource
  group `rg-ssplanner-prod` was deleted after verification.
