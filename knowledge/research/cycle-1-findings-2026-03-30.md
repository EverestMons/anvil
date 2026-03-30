# Anvil Cycle Report — invoice-pulse — Cycle 1
**Date:** 2026-03-30

## Executive Summary
- **Total files:** 939
- **Total chunks:** 3247
- **High risk chunks:** 119
- **Average composite score:** 0.2616
- **Total findings:** 1212

## Coverage Gaps (117 findings)
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
| web/action_queue.py | _get_db | function | 0.744 | 1.00 | 0.78 |
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
| engines/validator.py | gate_3_billto | function | 0.700 | 1.00 | 0.96 |

## Coupling Hotspots (17 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| profile_ingestion.py | execute | 1.000 | 4148 | 0 | 0.440 |
| profile_ingestion.py | commit | 0.987 | 952 | 0 | 0.433 |
| profile_ingestion.py | close | 0.974 | 430 | 0 | 0.428 |
| contract_tables.py | create_contract_tables | 0.962 | 36 | 212 | 0.647 |
| tests/test_accessorial_aliases.py | _insert_invoice | 0.949 | 238 | 1 | 0.498 |
| tests/test_lifecycle.py | test_main | 0.936 | 0 | 216 | 0.461 |
| tests/test_validator.py | test_main | 0.923 | 0 | 198 | 0.617 |
| tests/test_carrier_profiles.py | get_db | 0.910 | 179 | 1 | 0.550 |
| database.py | get_connection | 0.897 | 167 | 3 | 0.625 |
| web/action_queue.py | _get_db | 0.897 | 169 | 1 | 0.744 |
| database.py | _create_tables | 0.885 | 40 | 117 | 0.627 |
| tests/test_forms_and_uploads.py | test_main | 0.872 | 0 | 126 | 0.619 |
| tests/test_upload_endpoints.py | test_main | 0.859 | 0 | 102 | 0.484 |
| contract_tables.py | extend_existing_tables | 0.846 | 36 | 65 | 0.686 |
| engines/triangulation.py | triangulate | 0.833 | 83 | 11 | 0.595 |
| tests/test_activity_import.py | _seed_invoice | 0.821 | 86 | 2 | 0.478 |
| ingestion/ingest.py | _to_float | 0.808 | 82 | 0 | 0.614 |

## Clone Candidates (381 pairs)
| File A | Name A | File B | Name B | Similarity |
|---|---|---|---|---|
| database.py | __init__ | tests/test_remaining_pipeline_qa.py | __init__ | 1.000 |
| database.py | __getitem__ | tests/test_remaining_pipeline_qa.py | __getitem__ | 1.000 |
| engines/backtest.py | _table_exists | web/action_queue.py | _table_exists | 1.000 |
| engines/backtest.py | _table_exists | web/reporting.py | _table_exists | 1.000 |
| tests/test_accessorial_aliases.py | _make_db | tests/test_zip_5digit.py | _make_db | 1.000 |
| tests/test_activity_import.py | db | tests/test_carrier_auto_merge.py | db | 1.000 |
| tests/test_activity_import.py | app_client | tests/test_carrier_auto_merge.py | app_client | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3.py | db | 1.000 |
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

## Staleness Alerts (118 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.593 |
| engines/action_router.py | _build_summary | 1.000 | 0.722 |
| engines/backtest.py | _table_exists | 1.000 | 0.462 |
| engines/backtest.py | run_backtest | 1.000 | 0.564 |
| engines/circuit_breaker.py | _table_exists | 1.000 | 0.458 |
| engines/circuit_breaker.py | _trip_breaker | 1.000 | 0.500 |
| engines/circuit_breaker.py | reset_breaker | 1.000 | 0.501 |
| engines/confidence.py | _ensure_element | 1.000 | 0.447 |
| engines/confidence.py | _get_contract_invoice_filter | 1.000 | 0.435 |
| engines/confidence.py | transition_state | 1.000 | 0.494 |
| engines/confidence.py | _get_invoice_geo_simple | 1.000 | 0.442 |
| engines/confidence.py | get_contract_confidence_summary | 1.000 | 0.447 |
| engines/confidence.py | record_evidence | 1.000 | 0.509 |
| engines/confidence.py | get_element_evidence | 1.000 | 0.439 |
| engines/confidence.py | resolve_evidence | 1.000 | 0.446 |
| engines/confidence.py | derive_counts_from_evidence | 1.000 | 0.436 |
| engines/confidence.py | record_tier3_signal | 1.000 | 0.438 |
| engines/confidence.py | get_stale_carrier_rates | 1.000 | 0.445 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.527 |
| engines/priority.py | _get_invoice_age | 1.000 | 0.488 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.501 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.448 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.449 |
| system_logger.py | log_event | 1.000 | 0.516 |
| system_logger.py | get_recent_events | 1.000 | 0.467 |
| system_logger.py | get_errors_and_warnings | 1.000 | 0.448 |
| system_logger.py | get_data_freshness | 1.000 | 0.458 |
| system_logger.py | get_system_health | 1.000 | 0.441 |
| tests/conftest.py | app_client | 1.000 | 0.494 |
| tests/test_carrier_rules_tariff_ui.py | test_carrier_profile_detail_empty_cards | 1.000 | 0.203 |

