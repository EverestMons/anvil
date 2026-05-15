# Anvil Cycle Report — invoice-pulse — Cycle 9
**Date:** 2026-04-14

## Executive Summary
- **Total files:** 4635
- **Total chunks:** 3836
- **High risk chunks:** 510
- **Average composite score:** 0.2620
- **Total findings:** 3361

## Coverage Gaps (108 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.869 | 1.00 | 0.93 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.869 | 1.00 | 0.93 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.862 | 1.00 | 0.93 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.862 | 1.00 | 0.93 |
| web/contracts.py | contract_fuel_import_combined | function | 0.859 | 1.00 | 0.98 |
| web/contracts.py | contract_fuel_import_combined | function | 0.859 | 1.00 | 0.98 |
| web/contracts.py | contracts_list | function | 0.855 | 1.00 | 0.98 |
| web/contracts.py | contracts_list | function | 0.855 | 1.00 | 0.98 |
| web/action_queue.py | action_queue | function | 0.841 | 1.00 | 0.82 |
| web/action_queue.py | action_queue | function | 0.841 | 1.00 | 0.82 |
| ingestion/activity_import.py | import_activity_history | function | 0.834 | 1.00 | 0.62 |
| ingestion/activity_import.py | import_activity_history | function | 0.834 | 1.00 | 0.62 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.834 | 1.00 | 0.93 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.834 | 1.00 | 0.93 |
| web/action_queue.py | record_response | function | 0.818 | 1.00 | 0.82 |
| web/action_queue.py | record_response | function | 0.818 | 1.00 | 0.82 |
| web/contracts.py | contract_lanes_bulk | function | 0.816 | 1.00 | 0.98 |
| web/contracts.py | contract_lanes_bulk | function | 0.816 | 1.00 | 0.98 |
| web/rates.py | rates_grid | function | 0.810 | 1.00 | 0.89 |
| web/rates.py | rates_grid | function | 0.810 | 1.00 | 0.89 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.803 | 1.00 | 0.90 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.803 | 1.00 | 0.90 |
| app.py | dispute_brief | function | 0.802 | 1.00 | 1.00 |
| app.py | dispute_brief | function | 0.802 | 1.00 | 1.00 |
| app.py | team_dashboard | function | 0.796 | 1.00 | 1.00 |
| app.py | team_dashboard | function | 0.796 | 1.00 | 1.00 |
| ingestion/ingest.py | _run_ingestion_rows | function | 0.786 | 1.00 | 0.88 |
| ingestion/ingest.py | _run_ingestion_rows | function | 0.786 | 1.00 | 0.88 |
| app.py | invoice_detail | function | 0.785 | 1.00 | 1.00 |
| app.py | invoice_detail | function | 0.785 | 1.00 | 1.00 |

