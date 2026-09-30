# Requirements and validation traceability

All cases are planned and **not run**. This table shows intended CUS → SR → verification coverage, not proof of compliance or completeness across all system perspectives. Actual results and evidence belong in the registry and a candidate-specific release report. A cross-cutting SR can appear under more than one CUS.

| Customer-User-Story | System requirements | Planned verification |
| --- | --- | --- |
| CUS01 | SR01, SR02, SR27 | TC01, TC19 |
| CUS02 | SR03, SR04 | TC02, TC03 |
| CUS03 | SR05, SR06, SR07, SR28 | TC04, TC05, TC20 |
| CUS04 | SR08, SR09, SR29 | TC06, TC20 |
| CUS05 | SR10, SR11 | TC07 |
| CUS06 | SR12, SR13, SR30 | TC08, TC09, TC10, TC20 |
| CUS07 | SR14, SR15 | TC10 |
| CUS08 | SR16, SR17 | TC11 |
| CUS09 | SR18, SR19, SR31 | TC12, TC13, TC20 |
| CUS10 | SR20, SR21 | TC14 |
| CUS11 | SR22, SR23 | TC16 |
| CUS12 | SR24, SR25 | TC17 |
| CUS13 | SR26 | TC18 |

TC15 additionally validates the complete P0 user journey across CUS01–CUS10. No requirement is complete merely because its issue is closed. Trace every implemented statement to a PR or commit and candidate-specific passing evidence.

Task-level CUS → SR → task → validation links and dependencies are canonical in the registry and summarized as TK01–TK08 in the [WP01 requirements package](wp01-requirements-package.md). A task's planned cases are coverage intent, not results.
