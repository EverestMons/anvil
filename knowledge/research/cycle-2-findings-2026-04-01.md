# Anvil Cycle Report — invoice-pulse — Cycle 2
**Date:** 2026-04-01

## Executive Summary
- **Total files:** 1223
- **Total chunks:** 3355
- **High risk chunks:** 76
- **Average composite score:** 0.2658
- **Total findings:** 797

## Coverage Gaps (47 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| engines/validator.py | validate_invoice | function | 0.855 | 1.00 | 0.96 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.818 | 1.00 | 0.92 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.811 | 1.00 | 0.92 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.809 | 1.00 | 0.92 |
| engines/validator.py | gate_9_accessorials | function | 0.806 | 1.00 | 0.96 |
| engines/validator.py | gate_8_fuel | function | 0.800 | 1.00 | 0.96 |
| web/contracts.py | _build_dashboard_cards | function | 0.799 | 1.00 | 0.99 |
| engines/validator.py | gate_7_linehaul | function | 0.798 | 1.00 | 0.96 |
| web/contracts.py | contract_fuel_import_combined | function | 0.794 | 1.00 | 0.99 |
| web/contracts.py | contracts_list | function | 0.781 | 1.00 | 0.99 |
| web/training.py | training_batch_apply | function | 0.770 | 1.00 | 0.76 |
| web/action_queue.py | _get_db | function | 0.762 | 1.00 | 0.83 |
| app.py | dispute_brief | function | 0.761 | 1.00 | 1.00 |
| web/contract_import.py | import_contract_json | function | 0.760 | 1.00 | 0.85 |
| app.py | run_validation | function | 0.759 | 1.00 | 1.00 |
| web/contracts.py | contract_lanes_bulk | function | 0.756 | 1.00 | 0.99 |
| web/action_queue.py | action_queue | function | 0.754 | 1.00 | 0.83 |
| web/contract_import.py | _validate_contract_json | function | 0.752 | 1.00 | 0.85 |
| app.py | team_dashboard | function | 0.752 | 1.00 | 1.00 |
| ingestion/activity_import.py | import_activity_history | function | 0.750 | 1.00 | 0.58 |
| app.py | debug_export | function | 0.750 | 1.00 | 1.00 |
| web/documents.py | document_extract | function | 0.745 | 1.00 | 0.64 |
| web/gap_dashboard.py | import_section | function | 0.743 | 1.00 | 0.98 |
| web/gap_dashboard.py | _import_lanes_section | function | 0.742 | 1.00 | 0.98 |
| engines/action_router.py | route_actions | function | 0.741 | 1.00 | 0.89 |
| app.py | invoice_detail | function | 0.738 | 1.00 | 1.00 |
| web/gap_dashboard.py | import_contract_setup | function | 0.737 | 1.00 | 0.98 |
| web/gap_dashboard.py | enrich_invoice | function | 0.737 | 1.00 | 0.98 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.736 | 1.00 | 0.77 |
| web/contracts.py | contract_edit | function | 0.736 | 1.00 | 0.99 |

