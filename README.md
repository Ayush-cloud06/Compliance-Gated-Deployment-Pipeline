# Compliance-Gated Deployment Pipeline
# The pipeline will continue to evolve toward a full governance, risk, and compliance (GRC) workflow, including environment separation, policy maturity, and automated evidence-driven remediation.

A security-first CI/CD pipeline that enforces preventive and detective cloud compliance controls before and after Terraform-based AWS deployments.

This project demonstrates how modern cloud security teams combine Infrastructure as Code scanning, runtime posture assessment, and policy-as-code to produce verifiable, immutable compliance evidence — not just passing builds.

🎯 OBJECTIVES

- Prevent insecure infrastructure from being deployed
- Detect compliance drift after deployment
- Encode security and compliance requirements as machine-enforceable policies
- Generate audit-ready evidence artifacts stored immutably in Amazon S3
- Follow least-privilege, credentialless authentication using GitHub Actions OIDC


🧠 HIGH-LEVEL ARCHITECTURE

Pipeline Flow (GitHub Actions)

1) Pre-deployment (Preventive Controls)
   - Terraform Plan
   - Checkov static analysis on Terraform IaC

2) Deployment (Human-Gated)
   - Manual approval for production
   - Terraform Apply via OIDC (no long-lived AWS credentials)

3) Post-deployment (Detective Controls)
   - Prowler runtime security scan
   - Boto3-based AWS resource discovery
   - OPA (Rego) policy evaluation

4) Evidence Storage
   - All outputs uploaded to an immutable S3 bucket
   - Versioned, date-partitioned, audit-friendly structure

🔐 AUTHENTICATION & TRUST MODEL

- No AWS access keys are used
- GitHub Actions authenticates to AWS using OIDC

IAM Trust Restrictions:
- Repository scoped
- Branch scoped
- Workflow context aware

Permission Model (Least Privilege):
- Read-only permissions for audits
- Write-only permissions for compliance evidence
- Explicit iam:PassRole where required

🧩 TOOLING & RATIONALE

Terraform  → Infrastructure as Code  
Checkov    → Static security & compliance scanning of Terraform  
Prowler    → Runtime AWS security posture assessment  
OPA (Rego) → Policy-as-Code decision engine  
Boto3      → Live AWS state collection for OPA input  
GitHub Actions → CI/CD orchestration  
Amazon S3  → Immutable compliance evidence storage  



📂 REPOSITORY STRUCTURE


'''
├── README.md
├── policies
│   ├── ec2.rego        
│   ├── iam.rego       
│   └── s3.rego      
├── reports
│   └── opa
│       └── input.json  
├── scripts
│   ├── boto3_ec2_audit.py  
│   ├── boto3_iam_audit.py  
│   ├── boto3_s3_audit.py    
│   └── boto_opa_stream.py  
└── terraform
    ├── outputs.tf
    ├── provider.tf
    ├── resource.tf
    └── variables.tf
'''


🧪 POLICY EVALUATION MODEL (OPA)

OPA does not scan AWS directly.

Instead, the pipeline follows a strict facts → policy → decision model:

1) Boto3 scripts collect facts from AWS
2) Facts are normalized into a single input.json
3) Rego policies evaluate the input
4) OPA outputs decisions, not logs

Example OPA decision output:

'''
{
  "policy": "ec2_public_instance_block",
  "reason": "Public EC2 instance running in production",
  "resource_id": "i-abc123"
}
'''

This separation mirrors real-world GRC architectures used in enterprise environments.

📦 EVIDENCE & AUDIT READINESS

All security outputs are stored in S3 using the following structure:

'''
s3://compliance-evidence-<account-id>/
├── checkov/YYYY-MM-DD/
├── prowler/YYYY-MM-DD/
└── opa/YYYY-MM-DD/
'''

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

🚦 ENFORCEMENT PHILOSOPHY

- Checkov  → Advisory (visibility-first)
- OPA      → Decision authority (policy enforcement)
- Terraform Apply → Human-approved
- Prowler  → Continuous detection

This avoids false confidence while still enabling automation at scale.
