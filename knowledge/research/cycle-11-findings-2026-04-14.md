# Anvil Cycle Report — invoice-pulse — Cycle 11
**Date:** 2026-04-14

## Executive Summary
- **Total files:** 4635
- **Total chunks:** 3836
- **High risk chunks:** 624
- **Average composite score:** 0.2627
- **Total findings:** 2065

## Coverage Gaps (57 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.872 | 1.00 | 0.93 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.865 | 1.00 | 0.93 |
| web/contracts.py | contract_fuel_import_combined | function | 0.861 | 1.00 | 0.98 |
| web/contracts.py | contracts_list | function | 0.858 | 1.00 | 0.98 |
| web/action_queue.py | action_queue | function | 0.845 | 1.00 | 0.83 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.838 | 1.00 | 0.93 |
| ingestion/activity_import.py | import_activity_history | function | 0.834 | 1.00 | 0.61 |
| web/contracts.py | contract_lanes_bulk | function | 0.819 | 1.00 | 0.98 |
| web/action_queue.py | record_response | function | 0.816 | 1.00 | 0.83 |
| web/rates.py | rates_grid | function | 0.809 | 1.00 | 0.89 |
| app.py | dispute_brief | function | 0.805 | 1.00 | 1.00 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.804 | 1.00 | 0.90 |
| app.py | team_dashboard | function | 0.800 | 1.00 | 1.00 |
| app.py | invoice_detail | function | 0.791 | 1.00 | 1.00 |
| ingestion/ingest.py | _run_ingestion_rows | function | 0.790 | 1.00 | 0.88 |
| web/contracts.py | contract_edit | function | 0.789 | 1.00 | 0.98 |
| web/carrier_profiles.py | _build_carrier_cards | function | 0.785 | 1.00 | 0.93 |
| web/contract_import.py | _validate_contract_json | function | 0.784 | 1.00 | 0.73 |
| web/contracts.py | contract_fuel_brackets_bulk | function | 0.778 | 1.00 | 0.98 |
| web/carrier_profiles.py | carrier_profile_detail | function | 0.774 | 1.00 | 0.93 |
| contract_tables.py | extend_existing_tables | function | 0.774 | 1.00 | 0.94 |
| app.py | run_validation | function | 0.772 | 1.00 | 1.00 |
| web/email_triage.py | email_archiver | function | 0.770 | 1.00 | 0.86 |
| web/contracts.py | _save_contract | function | 0.767 | 1.00 | 0.98 |
| app.py | debug_export | function | 0.767 | 1.00 | 1.00 |
| app.py | ingest_xml_paste | function | 0.767 | 1.00 | 1.00 |
| app.py | invoices_list | function | 0.767 | 1.00 | 1.00 |
| web/contracts.py | contract_new | function | 0.762 | 1.00 | 0.98 |
| web/contracts.py | contract_fak_bulk | function | 0.762 | 1.00 | 0.98 |
| validate_batch.py | run_batch | function | 0.758 | 1.00 | 0.86 |

