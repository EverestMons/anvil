# Anvil Cycle Report — invoice-pulse — Cycle 5
**Date:** 2026-04-01

## Executive Summary
- **Total files:** 1252
- **Total chunks:** 3356
- **High risk chunks:** 222
- **Average composite score:** 0.2599
- **Total findings:** 1674

## Coverage Gaps (49 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/gap_dashboard.py | _reshape_for_apply | function | 0.863 | 1.00 | 0.98 |
| engines/validator.py | validate_invoice | function | 0.856 | 1.00 | 0.97 |
| web/contracts.py | _build_dashboard_cards | function | 0.852 | 1.00 | 0.99 |
| web/contracts.py | contract_fuel_import_combined | function | 0.824 | 1.00 | 0.99 |
| web/training.py | training_batch_apply | function | 0.805 | 1.00 | 0.76 |
| web/action_queue.py | action_queue | function | 0.802 | 1.00 | 0.83 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.800 | 1.00 | 0.92 |
| web/contract_import.py | _validate_contract_json | function | 0.794 | 1.00 | 0.85 |
| web/gap_dashboard.py | _parse_charge_csv_section | function | 0.791 | 1.00 | 0.98 |
| web/contracts.py | contracts_list | function | 0.791 | 1.00 | 0.99 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.790 | 1.00 | 0.92 |
| web/contract_import.py | import_contract_json | function | 0.788 | 1.00 | 0.85 |
| web/contracts.py | contract_lanes_bulk | function | 0.777 | 1.00 | 0.99 |
| web/action_queue.py | record_response | function | 0.774 | 1.00 | 0.83 |
| ingestion/activity_import.py | import_activity_history | function | 0.774 | 1.00 | 0.59 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.771 | 1.00 | 0.92 |
| database.py | _create_tables | function | 0.769 | 1.00 | 0.94 |
| web/rates.py | rates_grid | function | 0.764 | 1.00 | 0.86 |
| app.py | dispute_brief | function | 0.759 | 1.00 | 1.00 |
| contract_tables.py | extend_existing_tables | function | 0.756 | 1.00 | 0.95 |
| app.py | team_dashboard | function | 0.753 | 1.00 | 1.00 |
| app.py | debug_export | function | 0.749 | 1.00 | 1.00 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.748 | 1.00 | 0.78 |
| web/documents.py | document_extract | function | 0.747 | 1.00 | 0.65 |
| engines/action_router.py | route_actions | function | 0.746 | 1.00 | 0.88 |
| web/carrier_profiles.py | _build_carrier_cards | function | 0.738 | 1.00 | 0.92 |
| contract_tables.py | create_contract_tables | function | 0.738 | 1.00 | 0.95 |
| web/email_triage.py | email_archiver | function | 0.737 | 1.00 | 0.87 |
| web/contracts.py | contract_fuel_brackets_bulk | function | 0.736 | 1.00 | 0.99 |
| app.py | invoice_detail | function | 0.733 | 1.00 | 1.00 |

