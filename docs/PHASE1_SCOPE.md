This phase answers the question, "Given this student record, what risk level applies and why"?
## PURPOSE
Phase 1 establishes the core rule-evaluation engine for Sevis bridge.
Its purpose is to deterministically evaluate a single student record against a defined set of complinace risk rules and return an explainable, auditable result. 

it focuses exclusisvely on correctness, logic and traceability not user interface or institiutional integration. 

## What does phase 1 do?
- Evaluate a student's record using rules defined in RULES.md
- Identify all triggered rules for that student
- Assign a final risk level which could be RED, YELLOW or GREEN.
- Surface one primary reason to reduce user confusion
- Return a structued result in json format
- Maintain rule metadata(rule ID, description, recommended action)
- include timestamps and relest for auditability
- Support execution with a : command line interface or minimal API endpoint
- operate on sysnthetic or mock data only
- Be fully testable with unit tests for each rule.

## What does Phase 1 not do
- It does not provide any legal advice
- Intergrate with SEVIS, DHS, or any government system
- Store or process any real student data
- determine or assert immigation or legal status
- inclue authentication or role-based access
- include graphical user interface
- Send notifications via text, email or any alerts
- Handle document uploads or verification
- Handle multiple students/batch processing
- Implememt institutional policy customization

## Success criteria
Phase 1 is considered complete when;
- A developer can input a synthetic student record (JSON)
- The system returns a deterministic evaluation result with:
    -> final risk level
    -> primary reason
    -> list of triggered rules
- Rule precedence is correctly enforced(red>yellow>green)
- Rule evaulation is explainable and traceable to ruleIDS
- unit tests exists for all explainable rules
- Documentation clearly explains how ro run the evaluation
- the rules engine can be extended without modifying the existing rules.

## Phase1 non goals
- The following are not phase 1 goals and have been deffered for later phases
- User interfaces and dashboards
- Advisor or student workflows
- Institutional policy configuration
- Analytics and reporting
- Production deployment and scaling
- Security hardening beyond basic input validation

## Phase 1 output artefacts
At the end of phase 1, the project will include:
- a rules engine implementation
- A documented rule set(RULES.md)
- sample input and output records
- automated tests
- clear documentation for future purposes


  