## Coupling Hotspots (78 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| profile_ingestion.py | execute | 1.000 | 389600 | 0 | 0.222 |
| profile_ingestion.py | commit | 0.997 | 86622 | 0 | 0.213 |
| profile_ingestion.py | close | 0.994 | 39906 | 0 | 0.209 |
| contract_tables.py | create_contract_tables | 0.991 | 2569 | 20170 | 0.744 |
| tests/test_lifecycle.py | test_main | 0.988 | 0 | 19687 | 0.443 |
| tests/test_validator.py | test_main | 0.985 | 0 | 17979 | 0.569 |
| web/action_queue.py | _get_db | 0.983 | 16510 | 92 | 0.731 |
| tests/test_carrier_profiles.py | get_db | 0.980 | 16283 | 92 | 0.391 |
| database.py | get_connection | 0.977 | 15249 | 276 | 0.576 |
| database.py | _create_tables | 0.974 | 2834 | 11181 | 0.737 |
| tests/conftest.py | _insert_invoice | 0.971 | 11514 | 22 | 0.424 |
| tests/test_forms_and_uploads.py | test_main | 0.968 | 0 | 11481 | 0.516 |
| tests/test_upload_endpoints.py | test_main | 0.965 | 0 | 9384 | 0.435 |
| tests/test_activity_import.py | _seed_invoice | 0.962 | 8990 | 184 | 0.470 |
| contract_tables.py | extend_existing_tables | 0.959 | 2569 | 6333 | 0.774 |
| engines/triangulation.py | triangulate | 0.956 | 7488 | 1012 | 0.487 |
| database.py | init_db | 0.953 | 5381 | 2346 | 0.575 |
| ingestion/ingest.py | _to_float | 0.950 | 7610 | 0 | 0.643 |
| tests/test_confidence.py | test_main | 0.948 | 0 | 7452 | 0.471 |
| tests/test_training.py | test_main | 0.948 | 0 | 7452 | 0.478 |
| tests/test_integration.py | test_main | 0.945 | 0 | 7360 | 0.471 |
| engines/validator.py | validate_invoice | 0.942 | 3594 | 3654 | 0.619 |
| app.py | _table_exists | 0.939 | 7064 | 55 | 0.559 |
| tests/test_navisphere_attestation_qa.py | _setup_full_scenario | 0.936 | 4600 | 2300 | 0.364 |
| tests/test_conf_integration.py | test_main | 0.933 | 0 | 6716 | 0.471 |
| tests/test_captured_verified_counts.py | _seed_contract | 0.930 | 6336 | 276 | 0.370 |
| engines/validator.py | add | 0.927 | 6170 | 0 | 0.461 |
| tests/test_contracts.py | test_main | 0.924 | 0 | 6164 | 0.491 |
| tests/test_accessorial_aliases.py | _insert_invoice | 0.921 | 5788 | 92 | 0.404 |
| ingestion/activity_import.py | import_activity_history | 0.918 | 3956 | 1693 | 0.834 |

## Clone Candidates (490 pairs)
| File A | Name A | File B | Name B | Similarity |
|---|---|---|---|---|
| app.py | _dashboard_workload_card | app.py | _dashboard_workload_card | 1.000 |
| app.py | dashboard_yesterday_api | app.py | dashboard_yesterday_api | 1.000 |
| app.py | _all_reports_queries | app.py | _all_reports_queries | 1.000 |
| app.py | all_reports | app.py | all_reports | 1.000 |
| app.py | all_reports_export | app.py | all_reports_export | 1.000 |
| app.py | _resolve_entity_range | app.py | _resolve_entity_range | 1.000 |
| app.py | _render_entity_report | app.py | _render_entity_report | 1.000 |
| app.py | report_carrier | app.py | report_carrier | 1.000 |
| app.py | report_customer | app.py | report_customer | 1.000 |
| app.py | report_team | app.py | report_team | 1.000 |
| app.py | customers_list | app.py | customers_list | 1.000 |
| app.py | customer_profile | app.py | customer_profile | 1.000 |
| app.py | customer_activity_api | app.py | customer_activity_api | 1.000 |
| app.py | team_manage | app.py | team_manage | 1.000 |
| app.py | team_create | app.py | team_create | 1.000 |
| app.py | team_add_member | app.py | team_add_member | 1.000 |
| app.py | team_remove_member | app.py | team_remove_member | 1.000 |
| app.py | team_delete | app.py | team_delete | 1.000 |
| app.py | team_rename | app.py | team_rename | 1.000 |
| app.py | team_report_api | app.py | team_report_api | 1.000 |
| app.py | team_pacing_api | app.py | team_pacing_api | 1.000 |
| app.py | _training_data_queries | app.py | _training_data_queries | 1.000 |
| app.py | training_data_view | app.py | training_data_view | 1.000 |
| app.py | training_data_export | app.py | training_data_export | 1.000 |
| app.py | workload_page | app.py | workload_page | 1.000 |
| app.py | workload_list_page | app.py | workload_list_page | 1.000 |
| app.py | workload_list_export | app.py | workload_list_export | 1.000 |
| database.py | __init__ | tests/test_remaining_pipeline_qa.py | __init__ | 1.000 |
| database.py | __getitem__ | tests/test_remaining_pipeline_qa.py | __getitem__ | 1.000 |
| engines/backtest.py | _table_exists | web/action_queue.py | _table_exists | 1.000 |

