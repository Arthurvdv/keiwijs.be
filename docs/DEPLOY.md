# Deploying to Azure

Everything is deployed by `.github/workflows/deploy.yml` on every push to `main` (and on manual
`Run workflow`). GitHub authenticates to Azure with **OIDC** (a federated credential on an Entra app
registration); the only values stored in GitHub are identifiers, no passwords.

Resources (one resource group):

| Resource | Region | Why |
|---|---|---|
| Function App (Flex Consumption, Python 3.13, 512 MB) + plan | `belgiumcentral` | API, hourly renderer |
| Storage account (LRS, shared keys disabled) | `belgiumcentral` | deployment package, WebJobs host, Tables `FeedConfig`/`RolloverLog`, static website `$web` serving `feeds/*.ics` |
| Static Web App (Free) | `westeurope` | Hugo site; SWA only exists in Central US, East US 2, West US 2, West Europe, East Asia (location is metadata, content is global) |
| Log Analytics + Application Insights | `westeurope` | App Insights components are not offered in Belgium Central |
| Budget (2/month, e-mail at 50 % and 100 %) | n/a | cost guard |

Bicep: `infra/main.bicep` (`location` = primary region, `secondaryLocation` = `westeurope` for SWA and monitoring).

## GitHub configuration

Repository **secrets** (Settings → Secrets and variables → Actions → Secrets):

| Secret | Value |
|---|---|
| `AZURE_CLIENT_ID` | client id of the `ssplanner-github-deploy` app registration |
| `AZURE_TENANT_ID` | tenant id |
| `AZURE_SUBSCRIPTION_ID` | subscription id |
| `BUDGET_CONTACT_EMAIL` | address for budget alerts |

Repository **variables**:

| Variable | Value |
|---|---|
| `AZURE_RESOURCE_GROUP` | `rg-ssplanner-prod` |
| `AZURE_LOCATION` | `belgiumcentral` |
| `SITE_CUSTOM_DOMAIN` | optional, e.g. `planner.example.org`; unset for none |

Environment `prod` must exist (no reviewers required). All three deploy jobs run in it, which is what the
federated credential subject matches.

## One-time Azure setup

Already done for the production subscription on 2026-10-03; repeat only for a new subscription or a fork.
Run with `az` logged in to the right tenant; all steps are idempotent.

```bash
SUB=<subscription-id>
az account set --subscription $SUB
TENANT=$(az account show --query tenantId -o tsv)

for p in Microsoft.Web Microsoft.Storage Microsoft.Insights Microsoft.OperationalInsights \
         Microsoft.Consumption Microsoft.AlertsManagement; do az provider register -n $p; done

az group create -n rg-ssplanner-prod -l belgiumcentral

APP_ID=$(az ad app create --display-name ssplanner-github-deploy --sign-in-audience AzureADMyOrg --query appId -o tsv)
SP_OID=$(az ad sp create --id $APP_ID --query id -o tsv)

# GitHub presents the OIDC subject with the owner and repository ids embedded
# (repo:<owner>@<owner-id>/<repo>@<repo-id>:environment:prod). Register that exact
# subject; the plain form is kept as well in case the format changes back.
OWNER_ID=$(gh api users/Arthurvdv -q .id); REPO_ID=$(gh api repos/Arthurvdv/smartschool-planner-filter -q .id)
cat > fc.json <<EOF
{"name":"github-prod-ids","issuer":"https://token.actions.githubusercontent.com",
 "subject":"repo:Arthurvdv@${OWNER_ID}/smartschool-planner-filter@${REPO_ID}:environment:prod",
 "audiences":["api://AzureADTokenExchange"]}
EOF
az ad app federated-credential create --id $APP_ID --parameters @fc.json
sed -e 's/github-prod-ids/github-prod/' -e "s/Arthurvdv@${OWNER_ID}/Arthurvdv/" -e "s/filter@${REPO_ID}/filter/" fc.json > fc-plain.json
az ad app federated-credential create --id $APP_ID --parameters @fc-plain.json

SCOPE=$(az group show -n rg-ssplanner-prod --query id -o tsv)
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
gh api -X PUT repos/Arthurvdv/smartschool-planner-filter/environments/prod
gh secret set AZURE_CLIENT_ID -b "$APP_ID"
gh secret set AZURE_TENANT_ID -b "$TENANT"
gh secret set AZURE_SUBSCRIPTION_ID -b "$SUB"
gh secret set BUDGET_CONTACT_EMAIL -b "you@example.org"
gh variable set AZURE_RESOURCE_GROUP -b rg-ssplanner-prod
gh variable set AZURE_LOCATION -b belgiumcentral
```

