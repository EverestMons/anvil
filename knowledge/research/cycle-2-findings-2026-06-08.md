# Anvil Cycle Report — bellows — Cycle 2
**Date:** 2026-06-08

## Executive Summary
- **Total files:** 42
- **Total chunks:** 607
- **High risk chunks:** 2
- **Average composite score:** 0.2569
- **Total findings:** 82

## Coverage Gaps (0 findings)
No coverage gaps found.

## Untested Complexity (top-20 by coverage × complexity)
| File | Name | Coverage | Complexity | Cov×Comp | Composite |
|---|---|---|---|---|---|
| tests/test_decisions.py | TestExtractDecisionBlocks | 1.000 | 0.735 | 0.735 | 0.596 |
| decisions.py | extract_decision_blocks | 1.000 | 0.582 | 0.582 | 0.535 |
| notifier.py | _flush_buffer | 1.000 | 0.500 | 0.500 | 0.539 |
| scripts/check_backlog_freshness.py | find_candidates | 1.000 | 0.426 | 0.426 | 0.483 |
| bellows.py | start | 0.500 | 0.789 | 0.395 | 0.593 |
| tests/test_decisions.py | TestLoadPhrases | 1.000 | 0.375 | 0.375 | 0.488 |
| gates.py | _gate_scope_check | 1.000 | 0.368 | 0.368 | 0.484 |
| validators.py | check_stop_prose | 1.000 | 0.341 | 0.341 | 0.412 |
| bellows.py | _rotate_logs | 1.000 | 0.314 | 0.314 | 0.499 |
| gates.py | _hedging_in_status_vicinity | 1.000 | 0.237 | 0.237 | 0.440 |
| tests/test_worktree.py | git_repo | 1.000 | 0.216 | 0.216 | 0.418 |
| bellows.py | _check_queue_drain | 1.000 | 0.211 | 0.211 | 0.468 |
| tests/test_cleanup_verdicts.py | TestCleanupVerdictsForSlug | 1.000 | 0.206 | 0.206 | 0.437 |
| bellows.py | _log | 1.000 | 0.201 | 0.201 | 0.606 |
| bellows.py | Bellows | 0.200 | 1.000 | 0.200 | 0.540 |
| bellows.py | run_plan | 0.200 | 1.000 | 0.200 | 0.720 |
| bellows.py | _consume_verdicts | 0.200 | 0.996 | 0.199 | 0.665 |
| scripts/check_backlog_freshness.py | extract_fingerprint | 1.000 | 0.196 | 0.196 | 0.405 |
| gates.py | _gate_no_permission_denials | 1.000 | 0.187 | 0.187 | 0.425 |
| gates.py | _gate_rule_22_verification | 0.200 | 0.930 | 0.186 | 0.582 |

## Coupling Hotspots (7 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| bellows.py | run_plan | 1.000 | 117 | 306 | 0.720 |
| bellows.py | _log | 0.969 | 252 | 0 | 0.606 |
| gates.py | check | 0.906 | 186 | 33 | 0.369 |
| runner.py | run_step | 0.875 | 60 | 57 | 0.534 |
| bellows.py | slug_for | 0.844 | 105 | 0 | 0.558 |
| bellows.py | _consume_verdicts | 0.844 | 105 | 0 | 0.665 |
| bellows.py | _create_worktree | 0.812 | 81 | 18 | 0.599 |

## Clone Candidates (14 pairs)
| File A | Name A | File B | Name B | Similarity |
|---|---|---|---|---|
| gates.py | strip_fenced_code_blocks | verdict.py | strip_fenced_code_blocks | 1.000 |
| tests/test_bellows.py | _make_fake_run_step_result | tests/test_consume_verdicts.py | _make_fake_run_step_result | 1.000 |
| tests/test_bellows.py | _clean_gates | tests/test_consume_verdicts.py | _clean_gates | 1.000 |
| tests/test_gates.py | test_extract_step_text_ignores_inline_code_references | tests/test_verdict.py | test_extract_step_text_from_plan_ignores_inline_code_references | 0.898 |
| tests/test_bellows.py | test_pause_site_2_intermediate_step_gate_failure_renames_before_post | tests/test_bellows.py | test_pause_site_3_final_step_gate_failure_renames_before_post | 0.852 |
| tests/test_bellows.py | test_no_warning_multi_step_plan_with_pause_for_verdict | tests/test_bellows.py | test_no_warning_multi_step_plan_with_pause_always | 0.844 |
| tests/test_bellows.py | test_on_modified_preserves_seen_for_lifecycle_renames | tests/test_bellows.py | test_on_created_preserves_seen_for_lifecycle_renames | 0.828 |
| gates.py | _extract_step_text | verdict.py | _extract_step_text_from_plan | 0.797 |
| tests/test_gates.py | test_permission_denials_none_tool_name_fails | tests/test_gates.py | test_permission_denials_unknown_tool_fails | 0.766 |
| tests/test_gates.py | test_permission_denials_vexp_get_context_capsule_exempt | tests/test_gates.py | test_permission_denials_vexp_index_status_exempt | 0.734 |
| tests/test_gates.py | test_rule_20_gate_tolerates_bold_passed_line | tests/test_gates.py | test_rule_20_gate_tolerates_single_asterisk_passed_line | 0.734 |
| tests/test_gates.py | test_permission_denials_vexp_get_context_capsule_exempt | tests/test_gates.py | test_permission_denials_vexp_search_memory_exempt | 0.719 |
| bellows.py | strip_fenced_code_blocks | gates.py | strip_fenced_code_blocks | 0.711 |
| bellows.py | strip_fenced_code_blocks | verdict.py | strip_fenced_code_blocks | 0.711 |

