# Infrastructure

This directory is a **placeholder**. Production Azure resources (Container Apps Environment, Key Vault, ACR, Azure Files, managed identities, networking) are **hand-managed** today — not provisioned from Terraform in this repo.

Authoritative deployment notes:

- [`docs/reference/infrastructure-and-deployment.md`](../docs/reference/infrastructure-and-deployment.md)
- [`docs/agents/workflow.md`](../docs/agents/workflow.md) (deploy / PR rules)

## Future IaC (not implemented)

If/when Terraform modules land here, candidates include:

- [ ] Container Apps Environment
- [ ] Key Vault with RBAC conditions
- [ ] ACR for OpenClaw / Django images
- [ ] Azure Files for persistent workspaces
- [ ] Monitoring / Log Analytics

Until then, treat empty checklists below this line as aspirational — do not assume `infra/` applies changes to cloud.