## Coupling Hotspots (26 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| profile_ingestion.py | execute | 1.000 | 63438 | 0 | 0.392 |
| profile_ingestion.py | commit | 0.992 | 14368 | 0 | 0.382 |
| profile_ingestion.py | close | 0.984 | 6490 | 0 | 0.377 |
| contract_tables.py | create_contract_tables | 0.975 | 510 | 3246 | 0.738 |
| tests/test_lifecycle.py | test_main | 0.967 | 0 | 3240 | 0.456 |
| tests/test_accessorial_aliases.py | _insert_invoice | 0.959 | 3170 | 15 | 0.440 |
| tests/test_validator.py | test_main | 0.951 | 0 | 2940 | 0.621 |
| web/action_queue.py | _get_db | 0.943 | 2795 | 15 | 0.724 |
| tests/test_carrier_profiles.py | get_db | 0.934 | 2685 | 15 | 0.474 |
| database.py | get_connection | 0.926 | 2505 | 45 | 0.720 |
| database.py | _create_tables | 0.918 | 570 | 1805 | 0.769 |
| tests/test_forms_and_uploads.py | test_main | 0.910 | 0 | 1890 | 0.612 |
| tests/test_upload_endpoints.py | test_main | 0.902 | 0 | 1530 | 0.521 |
| engines/triangulation.py | triangulate | 0.885 | 1245 | 165 | 0.562 |
| tests/test_activity_import.py | _seed_invoice | 0.877 | 1290 | 30 | 0.425 |
| ingestion/ingest.py | _to_float | 0.869 | 1230 | 0 | 0.630 |
| app.py | _table_exists | 0.861 | 1200 | 15 | 0.547 |
| tests/test_accessorial_aliases.py | _insert_contract | 0.861 | 1185 | 30 | 0.422 |
| tests/test_confidence.py | test_main | 0.861 | 0 | 1215 | 0.468 |
| tests/test_training.py | test_main | 0.861 | 0 | 1215 | 0.468 |
| tests/test_integration.py | test_main | 0.853 | 0 | 1200 | 0.583 |
| tests/test_navisphere_attestation_qa.py | _setup_full_scenario | 0.836 | 750 | 375 | 0.408 |
| engines/validator.py | validate_invoice | 0.828 | 525 | 590 | 0.856 |
| tests/test_conf_integration.py | test_main | 0.820 | 0 | 1095 | 0.577 |
| tests/test_contracts.py | test_main | 0.811 | 0 | 1005 | 0.564 |
| engines/validator.py | add | 0.803 | 966 | 0 | 0.624 |

## Clone Candidates (434 pairs)
| File A | Name A | File B | Name B | Similarity |
|---|---|---|---|---|
| database.py | __init__ | tests/test_remaining_pipeline_qa.py | __init__ | 1.000 |
| database.py | __getitem__ | tests/test_remaining_pipeline_qa.py | __getitem__ | 1.000 |
| engines/backtest.py | _table_exists | web/reporting.py | _table_exists | 1.000 |
| engines/backtest.py | _table_exists | web/action_queue.py | _table_exists | 1.000 |
| tests/test_accessorial_aliases.py | _make_db | tests/test_zip_5digit.py | _make_db | 1.000 |
| tests/test_activity_import.py | db | tests/test_carrier_auto_merge.py | db | 1.000 |
| tests/test_activity_import.py | app_client | tests/test_carrier_auto_merge.py | app_client | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | _insert_contract | tests/test_auto_contract_phase2.py | _insert_contract | 1.000 |
| tests/test_auto_contract_phase2 2.py | _insert_invoice | tests/test_auto_contract_phase2.py | _insert_invoice | 1.000 |
| tests/test_auto_contract_phase2 2.py | TestRetireFlow | tests/test_auto_contract_phase2.py | TestRetireFlow | 1.000 |
| tests/test_auto_contract_phase2 2.py | test_retire_sets_status | tests/test_auto_contract_phase2.py | test_retire_sets_status | 1.000 |
| tests/test_auto_contract_phase2 2.py | test_retire_from_stub | tests/test_auto_contract_phase2.py | test_retire_from_stub | 1.000 |
| tests/test_auto_contract_phase2 2.py | TestResolveContractExclusion | tests/test_auto_contract_phase2.py | TestResolveContractExclusion | 1.000 |
| tests/test_auto_contract_phase2 2.py | test_retired_contract_not_matched | tests/test_auto_contract_phase2.py | test_retired_contract_not_matched | 1.000 |
| tests/test_auto_contract_phase2 2.py | test_active_contract_matched | tests/test_auto_contract_phase2.py | test_active_contract_matched | 1.000 |
| tests/test_auto_contract_phase2 2.py | test_stub_contract_matched | tests/test_auto_contract_phase2.py | test_stub_contract_matched | 1.000 |
| tests/test_auto_contract_phase2 2.py | test_retired_skipped_active_found | tests/test_auto_contract_phase2.py | test_retired_skipped_active_found | 1.000 |
| tests/test_auto_contract_phase2 2.py | TestStubPromotion | tests/test_auto_contract_phase2.py | TestStubPromotion | 1.000 |
| tests/test_auto_contract_phase2 2.py | test_activate_from_stub | tests/test_auto_contract_phase2.py | test_activate_from_stub | 1.000 |
| tests/test_auto_contract_phase2 2.py | test_activate_rejects_active | tests/test_auto_contract_phase2.py | test_activate_rejects_active | 1.000 |
| tests/test_auto_contract_phase2 2.py | test_activate_rejects_retired | tests/test_auto_contract_phase2.py | test_activate_rejects_retired | 1.000 |

