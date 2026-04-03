# Anvil Cycle Report — invoice-pulse — Cycle 6
**Date:** 2026-04-03

## Executive Summary
- **Total files:** 2011
- **Total chunks:** 3404
- **High risk chunks:** 281
- **Average composite score:** 0.2602
- **Total findings:** 1728

## Coverage Gaps (59 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/gap_dashboard.py | _reshape_for_apply | function | 0.881 | 1.00 | 0.97 |
| web/contracts.py | _build_dashboard_cards | function | 0.873 | 1.00 | 0.99 |
| engines/validator.py | validate_invoice | function | 0.867 | 1.00 | 0.96 |
| web/contracts.py | contract_fuel_import_combined | function | 0.850 | 1.00 | 0.99 |
| web/training.py | training_batch_apply | function | 0.827 | 1.00 | 0.73 |
| web/action_queue.py | action_queue | function | 0.826 | 1.00 | 0.81 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.825 | 1.00 | 0.91 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.817 | 1.00 | 0.91 |
| web/contracts.py | contracts_list | function | 0.815 | 1.00 | 0.99 |
| web/gap_dashboard.py | _parse_charge_csv_section | function | 0.813 | 1.00 | 0.97 |
| web/contract_import.py | _validate_contract_json | function | 0.810 | 1.00 | 0.82 |
| web/contract_import.py | import_contract_json | function | 0.806 | 1.00 | 0.82 |
| web/contracts.py | contract_lanes_bulk | function | 0.801 | 1.00 | 0.99 |
| web/action_queue.py | record_response | function | 0.795 | 1.00 | 0.81 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.794 | 1.00 | 0.91 |
| ingestion/activity_import.py | import_activity_history | function | 0.789 | 1.00 | 0.59 |
| app.py | dispute_brief | function | 0.788 | 1.00 | 1.00 |
| web/rates.py | rates_grid | function | 0.785 | 1.00 | 0.85 |
| app.py | team_dashboard | function | 0.780 | 1.00 | 1.00 |
| database.py | _create_tables | function | 0.777 | 1.00 | 0.94 |
| app.py | debug_export | function | 0.770 | 1.00 | 1.00 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.768 | 1.00 | 0.76 |
| web/documents.py | document_extract | function | 0.768 | 1.00 | 0.62 |
| contract_tables.py | extend_existing_tables | function | 0.768 | 1.00 | 0.95 |
| engines/action_router.py | route_actions | function | 0.764 | 1.00 | 0.87 |
| app.py | invoice_detail | function | 0.761 | 1.00 | 1.00 |
| web/carrier_profiles.py | _build_carrier_cards | function | 0.761 | 1.00 | 0.91 |
| web/contracts.py | contract_fuel_brackets_bulk | function | 0.761 | 1.00 | 0.99 |
| web/contracts.py | contract_edit | function | 0.756 | 1.00 | 0.99 |
| web/email_triage.py | email_archiver | function | 0.756 | 1.00 | 0.86 |

## Coupling Hotspots (53 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| profile_ingestion.py | execute | 1.000 | 88743 | 0 | 0.393 |
| profile_ingestion.py | commit | 0.996 | 20072 | 0 | 0.384 |
| profile_ingestion.py | close | 0.991 | 9081 | 0 | 0.379 |
| contract_tables.py | create_contract_tables | 0.987 | 711 | 4553 | 0.740 |
| tests/test_lifecycle.py | test_main | 0.983 | 0 | 4531 | 0.448 |
| tests/test_accessorial_aliases.py | _insert_invoice | 0.978 | 4386 | 21 | 0.444 |
| tests/test_validator.py | test_main | 0.974 | 0 | 4113 | 0.621 |
| web/action_queue.py | _get_db | 0.970 | 3908 | 21 | 0.725 |
| tests/test_carrier_profiles.py | get_db | 0.965 | 3754 | 21 | 0.471 |
| database.py | get_connection | 0.961 | 3492 | 63 | 0.727 |
| database.py | _create_tables | 0.957 | 794 | 2532 | 0.777 |
| tests/test_forms_and_uploads.py | test_main | 0.952 | 0 | 2643 | 0.611 |
| tests/test_upload_endpoints.py | test_main | 0.948 | 0 | 2142 | 0.522 |
| contract_tables.py | extend_existing_tables | 0.944 | 711 | 1397 | 0.768 |
| engines/triangulation.py | triangulate | 0.939 | 1739 | 231 | 0.569 |
| tests/test_activity_import.py | _seed_invoice | 0.935 | 1806 | 42 | 0.437 |
| ingestion/ingest.py | _to_float | 0.930 | 1722 | 0 | 0.640 |
| tests/test_accessorial_aliases.py | _insert_contract | 0.926 | 1659 | 42 | 0.433 |
| tests/test_confidence.py | test_main | 0.926 | 0 | 1701 | 0.467 |
| tests/test_training.py | test_main | 0.926 | 0 | 1701 | 0.467 |
| app.py | _table_exists | 0.922 | 1672 | 20 | 0.557 |
| database.py | init_db | 0.917 | 1228 | 458 | 0.718 |
| tests/test_integration.py | test_main | 0.913 | 0 | 1680 | 0.583 |
| tests/test_navisphere_attestation_qa.py | _setup_full_scenario | 0.909 | 1050 | 525 | 0.414 |
| engines/validator.py | validate_invoice | 0.904 | 735 | 828 | 0.867 |
| tests/test_conf_integration.py | test_main | 0.900 | 0 | 1533 | 0.582 |
| tests/test_contracts.py | test_main | 0.896 | 0 | 1407 | 0.571 |
| engines/validator.py | add | 0.891 | 1359 | 0 | 0.637 |
| ingestion/activity_import.py | import_activity_history | 0.887 | 903 | 379 | 0.789 |
| tests/test_carrier_profiles.py | test_main | 0.883 | 0 | 1260 | 0.482 |