## Coupling Hotspots (27 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| profile_ingestion.py | execute | 1.000 | 12561 | 0 | 0.435 |
| profile_ingestion.py | commit | 0.992 | 2863 | 0 | 0.428 |
| profile_ingestion.py | close | 0.983 | 1294 | 0 | 0.424 |
| contract_tables.py | create_contract_tables | 0.974 | 105 | 642 | 0.651 |
| tests/test_accessorial_aliases.py | _insert_invoice | 0.966 | 674 | 3 | 0.499 |
| tests/test_lifecycle.py | test_main | 0.957 | 0 | 648 | 0.453 |
| tests/test_validator.py | test_main | 0.949 | 0 | 591 | 0.623 |
| tests/test_carrier_profiles.py | get_db | 0.940 | 537 | 3 | 0.542 |
| web/action_queue.py | _get_db | 0.932 | 533 | 3 | 0.762 |
| database.py | get_connection | 0.923 | 501 | 9 | 0.634 |
| database.py | _create_tables | 0.914 | 117 | 356 | 0.637 |
| tests/test_forms_and_uploads.py | test_main | 0.906 | 0 | 378 | 0.613 |
| tests/test_upload_endpoints.py | test_main | 0.897 | 0 | 306 | 0.515 |
| contract_tables.py | extend_existing_tables | 0.889 | 105 | 197 | 0.715 |
| engines/triangulation.py | triangulate | 0.880 | 249 | 33 | 0.586 |
| tests/test_activity_import.py | _seed_invoice | 0.872 | 258 | 6 | 0.481 |
| ingestion/ingest.py | _to_float | 0.863 | 246 | 0 | 0.627 |
| app.py | _table_exists | 0.855 | 240 | 3 | 0.640 |
| tests/test_accessorial_aliases.py | _insert_contract | 0.855 | 237 | 6 | 0.480 |
| tests/test_confidence.py | test_main | 0.855 | 0 | 243 | 0.465 |
| tests/test_training.py | test_main | 0.855 | 0 | 243 | 0.465 |
| tests/test_integration.py | test_main | 0.846 | 0 | 240 | 0.577 |
| database.py | init_db | 0.838 | 170 | 59 | 0.626 |
| tests/test_navisphere_attestation_qa.py | _setup_full_scenario | 0.829 | 150 | 75 | 0.466 |
| engines/validator.py | validate_invoice | 0.821 | 105 | 116 | 0.855 |
| tests/test_conf_integration.py | test_main | 0.812 | 0 | 219 | 0.574 |
| tests/test_contracts.py | test_main | 0.803 | 0 | 201 | 0.558 |

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
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile.py | db | 1.000 |
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
| app.py | before_request | 1.000 | 0.665 |
| app.py | run_single_validation | 1.000 | 0.672 |
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.600 |
| engines/action_router.py | _build_summary | 1.000 | 0.726 |
| engines/backtest.py | _table_exists | 1.000 | 0.455 |
| engines/backtest.py | run_backtest | 1.000 | 0.580 |
| engines/confidence.py | _ensure_element | 1.000 | 0.458 |
| engines/confidence.py | _get_contract_invoice_filter | 1.000 | 0.439 |
| engines/confidence.py | transition_state | 1.000 | 0.515 |
| engines/confidence.py | _get_invoice_geo_simple | 1.000 | 0.444 |
| engines/confidence.py | get_contract_confidence_summary | 1.000 | 0.462 |
| engines/confidence.py | record_evidence | 1.000 | 0.527 |
| engines/confidence.py | get_element_evidence | 1.000 | 0.445 |
| engines/confidence.py | resolve_evidence | 1.000 | 0.457 |
| engines/confidence.py | derive_counts_from_evidence | 1.000 | 0.444 |
| engines/confidence.py | record_tier3_signal | 1.000 | 0.444 |
| engines/confidence.py | get_stale_carrier_rates | 1.000 | 0.455 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.542 |
| engines/priority.py | _get_invoice_age | 1.000 | 0.478 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.507 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.451 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.452 |
| system_logger.py | log_event | 1.000 | 0.529 |
| system_logger.py | get_recent_events | 1.000 | 0.472 |
| system_logger.py | get_errors_and_warnings | 1.000 | 0.448 |
| system_logger.py | get_data_freshness | 1.000 | 0.465 |
| system_logger.py | get_system_health | 1.000 | 0.442 |
| tests/conftest.py | app_client | 1.000 | 0.484 |
| tests/test_carrier_rules_tariff_ui.py | test_carrier_profile_detail_empty_cards | 1.000 | 0.198 |
| tests/test_carrier_rules_tariff_ui.py | test_accessorials_page_200 | 1.000 | 0.195 |

## Complexity Hotspots (80 findings)
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
| contract_tables.py | database.py | 12 | 0.250 |
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
| PROJECT_STATUS.md | contract_tables.py | 8 | 0.096 |
| app.py | validate_batch.py | 8 | 0.116 |
| contract_tables.py | copilot_prompts.py | 8 | 0.160 |
| contract_tables.py | engines/validator.py | 8 | 0.123 |
| contract_tables.py | web/contracts.py | 8 | 0.114 |
| engines/validator.py | web/templates/invoice_detail.html | 8 | 0.104 |
| web/contracts.py | web/templates/contract_accessorials.html | 8 | 0.148 |
| web/contracts.py | web/templates/contract_lanes.html | 8 | 0.148 |
| web/templates/carrier_fuel.html | web/templates/carrier_minimums.html | 8 | 0.667 |
| web/templates/contract_accessorials.html | web/templates/contract_areas.html | 8 | 0.500 |
| web/templates/contract_billto.html | web/templates/contract_fuel.html | 8 | 0.296 |
| web/templates/contract_billto.html | web/templates/contract_lanes.html | 8 | 0.444 |

