# Anvil Cycle Report — invoice-pulse — Cycle 3
**Date:** 2026-04-01

## Executive Summary
- **Total files:** 1233
- **Total chunks:** 3356
- **High risk chunks:** 122
- **Average composite score:** 0.2621
- **Total findings:** 862

## Coverage Gaps (46 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/gap_dashboard.py | _reshape_for_apply | function | 0.858 | 1.00 | 0.98 |
| engines/validator.py | validate_invoice | function | 0.853 | 1.00 | 0.96 |
| web/contracts.py | _build_dashboard_cards | function | 0.847 | 1.00 | 0.99 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.842 | 1.00 | 0.92 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.831 | 1.00 | 0.92 |
| web/contracts.py | contract_fuel_import_combined | function | 0.830 | 1.00 | 0.99 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.820 | 1.00 | 0.92 |
| web/contracts.py | contracts_list | function | 0.797 | 1.00 | 0.99 |
| web/training.py | training_batch_apply | function | 0.796 | 1.00 | 0.75 |
| web/action_queue.py | action_queue | function | 0.795 | 1.00 | 0.82 |
| web/contract_import.py | _validate_contract_json | function | 0.785 | 1.00 | 0.85 |
| web/contracts.py | contract_lanes_bulk | function | 0.784 | 1.00 | 0.99 |
| web/gap_dashboard.py | _parse_charge_csv_section | function | 0.783 | 1.00 | 0.98 |
| web/contract_import.py | import_contract_json | function | 0.778 | 1.00 | 0.85 |
| ingestion/activity_import.py | import_activity_history | function | 0.769 | 1.00 | 0.59 |
| app.py | run_validation | function | 0.768 | 1.00 | 1.00 |
| database.py | _create_tables | function | 0.766 | 1.00 | 0.94 |
| web/action_queue.py | record_response | function | 0.765 | 1.00 | 0.82 |
| web/rates.py | rates_grid | function | 0.754 | 1.00 | 0.86 |
| contract_tables.py | extend_existing_tables | function | 0.752 | 1.00 | 0.95 |
| app.py | dispute_brief | function | 0.751 | 1.00 | 1.00 |
| web/contracts.py | contract_fuel_brackets_bulk | function | 0.746 | 1.00 | 0.99 |
| web/contracts.py | contract_new | function | 0.746 | 1.00 | 0.99 |
| web/contracts.py | contract_fak_bulk | function | 0.744 | 1.00 | 0.99 |
| app.py | team_dashboard | function | 0.743 | 1.00 | 1.00 |
| engines/action_router.py | route_actions | function | 0.741 | 1.00 | 0.88 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.741 | 1.00 | 0.78 |
| app.py | debug_export | function | 0.738 | 1.00 | 1.00 |
| contract_tables.py | create_contract_tables | function | 0.737 | 1.00 | 0.95 |
| web/documents.py | document_extract | function | 0.737 | 1.00 | 0.65 |

