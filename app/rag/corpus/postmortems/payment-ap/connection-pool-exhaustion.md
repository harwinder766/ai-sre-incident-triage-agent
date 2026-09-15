# Payment API Connection Pool Exhaustion Postmortem

## Incident Summary

The payment service experienced elevated failures because application
workers exhausted the database connection pool.

## Root Cause

A code change introduced a connection lifecycle problem.

Connections were not released correctly under an error condition.

## Evidence

Relevant log messages included database connection timeout and
connection pool exhaustion.

The payment error rate increased significantly during the incident.

## Remediation

Workers were restarted to restore service.

The connection lifecycle implementation was fixed.

Additional monitoring was added.

## Prevention

Future changes involving database access should be reviewed for:

- connection leaks
- transaction lifecycle problems
- pool exhaustion
- timeout handling