## Staleness Alerts (62 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.501 |
| engines/action_router.py | _build_dispute_email | 1.000 | 0.645 |
| engines/action_router.py | _build_pricing_ticket | 1.000 | 0.652 |
| engines/action_router.py | _build_summary | 1.000 | 0.723 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.572 |
| engines/training.py | _build_discrepancy | 1.000 | 0.453 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.464 |
| extraction_tracking.py | compute_prompt_version | 1.000 | 0.596 |
| extraction_tracking.py | _compute_fields_multi_section | 1.000 | 0.700 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.471 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.472 |
| tests/conftest.py | app_client | 1.000 | 0.448 |
| tests/test_base_rates_file_upload.py | test_blank_csv_download_returns_correct_headers | 1.000 | 0.256 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_auto_links_contract | 1.000 | 0.248 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_rejects_mismatch | 1.000 | 0.245 |
| tests/test_base_rates_file_upload.py | test_csv_upload_rejects_invalid_extension | 1.000 | 0.245 |
| tests/test_base_rates_file_upload.py | test_csv_upload_with_missing_columns | 1.000 | 0.245 |
| tests/test_contract_display_label.py | test_label_none_contract | 1.000 | 0.190 |
| tests/test_contract_rates_paste.py | test_invoice_detail_rates_url_targets_import_section | 1.000 | 0.338 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_standard | 1.000 | 0.251 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_empty | 1.000 | 0.218 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_valid | 1.000 | 0.228 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_none_safety | 1.000 | 0.218 |
| tests/test_csv_parsers.py | test_contract_setup_happy_path | 1.000 | 0.225 |
| tests/test_csv_parsers.py | test_lanes_combined_format | 1.000 | 0.222 |
| tests/test_csv_parsers.py | test_fuel_float_parsing | 1.000 | 0.222 |
| tests/test_csv_parsers.py | test_empty_csv_returns_error | 1.000 | 0.219 |
| tests/test_csv_parsers.py | test_unknown_section_type_returns_error | 1.000 | 0.216 |
| tests/test_eia_padd_regions.py | test_env | 1.000 | 0.198 |
| tests/test_email_archiver_scope.py | test_resolved_with_dispute_appears | 1.000 | 0.198 |

## Complexity Hotspots (189 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 86 | 5 | 1 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 91 | 4 | 0 |
| tests/test_contract_templates.py | test_main | 1.000 | 108 | 1 | 1 |
| tests/test_contracts.py | test_main | 1.000 | 101 | 1 | 1 |
| tests/test_disputes.py | test_main | 1.000 | 105 | 1 | 1 |
| tests/test_forms_and_uploads.py | test_main | 1.000 | 128 | 4 | 1 |
| tests/test_lifecycle.py | test_main | 1.000 | 113 | 2 | 1 |
| tests/test_upload_endpoints.py | test_main | 1.000 | 106 | 3 | 1 |
| tests/test_validator.py | test_main | 1.000 | 131 | 1 | 1 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/rates.py | rates_grid | 1.000 | 69 | 4 | 0 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 65 | 3 | 6 |
| engines/validator.py | gate_7_linehaul | 0.999 | 62 | 4 | 6 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 63 | 5 | 1 |
| tests/test_training.py | test_main | 0.999 | 63 | 1 | 1 |
| web/gap_dashboard.py | import_contract_setup | 0.999 | 60 | 5 | 1 |
| engines/validator.py | gate_9_accessorials | 0.998 | 56 | 6 | 8 |
| app.py | team_dashboard | 0.998 | 59 | 5 | 0 |
| tests/test_confidence.py | test_main | 0.998 | 61 | 1 | 1 |
| ingestion/activity_import.py | import_activity_history | 0.998 | 58 | 3 | 3 |
| web/gap_dashboard.py | enrich_invoice | 0.998 | 58 | 4 | 1 |
| app.py | team_member_profile | 0.996 | 54 | 5 | 1 |
| tests/test_xml_validation_enrichment.py | TestScenario1_EnrichmentSucceeds | 0.996 | 57 | 0 | 0 |
| web/action_queue.py | action_queue | 0.996 | 52 | 8 | 0 |
| web/contracts.py | contracts_list | 0.995 | 52 | 5 | 0 |
| engines/validator.py | gate_8_fuel | 0.994 | 49 | 4 | 7 |
| web/documents.py | document_extract | 0.993 | 48 | 7 | 2 |
| tests/test_validation_results.py | test_main | 0.992 | 52 | 0 | 1 |
| web/gap_dashboard.py | _import_lanes_section | 0.991 | 48 | 4 | 3 |
| web/gap_dashboard.py | _parse_generic_csv | 0.991 | 46 | 7 | 2 |