## Coupling Hotspots (23 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| profile_ingestion.py | execute | 1.000 | 25246 | 0 | 0.392 |
| profile_ingestion.py | commit | 0.991 | 5736 | 0 | 0.382 |
| profile_ingestion.py | close | 0.981 | 2592 | 0 | 0.376 |
| contract_tables.py | create_contract_tables | 0.972 | 207 | 1291 | 0.737 |
| tests/test_accessorial_aliases.py | _insert_invoice | 0.963 | 1308 | 6 | 0.439 |
| tests/test_lifecycle.py | test_main | 0.953 | 0 | 1296 | 0.455 |
| tests/test_validator.py | test_main | 0.944 | 0 | 1179 | 0.620 |
| web/action_queue.py | _get_db | 0.935 | 1092 | 6 | 0.722 |
| tests/test_carrier_profiles.py | get_db | 0.925 | 1074 | 6 | 0.469 |
| database.py | get_connection | 0.916 | 1002 | 18 | 0.717 |
| database.py | _create_tables | 0.906 | 231 | 717 | 0.766 |
| tests/test_forms_and_uploads.py | test_main | 0.897 | 0 | 756 | 0.610 |
| tests/test_upload_endpoints.py | test_main | 0.888 | 0 | 612 | 0.515 |
| engines/triangulation.py | triangulate | 0.869 | 498 | 66 | 0.557 |
| tests/test_activity_import.py | _seed_invoice | 0.860 | 516 | 12 | 0.423 |
| ingestion/ingest.py | _to_float | 0.851 | 492 | 0 | 0.626 |
| app.py | _table_exists | 0.841 | 480 | 6 | 0.544 |
| tests/test_accessorial_aliases.py | _insert_contract | 0.841 | 474 | 12 | 0.417 |
| tests/test_confidence.py | test_main | 0.841 | 0 | 486 | 0.466 |
| tests/test_training.py | test_main | 0.841 | 0 | 486 | 0.466 |
| tests/test_integration.py | test_main | 0.832 | 0 | 480 | 0.576 |
| tests/test_navisphere_attestation_qa.py | _setup_full_scenario | 0.813 | 300 | 150 | 0.405 |
| engines/validator.py | validate_invoice | 0.804 | 210 | 234 | 0.853 |

## Clone Candidates (434 pairs)
| File A | Name A | File B | Name B | Similarity |
|---|---|---|---|---|
| database.py | __init__ | tests/test_remaining_pipeline_qa.py | __init__ | 1.000 |
| database.py | __getitem__ | tests/test_remaining_pipeline_qa.py | __getitem__ | 1.000 |
| engines/backtest.py | _table_exists | web/action_queue.py | _table_exists | 1.000 |
| engines/backtest.py | _table_exists | web/reporting.py | _table_exists | 1.000 |
| tests/test_accessorial_aliases.py | _make_db | tests/test_zip_5digit.py | _make_db | 1.000 |
| tests/test_activity_import.py | db | tests/test_carrier_auto_merge.py | db | 1.000 |
| tests/test_activity_import.py | app_client | tests/test_carrier_auto_merge.py | app_client | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3 2.py | db | 1.000 |
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

## Staleness Alerts (84 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| app.py | before_request | 1.000 | 0.569 |
| app.py | run_single_validation | 1.000 | 0.580 |
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.521 |
| engines/action_router.py | _build_summary | 1.000 | 0.729 |
| engines/backtest.py | _table_exists | 1.000 | 0.496 |
| engines/backtest.py | run_backtest | 1.000 | 0.613 |
| engines/confidence.py | _ensure_element | 1.000 | 0.504 |
| engines/confidence.py | _get_contract_invoice_filter | 1.000 | 0.485 |
| engines/confidence.py | transition_state | 1.000 | 0.572 |
| engines/confidence.py | _get_invoice_geo_simple | 1.000 | 0.487 |
| engines/confidence.py | get_contract_confidence_summary | 1.000 | 0.509 |
| engines/confidence.py | record_evidence | 1.000 | 0.589 |
| engines/confidence.py | get_element_evidence | 1.000 | 0.490 |
| engines/confidence.py | resolve_evidence | 1.000 | 0.504 |
| engines/confidence.py | derive_counts_from_evidence | 1.000 | 0.492 |
| engines/confidence.py | record_tier3_signal | 1.000 | 0.491 |
| engines/confidence.py | get_stale_carrier_rates | 1.000 | 0.501 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.532 |
| engines/priority.py | _get_invoice_age | 1.000 | 0.429 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.457 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.449 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.450 |
| system_logger.py | log_event | 1.000 | 0.524 |
| system_logger.py | get_recent_events | 1.000 | 0.436 |
| system_logger.py | get_errors_and_warnings | 1.000 | 0.408 |
| system_logger.py | get_data_freshness | 1.000 | 0.420 |
| system_logger.py | get_system_health | 1.000 | 0.396 |
| tests/conftest.py | app_client | 1.000 | 0.432 |
| tests/test_carrier_rules_tariff_ui.py | test_carrier_profile_detail_empty_cards | 1.000 | 0.197 |
| tests/test_carrier_rules_tariff_ui.py | test_accessorials_page_200 | 1.000 | 0.194 |

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
| engines/validator.py | gate_8_fuel | 0.994 | 49 | 4 | 7 |
| web/documents.py | document_extract | 0.993 | 48 | 7 | 2 |
| engines/validator.py | gate_7_linehaul | 0.992 | 47 | 4 | 6 |
| web/gap_dashboard.py | _import_lanes_section | 0.991 | 48 | 4 | 3 |
| engines/email_generator.py | generate_pricing_ticket | 0.990 | 45 | 6 | 5 |
| app.py | dispute_brief | 0.989 | 46 | 6 | 1 |

