# Specification: work-anniversary-email-workflow

> **Guidelines**: Read [guidelines-n8n-workflow.md](../guidelines-n8n-workflow.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` before building any node

---

## Workflow: Work Anniversary Email (`assets/workflows/work-anniversary-email-workflow/`)

### Purpose
Called by the Main Orchestrator for each employee whose work anniversary date (DD.MM of `dateOfJoining`) matches today. Generates a personalized work anniversary email using a SAP Agent and dispatches it via the available email node.

---

## Nodes to Build

### Trigger
- [ ] Add a **Webhook** trigger node named `"Work Anniversary Email Received"` with method POST
  - Path: `work-anniversary-email`
  - Response mode: `responseNode`
  - Expected payload: `{ name, email, dateOfJoining }`

### Extract Employee Data
- [ ] Add a **Set** node named `"Set Employee Fields"` that maps:
  - `employeeName` ← `$json.body.name`
  - `employeeEmail` ← `$json.body.email`
  - `dateOfJoining` ← `$json.body.dateOfJoining`

### Calculate Years of Service
- [ ] Add a **Code** node named `"Calculate Tenure"` that:
  - Parses `dateOfJoining` (DD.MM.YYYY format) and computes years of service from today
  - Returns `{ employeeName, employeeEmail, dateOfJoining, yearsOfService }`

### AI Email Generation (SAP Agent)
- [ ] Look up `CUSTOM.sapAgent` from the node catalog before adding it
- [ ] Add a **SAP Agent** node named `"Generate Anniversary Email"` that:
  - Receives `employeeName` and `yearsOfService`
  - Is instructed to generate a warm, personalized work anniversary email in plain text
  - System prompt: "You are an HR communications assistant. Write a warm and sincere work anniversary email congratulating {{employeeName}} on completing {{yearsOfService}} year(s) with the company. Address them by first name. Keep it to 3–4 sentences. Return only the email body text, no subject line."
  - Returns the generated email body as a plain string in the response

### Set Email Subject
- [ ] Add a **Set** node named `"Set Email Subject"` that:
  - Sets `subject` to `"Happy Work Anniversary, {{employeeName}}!"`
  - Carries forward `employeeEmail` and `emailBody` from the agent output

### Send Email (Placeholder)
- [ ] Look up `n8n-nodes-base.microsoftOutlook` from the node catalog before adding it
- [ ] Add a **Microsoft Outlook** node named `"Send Anniversary Email"` that:
  - Sends to `employeeEmail`
  - Subject: from `Set Email Subject`
  - Body: from the SAP Agent output (email body text)
  - NOTE: Email provider is a placeholder — Microsoft Outlook node is used as the default. Replace with the confirmed provider when known.

### Respond to Orchestrator
- [ ] Add a **Respond to Webhook** node named `"Respond — Sent"` that returns HTTP 200 with `{ "status": "sent", "employee": "{{employeeName}}" }`

### Error Path
- [ ] Add error handling so that if any node fails, a **Respond to Webhook** node named `"Respond — Error"` returns HTTP 500 with `{ "status": "error", "employee": "{{employeeName}}", "reason": "..." }`

---

## Asset Setup

- [ ] Create `assets/workflows/work-anniversary-email-workflow/asset.yaml`
- [ ] After writing the `.n8n.json`, run the `generate-workflow-asset.js` script to produce `workflow` and `provides.apis[]` for `asset.yaml`
- [ ] Fill in `description` for each `kind: rest` entry in `asset.yaml`
- [ ] Add entry in `solution.yaml`:
  ```yaml
    - ref: ./assets/workflows/work-anniversary-email-workflow/asset.yaml
  ```

## Validation

- [ ] Confirm the Webhook trigger is the entry point and every node is reachable from it
- [ ] Confirm both success and error paths each contain a `respondToWebhook` node
- [ ] Run `validate-n8n-workflow` before writing the file — fix all errors
- [ ] Write the final file to `assets/workflows/work-anniversary-email-workflow/work-anniversary-email-workflow.n8n.json` in a single write call
