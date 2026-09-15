# Payment API High Latency Runbook

## Symptoms

- Payment API requests take longer than normal.
- Average request latency exceeds 2 seconds.
- Requests may eventually timeout.

## Investigation

Check:

- payment_request_duration_seconds
- payment_requests_total
- payment_errors_total

Inspect recent application commits.

Inspect application logs for:

- timeout
- slow database queries
- external API delays

## Remediation

If latency is caused by an application-level problem:

1. Identify the recent change.
2. Check whether the change correlates with the incident start time.
3. Escalate for rollback if the deployment is responsible.

## Verification

Confirm that:

- average latency is below the alert threshold
- timeout errors have stopped
- error rate has returned to normal