# Anvil Cycle Report — bellows — Cycle 1
**Date:** 2026-06-08

## Executive Summary
- **Total files:** 42
- **Total chunks:** 607
- **High risk chunks:** 1
- **Average composite score:** 0.2583
- **Total findings:** 113

## Coverage Gaps (28 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| engines/validator.py | gate_9_accessorials | function | 0.793 | 1.00 | 0.96 |
| engines/validator.py | gate_8_fuel | function | 0.785 | 1.00 | 0.96 |
| engines/validator.py | gate_7_linehaul | function | 0.783 | 1.00 | 0.96 |
| web/training.py | training_batch_apply | function | 0.783 | 1.00 | 0.76 |
| web/contracts.py | _build_dashboard_cards | function | 0.778 | 1.00 | 0.97 |
| web/training.py | _identify_training_gaps | function | 0.773 | 1.00 | 0.76 |
| web/action_queue.py | action_queue | function | 0.766 | 1.00 | 0.78 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.752 | 1.00 | 0.88 |
| web/contracts.py | contract_fuel_import_combined | function | 0.743 | 1.00 | 0.97 |
| app.py | dispute_brief | function | 0.733 | 1.00 | 0.99 |
| web/contract_import.py | _validate_contract_json | function | 0.731 | 1.00 | 0.84 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.730 | 1.00 | 0.88 |
| web/gap_dashboard.py | _import_lanes_section | function | 0.725 | 1.00 | 1.00 |
| engines/action_router.py | route_actions | function | 0.724 | 1.00 | 0.89 |
| app.py | debug_export | function | 0.723 | 1.00 | 0.99 |
| web/gap_dashboard.py | import_contract_setup | function | 0.723 | 1.00 | 1.00 |
| web/gap_dashboard.py | enrich_invoice | function | 0.723 | 1.00 | 1.00 |
| engines/action_router.py | _build_summary | function | 0.722 | 1.00 | 0.89 |
| app.py | team_dashboard | function | 0.722 | 1.00 | 0.99 |
| web/gap_dashboard.py | _parse_csv_to_json | function | 0.719 | 1.00 | 1.00 |
| web/gap_dashboard.py | import_section | function | 0.719 | 1.00 | 1.00 |
| engines/validator.py | validate_invoice | function | 0.718 | 1.00 | 0.96 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.716 | 1.00 | 0.88 |
| app.py | invoices_list | function | 0.716 | 1.00 | 0.99 |
| app.py | run_validation | function | 0.709 | 1.00 | 0.99 |
| web/rates.py | rates_grid | function | 0.705 | 1.00 | 0.55 |
| web/gap_dashboard.py | _reshape_for_apply | function | 0.705 | 1.00 | 1.00 |
| web/contracts.py | contract_lanes_bulk | function | 0.704 | 1.00 | 0.97 |

## Untested Complexity (top-20 by coverage × complexity)
| File | Name | Coverage | Complexity | Cov×Comp | Composite |
|---|---|---|---|---|---|
| tests/test_decisions.py | TestExtractDecisionBlocks | 1.000 | 0.735 | 0.735 | 0.596 |
| decisions.py | extract_decision_blocks | 1.000 | 0.582 | 0.582 | 0.535 |
| notifier.py | _flush_buffer | 1.000 | 0.500 | 0.500 | 0.539 |
| scripts/check_backlog_freshness.py | find_candidates | 1.000 | 0.426 | 0.426 | 0.483 |
| bellows.py | start | 0.500 | 0.789 | 0.395 | 0.593 |
| tests/test_decisions.py | TestLoadPhrases | 1.000 | 0.375 | 0.375 | 0.488 |
| verdict.py | post_verdict_request | 1.000 | 0.375 | 0.375 | 0.533 |
| gates.py | _gate_scope_check | 1.000 | 0.368 | 0.368 | 0.484 |
| verdict.py | _build_verification_results_table | 1.000 | 0.347 | 0.347 | 0.445 |
| validators.py | check_stop_prose | 1.000 | 0.341 | 0.341 | 0.412 |
| verdict.py | extract_primary_deposit | 1.000 | 0.334 | 0.334 | 0.465 |
| bellows.py | _rotate_logs | 1.000 | 0.314 | 0.314 | 0.499 |
| gates.py | _hedging_in_status_vicinity | 1.000 | 0.237 | 0.237 | 0.440 |
| tests/test_worktree.py | git_repo | 1.000 | 0.216 | 0.216 | 0.418 |
| bellows.py | _check_queue_drain | 1.000 | 0.211 | 0.211 | 0.468 |
| tests/test_cleanup_verdicts.py | TestCleanupVerdictsForSlug | 1.000 | 0.206 | 0.206 | 0.437 |
| bellows.py | _log | 1.000 | 0.201 | 0.201 | 0.606 |
| bellows.py | Bellows | 0.200 | 1.000 | 0.200 | 0.540 |
| bellows.py | run_plan | 0.200 | 1.000 | 0.200 | 0.720 |
| bellows.py | _consume_verdicts | 0.200 | 0.996 | 0.199 | 0.665 |

