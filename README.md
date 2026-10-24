# Compliance-Gated Deployment Pipeline

> **Status: being modernised.** This repo started as a learning project (Jan 2026) and is being
> rebuilt in public, one PR at a time. Some sections below describe the *target* design; the
> audit and modernisation work is tracked through issues and PRs.
>
> The pipeline will continue to evolve toward a full governance, risk, and compliance (GRC)
> workflow, including environment separation, policy maturity, and automated evidence-driven
> remediation.

A security-first CI/CD pipeline that enforces preventive and detective cloud compliance controls before and after Terraform-based AWS deployments.

This project demonstrates how modern cloud security teams combine Infrastructure as Code scanning, runtime posture assessment, and policy-as-code to produce verifiable, immutable compliance evidence — not just passing builds.

## 🎯 Objectives

- Prevent insecure infrastructure from being deployed
- Detect compliance drift after deployment
- Encode security and compliance requirements as machine-enforceable policies
- Generate audit-ready evidence artifacts stored immutably in Amazon S3
- Follow least-privilege, credentialless authentication using GitHub Actions OIDC

## 🧠 High-Level Architecture

Pipeline flow (GitHub Actions):

1. **Pre-deployment (preventive controls)**
   - Terraform Plan
   - Checkov static analysis on Terraform IaC
2. **Deployment (human-gated)**
   - Manual approval for production
   - Terraform Apply via OIDC (no long-lived AWS credentials)
3. **Post-deployment (detective controls)**
   - Prowler runtime security scan
   - Boto3-based AWS resource discovery
   - OPA (Rego) policy evaluation
4. **Evidence storage**
   - All outputs uploaded to an immutable S3 bucket
   - Versioned, date-partitioned, audit-friendly structure

## 🔐 Authentication & Trust Model

- No AWS access keys are used
- GitHub Actions authenticates to AWS using OIDC

IAM trust restrictions:
- Repository scoped
- Branch scoped
- Workflow context aware

Permission model (least privilege):
- Read-only permissions for audits
- Write-only permissions for compliance evidence
- Explicit `iam:PassRole` where required

## 🧩 Tooling & Rationale

| Tool | Role |
|---|---|
| Terraform | Infrastructure as Code |
| Checkov | Static security & compliance scanning of Terraform |
| Prowler | Runtime AWS security posture assessment |
| OPA (Rego) | Policy-as-Code decision engine |
| Boto3 | Live AWS state collection for OPA input |
| moto | Local AWS mock for development and tests |
| GitHub Actions | CI/CD orchestration |
| Amazon S3 | Immutable compliance evidence storage |

## 📂 Repository Structure

```
├── .github/workflows/
│   ├── ci.yml              # lint checks on every PR
│   └── compliance.yml      # compliance pipeline (manual for now)
├── examples/opa/
│   ├── input.json          # sample OPA input with violations
│   └── input_clean.json    # sample OPA input with no violations
├── policies/               # Rego v1 policies (package compliance.*)
│   ├── compliance.rego     # aggregate: data.compliance.deny
│   ├── ec2.rego / iam.rego / s3.rego
│   ├── lib/lib.rego        # shared helpers (is_prod, decision shape)
│   └── *_test.rego         # opa test (package tests.*)
├── tests/                  # pytest + moto tests for the collectors
├── scripts/                # Boto3 collectors → OPA input
│   ├── boto3_ec2_audit.py
│   ├── boto3_iam_audit.py
│   ├── boto3_s3_audit.py
│   └── boto_opa_stream.py
├── terraform/
│   ├── outputs.tf
│   ├── provider.tf
│   ├── resource.tf
│   └── variables.tf
├── .pre-commit-config.yaml # local mirror of CI lint checks
├── pyproject.toml          # ruff config
├── requirements-dev.txt    # local dev deps (boto3, moto, pytest, pre-commit)
└── README.md
```

## 🧪 Policy Evaluation Model (OPA)

OPA does not scan AWS directly.

Instead, the pipeline follows a strict facts → policy → decision model:

1. Boto3 scripts collect facts from AWS
2. Facts are normalized into a single `input.json`
3. Rego policies evaluate the input
4. OPA outputs decisions, not logs

Example OPA decision output:

```json
{
  "policy": "ec2_public_instance_block",
  "title": "No public EC2 instances in production",
  "severity": "high",
  "resource_type": "ec2_instance",
  "resource_id": "i-abc123",
  "reason": "Public EC2 instance running in production"
}
```

Every policy emits one decision per resource in this shape. `data.compliance.deny` is the
union across all domains. Policy title, ID and severity come from each rule's `# METADATA`.

This separation mirrors real-world GRC architectures used in enterprise environments.

## 📦 Evidence & Audit Readiness

All security outputs are stored in S3 using the following structure:

```
s3://compliance-evidence-<account-id>/
├── checkov/YYYY-MM-DD/
├── prowler/YYYY-MM-DD/
└── opa/YYYY-MM-DD/
```

Each pipeline run is:
- Immutable
- Versioned
- Fully traceable to:
  - Git commit
  - Actor
  - Workflow run ID
  - Timestamp

This enables:
- External audits
- Internal security reviews
- Historical drift analysis

## 🚦 Enforcement Philosophy

| Component | Role |
|---|---|
| Checkov | Advisory (visibility-first) |
| OPA | Decision authority (policy enforcement) |
| Terraform Apply | Human-approved |
| Prowler | Continuous detection |

This avoids false confidence while still enabling automation at scale.

## 🛠 Local Development

Requires Python 3.10+, [uv](https://docs.astral.sh/uv/), Terraform, OPA, and Docker (for the actionlint/tflint hooks).

```bash
# Python env with boto3 + moto
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements-dev.txt

# Git hooks: run the same lint checks as CI before every commit
pre-commit install
pre-commit run --all-files

# Local mock AWS (no real account needed)
moto_server -p 5000

# Collect EC2/IAM/S3 facts into OPA input (against moto, in another shell)
AWS_ENDPOINT_URL=http://localhost:5000 AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
  python scripts/boto_opa_stream.py --environment prod --output reports/opa/input.json

# Tests
pytest                       # collectors (moto)
opa test policies -v         # policies

# Evaluate the policies against the sample inputs
opa eval -d policies -i examples/opa/input.json 'data.compliance.deny' --format pretty
opa eval -d policies -i examples/opa/input_clean.json 'data.compliance.deny' --format pretty

# Terraform checks (no AWS credentials needed)
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
terraform -chdir=terraform fmt -check
```
