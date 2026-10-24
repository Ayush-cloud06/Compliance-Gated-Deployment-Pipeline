# METADATA
# title: Shared helpers for compliance policies
package compliance.lib

is_prod if input.environment == "prod"

# Standard decision shape, built from the calling rule's METADATA.
decision(meta, resource_type, resource_id, reason) := {
	"policy": meta.custom.policy_id,
	"title": meta.title,
	"severity": meta.custom.severity,
	"resource_type": resource_type,
	"resource_id": resource_id,
	"reason": reason,
}