## Coupling Hotspots (142 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| profile_ingestion.py | execute | 1.000 | 282426 | 0 | 0.222 |
| profile_ingestion.py | execute | 1.000 | 282426 | 0 | 0.222 |
| profile_ingestion.py | commit | 0.997 | 63097 | 0 | 0.213 |
| profile_ingestion.py | commit | 0.997 | 63097 | 0 | 0.213 |
| profile_ingestion.py | close | 0.994 | 28947 | 0 | 0.209 |
| profile_ingestion.py | close | 0.994 | 28947 | 0 | 0.209 |
| contract_tables.py | create_contract_tables | 0.991 | 1991 | 14649 | 0.744 |
| contract_tables.py | create_contract_tables | 0.991 | 1991 | 14649 | 0.744 |
| tests/test_lifecycle.py | test_main | 0.988 | 0 | 14362 | 0.442 |
| tests/test_lifecycle.py | test_main | 0.988 | 0 | 14362 | 0.442 |
| tests/test_validator.py | test_main | 0.984 | 0 | 13098 | 0.564 |
| tests/test_validator.py | test_main | 0.984 | 0 | 13098 | 0.564 |
| web/action_queue.py | _get_db | 0.981 | 12111 | 67 | 0.729 |
| web/action_queue.py | _get_db | 0.981 | 12111 | 67 | 0.729 |
| tests/test_carrier_profiles.py | get_db | 0.978 | 11883 | 67 | 0.390 |
| tests/test_carrier_profiles.py | get_db | 0.978 | 11883 | 67 | 0.390 |
| database.py | get_connection | 0.975 | 11076 | 201 | 0.576 |
| database.py | get_connection | 0.975 | 11076 | 201 | 0.576 |
| database.py | _create_tables | 0.972 | 2204 | 8127 | 0.737 |
| database.py | _create_tables | 0.972 | 2204 | 8127 | 0.737 |
| tests/test_forms_and_uploads.py | test_main | 0.969 | 0 | 8376 | 0.517 |
| tests/test_forms_and_uploads.py | test_main | 0.969 | 0 | 8376 | 0.517 |
| tests/conftest.py | _insert_invoice | 0.966 | 7159 | 11 | 0.422 |
| tests/conftest.py | _insert_invoice | 0.966 | 7159 | 11 | 0.422 |
| tests/test_upload_endpoints.py | test_main | 0.962 | 0 | 6834 | 0.434 |
| tests/test_upload_endpoints.py | test_main | 0.962 | 0 | 6834 | 0.434 |
| contract_tables.py | extend_existing_tables | 0.959 | 1991 | 4555 | 0.774 |
| contract_tables.py | extend_existing_tables | 0.959 | 1991 | 4555 | 0.774 |
| tests/test_activity_import.py | _seed_invoice | 0.956 | 6154 | 134 | 0.475 |
| tests/test_activity_import.py | _seed_invoice | 0.956 | 6154 | 134 | 0.475 |

## Clone Candidates (1420 pairs)
| File A | Name A | File B | Name B | Similarity |
|---|---|---|---|---|
| database.py | __init__ | tests/test_remaining_pipeline_qa.py | __init__ | 1.000 |
| database.py | __getitem__ | tests/test_remaining_pipeline_qa.py | __getitem__ | 1.000 |
| engines/backtest.py | _table_exists | web/reporting.py | _table_exists | 1.000 |
| engines/backtest.py | _table_exists | web/action_queue.py | _table_exists | 1.000 |
| tests/test_accessorial_aliases.py | _make_db | tests/test_zip_5digit.py | _make_db | 1.000 |
| tests/test_activity_import.py | db | tests/test_carrier_auto_merge.py | db | 1.000 |
| tests/test_activity_import.py | app_client | tests/test_carrier_auto_merge.py | app_client | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_analytics_phase3 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_team_member_profile 2.py | db | 1.000 |
| tests/test_auto_contract_phase2 2.py | db | tests/test_auto_contract_phase3.py | db | 1.000 |
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

## Staleness Alerts (124 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.505 |
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.505 |
| engines/action_router.py | _build_dispute_email | 1.000 | 0.647 |
| engines/action_router.py | _build_dispute_email | 1.000 | 0.647 |
| engines/action_router.py | _build_pricing_ticket | 1.000 | 0.653 |
| engines/action_router.py | _build_pricing_ticket | 1.000 | 0.653 |
| engines/action_router.py | _build_summary | 1.000 | 0.724 |
| engines/action_router.py | _build_summary | 1.000 | 0.724 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.570 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.570 |
| engines/training.py | _build_discrepancy | 1.000 | 0.452 |
| engines/training.py | _build_discrepancy | 1.000 | 0.452 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.460 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.460 |
| extraction_tracking.py | compute_prompt_version | 1.000 | 0.590 |
| extraction_tracking.py | compute_prompt_version | 1.000 | 0.590 |
| extraction_tracking.py | _compute_fields_multi_section | 1.000 | 0.698 |
| extraction_tracking.py | _compute_fields_multi_section | 1.000 | 0.698 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.472 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.472 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.473 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.473 |
| tests/conftest.py | app_client | 1.000 | 0.449 |
| tests/conftest.py | app_client | 1.000 | 0.449 |
| tests/test_base_rates_file_upload.py | test_blank_csv_download_returns_correct_headers | 1.000 | 0.255 |
| tests/test_base_rates_file_upload.py | test_blank_csv_download_returns_correct_headers | 1.000 | 0.255 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_auto_links_contract | 1.000 | 0.245 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_auto_links_contract | 1.000 | 0.245 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_rejects_mismatch | 1.000 | 0.244 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_rejects_mismatch | 1.000 | 0.244 |