## Co-Change Patterns (130 pairs)
| File A | File B | Co-changes | Jaccard |
|---|---|---|---|
| PROJECT_STATUS.md | knowledge/research/agent-prompt-feedback.md | 34 | 0.183 |
| app.py | web/templates/invoice_detail.html | 14 | 0.159 |
| web/templates/contract_fuel.html | web/templates/contract_lanes.html | 13 | 0.500 |
| copilot_prompts.py | web/gap_dashboard.py | 13 | 0.181 |
| contract_tables.py | database.py | 12 | 0.245 |
| web/templates/contract_accessorials.html | web/templates/contract_fuel.html | 12 | 0.444 |
| copilot_prompts.py | web/contracts.py | 11 | 0.175 |
| web/templates/contract_accessorials.html | web/templates/contract_lanes.html | 11 | 0.579 |
| web/templates/contract_billto.html | web/templates/contract_fak.html | 11 | 1.000 |
| web/contracts.py | web/gap_dashboard.py | 11 | 0.117 |
| web/contracts.py | web/templates/contract_dashboard.html | 10 | 0.208 |
| web/contracts.py | web/templates/contract_fuel.html | 10 | 0.164 |
| web/templates/contract_accessorials.html | web/templates/contract_billto.html | 10 | 0.625 |
| web/templates/contract_accessorials.html | web/templates/contract_fak.html | 10 | 0.625 |
| engines/validator.py | web/contracts.py | 9 | 0.113 |
| web/templates/contract_areas.html | web/templates/contract_billto.html | 9 | 0.818 |
| web/templates/contract_areas.html | web/templates/contract_fak.html | 9 | 0.818 |
| app.py | database.py | 8 | 0.100 |
| PROJECT_STATUS.md | contract_tables.py | 8 | 0.095 |
| app.py | validate_batch.py | 8 | 0.114 |
| contract_tables.py | copilot_prompts.py | 8 | 0.157 |
| contract_tables.py | engines/validator.py | 8 | 0.121 |
| contract_tables.py | web/contracts.py | 8 | 0.113 |
| engines/validator.py | web/templates/invoice_detail.html | 8 | 0.104 |
| web/contracts.py | web/templates/contract_accessorials.html | 8 | 0.148 |
| web/contracts.py | web/templates/contract_lanes.html | 8 | 0.148 |
| web/templates/carrier_fuel.html | web/templates/carrier_minimums.html | 8 | 0.667 |
| web/templates/contract_accessorials.html | web/templates/contract_areas.html | 8 | 0.500 |
| web/templates/contract_billto.html | web/templates/contract_fuel.html | 8 | 0.296 |
| web/templates/contract_billto.html | web/templates/contract_lanes.html | 8 | 0.444 |

## Planner Constraints (193 total)