## Complexity Hotspots (76 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| tests/test_contract_templates.py | test_main | 1.000 | 108 | 1 | 1 |
| tests/test_contracts.py | test_main | 1.000 | 101 | 1 | 1 |
| tests/test_disputes.py | test_main | 1.000 | 105 | 1 | 1 |
| tests/test_forms_and_uploads.py | test_main | 1.000 | 132 | 4 | 1 |
| tests/test_lifecycle.py | test_main | 1.000 | 126 | 2 | 1 |
| tests/test_upload_endpoints.py | test_main | 1.000 | 106 | 3 | 1 |
| tests/test_validator.py | test_main | 1.000 | 135 | 1 | 1 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 80 | 4 | 0 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/gap_dashboard.py | _parse_csv_to_json | 1.000 | 72 | 6 | 2 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 63 | 3 | 6 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 63 | 5 | 1 |
| app.py | invoices_list | 0.999 | 61 | 5 | 0 |
| tests/test_training.py | test_main | 0.999 | 63 | 1 | 1 |
| web/gap_dashboard.py | import_contract_setup | 0.999 | 60 | 5 | 1 |
| engines/validator.py | gate_9_accessorials | 0.998 | 56 | 6 | 8 |
| tests/test_confidence.py | test_main | 0.998 | 61 | 1 | 1 |
| web/gap_dashboard.py | enrich_invoice | 0.998 | 58 | 4 | 1 |
| tests/test_validation_results.py | test_main | 0.998 | 60 | 0 | 1 |
| web/rates.py | rates_grid | 0.997 | 57 | 4 | 0 |
| tests/test_xml_validation_enrichment.py | TestScenario1_EnrichmentSucceeds | 0.996 | 57 | 0 | 0 |
| engines/validator.py | gate_7_linehaul | 0.996 | 52 | 4 | 6 |
| ingestion/activity_import.py | import_activity_history | 0.996 | 53 | 3 | 3 |
| web/action_queue.py | action_queue | 0.995 | 51 | 8 | 0 |
| engines/validator.py | gate_8_fuel | 0.994 | 49 | 4 | 7 |
| web/documents.py | document_extract | 0.993 | 48 | 7 | 2 |
| web/gap_dashboard.py | _import_lanes_section | 0.991 | 48 | 4 | 3 |
| app.py | team_dashboard | 0.991 | 48 | 5 | 0 |
| engines/email_generator.py | generate_pricing_ticket | 0.990 | 45 | 6 | 5 |
| app.py | team_member_profile | 0.990 | 47 | 5 | 1 |

## Co-Change Patterns (503 pairs)
| File A | File B | Co-changes | Jaccard |
|---|---|---|---|
| PROJECT_STATUS.md | knowledge/research/agent-prompt-feedback.md | 27 | 0.168 |
| app.py | web/templates/invoice_detail.html | 12 | 0.171 |
| copilot_prompts.py | web/gap_dashboard.py | 12 | 0.197 |
| copilot_prompts.py | web/contracts.py | 11 | 0.234 |
| web/contracts.py | web/gap_dashboard.py | 10 | 0.127 |
| engines/validator.py | web/contracts.py | 9 | 0.141 |
| web/contracts.py | web/templates/contract_fuel.html | 9 | 0.204 |
| web/templates/contract_accessorials.html | web/templates/contract_fuel.html | 9 | 0.529 |
| PROJECT_STATUS.md | contract_tables.py | 8 | 0.143 |
| contract_tables.py | web/contracts.py | 8 | 0.151 |
| engines/validator.py | web/templates/invoice_detail.html | 8 | 0.119 |
| web/contracts.py | web/templates/contract_dashboard.html | 8 | 0.210 |
| web/templates/contract_accessorials.html | web/templates/contract_lanes.html | 8 | 0.667 |
| web/templates/contract_billto.html | web/templates/contract_fak.html | 8 | 1.000 |
| web/templates/contract_fuel.html | web/templates/contract_lanes.html | 8 | 0.444 |
| app.py | database.py | 7 | 0.130 |
| app.py | ingestion/ingest.py | 7 | 0.146 |
| PROJECT_STATUS.md | app.py | 7 | 0.092 |
| app.py | validate_batch.py | 7 | 0.135 |
| contract_tables.py | database.py | 7 | 0.200 |
| contract_tables.py | knowledge/research/agent-prompt-feedback.md | 7 | 0.042 |
| engines/validator.py | knowledge/research/agent-prompt-feedback.md | 7 | 0.040 |
| knowledge/research/agent-prompt-feedback.md | web/contracts.py | 7 | 0.039 |
| knowledge/research/copilot-extraction-quality.md | knowledge/research/validation-quality-summary.md | 7 | 0.700 |
| web/contracts.py | web/templates/contract_lanes.html | 7 | 0.175 |
| web/email_triage.py | web/templates/email_triage.html | 7 | 0.636 |
| web/templates/contract_accessorials.html | web/templates/contract_billto.html | 7 | 0.636 |
| web/templates/contract_accessorials.html | web/templates/contract_fak.html | 7 | 0.636 |
| web/templates/contract_areas.html | web/templates/contract_billto.html | 7 | 0.875 |
| web/templates/contract_areas.html | web/templates/contract_fak.html | 7 | 0.875 |