## Complexity Hotspots (378 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 86 | 5 | 1 |
| app.py | invoice_detail | 1.000 | 86 | 5 | 1 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 91 | 4 | 0 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 91 | 4 | 0 |
| tests/test_contract_templates.py | test_main | 1.000 | 108 | 1 | 1 |
| tests/test_contract_templates.py | test_main | 1.000 | 108 | 1 | 1 |
| tests/test_contracts.py | test_main | 1.000 | 101 | 1 | 1 |
| tests/test_contracts.py | test_main | 1.000 | 101 | 1 | 1 |
| tests/test_disputes.py | test_main | 1.000 | 105 | 1 | 1 |
| tests/test_disputes.py | test_main | 1.000 | 105 | 1 | 1 |
| tests/test_forms_and_uploads.py | test_main | 1.000 | 128 | 4 | 1 |
| tests/test_forms_and_uploads.py | test_main | 1.000 | 128 | 4 | 1 |
| tests/test_lifecycle.py | test_main | 1.000 | 113 | 2 | 1 |
| tests/test_lifecycle.py | test_main | 1.000 | 113 | 2 | 1 |
| tests/test_upload_endpoints.py | test_main | 1.000 | 106 | 3 | 1 |
| tests/test_upload_endpoints.py | test_main | 1.000 | 106 | 3 | 1 |
| tests/test_validator.py | test_main | 1.000 | 131 | 1 | 1 |
| tests/test_validator.py | test_main | 1.000 | 131 | 1 | 1 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/rates.py | rates_grid | 1.000 | 69 | 4 | 0 |
| web/rates.py | rates_grid | 1.000 | 69 | 4 | 0 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 65 | 3 | 6 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 65 | 3 | 6 |
| engines/validator.py | gate_7_linehaul | 0.999 | 62 | 4 | 6 |
| engines/validator.py | gate_7_linehaul | 0.999 | 62 | 4 | 6 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 63 | 5 | 1 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 63 | 5 | 1 |
| tests/test_training.py | test_main | 0.999 | 63 | 1 | 1 |
| tests/test_training.py | test_main | 0.999 | 63 | 1 | 1 |

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
| CRITICAL | coverage_gap | dispute_brief (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | team_dashboard (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | team_dashboard (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | invoice_detail (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | invoice_detail (app.py) — uncovered high-volatility function | Fix |
| LOW | coupling_hotspot | execute (profile_ingestion.py) — high-coupling node (coupling_score=1.00) | Architecture check |
| LOW | coupling_hotspot | execute (profile_ingestion.py) — high-coupling node (coupling_score=1.00) | Architecture check |
| LOW | coupling_hotspot | commit (profile_ingestion.py) — high-coupling node (coupling_score=1.00) | Architecture check |
| LOW | coupling_hotspot | commit (profile_ingestion.py) — high-coupling node (coupling_score=1.00) | Architecture check |
| LOW | coupling_hotspot | close (profile_ingestion.py) — high-coupling node (coupling_score=0.99) | Architecture check |
| LOW | coupling_hotspot | close (profile_ingestion.py) — high-coupling node (coupling_score=0.99) | Architecture check |
| CRITICAL | complexity_hotspot | invoice_detail (app.py) — high cyclomatic complexity (complexity_score=1.00, cyc | Fix |
| CRITICAL | complexity_hotspot | invoice_detail (app.py) — high cyclomatic complexity (complexity_score=1.00, cyc | Fix |
| MEDIUM | complexity_hotspot | InvoiceXMLParser (ingestion/xml_parser.py) — high cyclomatic complexity (complex | Fix |
| MEDIUM | complexity_hotspot | InvoiceXMLParser (ingestion/xml_parser.py) — high cyclomatic complexity (complex | Fix |
| MEDIUM | complexity_hotspot | test_main (tests/test_contract_templates.py) — high cyclomatic complexity (compl | Fix |
| MEDIUM | complexity_hotspot | test_main (tests/test_contract_templates.py) — high cyclomatic complexity (compl | Fix |
| MEDIUM | complexity_hotspot | test_main (tests/test_contracts.py) — high cyclomatic complexity (complexity_sco | Fix |
| MEDIUM | complexity_hotspot | test_main (tests/test_contracts.py) — high cyclomatic complexity (complexity_sco | Fix |

## Planner Constraints (444 total)

### coverage_required (108)
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.87, no test coverage, volatility 0.93
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.87, no test coverage, volatility 0.93
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.86, no test coverage, volatility 0.93
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.86, no test coverage, volatility 0.93
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.86, no test coverage, volatility 0.98
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.86, no test coverage, volatility 0.98
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.85, no test coverage, volatility 0.98
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.85, no test coverage, volatility 0.98
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.84, no test coverage, volatility 0.82
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.84, no test coverage, volatility 0.82
- **[high]** `ingestion/activity_import.py::import_activity_history` — Composite score 0.83, no test coverage, volatility 0.62
- **[high]** `ingestion/activity_import.py::import_activity_history` — Composite score 0.83, no test coverage, volatility 0.62
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.83, no test coverage, volatility 0.93
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.83, no test coverage, volatility 0.93
- **[high]** `web/action_queue.py::record_response` — Composite score 0.82, no test coverage, volatility 0.82

### verify_dependents (142)
- **[high]** `profile_ingestion.py::execute` — Coupling score 1.00, 282426 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::execute` — Coupling score 1.00, 282426 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::commit` — Coupling score 1.00, 63097 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::commit` — Coupling score 1.00, 63097 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::close` — Coupling score 0.99, 28947 inbound + 0 outbound deps
- **[high]** `profile_ingestion.py::close` — Coupling score 0.99, 28947 inbound + 0 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.99, 1991 inbound + 14649 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.99, 1991 inbound + 14649 outbound deps
- **[medium]** `tests/test_lifecycle.py::test_main` — Coupling score 0.99, 0 inbound + 14362 outbound deps
- **[medium]** `tests/test_lifecycle.py::test_main` — Coupling score 0.99, 0 inbound + 14362 outbound deps
- **[medium]** `tests/test_validator.py::test_main` — Coupling score 0.98, 0 inbound + 13098 outbound deps
- **[medium]** `tests/test_validator.py::test_main` — Coupling score 0.98, 0 inbound + 13098 outbound deps
- **[high]** `web/action_queue.py::_get_db` — Coupling score 0.98, 12111 inbound + 67 outbound deps
- **[high]** `web/action_queue.py::_get_db` — Coupling score 0.98, 12111 inbound + 67 outbound deps
- **[high]** `tests/test_carrier_profiles.py::get_db` — Coupling score 0.98, 11883 inbound + 67 outbound deps

### refactor_candidate (40)
- **[medium]** `database.py::__init__ ↔ tests/test_remaining_pipeline_qa.py::__init__` — Similarity 1.00 — potential duplicate
- **[medium]** `database.py::__getitem__ ↔ tests/test_remaining_pipeline_qa.py::__getitem__` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/reporting.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `engines/backtest.py::_table_exists ↔ web/action_queue.py::_table_exists` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_accessorial_aliases.py::_make_db ↔ tests/test_zip_5digit.py::_make_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::db ↔ tests/test_carrier_auto_merge.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_activity_import.py::app_client ↔ tests/test_carrier_auto_merge.py::app_client` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_analytics_phase3 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_team_member_profile 2.py::db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_auto_contract_phase2 2.py::db ↔ tests/test_auto_contract_phase3.py::db` — Similarity 1.00 — potential duplicate

### investigation_needed (124)
- **[high]** `eia_fetcher.py::get_eia_price_for_date` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `eia_fetcher.py::get_eia_price_for_date` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_dispute_email` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_dispute_email` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_pricing_ticket` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_pricing_ticket` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_summary` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_summary` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/email_matcher.py::match_pros_to_invoices` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/email_matcher.py::match_pros_to_invoices` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/training.py::_build_discrepancy` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/training.py::_build_discrepancy` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/variance_analyzer.py::_adjust_confidence_by_history` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/variance_analyzer.py::_adjust_confidence_by_history` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `extraction_tracking.py::compute_prompt_version` — Staleness score 1.00 — dependencies updated but chunk unchanged

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
- Dependencies: 812908
- Similarity pairs: 4849
- Average health score: 0.2620
- High risk count: 510
t: 510
