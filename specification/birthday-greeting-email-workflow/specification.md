# Specification: birthday-greeting-email-workflow

> **Guidelines**: Read [guidelines-n8n-workflow.md](../guidelines-n8n-workflow.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` before building any node

---

## Workflow: Birthday Greeting Email (`assets/workflows/birthday-greeting-email-workflow/`)

### Purpose
Called by the Main Orchestrator for each employee whose birthday (DD.MM of `dateOfBirth`) matches today. Generates a personalized birthday greeting email using a SAP Agent and dispatches it via the available email node.

---

## Nodes to Build

### Trigger
- [ ] Add a **Webhook** trigger node named `"Birthday Greeting Email Received"` with method POST
  - Path: `birthday-greeting-email`
  - Response mode: `responseNode`
  - Expected payload: `{ name, email, dateOfBirth }`

### Extract Employee Data
- [ ] Add a **Set** node named `"Set Employee Fields"` that maps:
  - `employeeName` ← `$json.body.name`
  - `employeeEmail` ← `$json.body.email`
  - `dateOfBirth` ← `$json.body.dateOfBirth`

### AI Email Generation (SAP Agent)
- [ ] Look up `CUSTOM.sapAgent` from the node catalog before adding it
- [ ] Add a **SAP Agent** node named `"Generate Birthday Email"` that:
  - Receives `employeeName`
  - Is instructed to generate a warm, personalized birthday greeting email in plain text
  - System prompt: "You are an HR communications assistant. Write a warm and cheerful birthday greeting email for {{employeeName}}. Address them by first name. Keep it to 3–4 sentences. Return only the email body text, no subject line."
  - Returns the generated email body as a plain string in the response

### Set Email Subject
- [ ] Add a **Set** node named `"Set Email Subject"` that:
  - Sets `subject` to `"Happy Birthday, {{employeeName}}! 🎂"`
  - Carries forward `employeeEmail` and `emailBody` from the agent output

### Send Email (Placeholder)
- [ ] Look up `n8n-nodes-base.microsoftOutlook` from the node catalog before adding it
- [ ] Add a **Microsoft Outlook** node named `"Send Birthday Email"` that:
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

- [ ] Create `assets/workflows/birthday-greeting-email-workflow/asset.yaml`
- [ ] After writing the `.n8n.json`, run the `generate-workflow-asset.js` script to produce `workflow` and `provides.apis[]` for `asset.yaml`
- [ ] Fill in `description` for each `kind: rest` entry in `asset.yaml`
- [ ] Add entry in `solution.yaml`:
  ```yaml
    - ref: ./assets/workflows/birthday-greeting-email-workflow/asset.yaml
  ```

## Validation

- [ ] Confirm the Webhook trigger is the entry point and every node is reachable from it
- [ ] Confirm both success and error paths each contain a `respondToWebhook` node
- [ ] Run `validate-n8n-workflow` before writing the file — fix all errors
- [ ] Write the final file to `assets/workflows/birthday-greeting-email-workflow/birthday-greeting-email-workflow.n8n.json` in a single write call
