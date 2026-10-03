targetScope = 'resourceGroup'

param name string
@description('Monthly budget amount in the subscription currency.')
param amount int = 2
@description('E-mail address notified at 50% and 100% of the budget.')
param contactEmail string
@description('First day of a month (yyyy-MM-01). Empty = current month at deployment time (keep it stable afterwards by passing the value explicitly).')
param startDate string = ''
param currentMonth string = utcNow('yyyy-MM')

var effectiveStart = empty(startDate) ? '${currentMonth}-01' : startDate

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: name
  properties: {
    category: 'Cost'
    amount: amount
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: effectiveStart
    }
    notifications: {
      actual50: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 50
        thresholdType: 'Actual'
        contactEmails: [
          contactEmail
        ]
      }
      actual100: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Actual'
        contactEmails: [
          contactEmail
        ]
      }
    }
  }
}
