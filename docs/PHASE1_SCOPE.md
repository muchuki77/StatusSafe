This phase answers the question, "Given this student record, what risk level applies and why"?
## PURPOSE
Phase 1 establishes the core rule-evaluation engine for Sevis bridge.
Its purpose is to deterministically evaluate a single student record against a defined set of complinace risk rules and return an explainable, auditable result. 

it focuses exclusisvely on correctness, logic and traceability not user interface or institiutional integration. 

## WHAT DOES PHASE1 DO?
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

## WHAT DOES PHASE 1 NOT DO
- It does not provide any legal advice
- Intergrate with SEVIS, DHS, or any government system
- Store or process any real student data
- determine or assert immigation or ;egal status
- inclue authentication or role-based access
- include graphical user interface
- Sebd notifications via text, email or any alerts
- Handle document uploads or verification
- Handle mulitple students/batch processing
- Implememt institutional policy customization

## SUCCESS CRITERIA
phase 1 is considered complete when;
- A developer can input a synthetic stident record (JSON)
- The system returns a deterministic evaluation result with:
    ->final risk level
    ->primary reason
    ->list of triggered rules
-Rule precedence is correctly enforced(red>yellow>green)
-Rule evaulation is explainable and traceable to rules IDS
-unit tests exists for all explainable rules
-Documentation clearly explains how ro run the evalution
-the rules engine can be extended without modifying the existing rules.

## phase1 non goals
The following are not phase goals and have been deffered for later phases
User interfaces and dashboards
Advisor or student workflows
Institutional policy configuration
Analytics and reporting
Production deployment and scaling
Security hardening beyond basic input validation

## Phase 1 output artefacts
At the end of phase 1, the project will include
- a rules engine implementation
- A documented rule set(RULES.md)
- sample in[ut and putput records
- automated tests
- clear documentation for future purposes


  
