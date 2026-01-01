# Compliance-Gated-Deployment-Pipeline
GitHub Actions pipeline that enforces security and compliance policies before Terraform deployments using Checkov, Prowler, and OPA (Rego).


## 📂 Repository Structure

```text
.
├── README.md
├── policies
│   ├── iam.rego
│   └── s3.rego
├── reports
├── scripts
│   └── boto3_audit.py
└── terraform
    ├── outputs.tf
    ├── provider.tf
    ├── resource.tf
    └── variables.tf