## What the Deploy workflow does

1. `infra` job: `az deployment group create` with `infra/main.bicep`, then enables static website hosting
   (`az storage blob service-properties update --static-website --auth-mode login`; a data-plane property
   that Bicep cannot set; also creates `$web`). Outputs: function host, storage account, static website
   endpoint, SWA name and hostname.
2. `api` job: `Azure/functions-action@v1` zip deploy with remote build (`.funcignore` trims the package).
3. `site` job: Hugo build with `HUGO_PARAMS_APIBASE=https://<function host>` and `--baseURL` of the SWA
   (or the custom domain), substitutes the API and feed hosts into the CSP of `staticwebapp.config.json`,
   fetches the SWA deployment token at run time (masked, never stored) and uploads with
   `Azure/static-web-apps-deploy@v1`.

Notes:

- `primaryEndpoints.web` is available from ARM as soon as the storage account exists, so `FEED_BASE_URL`
  is set from the Bicep output. If it is ever empty, set it afterwards with
  `az functionapp config appsettings set --settings FEED_BASE_URL=https://<acct>.z?.web.core.windows.net`.
- The budget `startDate` defaults to the current month at first deployment; if a later run in another
  month is rejected, pin `budgetStartDate` (`yyyy-MM-01`) in `infra/main.bicepparam`.

## Finding the URLs

```bash
az deployment group show -g rg-ssplanner-prod -n main-<run-id> --query properties.outputs
az storage account show -n <storage> -g rg-ssplanner-prod --query primaryEndpoints.web -o tsv   # feeds
az staticwebapp show -n <swa-name> -g rg-ssplanner-prod --query defaultHostname -o tsv          # site
az functionapp show -n <func-name> -g rg-ssplanner-prod --query defaultHostName -o tsv          # API
```

The outputs are also printed in the `infra` job log.

## Custom domain on the Static Web App (optional)

1. Create a CNAME from `planner.example.org` to the SWA default hostname.
2. `az staticwebapp hostname set -n <swa-name> -g rg-ssplanner-prod --hostname planner.example.org`
   (apex domains need TXT validation, see the portal).
3. Set the repo variable `SITE_CUSTOM_DOMAIN=planner.example.org` and re-run Deploy: this updates
   `SITE_URL`, the CORS allow-list (default hostname and custom domain) and the Hugo `--baseURL`.

## Secrets and rotation

No long-lived secrets exist: GitHub uses OIDC, the function uses its managed identity, the storage account
has shared keys disabled, and the SWA deployment token is fetched per run. Nothing to rotate. To revoke
GitHub's access, delete the federated credential or the app registration.

## Operations

Ops routes need a function key (`host.json` has an empty route prefix, so there is no `/api` in front):

```bash
KEY=$(az functionapp keys list -n <func-name> -g rg-ssplanner-prod --query functionKeys.default -o tsv)
curl -X POST "https://<func-host>/ops/render" -H "x-functions-key: $KEY"                 # render all feeds now
curl -X POST "https://<func-host>/ops/render?rowKey=<hash>" -H "x-functions-key: $KEY"   # one feed
curl -X POST "https://<func-host>/ops/rollover?dryRun=1" -H "x-functions-key: $KEY"      # show due rollovers
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