## Staleness Alerts (21 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| gates.py | _extract_step_text | 1.000 | 0.411 |
| gates.py | _gate_is_qa_step | 1.000 | 0.474 |
| scripts/check_backlog_freshness.py | parse_ps_entries | 1.000 | 0.533 |
| tests/test_rule_26_deposit_parser.py | test_extract_plan_required_deposits_prefers_declared_block | 1.000 | 0.228 |
| tests/test_rule_26_deposit_parser.py | test_extract_plan_required_deposits_falls_back_to_legacy_when_no_block | 1.000 | 0.226 |
| tests/test_rule_26_deposit_parser.py | test_extract_plan_required_deposits_handles_none_bullet | 1.000 | 0.226 |
| tests/test_rule_26_deposit_parser.py | test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present | 1.000 | 0.230 |
| tests/test_rule_26_deposit_parser.py | test_extract_primary_deposit_scoping_in_post_verdict_request | 1.000 | 0.235 |
| tests/test_rule_26_deposit_parser.py | test_extract_plan_required_deposits_blank_quoted_line | 1.000 | 0.226 |
| tests/test_rule_26_deposit_parser.py | test_extract_plan_required_deposits_multiple_blank_quoted_lines | 1.000 | 0.226 |
| tests/test_rule_26_deposit_parser.py | test_extract_plan_required_deposits_does_not_span_paragraphs | 1.000 | 0.226 |
| tests/test_rule_26_deposit_parser.py | test_extract_step_text_helper_gates_py | 1.000 | 0.233 |
| tests/test_runner.py | test_configurable_timeout_respected | 1.000 | 0.202 |
| tests/test_runner.py | test_timeout_returns_cost_none | 1.000 | 0.200 |
| tests/test_runner.py | test_timeout_writes_log_file | 1.000 | 0.206 |
| tests/test_runner.py | test_generic_exception_returns_cost_none | 1.000 | 0.200 |
| tests/test_runner.py | test_generic_exception_message_contains_actual_error | 1.000 | 0.202 |
| tests/test_runner.py | test_generic_exception_writes_log_file | 1.000 | 0.206 |
| tests/test_runner_parser.py | test_run_step_timeout | 1.000 | 0.264 |
| tests/test_validators.py | _header_for | 1.000 | 0.538 |
| verdict.py | _extract_step_text_from_plan | 1.000 | 0.345 |

## Complexity Hotspots (12 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| bellows.py | Bellows | 1.000 | 121 | 7 | 0 |
| bellows.py | run_plan | 1.000 | 74 | 6 | 5 |
| bellows.py | _consume_verdicts | 0.996 | 52 | 7 | 1 |
| gates.py | _gate_rule_22_verification | 0.930 | 32 | 4 | 7 |
| runner.py | run_step | 0.897 | 29 | 3 | 9 |
| bellows.py | _teardown_worktree | 0.851 | 28 | 4 | 3 |
| bellows.py | _create_worktree | 0.789 | 25 | 5 | 2 |
| bellows.py | start | 0.789 | 24 | 6 | 3 |
| gates.py | _gate_deposit_exists | 0.639 | 18 | 5 | 7 |
| decisions.py | extract_decision_blocks | 0.582 | 19 | 4 | 2 |
| bellows.py | PlanHandler | 0.567 | 20 | 3 | 0 |
| notifier.py | _flush_buffer | 0.500 | 17 | 5 | 0 |

