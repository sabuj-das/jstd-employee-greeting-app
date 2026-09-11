# Specification: employee-greeting-orchestrator

> **Guidelines**: Read [guidelines-n8n-workflow.md](../guidelines-n8n-workflow.md) before executing ANY tasks below. Follow all constraints described there throughout execution.

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` before building any node
- [ ] Run the `setup-solution` skill to create `solution.yaml` and `asset.yaml` for all workflow assets

---

## Workflow: Main Orchestrator (`assets/workflows/employee-greeting-orchestrator/`)

### Purpose
Receives the HR-uploaded CSV file via webhook, parses the employees, uses a SAP Agent to determine date matches (work anniversary and/or birthday), collects matched employees, presents them to HR for approval via SAP Task Center, then calls the Work Anniversary and/or Birthday Greeting sub-workflows for every approved employee.

---

## Nodes to Build

### Trigger
- [ ] Add a **Webhook** trigger node named `"CSV Upload"` with method POST
  - Path: `csv-upload`
  - Response mode: `responseNode` (the workflow will respond after processing is complete)
  - The incoming payload is a multipart/form-data or base64-encoded CSV file body

### CSV Parsing
- [ ] Add a **Code** node named `"Parse CSV"` that:
  - Reads the uploaded CSV content from `$json.body` (semicolon-delimited)
  - Parses all rows into structured employee objects: `{ name, email, dateOfJoining, dateOfBirth }`
  - Returns one n8n item per employee row
  - Validates that all four columns exist; stops with an error if the CSV is malformed
  - Emits log: `M1.achieved: CSV uploaded and parsed successfully — {n} employee rows extracted`
  - Emits log on failure: `M1.missed: CSV upload failed or file could not be parsed — workflow halted`

### Loop Over Employees
- [ ] Add a **Split Out** node named `"Split Employees"` to split the parsed employee array into individual items

### AI Date Matching (SAP Agent)
- [ ] Look up `CUSTOM.sapAgent` from the node catalog before adding it
- [ ] Add a **SAP Agent** node named `"Date Match Agent"` that:
  - Receives each employee item (`name`, `email`, `dateOfJoining`, `dateOfBirth`)
  - Is instructed to compare the DD.MM of `dateOfJoining` and `dateOfBirth` against today's date
  - Returns a structured JSON with fields: `{ name, email, dateOfJoining, dateOfBirth, anniversaryMatch: true/false, birthdayMatch: true/false }`
  - System prompt must instruct: "You are a date-matching assistant. Today's date is provided. Compare DD.MM of dateOfJoining and dateOfBirth with today's DD.MM. Return valid JSON only with fields: name, email, dateOfJoining, dateOfBirth, anniversaryMatch (boolean), birthdayMatch (boolean). Do not add commentary."
  - Emits log on completion of all rows: `M2.achieved: AI matching complete`
  - Emits log on failure: `M2.missed: Agent evaluation did not complete`

### Filter — Keep Only Matches
- [ ] Add a **Filter** node named `"Keep Matches Only"` that passes through only employees where `anniversaryMatch === true` OR `birthdayMatch === true`

### HR Approval (SAP Task Center)
- [ ] Look up `CUSTOM.sapTaskCenter` from the node catalog before adding it
- [ ] Add a **SAP Task Center** node named `"HR Approval"` that:
  - Sends the full list of matched employees for HR review
  - Task subject: `"Greeting Email Approval — {n} employee(s) matched today"`
  - Task body: list of matched employees with their greeting type(s) (anniversary / birthday / both)
  - Uses a recipient target (HR approver role or email)
  - The workflow waits for the HR decision
  - Emits log on approval: `M3.achieved: HR approval received — {n} employees approved for greeting dispatch`
  - Emits log on rejection/timeout: `M3.missed: HR approval not received within timeout or was rejected — no emails sent`

### Route on HR Decision
- [ ] Add a **Switch** node named `"Check Approval"` that:
  - Routes to the dispatch branch on `approved`
  - Routes to the reject branch on `rejected` or timeout

### Reject Branch
- [ ] Add a **Respond to Webhook** node named `"Respond — Rejected"` that returns HTTP 200 with body `{ "status": "rejected", "message": "HR did not approve. No emails sent." }`

### Dispatch Loop — Split Approved Employees
- [ ] Add a **Split Out** node named `"Split Approved"` to iterate over approved employees

### Route Anniversary vs Birthday
- [ ] Add a **Switch** node named `"Route Greeting Type"` with three outputs:
  - Output 0 — `anniversaryMatch === true AND birthdayMatch === false` → anniversary only
  - Output 1 — `birthdayMatch === true AND anniversaryMatch === false` → birthday only
  - Output 2 — `anniversaryMatch === true AND birthdayMatch === true` → both (fan-out to both branches)

### Call Work Anniversary Sub-Workflow
- [ ] Add an **HTTP Request** node named `"Trigger Anniversary Workflow"` that:
  - POSTs employee data `{ name, email, dateOfJoining }` to the Work Anniversary sub-workflow webhook URL
  - URL: configurable placeholder `https://YOUR_N8N_HOST/webhook/work-anniversary-email`

### Call Birthday Greeting Sub-Workflow
- [ ] Add an **HTTP Request** node named `"Trigger Birthday Workflow"` that:
  - POSTs employee data `{ name, email, dateOfBirth }` to the Birthday Greeting sub-workflow webhook URL
  - URL: configurable placeholder `https://YOUR_N8N_HOST/webhook/birthday-greeting-email`

### Dual-match Fan-out
- [ ] For employees where both flags are true, ensure both `"Trigger Anniversary Workflow"` and `"Trigger Birthday Workflow"` are called (two parallel branches off Switch output 2)

### Merge After Dispatch
- [ ] Add a **Merge** node named `"Merge Dispatch Results"` to converge the three routing branches back before responding
- [ ] Ensure all execution paths (anniversary-only, birthday-only, both) reach the Merge node

### Final Response
- [ ] Add a **Code** node named `"Build Summary"` that counts sent emails and builds a summary message
  - Emits log: `M4.achieved: All greeting emails dispatched successfully — {n} emails sent`
  - Emits log on error: `M4.missed: One or more emails failed to send — HR notified for follow-up`
- [ ] Add a **Respond to Webhook** node named `"Respond — Success"` that returns HTTP 200 with the summary

---

## Asset Setup

- [ ] Run `setup-solution` skill to create `solution.yaml` (if not yet done) and `asset.yaml` for this workflow
- [ ] After writing the `.n8n.json`, run the `generate-workflow-asset.js` script to produce `workflow` and `provides.apis[]` for `asset.yaml`
- [ ] Fill in `description` for each `kind: rest` entry in `asset.yaml`
- [ ] Add entry in `solution.yaml`:
  ```yaml
    - ref: ./assets/workflows/employee-greeting-orchestrator/asset.yaml
  ```

## Validation

- [ ] Confirm every node is reachable from the Webhook trigger
- [ ] Confirm all convergence points (dual-match fan-out) pass through the Merge node before `Respond — Success`
- [ ] Confirm both reject and success paths each contain a `respondToWebhook` node
- [ ] Run `validate-n8n-workflow` before writing the file — fix all errors
- [ ] Write the final file to `assets/workflows/employee-greeting-orchestrator/employee-greeting-orchestrator.n8n.json` in a single write call