## Co-Change Patterns (189 pairs)
| File A | File B | Co-changes | Jaccard |
|---|---|---|---|
| PROJECT_STATUS.md | knowledge/research/agent-prompt-feedback.md | 138 | 0.346 |
| knowledge/research/copilot-extraction-quality.md | knowledge/research/validation-quality-summary.md | 30 | 0.857 |
| app.py | web/templates/invoice_detail.html | 17 | 0.123 |
| contract_tables.py | database.py | 17 | 0.239 |
| copilot_prompts.py | web/gap_dashboard.py | 17 | 0.144 |
| knowledge/research/activity-notes-patterns.md | knowledge/research/validation-quality-summary.md | 16 | 0.485 |
| app.py | knowledge/research/agent-prompt-feedback.md | 16 | 0.041 |
| knowledge/research/activity-notes-patterns.md | knowledge/research/copilot-extraction-quality.md | 15 | 0.429 |
| web/templates/contract_fuel.html | web/templates/contract_lanes.html | 15 | 0.500 |
| web/contracts.py | web/gap_dashboard.py | 15 | 0.099 |
| web/templates/contract_accessorials.html | web/templates/contract_fuel.html | 14 | 0.483 |
| engines/validator.py | web/contracts.py | 13 | 0.118 |
| web/templates/contract_accessorials.html | web/templates/contract_lanes.html | 13 | 0.565 |
| copilot_prompts.py | web/contracts.py | 12 | 0.118 |
| web/contracts.py | web/templates/contract_dashboard.html | 12 | 0.154 |
| web/templates/contract_accessorials.html | web/templates/contract_fak.html | 12 | 0.667 |
| web/templates/contract_billto.html | web/templates/contract_fak.html | 12 | 0.857 |
| app.py | web/templates/dashboard.html | 12 | 0.110 |
| contract_tables.py | knowledge/research/agent-prompt-feedback.md | 11 | 0.032 |
| web/templates/carrier_fuel.html | web/templates/carrier_minimums.html | 11 | 0.733 |
| web/templates/contract_accessorials.html | web/templates/contract_billto.html | 11 | 0.579 |
| web/templates/contract_areas.html | web/templates/contract_fak.html | 11 | 0.786 |
| app.py | ingestion/ingest.py | 10 | 0.090 |
| app.py | web/contracts.py | 10 | 0.061 |
| web/carrier_profiles.py | web/templates/carrier_profile_detail.html | 10 | 0.233 |
| web/contracts.py | web/templates/contract_fuel.html | 10 | 0.112 |
| web/templates/carrier_accessorials.html | web/templates/carrier_fuel.html | 10 | 0.625 |
| web/templates/carrier_accessorials.html | web/templates/carrier_minimums.html | 10 | 0.833 |
| web/templates/carrier_accessorials.html | web/templates/carrier_remote_access.html | 10 | 0.909 |
| web/templates/carrier_fuel.html | web/templates/carrier_remote_access.html | 10 | 0.667 |

## Research Recommendations (980 deviations across 4 roles)

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

### route_handler (57 deviations)
- **[medium]** `web/action_queue.py::action_queue` -- single_responsibility: Function has 265 lines (threshold: 80)
- **[medium]** `web/action_queue.py::confirm_carrier` -- single_responsibility: Function has 125 lines (threshold: 80)
- **[medium]** `web/action_queue.py::record_response` -- single_responsibility: Function has 165 lines (threshold: 80)
- **[medium]** `web/action_queue.py::_auto_route_after_response` -- single_responsibility: Function has 118 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profiles_list` -- single_responsibility: Function has 142 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::_build_carrier_cards` -- single_responsibility: Function has 246 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profile_detail` -- single_responsibility: Function has 200 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_accessorials` -- single_responsibility: Function has 202 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_fuel` -- single_responsibility: Function has 270 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_minimums` -- single_responsibility: Function has 192 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_validate_contract_json` -- single_responsibility: Function has 226 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_import_contract` -- single_responsibility: Function has 310 lines (threshold: 80)
- **[medium]** `web/contract_import.py::import_contract_json` -- single_responsibility: Function has 199 lines (threshold: 80)
- **[medium]** `web/contract_template_routes.py::template_upload` -- single_responsibility: Function has 112 lines (threshold: 80)
- **[medium]** `web/contract_template_routes.py::template_apply` -- single_responsibility: Function has 87 lines (threshold: 80)