## Clone Candidates (436 pairs)
| File A | Name A | File B | Name B | Similarity |
|---|---|---|---|---|
| database.py | __init__ | tests/test_remaining_pipeline_qa.py | __init__ | 1.000 |
| database.py | __getitem__ | tests/test_remaining_pipeline_qa.py | __getitem__ | 1.000 |
| engines/backtest.py | _table_exists | web/reporting.py | _table_exists | 1.000 |
| engines/backtest.py | _table_exists | web/action_queue.py | _table_exists | 1.000 |
| tests/test_accessorial_aliases.py | _make_db | tests/test_zip_5digit.py | _make_db | 1.000 |
| tests/test_activity_import.py | db | tests/test_carrier_auto_merge.py | db | 1.000 |
| tests/test_activity_import.py | app_client | tests/test_carrier_auto_merge.py | app_client | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics 2.py | db | 1.000 |
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
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.522 |
| engines/action_router.py | _build_summary | 1.000 | 0.733 |
| engines/backtest.py | _table_exists | 1.000 | 0.498 |
| engines/backtest.py | run_backtest | 1.000 | 0.645 |
| engines/confidence.py | _ensure_element | 1.000 | 0.536 |
| engines/confidence.py | _get_contract_invoice_filter | 1.000 | 0.500 |
| engines/confidence.py | transition_state | 1.000 | 0.619 |
| engines/confidence.py | _get_invoice_geo_simple | 1.000 | 0.496 |
| engines/confidence.py | get_contract_confidence_summary | 1.000 | 0.549 |
| engines/confidence.py | record_evidence | 1.000 | 0.632 |
| engines/confidence.py | get_element_evidence | 1.000 | 0.510 |
| engines/confidence.py | resolve_evidence | 1.000 | 0.536 |
| engines/confidence.py | derive_counts_from_evidence | 1.000 | 0.514 |
| engines/confidence.py | record_tier3_signal | 1.000 | 0.512 |
| engines/confidence.py | get_stale_carrier_rates | 1.000 | 0.529 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.566 |
| engines/priority.py | _get_invoice_age | 1.000 | 0.435 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.469 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.460 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.461 |
| system_logger.py | log_event | 1.000 | 0.558 |
| system_logger.py | get_recent_events | 1.000 | 0.455 |
| system_logger.py | get_errors_and_warnings | 1.000 | 0.422 |
| system_logger.py | get_data_freshness | 1.000 | 0.444 |
| system_logger.py | get_system_health | 1.000 | 0.411 |
| tests/conftest.py | app_client | 1.000 | 0.429 |
| tests/test_carrier_rules_tariff_ui.py | test_carrier_profile_detail_empty_cards | 1.000 | 0.204 |
| tests/test_carrier_rules_tariff_ui.py | test_accessorials_page_200 | 1.000 | 0.201 |
| tests/test_carrier_rules_tariff_ui.py | test_fuel_page_200 | 1.000 | 0.201 |
| tests/test_carrier_rules_tariff_ui.py | test_minimums_page_200 | 1.000 | 0.201 |