### coverage_required (46)
- **[high]** `web/gap_dashboard.py::_reshape_for_apply` — Composite score 0.86, no test coverage, volatility 0.98
- **[high]** `engines/validator.py::validate_invoice` — Composite score 0.85, no test coverage, volatility 0.96
- **[high]** `web/contracts.py::_build_dashboard_cards` — Composite score 0.85, no test coverage, volatility 0.99
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.84, no test coverage, volatility 0.92
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.83, no test coverage, volatility 0.92
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.83, no test coverage, volatility 0.99
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.82, no test coverage, volatility 0.92
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.80, no test coverage, volatility 0.99
- **[high]** `web/training.py::training_batch_apply` — Composite score 0.80, no test coverage, volatility 0.75
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.79, no test coverage, volatility 0.82
- **[high]** `web/contract_import.py::_validate_contract_json` — Composite score 0.79, no test coverage, volatility 0.85
- **[high]** `web/contracts.py::contract_lanes_bulk` — Composite score 0.78, no test coverage, volatility 0.99
- **[high]** `web/gap_dashboard.py::_parse_charge_csv_section` — Composite score 0.78, no test coverage, volatility 0.98
- **[high]** `web/contract_import.py::import_contract_json` — Composite score 0.78, no test coverage, volatility 0.85
- **[high]** `ingestion/activity_import.py::import_activity_history` — Composite score 0.77, no test coverage, volatility 0.59

### verify_dependents (23)
- **[high]** `profile_ingestion.py::execute` — Coupling score 1.00, 25246 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::commit` — Coupling score 0.99, 5736 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::close` — Coupling score 0.98, 2592 inbound + 0 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.97, 207 inbound + 1291 outbound deps
- **[high]** `tests/test_accessorial_aliases.py::_insert_invoice` — Coupling score 0.96, 1308 inbound + 6 outbound deps
- **[medium]** `tests/test_lifecycle.py::test_main` — Coupling score 0.95, 0 inbound + 1296 outbound deps
- **[medium]** `tests/test_validator.py::test_main` — Coupling score 0.94, 0 inbound + 1179 outbound deps
- **[high]** `web/action_queue.py::_get_db` — Coupling score 0.93, 1092 inbound + 6 outbound deps
- **[high]** `tests/test_carrier_profiles.py::get_db` — Coupling score 0.93, 1074 inbound + 6 outbound deps
- **[high]** `database.py::get_connection` — Coupling score 0.92, 1002 inbound + 18 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.91, 231 inbound + 717 outbound deps
- **[medium]** `tests/test_forms_and_uploads.py::test_main` — Coupling score 0.90, 0 inbound + 756 outbound deps
- **[medium]** `tests/test_upload_endpoints.py::test_main` — Coupling score 0.89, 0 inbound + 612 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.87, 498 inbound + 66 outbound deps
- **[high]** `tests/test_activity_import.py::_seed_invoice` — Coupling score 0.86, 516 inbound + 12 outbound deps

### refactor_candidate (40)
- **[medium]** `database.py::__init__ ↔ tests/test_remaining_pipeline_qa.py::__init__` — Similarity 1.00 — potential duplicate
- **[medium]** `database.py::__getitem__ ↔ tests/test_remaining_pipeline_qa.py::__getitem__` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/action_queue.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/reporting.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_accessorial_aliases.py::_make_db ↔ tests/test_zip_5digit.py::_make_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::db ↔ tests/test_carrier_auto_merge.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::app_client ↔ tests/test_carrier_auto_merge.py::app_client` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase3.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase2.py::db` — Similarity 1.00 — potential duplicate

### investigation_needed (84)
- **[high]** `app.py::before_request` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `app.py::run_single_validation` — Staleness score 1.00 — dependencies updated but chunk unchanged
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

## Specialist Update Data
- Functions: 1166
- Classes: 373
- Methods: 67
- Test cases: 1750
- Dependencies: 73340
- Similarity pairs: 1249
- Average health score: 0.2621
- High risk count: 122
