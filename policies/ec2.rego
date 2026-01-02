package compliance.ec2

deny[msg] {
  input.environment == "prod"
  input.ec2.high_severity_findings > 0

  msg := {
    "policy": "ec2_high_severity_block",
    "reason": "High severity EC2 findings detected in production"
  }
}