## Complexity Hotspots (150 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 91 | 4 | 0 |
| tests/test_contract_templates.py | test_main | 1.000 | 108 | 1 | 1 |
| tests/test_contracts.py | test_main | 1.000 | 101 | 1 | 1 |
| tests/test_disputes.py | test_main | 1.000 | 105 | 1 | 1 |
| tests/test_forms_and_uploads.py | test_main | 1.000 | 128 | 4 | 1 |
| tests/test_lifecycle.py | test_main | 1.000 | 113 | 2 | 1 |
| tests/test_upload_endpoints.py | test_main | 1.000 | 106 | 3 | 1 |
| tests/test_validator.py | test_main | 1.000 | 131 | 1 | 1 |
| web/gap_dashboard.py | _parse_csv_to_json | 1.000 | 109 | 6 | 2 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/rates.py | rates_grid | 1.000 | 69 | 4 | 0 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 63 | 3 | 6 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 63 | 5 | 1 |
| tests/test_training.py | test_main | 0.999 | 63 | 1 | 1 |
| web/gap_dashboard.py | import_contract_setup | 0.999 | 60 | 5 | 1 |
| app.py | invoice_detail | 0.998 | 60 | 4 | 1 |
| engines/validator.py | gate_9_accessorials | 0.998 | 56 | 6 | 8 |
| app.py | team_dashboard | 0.998 | 59 | 5 | 0 |
| tests/test_confidence.py | test_main | 0.998 | 61 | 1 | 1 |
| ingestion/activity_import.py | import_activity_history | 0.998 | 58 | 3 | 3 |
| web/gap_dashboard.py | enrich_invoice | 0.998 | 58 | 4 | 1 |
| tests/test_validation_results.py | test_main | 0.998 | 60 | 0 | 1 |
| app.py | team_member_profile | 0.996 | 54 | 5 | 1 |
| tests/test_xml_validation_enrichment.py | TestScenario1_EnrichmentSucceeds | 0.996 | 57 | 0 | 0 |
| web/action_queue.py | action_queue | 0.996 | 52 | 8 | 0 |
| web/contracts.py | contracts_list | 0.995 | 52 | 5 | 0 |
| engines/validator.py | gate_8_fuel | 0.994 | 49 | 4 | 7 |
| web/documents.py | document_extract | 0.993 | 48 | 7 | 2 |
| engines/validator.py | gate_7_linehaul | 0.992 | 47 | 4 | 6 |
| web/gap_dashboard.py | _import_lanes_section | 0.991 | 48 | 4 | 3 |

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

## Research Recommendations (819 deviations across 4 roles)

### data_model (9 deviations)
- **[high]** `contract_tables.py::_migrate_eia_fuel_prices` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `contract_tables.py::_relax_fk_not_null` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_contracts_schema` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_contract_lanes_schema` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_accessorial_aliases` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_alias_unique_constraint` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_fix_stale_fk_references` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_migrate_tariff_rates_unique` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `database.py::_fix_invoice_charges_tariff_fk` -- idempotent_schema: CREATE TABLE without IF NOT EXISTS

### route_handler (55 deviations)
- **[medium]** `web/action_queue.py::action_queue` -- single_responsibility: Function has 265 lines (threshold: 80)
- **[medium]** `web/action_queue.py::confirm_carrier` -- single_responsibility: Function has 125 lines (threshold: 80)
- **[medium]** `web/action_queue.py::record_response` -- single_responsibility: Function has 165 lines (threshold: 80)
- **[medium]** `web/action_queue.py::_auto_route_after_response` -- single_responsibility: Function has 118 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profiles_list` -- single_responsibility: Function has 142 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::_build_carrier_cards` -- single_responsibility: Function has 246 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profile_detail` -- single_responsibility: Function has 200 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_accessorials` -- single_responsibility: Function has 200 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_fuel` -- single_responsibility: Function has 264 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_minimums` -- single_responsibility: Function has 190 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_validate_contract_json` -- single_responsibility: Function has 226 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_import_contract` -- single_responsibility: Function has 310 lines (threshold: 80)
- **[medium]** `web/contract_import.py::import_contract_json` -- single_responsibility: Function has 205 lines (threshold: 80)
- **[medium]** `web/contract_template_routes.py::template_upload` -- single_responsibility: Function has 112 lines (threshold: 80)
- **[medium]** `web/contract_templates.py::parse_csv` -- single_responsibility: Function has 87 lines (threshold: 80)

### utility (750 deviations)
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

## Planner Constraints (261 total)