## Co-Change Patterns (10 pairs)
| File A | File B | Co-changes | Jaccard |
|---|---|---|---|
| bellows.py | tests/test_bellows.py | 12 | 0.375 |
| gates.py | tests/test_gates.py | 12 | 0.857 |
| NEXT_SESSION.md | knowledge/BACKLOG.md | 11 | 0.147 |
| PROJECT_STATUS.md | knowledge/research/agent-prompt-feedback.md | 9 | 0.071 |
| bellows.py | tests/test_consume_verdicts.py | 9 | 0.290 |
| NEXT_SESSION.md | PROJECT_STATUS.md | 8 | 0.108 |
| bellows.py | knowledge/research/agent-prompt-feedback.md | 7 | 0.065 |
| PROJECT_STATUS.md | knowledge/BACKLOG.md | 5 | 0.050 |
| gates.py | knowledge/research/agent-prompt-feedback.md | 5 | 0.054 |
| knowledge/research/agent-prompt-feedback.md | tests/test_gates.py | 5 | 0.054 |

## Research Recommendations (18 deviations across 1 roles)

### utility (18 deviations)
- **[medium]** `bellows.py::load_config` -- pure_functions: File I/O found in utility function
- **[medium]** `bellows.py::migrate_db` -- pure_functions: Database connection parameter found in utility function
- **[medium]** `bellows.py::load_file` -- pure_functions: File I/O found in utility function
- **[medium]** `bellows.py::record_run` -- pure_functions: Database connection parameter found in utility function
- **[medium]** `bellows.py::run_plan` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `bellows.py::_capture_git_diff` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `bellows.py::_teardown_worktree` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `gates.py::_extract_plan_required_deposits` -- pure_functions: File I/O found in utility function
- **[medium]** `gates.py::_gate_rule_20_self_check` -- pure_functions: File I/O found in utility function
- **[medium]** `gates.py::_gate_rule_22_verification` -- pure_functions: File I/O found in utility function
- **[medium]** `planner.py::_log_consultation` -- pure_functions: File I/O found in utility function
- **[medium]** `runner.py::_write_log` -- pure_functions: File I/O found in utility function
- **[medium]** `scripts/migrate_config.py::migrate` -- pure_functions: File I/O found in utility function
- **[medium]** `scripts/migrate_orphan_verdicts.py::main` -- pure_functions: File I/O found in utility function
- **[medium]** `tests/test_bellows.py::_create_test_db` -- pure_functions: Database connection parameter found in utility function

## Intent Gaps (0 findings)
No intent gaps found.

## Planner Constraints (72 total)

### verify_dependents (7)
- **[high]** `bellows.py::run_plan` — Coupling score 1.00, 117 inbound + 306 outbound deps
- **[high]** `bellows.py::_log` — Coupling score 0.97, 252 inbound + 0 outbound deps
- **[high]** `gates.py::check` — Coupling score 0.91, 186 inbound + 33 outbound deps
- **[high]** `runner.py::run_step` — Coupling score 0.88, 60 inbound + 57 outbound deps
- **[high]** `bellows.py::slug_for` — Coupling score 0.84, 105 inbound + 0 outbound deps
- **[high]** `bellows.py::_consume_verdicts` — Coupling score 0.84, 105 inbound + 0 outbound deps
- **[high]** `bellows.py::_create_worktree` — Coupling score 0.81, 81 inbound + 18 outbound deps

