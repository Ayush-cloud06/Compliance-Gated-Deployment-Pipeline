# METADATA
# title: Aggregate decision across all domains
package compliance

deny := (data.compliance.ec2.deny | data.compliance.iam.deny) | data.compliance.s3.deny