## Staleness Alerts (79 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.521 |
| engines/action_router.py | _build_summary | 1.000 | 0.728 |
| engines/backtest.py | _table_exists | 1.000 | 0.496 |
| engines/backtest.py | run_backtest | 1.000 | 0.620 |
| engines/confidence.py | _ensure_element | 1.000 | 0.512 |
| engines/confidence.py | _get_contract_invoice_filter | 1.000 | 0.486 |
| engines/confidence.py | transition_state | 1.000 | 0.584 |
| engines/confidence.py | _get_invoice_geo_simple | 1.000 | 0.487 |
| engines/confidence.py | get_contract_confidence_summary | 1.000 | 0.520 |
| engines/confidence.py | record_evidence | 1.000 | 0.601 |
| engines/confidence.py | get_element_evidence | 1.000 | 0.492 |
| engines/confidence.py | resolve_evidence | 1.000 | 0.511 |
| engines/confidence.py | derive_counts_from_evidence | 1.000 | 0.495 |
| engines/confidence.py | record_tier3_signal | 1.000 | 0.495 |
| engines/confidence.py | get_stale_carrier_rates | 1.000 | 0.505 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.541 |
| engines/priority.py | _get_invoice_age | 1.000 | 0.428 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.459 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.449 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.450 |
| system_logger.py | log_event | 1.000 | 0.532 |
| system_logger.py | get_recent_events | 1.000 | 0.438 |
| system_logger.py | get_errors_and_warnings | 1.000 | 0.409 |
| system_logger.py | get_data_freshness | 1.000 | 0.425 |
| system_logger.py | get_system_health | 1.000 | 0.397 |
| tests/conftest.py | app_client | 1.000 | 0.432 |
| tests/test_carrier_rules_tariff_ui.py | test_carrier_profile_detail_empty_cards | 1.000 | 0.197 |
| tests/test_carrier_rules_tariff_ui.py | test_accessorials_page_200 | 1.000 | 0.195 |
| tests/test_carrier_rules_tariff_ui.py | test_fuel_page_200 | 1.000 | 0.195 |
| tests/test_carrier_rules_tariff_ui.py | test_minimums_page_200 | 1.000 | 0.195 |

## Complexity Hotspots (145 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| tests/test_contract_templates.py | test_main | 1.000 | 108 | 1 | 1 |
| tests/test_contracts.py | test_main | 1.000 | 101 | 1 | 1 |
| tests/test_disputes.py | test_main | 1.000 | 105 | 1 | 1 |
| tests/test_forms_and_uploads.py | test_main | 1.000 | 132 | 4 | 1 |
| tests/test_lifecycle.py | test_main | 1.000 | 126 | 2 | 1 |
| tests/test_upload_endpoints.py | test_main | 1.000 | 106 | 3 | 1 |
| tests/test_validator.py | test_main | 1.000 | 131 | 1 | 1 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 80 | 4 | 0 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/gap_dashboard.py | _parse_csv_to_json | 1.000 | 72 | 6 | 2 |
| web/rates.py | rates_grid | 1.000 | 69 | 4 | 0 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 63 | 3 | 6 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 63 | 5 | 1 |
| tests/test_training.py | test_main | 0.999 | 63 | 1 | 1 |
| web/gap_dashboard.py | import_contract_setup | 0.999 | 60 | 5 | 1 |
| engines/validator.py | gate_9_accessorials | 0.998 | 56 | 6 | 8 |
| app.py | team_dashboard | 0.998 | 59 | 5 | 0 |
| tests/test_confidence.py | test_main | 0.998 | 61 | 1 | 1 |
| web/gap_dashboard.py | enrich_invoice | 0.998 | 58 | 4 | 1 |
| tests/test_validation_results.py | test_main | 0.998 | 60 | 0 | 1 |
| app.py | team_member_profile | 0.996 | 54 | 5 | 1 |
| ingestion/activity_import.py | import_activity_history | 0.996 | 54 | 3 | 3 |
| tests/test_xml_validation_enrichment.py | TestScenario1_EnrichmentSucceeds | 0.996 | 57 | 0 | 0 |
| web/action_queue.py | action_queue | 0.995 | 51 | 8 | 0 |
| web/contracts.py | contracts_list | 0.995 | 52 | 5 | 0 |
| engines/validator.py | gate_8_fuel | 0.994 | 49 | 4 | 7 |
| web/documents.py | document_extract | 0.993 | 48 | 7 | 2 |
| engines/validator.py | gate_7_linehaul | 0.992 | 47 | 4 | 6 |
| web/gap_dashboard.py | _import_lanes_section | 0.991 | 48 | 4 | 3 |
| engines/email_generator.py | generate_pricing_ticket | 0.990 | 45 | 6 | 5 |