### refactor_candidate (26)
- **[medium]** `gates.py::strip_fenced_code_blocks ↔ verdict.py::strip_fenced_code_blocks` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_bellows.py::_make_fake_run_step_result ↔ tests/test_consume_verdicts.py::_make_fake_run_step_result` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_bellows.py::_clean_gates ↔ tests/test_consume_verdicts.py::_clean_gates` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_gates.py::test_extract_step_text_ignores_inline_code_references ↔ tests/test_verdict.py::test_extract_step_text_from_plan_ignores_inline_code_references` — Similarity 0.90 — potential duplicate
- **[medium]** `tests/test_bellows.py::test_pause_site_2_intermediate_step_gate_failure_renames_before_post ↔ tests/test_bellows.py::test_pause_site_3_final_step_gate_failure_renames_before_post` — Similarity 0.85 — potential duplicate
- **[medium]** `tests/test_bellows.py::test_no_warning_multi_step_plan_with_pause_for_verdict ↔ tests/test_bellows.py::test_no_warning_multi_step_plan_with_pause_always` — Similarity 0.84 — potential duplicate
- **[medium]** `tests/test_bellows.py::test_on_modified_preserves_seen_for_lifecycle_renames ↔ tests/test_bellows.py::test_on_created_preserves_seen_for_lifecycle_renames` — Similarity 0.83 — potential duplicate
- **[medium]** `gates.py::_extract_step_text ↔ verdict.py::_extract_step_text_from_plan` — Similarity 0.80 — potential duplicate
- **[medium]** `tests/test_gates.py::test_permission_denials_none_tool_name_fails ↔ tests/test_gates.py::test_permission_denials_unknown_tool_fails` — Similarity 0.77 — potential duplicate
- **[medium]** `tests/test_gates.py::test_permission_denials_vexp_get_context_capsule_exempt ↔ tests/test_gates.py::test_permission_denials_vexp_index_status_exempt` — Similarity 0.73 — potential duplicate
- **[medium]** `tests/test_gates.py::test_rule_20_gate_tolerates_bold_passed_line ↔ tests/test_gates.py::test_rule_20_gate_tolerates_single_asterisk_passed_line` — Similarity 0.73 — potential duplicate
- **[medium]** `tests/test_gates.py::test_permission_denials_vexp_get_context_capsule_exempt ↔ tests/test_gates.py::test_permission_denials_vexp_search_memory_exempt` — Similarity 0.72 — potential duplicate
- **[medium]** `bellows.py::strip_fenced_code_blocks ↔ gates.py::strip_fenced_code_blocks` — Similarity 0.71 — potential duplicate
- **[medium]** `bellows.py::strip_fenced_code_blocks ↔ verdict.py::strip_fenced_code_blocks` — Similarity 0.71 — potential duplicate
- **[medium]** `bellows.py::Bellows` — Complexity score 1.00, cyclomatic=121, depth=7

### investigation_needed (21)
- **[high]** `gates.py::_extract_step_text` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `gates.py::_gate_is_qa_step` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `scripts/check_backlog_freshness.py::parse_ps_entries` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_prefers_declared_block` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_falls_back_to_legacy_when_no_block` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_handles_none_bullet` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_ignores_paths_in_code_fences_when_block_present` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_rule_26_deposit_parser.py::test_extract_primary_deposit_scoping_in_post_verdict_request` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_blank_quoted_line` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_multiple_blank_quoted_lines` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_rule_26_deposit_parser.py::test_extract_plan_required_deposits_does_not_span_paragraphs` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_rule_26_deposit_parser.py::test_extract_step_text_helper_gates_py` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_runner.py::test_configurable_timeout_respected` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_runner.py::test_timeout_returns_cost_none` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_runner.py::test_timeout_writes_log_file` — Staleness score 1.00 — dependencies updated but chunk unchanged

### pattern_recommendation (18)
- **[medium]** `bellows.py::load_config` — utility deviates from pure_functions: File I/O found in utility function
- **[medium]** `bellows.py::migrate_db` — utility deviates from pure_functions: Database connection parameter found in utility function
- **[medium]** `bellows.py::load_file` — utility deviates from pure_functions: File I/O found in utility function
- **[medium]** `bellows.py::record_run` — utility deviates from pure_functions: Database connection parameter found in utility function
- **[medium]** `bellows.py::run_plan` — utility deviates from no_domain_logic: Domain-specific term found in utility function
- **[medium]** `bellows.py::_capture_git_diff` — utility deviates from no_domain_logic: Domain-specific term found in utility function
- **[medium]** `bellows.py::_teardown_worktree` — utility deviates from no_domain_logic: Domain-specific term found in utility function
- **[medium]** `gates.py::_extract_plan_required_deposits` — utility deviates from pure_functions: File I/O found in utility function
- **[medium]** `gates.py::_gate_rule_20_self_check` — utility deviates from pure_functions: File I/O found in utility function
- **[medium]** `gates.py::_gate_rule_22_verification` — utility deviates from pure_functions: File I/O found in utility function
- **[medium]** `planner.py::_log_consultation` — utility deviates from pure_functions: File I/O found in utility function
- **[medium]** `runner.py::_write_log` — utility deviates from pure_functions: File I/O found in utility function
- **[medium]** `scripts/migrate_config.py::migrate` — utility deviates from pure_functions: File I/O found in utility function
- **[medium]** `scripts/migrate_orphan_verdicts.py::main` — utility deviates from pure_functions: File I/O found in utility function
- **[medium]** `tests/test_bellows.py::_create_test_db` — utility deviates from pure_functions: Database connection parameter found in utility function

## Specialist Update Data
- Functions: 127
- Classes: 8
- Methods: 20
- Test cases: 452
- Dependencies: 3516
- Similarity pairs: 28
- Average health score: 0.2569
- High risk count: 2