## Planner Constraints (193 total)

### coverage_required (47)
- **[high]** `engines/validator.py::validate_invoice` — Composite score 0.85, no test coverage, volatility 0.96
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.82, no test coverage, volatility 0.92
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.81, no test coverage, volatility 0.92
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.81, no test coverage, volatility 0.92
- **[high]** `engines/validator.py::gate_9_accessorials` — Composite score 0.81, no test coverage, volatility 0.96
- **[high]** `engines/validator.py::gate_8_fuel` — Composite score 0.80, no test coverage, volatility 0.96
- **[high]** `web/contracts.py::_build_dashboard_cards` — Composite score 0.80, no test coverage, volatility 0.99
- **[high]** `engines/validator.py::gate_7_linehaul` — Composite score 0.80, no test coverage, volatility 0.96
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.79, no test coverage, volatility 0.99
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.78, no test coverage, volatility 0.99
- **[high]** `web/training.py::training_batch_apply` — Composite score 0.77, no test coverage, volatility 0.76
- **[high]** `web/action_queue.py::_get_db` — Composite score 0.76, no test coverage, volatility 0.83
- **[high]** `app.py::dispute_brief` — Composite score 0.76, no test coverage, volatility 1.00
- **[high]** `web/contract_import.py::import_contract_json` — Composite score 0.76, no test coverage, volatility 0.85
- **[high]** `app.py::run_validation` — Composite score 0.76, no test coverage, volatility 1.00

### verify_dependents (27)
- **[high]** `profile_ingestion.py::execute` — Coupling score 1.00, 12561 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::commit` — Coupling score 0.99, 2863 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::close` — Coupling score 0.98, 1294 inbound + 0 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.97, 105 inbound + 642 outbound deps
- **[high]** `tests/test_accessorial_aliases.py::_insert_invoice` — Coupling score 0.97, 674 inbound + 3 outbound deps
- **[medium]** `tests/test_lifecycle.py::test_main` — Coupling score 0.96, 0 inbound + 648 outbound deps
- **[medium]** `tests/test_validator.py::test_main` — Coupling score 0.95, 0 inbound + 591 outbound deps
- **[high]** `tests/test_carrier_profiles.py::get_db` — Coupling score 0.94, 537 inbound + 3 outbound deps
- **[high]** `web/action_queue.py::_get_db` — Coupling score 0.93, 533 inbound + 3 outbound deps
- **[high]** `database.py::get_connection` — Coupling score 0.92, 501 inbound + 9 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.91, 117 inbound + 356 outbound deps
- **[medium]** `tests/test_forms_and_uploads.py::test_main` — Coupling score 0.91, 0 inbound + 378 outbound deps
- **[medium]** `tests/test_upload_endpoints.py::test_main` — Coupling score 0.90, 0 inbound + 306 outbound deps
- **[high]** `contract_tables.py::extend_existing_tables` — Coupling score 0.89, 105 inbound + 197 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.88, 249 inbound + 33 outbound deps

### refactor_candidate (40)
- **[medium]** `database.py::__init__ ↔ tests/test_remaining_pipeline_qa.py::__init__` — Similarity 1.00 — potential duplicate
- **[medium]** `database.py::__getitem__ ↔ tests/test_remaining_pipeline_qa.py::__getitem__` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/action_queue.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/reporting.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_accessorial_aliases.py::_make_db ↔ tests/test_zip_5digit.py::_make_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::db ↔ tests/test_carrier_auto_merge.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::app_client ↔ tests/test_carrier_auto_merge.py::app_client` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase3 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase3.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3.py::db` — Similarity 1.00 — potential duplicate

### investigation_needed (79)
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
- Functions: 1165
- Classes: 373
- Methods: 67
- Test cases: 1750
- Dependencies: 36585
- Similarity pairs: 815
- Average health score: 0.2658
- High risk count: 76