## Co-Change Patterns (132 pairs)
| File A | File B | Co-changes | Jaccard |
|---|---|---|---|
| PROJECT_STATUS.md | knowledge/research/agent-prompt-feedback.md | 34 | 0.183 |
| app.py | web/templates/invoice_detail.html | 14 | 0.154 |
| web/templates/contract_fuel.html | web/templates/contract_lanes.html | 14 | 0.518 |
| web/templates/contract_accessorials.html | web/templates/contract_fuel.html | 13 | 0.464 |
| copilot_prompts.py | web/gap_dashboard.py | 13 | 0.181 |
| contract_tables.py | database.py | 12 | 0.245 |
| web/templates/contract_accessorials.html | web/templates/contract_lanes.html | 12 | 0.600 |
| web/templates/contract_billto.html | web/templates/contract_fak.html | 12 | 1.000 |
| copilot_prompts.py | web/contracts.py | 11 | 0.169 |
| web/templates/contract_accessorials.html | web/templates/contract_billto.html | 11 | 0.647 |
| web/templates/contract_accessorials.html | web/templates/contract_fak.html | 11 | 0.647 |
| web/contracts.py | web/gap_dashboard.py | 11 | 0.115 |
| web/contracts.py | web/templates/contract_dashboard.html | 10 | 0.196 |
| web/contracts.py | web/templates/contract_fuel.html | 10 | 0.156 |
| web/templates/contract_areas.html | web/templates/contract_billto.html | 10 | 0.833 |
| web/templates/contract_areas.html | web/templates/contract_fak.html | 10 | 0.833 |
| engines/validator.py | web/contracts.py | 9 | 0.110 |
| web/templates/carrier_fuel.html | web/templates/carrier_minimums.html | 9 | 0.692 |
| web/templates/contract_accessorials.html | web/templates/contract_areas.html | 9 | 0.529 |
| web/templates/contract_billto.html | web/templates/contract_fuel.html | 9 | 0.321 |
| web/templates/contract_billto.html | web/templates/contract_lanes.html | 9 | 0.474 |
| web/templates/contract_fak.html | web/templates/contract_fuel.html | 9 | 0.321 |
| web/templates/contract_fak.html | web/templates/contract_lanes.html | 9 | 0.474 |
| web/contracts.py | web/templates/contracts_list.html | 9 | 0.180 |
| app.py | database.py | 8 | 0.098 |
| PROJECT_STATUS.md | contract_tables.py | 8 | 0.095 |
| app.py | validate_batch.py | 8 | 0.111 |
| contract_tables.py | copilot_prompts.py | 8 | 0.157 |
| contract_tables.py | engines/validator.py | 8 | 0.121 |
| contract_tables.py | web/contracts.py | 8 | 0.110 |

## Research Recommendations (809 deviations across 4 roles)

### data_model (8 deviations)
- **[high]** `contract_tables.py::_migrate_eia_fuel_prices` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `contract_tables.py::_relax_fk_not_null` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_contracts_schema` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_contract_lanes_schema` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_accessorial_aliases` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_alias_unique_constraint` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_fix_stale_fk_references` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_tariff_rates_unique` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS

### route_handler (53 deviations)
- **[medium]** `web/action_queue.py::action_queue` -- single_responsibility: Function has 258 lines (threshold: 80)
- **[medium]** `web/action_queue.py::confirm_carrier` -- single_responsibility: Function has 125 lines (threshold: 80)
- **[medium]** `web/action_queue.py::record_response` -- single_responsibility: Function has 165 lines (threshold: 80)
- **[medium]** `web/action_queue.py::_auto_route_after_response` -- single_responsibility: Function has 118 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profiles_list` -- single_responsibility: Function has 140 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::_build_carrier_cards` -- single_responsibility: Function has 246 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profile_detail` -- single_responsibility: Function has 188 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_accessorials` -- single_responsibility: Function has 200 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_fuel` -- single_responsibility: Function has 264 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_minimums` -- single_responsibility: Function has 190 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_validate_contract_json` -- single_responsibility: Function has 226 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_import_contract` -- single_responsibility: Function has 310 lines (threshold: 80)
- **[medium]** `web/contract_import.py::import_contract_json` -- single_responsibility: Function has 205 lines (threshold: 80)
- **[medium]** `web/contract_template_routes.py::template_upload` -- single_responsibility: Function has 112 lines (threshold: 80)
- **[medium]** `web/contract_templates.py::parse_csv` -- single_responsibility: Function has 87 lines (threshold: 80)