### utility (912 deviations)
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

### validation_gate (2 deviations)
- **[medium]** `engines/validator.py::_feed_confidence_system` -- deterministic_output: datetime.now() used in gate function
- **[medium]** `engines/validator.py::_check_tariff_freshness` -- deterministic_output: datetime.now() used in gate function

## Intent Gaps (20 findings)
| Severity | Signal Type | Title | Diagnostic |
|---|---|---|---|
| CRITICAL | coverage_gap | dispute_brief (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | team_dashboard (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | invoice_detail (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | run_validation (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | debug_export (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | ingest_xml_paste (app.py) — uncovered high-volatility function | Fix |
| LOW | coupling_hotspot | execute (profile_ingestion.py) — high-coupling node (coupling_score=1.00) | Architecture check |
| LOW | coupling_hotspot | commit (profile_ingestion.py) — high-coupling node (coupling_score=1.00) | Architecture check |
| LOW | coupling_hotspot | close (profile_ingestion.py) — high-coupling node (coupling_score=0.99) | Architecture check |
| HIGH | coupling_hotspot | create_contract_tables (contract_tables.py) — high-coupling node (coupling_score | Architecture check |
| HIGH | coupling_hotspot | _get_db (web/action_queue.py) — high-coupling node (coupling_score=0.98) | Architecture check |
| MEDIUM | coupling_hotspot | get_connection (database.py) — high-coupling node (coupling_score=0.98) | Architecture check |
| CRITICAL | complexity_hotspot | invoice_detail (app.py) — high cyclomatic complexity (complexity_score=1.00, cyc | Fix |
| MEDIUM | complexity_hotspot | InvoiceXMLParser (ingestion/xml_parser.py) — high cyclomatic complexity (complex | Fix |
| CRITICAL | complexity_hotspot | _validate_contract_json (web/contract_import.py) — high cyclomatic complexity (c | Fix |
| CRITICAL | complexity_hotspot | rates_grid (web/rates.py) — high cyclomatic complexity (complexity_score=1.00, c | Fix |
| HIGH | complexity_hotspot | _build_dashboard_cards (web/contracts.py) — high cyclomatic complexity (complexi | Fix |
| MEDIUM | complexity_hotspot | gate_7_linehaul (engines/validator.py) — high cyclomatic complexity (complexity_ | Fix |
| CRITICAL | complexity_hotspot | contract_fuel_import_combined (web/contracts.py) — high cyclomatic complexity (c | Fix |
| HIGH | complexity_hotspot | import_contract_setup (web/gap_dashboard.py) — high cyclomatic complexity (compl | Fix |

## Planner Constraints (267 total)

### coverage_required (57)
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.87, no test coverage, volatility 0.93
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.86, no test coverage, volatility 0.93
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.86, no test coverage, volatility 0.98
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.86, no test coverage, volatility 0.98
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.85, no test coverage, volatility 0.83
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.84, no test coverage, volatility 0.93
- **[high]** `ingestion/activity_import.py::import_activity_history` — Composite score 0.83, no test coverage, volatility 0.61
- **[high]** `web/contracts.py::contract_lanes_bulk` — Composite score 0.82, no test coverage, volatility 0.98
- **[high]** `web/action_queue.py::record_response` — Composite score 0.82, no test coverage, volatility 0.83
- **[high]** `web/rates.py::rates_grid` — Composite score 0.81, no test coverage, volatility 0.89
- **[high]** `app.py::dispute_brief` — Composite score 0.80, no test coverage, volatility 1.00
- **[high]** `extraction_tracking.py::write_extraction_quality_report` — Composite score 0.80, no test coverage, volatility 0.90
- **[high]** `app.py::team_dashboard` — Composite score 0.80, no test coverage, volatility 1.00
- **[high]** `app.py::invoice_detail` — Composite score 0.79, no test coverage, volatility 1.00
- **[high]** `ingestion/ingest.py::_run_ingestion_rows` — Composite score 0.79, no test coverage, volatility 0.88

### verify_dependents (78)
- **[high]** `profile_ingestion.py::execute` — Coupling score 1.00, 389600 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::commit` — Coupling score 1.00, 86622 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::close` — Coupling score 0.99, 39906 inbound + 0 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.99, 2569 inbound + 20170 outbound deps
- **[medium]** `tests/test_lifecycle.py::test_main` — Coupling score 0.99, 0 inbound + 19687 outbound deps
- **[medium]** `tests/test_validator.py::test_main` — Coupling score 0.99, 0 inbound + 17979 outbound deps
- **[high]** `web/action_queue.py::_get_db` — Coupling score 0.98, 16510 inbound + 92 outbound deps
- **[high]** `tests/test_carrier_profiles.py::get_db` — Coupling score 0.98, 16283 inbound + 92 outbound deps
- **[high]** `database.py::get_connection` — Coupling score 0.98, 15249 inbound + 276 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.97, 2834 inbound + 11181 outbound deps
- **[high]** `tests/conftest.py::_insert_invoice` — Coupling score 0.97, 11514 inbound + 22 outbound deps
- **[medium]** `tests/test_forms_and_uploads.py::test_main` — Coupling score 0.97, 0 inbound + 11481 outbound deps
- **[medium]** `tests/test_upload_endpoints.py::test_main` — Coupling score 0.96, 0 inbound + 9384 outbound deps
- **[high]** `tests/test_activity_import.py::_seed_invoice` — Coupling score 0.96, 8990 inbound + 184 outbound deps
- **[high]** `contract_tables.py::extend_existing_tables` — Coupling score 0.96, 2569 inbound + 6333 outbound deps

### refactor_candidate (40)
- **[medium]** `app.py::_dashboard_workload_card ↔ app.py::_dashboard_workload_card` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::dashboard_yesterday_api ↔ app.py::dashboard_yesterday_api` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::_all_reports_queries ↔ app.py::_all_reports_queries` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::all_reports ↔ app.py::all_reports` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::all_reports_export ↔ app.py::all_reports_export` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::_resolve_entity_range ↔ app.py::_resolve_entity_range` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::_render_entity_report ↔ app.py::_render_entity_report` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::report_carrier ↔ app.py::report_carrier` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::report_customer ↔ app.py::report_customer` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::report_team ↔ app.py::report_team` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::customers_list ↔ app.py::customers_list` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::customer_profile ↔ app.py::customer_profile` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::customer_activity_api ↔ app.py::customer_activity_api` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::team_manage ↔ app.py::team_manage` — Similarity 1.00 — potential duplicate
- **[medium]** `app.py::team_create ↔ app.py::team_create` — Similarity 1.00 — potential duplicate

### investigation_needed (62)
- **[high]** `eia_fetcher.py::get_eia_price_for_date` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_dispute_email` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_pricing_ticket` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_summary` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/email_matcher.py::match_pros_to_invoices` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/training.py::_build_discrepancy` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/variance_analyzer.py::_adjust_confidence_by_history` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `extraction_tracking.py::compute_prompt_version` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `extraction_tracking.py::_compute_fields_multi_section` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `ingestion/csv_reader.py::_map_rows` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `ingestion/csv_reader.py::_read_excel` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/conftest.py::app_client` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_base_rates_file_upload.py::test_blank_csv_download_returns_correct_headers` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_base_rates_file_upload.py::test_csv_file_upload_auto_links_contract` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_base_rates_file_upload.py::test_csv_file_upload_rejects_mismatch` — Staleness score 1.00 — dependencies updated but chunk unchanged

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
- **[medium]** `web/action_queue.py::action_queue` — route_handler deviates from single_responsibility: Function has 265 lines (threshold: 80)
- **[medium]** `web/action_queue.py::confirm_carrier` — route_handler deviates from single_responsibility: Function has 125 lines (threshold: 80)
- **[medium]** `web/action_queue.py::record_response` — route_handler deviates from single_responsibility: Function has 165 lines (threshold: 80)
- **[medium]** `web/action_queue.py::_auto_route_after_response` — route_handler deviates from single_responsibility: Function has 118 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profiles_list` — route_handler deviates from single_responsibility: Function has 142 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::_build_carrier_cards` — route_handler deviates from single_responsibility: Function has 246 lines (threshold: 80)

## Specialist Update Data
- Functions: 1370
- Classes: 423
- Methods: 68
- Test cases: 1975
- Dependencies: 1120028
- Similarity pairs: 5829
- Average health score: 0.2627
- High risk count: 624