### coverage_required (59)
- **[high]** `web/gap_dashboard.py::_reshape_for_apply` — Composite score 0.88, no test coverage, volatility 0.97
- **[high]** `web/contracts.py::_build_dashboard_cards` — Composite score 0.87, no test coverage, volatility 0.99
- **[high]** `engines/validator.py::validate_invoice` — Composite score 0.87, no test coverage, volatility 0.96
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.85, no test coverage, volatility 0.99
- **[high]** `web/training.py::training_batch_apply` — Composite score 0.83, no test coverage, volatility 0.73
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.83, no test coverage, volatility 0.81
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.82, no test coverage, volatility 0.91
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.82, no test coverage, volatility 0.91
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.81, no test coverage, volatility 0.99
- **[high]** `web/gap_dashboard.py::_parse_charge_csv_section` — Composite score 0.81, no test coverage, volatility 0.97
- **[high]** `web/contract_import.py::_validate_contract_json` — Composite score 0.81, no test coverage, volatility 0.82
- **[high]** `web/contract_import.py::import_contract_json` — Composite score 0.81, no test coverage, volatility 0.82
- **[high]** `web/contracts.py::contract_lanes_bulk` — Composite score 0.80, no test coverage, volatility 0.99
- **[high]** `web/action_queue.py::record_response` — Composite score 0.80, no test coverage, volatility 0.81
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.79, no test coverage, volatility 0.91

### verify_dependents (53)
- **[high]** `profile_ingestion.py::execute` — Coupling score 1.00, 88743 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::commit` — Coupling score 1.00, 20072 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::close` — Coupling score 0.99, 9081 inbound + 0 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.99, 711 inbound + 4553 outbound deps
- **[medium]** `tests/test_lifecycle.py::test_main` — Coupling score 0.98, 0 inbound + 4531 outbound deps
- **[high]** `tests/test_accessorial_aliases.py::_insert_invoice` — Coupling score 0.98, 4386 inbound + 21 outbound deps
- **[medium]** `tests/test_validator.py::test_main` — Coupling score 0.97, 0 inbound + 4113 outbound deps
- **[high]** `web/action_queue.py::_get_db` — Coupling score 0.97, 3908 inbound + 21 outbound deps
- **[high]** `tests/test_carrier_profiles.py::get_db` — Coupling score 0.97, 3754 inbound + 21 outbound deps
- **[high]** `database.py::get_connection` — Coupling score 0.96, 3492 inbound + 63 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.96, 794 inbound + 2532 outbound deps
- **[medium]** `tests/test_forms_and_uploads.py::test_main` — Coupling score 0.95, 0 inbound + 2643 outbound deps
- **[medium]** `tests/test_upload_endpoints.py::test_main` — Coupling score 0.95, 0 inbound + 2142 outbound deps
- **[high]** `contract_tables.py::extend_existing_tables` — Coupling score 0.94, 711 inbound + 1397 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.94, 1739 inbound + 231 outbound deps

### refactor_candidate (40)
- **[medium]** `database.py::__init__ ↔ tests/test_remaining_pipeline_qa.py::__init__` — Similarity 1.00 — potential duplicate
- **[medium]** `database.py::__getitem__ ↔ tests/test_remaining_pipeline_qa.py::__getitem__` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/reporting.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/action_queue.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_accessorial_aliases.py::_make_db ↔ tests/test_zip_5digit.py::_make_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::db ↔ tests/test_carrier_auto_merge.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::app_client ↔ tests/test_carrier_auto_merge.py::app_client` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase3 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase3.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3 2.py::db` — Similarity 1.00 — potential duplicate

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
- **[high]** `database.py::_fix_invoice_charges_tariff_fk` — data_model deviates from idempotent_schema: CREATE TABLE without IF NOT EXISTS
- **[high]** `engines/validator.py::_resolve_area` — validation_gate deviates from structured_return_type: Returns raw boolean instead of GateResult
- **[high]** `engines/validator.py::_matches_lane_endpoint` — validation_gate deviates from structured_return_type: Returns raw boolean instead of GateResult
- **[high]** `engines/validator.py::_zip_in_range` — validation_gate deviates from structured_return_type: Returns raw boolean instead of GateResult
- **[medium]** `web/action_queue.py::action_queue` — route_handler deviates from single_responsibility: Function has 265 lines (threshold: 80)
- **[medium]** `web/action_queue.py::confirm_carrier` — route_handler deviates from single_responsibility: Function has 125 lines (threshold: 80)
- **[medium]** `web/action_queue.py::record_response` — route_handler deviates from single_responsibility: Function has 165 lines (threshold: 80)

## Specialist Update Data
- Functions: 1195
- Classes: 377
- Methods: 67
- Test cases: 1765
- Dependencies: 256886
- Similarity pairs: 2553
- Average health score: 0.2602
- High risk count: 281