### utility (743 deviations)
- **[medium]** `app.py::handle_csrf_error` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::ingest` -- pure_functions: File I/O found in utility function
- **[medium]** `app.py::ingest` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::ingest_activities` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::ingest_xml_paste` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::invoices_list` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::invoice_search` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::invoice_detail` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::_determine_alignment` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::_gate7_root_causes` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::_gate8_root_causes` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::_gate9_root_causes_per_acc` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::_build_comparison_rows` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::_build_contract_terms` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::dispute_brief` -- no_domain_logic: Domain-specific term found in utility function

### validation_gate (5 deviations)
- **[high]** `engines/validator.py::_resolve_area` -- structured_return_type: Returns raw boolean instead of GateResult
- **[high]** `engines/validator.py::_matches_lane_endpoint` -- structured_return_type: Returns raw boolean instead of GateResult
- **[high]** `engines/validator.py::_zip_in_range` -- structured_return_type: Returns raw boolean instead of GateResult
- **[medium]** `engines/validator.py::_feed_confidence_system` -- deterministic_output: datetime.now() used in gate function
- **[medium]** `engines/validator.py::_check_tariff_freshness` -- deterministic_output: datetime.now() used in gate function

## Planner Constraints (224 total)

### coverage_required (49)
- **[high]** `web/gap_dashboard.py::_reshape_for_apply` — Composite score 0.86, no test coverage, volatility 0.98
- **[high]** `engines/validator.py::validate_invoice` — Composite score 0.86, no test coverage, volatility 0.97
- **[high]** `web/contracts.py::_build_dashboard_cards` — Composite score 0.85, no test coverage, volatility 0.99
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.82, no test coverage, volatility 0.99
- **[high]** `web/training.py::training_batch_apply` — Composite score 0.80, no test coverage, volatility 0.76
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.80, no test coverage, volatility 0.83
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.80, no test coverage, volatility 0.92
- **[high]** `web/contract_import.py::_validate_contract_json` — Composite score 0.79, no test coverage, volatility 0.85
- **[high]** `web/gap_dashboard.py::_parse_charge_csv_section` — Composite score 0.79, no test coverage, volatility 0.98
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.79, no test coverage, volatility 0.99
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.79, no test coverage, volatility 0.92
- **[high]** `web/contract_import.py::import_contract_json` — Composite score 0.79, no test coverage, volatility 0.85
- **[high]** `web/contracts.py::contract_lanes_bulk` — Composite score 0.78, no test coverage, volatility 0.99
- **[high]** `web/action_queue.py::record_response` — Composite score 0.77, no test coverage, volatility 0.83
- **[high]** `ingestion/activity_import.py::import_activity_history` — Composite score 0.77, no test coverage, volatility 0.59

### verify_dependents (26)
- **[high]** `profile_ingestion.py::execute` — Coupling score 1.00, 63438 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::commit` — Coupling score 0.99, 14368 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::close` — Coupling score 0.98, 6490 inbound + 0 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.98, 510 inbound + 3246 outbound deps
- **[medium]** `tests/test_lifecycle.py::test_main` — Coupling score 0.97, 0 inbound + 3240 outbound deps
- **[high]** `tests/test_accessorial_aliases.py::_insert_invoice` — Coupling score 0.96, 3170 inbound + 15 outbound deps
- **[medium]** `tests/test_validator.py::test_main` — Coupling score 0.95, 0 inbound + 2940 outbound deps
- **[high]** `web/action_queue.py::_get_db` — Coupling score 0.94, 2795 inbound + 15 outbound deps
- **[high]** `tests/test_carrier_profiles.py::get_db` — Coupling score 0.93, 2685 inbound + 15 outbound deps
- **[high]** `database.py::get_connection` — Coupling score 0.93, 2505 inbound + 45 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.92, 570 inbound + 1805 outbound deps
- **[medium]** `tests/test_forms_and_uploads.py::test_main` — Coupling score 0.91, 0 inbound + 1890 outbound deps
- **[medium]** `tests/test_upload_endpoints.py::test_main` — Coupling score 0.90, 0 inbound + 1530 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.89, 1245 inbound + 165 outbound deps
- **[high]** `tests/test_activity_import.py::_seed_invoice` — Coupling score 0.88, 1290 inbound + 30 outbound deps

### refactor_candidate (40)
- **[medium]** `database.py::__init__ ↔ tests/test_remaining_pipeline_qa.py::__init__` — Similarity 1.00 — potential duplicate
- **[medium]** `database.py::__getitem__ ↔ tests/test_remaining_pipeline_qa.py::__getitem__` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/reporting.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/action_queue.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_accessorial_aliases.py::_make_db ↔ tests/test_zip_5digit.py::_make_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::db ↔ tests/test_carrier_auto_merge.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::app_client ↔ tests/test_carrier_auto_merge.py::app_client` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase3 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase3.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics 2.py::db` — Similarity 1.00 — potential duplicate

### investigation_needed (79)
- **[high]** `eia_fetcher.py::get_eia_price_for_date` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_summary` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/backtest.py::_table_exists` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/backtest.py::run_backtest` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::_ensure_element` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::_get_contract_invoice_filter` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::transition_state` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::_get_invoice_geo_simple` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::get_contract_confidence_summary` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::record_evidence` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::get_element_evidence` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::resolve_evidence` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::derive_counts_from_evidence` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::record_tier3_signal` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::get_stale_carrier_rates` — Staleness score 1.00 — dependencies updated but chunk unchanged

### pattern_recommendation (30)
- **[high]** `contract_tables.py::_migrate_eia_fuel_prices` — data_model deviates from idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `contract_tables.py::_relax_fk_not_null` — data_model deviates from idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_contracts_schema` — data_model deviates from idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_contract_lanes_schema` — data_model deviates from idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_accessorial_aliases` — data_model deviates from idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_alias_unique_constraint` — data_model deviates from idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_fix_stale_fk_references` — data_model deviates from idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_tariff_rates_unique` — data_model deviates from idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `engines/validator.py::_resolve_area` — validation_gate deviates from structured_return_type: Returns raw boolean instead of GateResult
- **[high]** `engines/validator.py::_matches_lane_endpoint` — validation_gate deviates from structured_return_type: Returns raw boolean instead of GateResult
- **[high]** `engines/validator.py::_zip_in_range` — validation_gate deviates from structured_return_type: Returns raw boolean instead of GateResult
- **[medium]** `web/action_queue.py::action_queue` — route_handler deviates from single_responsibility: Function has 258 lines (threshold: 80)
- **[medium]** `web/action_queue.py::confirm_carrier` — route_handler deviates from single_responsibility: Function has 125 lines (threshold: 80)
- **[medium]** `web/action_queue.py::record_response` — route_handler deviates from single_responsibility: Function has 165 lines (threshold: 80)
- **[medium]** `web/action_queue.py::_auto_route_after_response` — route_handler deviates from single_responsibility: Function has 118 lines (threshold: 80)

## Specialist Update Data
- Functions: 1166
- Classes: 373
- Methods: 67
- Test cases: 1750
- Dependencies: 183794
- Similarity pairs: 2117
- Average health score: 0.2599
- High risk count: 222
