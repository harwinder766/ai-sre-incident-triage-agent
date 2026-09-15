# Payment API Database Connection Pool Runbook

## Symptoms

Common symptoms include:

- Database connection pool exhausted
- Database connection timeout
- Increased payment API error rate
- Requests waiting for database connections
- Increased request latency

## Investigation

Check the following Prometheus metrics:

- payment_requests_total
- payment_errors_total
- payment_request_duration_seconds

Check application logs for:

- connection pool exhausted
- database timeout
- database connection refused

Check recent GitHub commits for changes involving:

- database connection handling
- SQL queries
- connection pool configuration
- transaction management

## Remediation

If the connection pool is exhausted:

1. Check whether the error rate is increasing.
2. Check recent application deployments.
3. Check database connection usage.
4. If the issue is caused by a connection leak, restart the affected
   application workers.
5. Verify that the error rate returns to normal.

## Verification

The incident should not be considered resolved until:

- error rate decreases
- request latency returns to normal
- database connection errors disappear from logs