## Planner Constraints (292 total)

### coverage_required (117)
- **[high]** `engines/validator.py::gate_9_accessorials` — Composite score 0.79, no test coverage, volatility 0.96
- **[high]** `engines/validator.py::gate_8_fuel` — Composite score 0.78, no test coverage, volatility 0.96
- **[high]** `engines/validator.py::gate_7_linehaul` — Composite score 0.78, no test coverage, volatility 0.96
- **[high]** `web/training.py::training_batch_apply` — Composite score 0.78, no test coverage, volatility 0.76
- **[high]** `web/contracts.py::_build_dashboard_cards` — Composite score 0.78, no test coverage, volatility 0.97
- **[high]** `web/training.py::_identify_training_gaps` — Composite score 0.77, no test coverage, volatility 0.76
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.77, no test coverage, volatility 0.78
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.75, no test coverage, volatility 0.88
- **[high]** `web/action_queue.py::_get_db` — Composite score 0.74, no test coverage, volatility 0.78
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.74, no test coverage, volatility 0.97
- **[high]** `app.py::dispute_brief` — Composite score 0.73, no test coverage, volatility 0.99
- **[high]** `web/contract_import.py::_validate_contract_json` — Composite score 0.73, no test coverage, volatility 0.84
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.73, no test coverage, volatility 0.88
- **[high]** `web/gap_dashboard.py::_import_lanes_section` — Composite score 0.73, no test coverage, volatility 1.00
- **[high]** `engines/action_router.py::route_actions` — Composite score 0.72, no test coverage, volatility 0.89

### verify_dependents (17)
- **[high]** `profile_ingestion.py::execute` — Coupling score 1.00, 4148 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::commit` — Coupling score 0.99, 952 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::close` — Coupling score 0.97, 430 inbound + 0 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.96, 36 inbound + 212 outbound deps
- **[high]** `tests/test_accessorial_aliases.py::_insert_invoice` — Coupling score 0.95, 238 inbound + 1 outbound deps
- **[medium]** `tests/test_lifecycle.py::test_main` — Coupling score 0.94, 0 inbound + 216 outbound deps
- **[medium]** `tests/test_validator.py::test_main` — Coupling score 0.92, 0 inbound + 198 outbound deps
- **[high]** `tests/test_carrier_profiles.py::get_db` — Coupling score 0.91, 179 inbound + 1 outbound deps
- **[high]** `database.py::get_connection` — Coupling score 0.90, 167 inbound + 3 outbound deps
- **[high]** `web/action_queue.py::_get_db` — Coupling score 0.90, 169 inbound + 1 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.88, 40 inbound + 117 outbound deps
- **[medium]** `tests/test_forms_and_uploads.py::test_main` — Coupling score 0.87, 0 inbound + 126 outbound deps
- **[medium]** `tests/test_upload_endpoints.py::test_main` — Coupling score 0.86, 0 inbound + 102 outbound deps
- **[high]** `contract_tables.py::extend_existing_tables` — Coupling score 0.85, 36 inbound + 65 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.83, 83 inbound + 11 outbound deps

### refactor_candidate (40)
- **[medium]** `database.py::__init__ ↔ tests/test_remaining_pipeline_qa.py::__init__` — Similarity 1.00 — potential duplicate
- **[medium]** `database.py::__getitem__ ↔ tests/test_remaining_pipeline_qa.py::__getitem__` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/action_queue.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/reporting.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_accessorial_aliases.py::_make_db ↔ tests/test_zip_5digit.py::_make_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::db ↔ tests/test_carrier_auto_merge.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::app_client ↔ tests/test_carrier_auto_merge.py::app_client` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase3 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3 2.py::db` — Similarity 1.00 — potential duplicate

### investigation_needed (118)
- **[high]** `eia_fetcher.py::get_eia_price_for_date` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_summary` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/backtest.py::_table_exists` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/backtest.py::run_backtest` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/circuit_breaker.py::_table_exists` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/circuit_breaker.py::_trip_breaker` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/circuit_breaker.py::reset_breaker` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::_ensure_element` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::_get_contract_invoice_filter` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::transition_state` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::_get_invoice_geo_simple` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::get_contract_confidence_summary` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::record_evidence` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::get_element_evidence` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/confidence.py::resolve_evidence` — Staleness score 1.00 — dependencies updated but chunk unchanged

## Specialist Update Data
- Functions: 1101
- Classes: 359
- Methods: 67
- Test cases: 1720
- Dependencies: 12142
- Similarity pairs: 381
- Average health score: 0.2616
- High risk count: 119