## Coupling Hotspots (10 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| bellows.py | run_plan | 1.000 | 39 | 102 | 0.720 |
| bellows.py | _log | 0.969 | 84 | 0 | 0.606 |
| contract_tables.py | create_contract_tables | 0.962 | 5665 | 56162 | 0.647 |
| gates.py | check | 0.906 | 62 | 11 | 0.369 |
| runner.py | run_step | 0.875 | 20 | 19 | 0.534 |
| bellows.py | slug_for | 0.844 | 35 | 0 | 0.558 |
| bellows.py | _consume_verdicts | 0.844 | 35 | 0 | 0.665 |
| engines/triangulation.py | triangulate | 0.833 | 20466 | 2794 | 0.595 |
| bellows.py | _create_worktree | 0.812 | 27 | 6 | 0.599 |
| ingestion/ingest.py | _to_float | 0.808 | 21191 | 0 | 0.614 |

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
| verdict.py | _extract_step_text_from_plan | 1.000 | 0.505 |

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

## Planner Constraints (103 total)

### coverage_required (28)
- **[high]** `engines/validator.py::gate_9_accessorials` — Composite score 0.79, no test coverage, volatility 0.96
- **[high]** `engines/validator.py::gate_8_fuel` — Composite score 0.78, no test coverage, volatility 0.96
- **[high]** `engines/validator.py::gate_7_linehaul` — Composite score 0.78, no test coverage, volatility 0.96
- **[high]** `web/training.py::training_batch_apply` — Composite score 0.78, no test coverage, volatility 0.76
- **[high]** `web/contracts.py::_build_dashboard_cards` — Composite score 0.78, no test coverage, volatility 0.97
- **[high]** `web/training.py::_identify_training_gaps` — Composite score 0.77, no test coverage, volatility 0.76
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.77, no test coverage, volatility 0.78
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.75, no test coverage, volatility 0.88
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.74, no test coverage, volatility 0.97
- **[high]** `app.py::dispute_brief` — Composite score 0.73, no test coverage, volatility 0.99
- **[high]** `web/contract_import.py::_validate_contract_json` — Composite score 0.73, no test coverage, volatility 0.84
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.73, no test coverage, volatility 0.88
- **[high]** `web/gap_dashboard.py::_import_lanes_section` — Composite score 0.73, no test coverage, volatility 1.00
- **[high]** `engines/action_router.py::route_actions` — Composite score 0.72, no test coverage, volatility 0.89
- **[high]** `app.py::debug_export` — Composite score 0.72, no test coverage, volatility 0.99

### verify_dependents (10)
- **[high]** `bellows.py::run_plan` — Coupling score 1.00, 39 inbound + 102 outbound deps
- **[high]** `bellows.py::_log` — Coupling score 0.97, 84 inbound + 0 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.96, 5665 inbound + 56162 outbound deps
- **[high]** `gates.py::check` — Coupling score 0.91, 62 inbound + 11 outbound deps
- **[high]** `runner.py::run_step` — Coupling score 0.88, 20 inbound + 19 outbound deps
- **[high]** `bellows.py::slug_for` — Coupling score 0.84, 35 inbound + 0 outbound deps
- **[high]** `bellows.py::_consume_verdicts` — Coupling score 0.84, 35 inbound + 0 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.83, 20466 inbound + 2794 outbound deps
- **[high]** `bellows.py::_create_worktree` — Coupling score 0.81, 27 inbound + 6 outbound deps
- **[high]** `ingestion/ingest.py::_to_float` — Coupling score 0.81, 21191 inbound + 0 outbound deps

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
- Dependencies: 1172
- Similarity pairs: 14
- Average health score: 0.2583
- High risk count: 1
