# Employee Greeting Automation

Automate work anniversary and birthday greeting emails to employees via CSV-driven n8n workflow with AI-based matching and HR approval.

## Business challenge

As an HR employee, I need to upload a CSV file containing employee data (name, email, date of joining, date of birth) to trigger automated greeting emails. The system should use an AI agent to determine, based on today's date, whether each employee's work anniversary (dateOfJoining DD.MM matches today) or birthday (dateOfBirth DD.MM matches today) falls on the current day, then route to the appropriate sub-workflow (Work Anniversary email or Birthday Greeting email) with HR review before sending. Both emails can be sent if both dates match the same day.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Employees with anniversary/birthday receiving greeting email | — | 100% coverage, zero missed | — | HR Employee Engagement | user |

## Key Milestones

- **CSV Uploaded**: HR uploads a valid semicolon-delimited CSV file via webhook trigger
- **AI Matching Complete**: Agent has evaluated each employee row and determined which greeting type(s) apply
- **HR Approval Done**: HR employee has reviewed and approved the list of emails to send
- **Emails Dispatched**: Greeting emails successfully sent to all matched employees

## Business Architecture (RBA)

### End-to-End Process

Recruit to Retire

### Process Hierarchy

```
Recruit to Retire
└── Manage Workforce (generic)
    └── Manage employee information and reporting (generic)
        └── Manage employee milestone notifications
        └── HR employee engagement via automated communications
```

### Summary

The solution maps to the "Recruit to Retire" E2E process under "Manage Workforce → Manage employee information and reporting", covering employee milestone engagement automation.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Data Product ORD ID | Gap? | Notes / assumptions |
| ---------------------- | ----------------------- | ---------- | ----------------- | ------------------ | ------------------- | ---- | ------------------- |
| Parse and process employee CSV with date matching | — | — | — | — | — | Yes | Custom n8n workflow with Code node; no standard SAP product covers CSV-based milestone matching |
| AI-based determination of which greeting to send | — | — | — | — | — | Yes | SAP Agent node in n8n to perform date comparison logic and content generation |
| Send Work Anniversary email | — | — | — | — | — | Yes | Email delivery node (Microsoft Outlook or placeholder); no standard SAP HR notification module in scope |
| Send Birthday Greeting email | — | — | — | — | — | Yes | Same email delivery mechanism as above |
| HR approval before email dispatch | SAP Task Center (optional) | — | — | — | — | Maybe | Can use SAP Task Center for approval or simplified n8n approval step |

### Key findings
- No standard SAP product natively covers CSV-driven employee greeting automation — full custom n8n workflow required
- SAP SuccessFactors Employee Central covers employee data management but is not the data source in this scenario (CSV is)
- The AI agent role is content generation and date-match decision (anniversary vs birthday vs both)
- HR approval step is required before any email is dispatched
- Microsoft Outlook is available as the email delivery node; placeholder will be used until confirmed
- Both anniversary and birthday emails can trigger for the same employee on the same day — workflow must handle both branches

## Recommendations

### Employee Greeting Automation via n8n Workflow with AI Agent

#### Executive Summary

Custom n8n workflow with SAP Agent for greeting logic and HR approval gate before email dispatch.

#### Recommended Solution

Build three n8n workflows:
1. **Main Orchestrator Workflow**: Triggered via webhook (HR uploads CSV). Parses the CSV, loops over each employee row, calls the SAP Agent to determine which greeting applies based on today's date, then routes to anniversary and/or birthday sub-workflows as appropriate. Presents matched employees to HR for approval before dispatching.
2. **Work Anniversary Sub-Workflow**: Receives employee data, generates a personalized work anniversary email via SAP Agent, and sends it via email node.
3. **Birthday Greeting Sub-Workflow**: Receives employee data, generates a personalized birthday greeting email via SAP Agent, and sends it via email node.

#### Recommended solution category

n8n Workflow

#### Intent fit
92%
