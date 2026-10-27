<!-- sdlc:auto:start adr -->
# ADR-0004: Use AWS for Cloud

Status: Accepted  
Date: 2026-10-27

## Context and Problem Statement

Which Cloud technology does the project use? Decided in architecture v1.

## Considered Options

- AWS
- GCP
- Azure

## Decision Outcome

Chosen option: AWS, because S3 holds the original PDFs, RDS runs Postgres, and ECS Fargate runs the API, worker and Redis container, giving one provider for storage, compute and database at this scale.

## Consequences

Running Redis as a self-managed Fargate container (per the approved redis:7-alpine image) instead of ElastiCache keeps dev simple but means the team owns its persistence/restart behavior.
<!-- sdlc:auto:end adr -->