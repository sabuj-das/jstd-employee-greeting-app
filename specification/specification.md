# Specification

> **Guidelines**: Read [guidelines.md](./guidelines.md) before executing ANY tasks below.

Check off items as completed.

## Solution Setup

- [ ] Create asset directories:
  ```bash
  mkdir -p assets/workflows/employee-greeting-orchestrator
  mkdir -p assets/workflows/work-anniversary-email-workflow
  mkdir -p assets/workflows/birthday-greeting-email-workflow
  ```
- [ ] Invoke `setup-solution` skill to create `solution.yaml` and `asset.yaml` files for every workflow asset
- [ ] Validate all `asset.yaml` and `solution.yaml` files exist and are well-formed

## Asset Implementation

- [ ] Execute `specification/employee-greeting-orchestrator/specification.md` (all items)
- [ ] Execute `specification/work-anniversary-email-workflow/specification.md` (all items)
- [ ] Execute `specification/birthday-greeting-email-workflow/specification.md` (all items)

## Cross-Implementation Compatibility Check

- [ ] Verify that the orchestrator's `"Trigger Anniversary Workflow"` HTTP Request node posts to the correct path (`/webhook/work-anniversary-email`) matching the Work Anniversary sub-workflow's Webhook node path
- [ ] Verify that the orchestrator's `"Trigger Birthday Workflow"` HTTP Request node posts to the correct path (`/webhook/birthday-greeting-email`) matching the Birthday Greeting sub-workflow's Webhook node path
- [ ] Verify that the payload shape sent by the orchestrator (`{ name, email, dateOfJoining }` for anniversary; `{ name, email, dateOfBirth }` for birthday) matches what the sub-workflows expect in their Set nodes (`$json.body.name`, `$json.body.email`, etc.)
- [ ] Confirm that all three workflows reference `CUSTOM.sapAgent` consistently and that SAP AI Core credentials are expected uniformly across all three workflows
- [ ] Confirm all three `asset.yaml` files are referenced in `solution.yaml`
