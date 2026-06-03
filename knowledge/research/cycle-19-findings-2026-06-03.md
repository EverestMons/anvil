# Anvil Cycle Report — invoice-pulse — Cycle 19
**Date:** 2026-06-03

## Executive Summary
- **Total files:** 5211
- **Total chunks:** 4175
- **High risk chunks:** 1012
- **Average composite score:** 0.2569
- **Total findings:** 2114

## Coverage Gaps (44 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/contracts.py | contract_fuel_import_combined | function | 0.882 | 1.00 | 0.92 |
| web/contracts.py | contracts_list | function | 0.875 | 1.00 | 0.92 |
| web/contracts.py | contract_lanes_bulk | function | 0.829 | 1.00 | 0.92 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.816 | 1.00 | 0.00 |
| ingestion/activity_import.py | import_activity_history | function | 0.814 | 1.00 | 0.00 |
| profile_ingestion.py | run_profiled_ingestion | function | 0.813 | 1.00 | 0.00 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.807 | 1.00 | 0.00 |
| app.py | invoice_detail | function | 0.798 | 1.00 | 0.79 |
| web/contracts.py | contract_new | function | 0.789 | 1.00 | 0.92 |
| web/contracts.py | contract_edit | function | 0.781 | 1.00 | 0.92 |
| web/contracts.py | _save_contract | function | 0.781 | 1.00 | 0.92 |
| web/contract_import.py | _validate_contract_json | function | 0.781 | 1.00 | 0.00 |
| web/action_queue.py | action_queue | function | 0.780 | 1.00 | 0.17 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.778 | 1.00 | 0.00 |
| web/rates.py | rates_grid | function | 0.775 | 1.00 | 0.00 |
| app.py | dispute_brief | function | 0.767 | 1.00 | 0.79 |
| engines/lane_matcher.py | match_lane | function | 0.767 | 1.00 | 0.29 |
| web/training.py | training_batch_apply | function | 0.766 | 1.00 | 0.00 |
| web/contracts.py | contract_fuel_brackets_bulk | function | 0.764 | 1.00 | 0.92 |
| app.py | team_dashboard | function | 0.763 | 1.00 | 0.79 |
| web/contracts.py | contract_fuel_save | function | 0.762 | 1.00 | 0.92 |
| web/documents.py | document_extract | function | 0.761 | 1.00 | 0.00 |
| web/contracts.py | contract_fak_bulk | function | 0.756 | 1.00 | 0.92 |
| web/carrier_profiles.py | carrier_profile_detail | function | 0.743 | 1.00 | 0.00 |
| web/contract_import.py | import_contract_json | function | 0.741 | 1.00 | 0.00 |
| engines/triangulation.py | get_attestation_requests | function | 0.737 | 1.00 | 0.00 |
| app.py | run_validation | function | 0.736 | 1.00 | 0.79 |
| web/carrier_profiles.py | carrier_profiles_list | function | 0.733 | 1.00 | 0.00 |
| app.py | invoices_list | function | 0.732 | 1.00 | 0.79 |
| web/contracts.py | contract_merge | function | 0.732 | 1.00 | 0.92 |

## Untested Complexity (top-20 by coverage × complexity)
| File | Name | Coverage | Complexity | Cov×Comp | Composite |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 1.000 | 1.000 | 0.798 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 1.000 | 1.000 | 0.616 |
| web/contract_import.py | _validate_contract_json | 1.000 | 1.000 | 1.000 | 0.781 |
| web/rates.py | rates_grid | 1.000 | 1.000 | 1.000 | 0.775 |
| web/contracts.py | contract_fuel_import_combined | 1.000 | 0.999 | 0.999 | 0.882 |
| web/gap_dashboard.py | import_contract_setup | 1.000 | 0.999 | 0.999 | 0.604 |
| app.py | team_dashboard | 1.000 | 0.998 | 0.998 | 0.763 |
| ingestion/activity_import.py | import_activity_history | 1.000 | 0.998 | 0.998 | 0.814 |
| web/gap_dashboard.py | enrich_invoice | 1.000 | 0.998 | 0.998 | 0.641 |
| tests/test_xml_validation_enrichment.py | TestScenario1_EnrichmentSucceeds | 1.000 | 0.996 | 0.996 | 0.599 |
| web/gap_dashboard.py | _parse_generic_csv | 1.000 | 0.996 | 0.996 | 0.574 |
| web/contracts.py | contracts_list | 1.000 | 0.995 | 0.995 | 0.875 |
| web/gap_dashboard.py | _import_fuel_section | 1.000 | 0.994 | 0.994 | 0.601 |
| web/documents.py | document_extract | 1.000 | 0.993 | 0.993 | 0.761 |
| web/gap_dashboard.py | _import_lanes_section | 1.000 | 0.991 | 0.991 | 0.647 |
| engines/email_generator.py | generate_pricing_ticket | 1.000 | 0.990 | 0.990 | 0.698 |
| app.py | dispute_brief | 1.000 | 0.989 | 0.989 | 0.767 |
| web/carrier_profiles.py | carrier_import_fuel | 1.000 | 0.989 | 0.989 | 0.816 |
| app.py | debug_export | 1.000 | 0.987 | 0.987 | 0.718 |
| tests/test_copilot_contract_import.py | TestImport | 1.000 | 0.984 | 0.984 | 0.595 |

## Coupling Hotspots (51 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| contract_tables.py | create_contract_tables | 0.992 | 5281 | 51260 | 0.635 |
| database.py | _create_tables | 0.974 | 5754 | 28357 | 0.701 |
| contract_tables.py | extend_existing_tables | 0.961 | 5281 | 16649 | 0.666 |
| engines/triangulation.py | triangulate | 0.959 | 18708 | 2552 | 0.576 |
| database.py | init_db | 0.956 | 13555 | 6555 | 0.539 |
| engines/validator.py | validate_invoice | 0.954 | 10494 | 9244 | 0.494 |
| ingestion/ingest.py | _to_float | 0.951 | 19342 | 0 | 0.567 |
| app.py | _table_exists | 0.943 | 17464 | 95 | 0.518 |
| engines/validator.py | add | 0.936 | 15906 | 0 | 0.387 |
| ingestion/activity_import.py | import_activity_history | 0.931 | 9976 | 4313 | 0.814 |
| engines/validator.py | gate_9_accessorials | 0.923 | 9280 | 4408 | 0.371 |
| contract_tables.py | _safe_add_column | 0.920 | 13120 | 232 | 0.615 |
| web/contracts.py | _build_dashboard_cards | 0.918 | 6171 | 6575 | 0.631 |
| engines/validator.py | gate_8_fuel | 0.913 | 7664 | 4273 | 0.369 |
| engines/validator.py | gate_7_linehaul | 0.910 | 7056 | 4790 | 0.474 |
| engines/exit_interview.py | run_pro_exit_interviews | 0.905 | 10208 | 928 | 0.293 |
| engines/action_router.py | route_actions | 0.900 | 7533 | 3248 | 0.697 |
| ingestion/ingest.py | _insert_charge | 0.897 | 10440 | 232 | 0.542 |
| web/carrier_profiles.py | _float_or_none | 0.889 | 10159 | 0 | 0.561 |
| extraction_tracking.py | write_extraction_quality_report | 0.887 | 6032 | 3248 | 0.727 |
| ingestion/ingest.py | enrich_invoice_xml | 0.884 | 8120 | 928 | 0.545 |
| web/utils.py | normalize_zip | 0.882 | 8880 | 0 | 0.561 |
| ingestion/xml_parser.py | parse | 0.879 | 8553 | 0 | 0.552 |
| extraction_tracking.py | record_extraction_result | 0.874 | 8120 | 232 | 0.476 |
| web/data_hygiene.py | data_hygiene_page | 0.874 | 0 | 8352 | 0.552 |
| backup.py | main | 0.872 | 7035 | 1160 | 0.354 |
| web/contract_import.py | _import_contract | 0.869 | 232 | 7888 | 0.668 |
| web/utils.py | flash_safe_error | 0.866 | 8083 | 0 | 0.545 |
| engines/email_matcher.py | extract_pro_numbers | 0.864 | 6748 | 1160 | 0.635 |
| engines/confidence.py | record_evidence | 0.861 | 6960 | 928 | 0.548 |

## Clone Candidates (537 pairs)
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

## Staleness Alerts (73 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| app.py | before_request | 1.000 | 0.544 |
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.494 |
| engines/action_router.py | _build_dispute_email | 1.000 | 0.597 |
| engines/action_router.py | _build_pricing_ticket | 1.000 | 0.603 |
| engines/action_router.py | _build_summary | 1.000 | 0.674 |
| engines/training.py | _build_discrepancy | 1.000 | 0.526 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.565 |
| extraction_tracking.py | compute_prompt_version | 1.000 | 0.548 |
| extraction_tracking.py | _compute_fields_multi_section | 1.000 | 0.638 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.601 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.601 |
| tests/conftest.py | app_client | 1.000 | 0.496 |
| tests/conftest.py | _xdist_db_isolation | 1.000 | 0.468 |
| tests/test_all_routes_modes.py | routes_app | 1.000 | 0.468 |
| tests/test_base_rates_file_upload.py | test_blank_csv_download_returns_correct_headers | 1.000 | 0.191 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_auto_links_contract | 1.000 | 0.188 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_rejects_mismatch | 1.000 | 0.180 |
| tests/test_base_rates_file_upload.py | test_csv_upload_rejects_invalid_extension | 1.000 | 0.180 |
| tests/test_base_rates_file_upload.py | test_csv_upload_with_missing_columns | 1.000 | 0.180 |
| tests/test_contract_display_label.py | test_label_none_contract | 1.000 | 0.182 |
| tests/test_contract_rates_paste.py | test_invoice_detail_rates_url_targets_import_section | 1.000 | 0.182 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_standard | 1.000 | 0.214 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_empty | 1.000 | 0.181 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_valid | 1.000 | 0.191 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_none_safety | 1.000 | 0.181 |
| tests/test_csv_parsers.py | test_contract_setup_happy_path | 1.000 | 0.188 |
| tests/test_csv_parsers.py | test_lanes_combined_format | 1.000 | 0.184 |
| tests/test_csv_parsers.py | test_fuel_float_parsing | 1.000 | 0.184 |
| tests/test_csv_parsers.py | test_empty_csv_returns_error | 1.000 | 0.182 |
| tests/test_csv_parsers.py | test_unknown_section_type_returns_error | 1.000 | 0.179 |

## Complexity Hotspots (124 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 86 | 5 | 1 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 91 | 4 | 0 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/rates.py | rates_grid | 1.000 | 69 | 4 | 0 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 65 | 3 | 6 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 65 | 5 | 1 |
| engines/validator.py | gate_7_linehaul | 0.999 | 62 | 4 | 6 |
| web/gap_dashboard.py | import_contract_setup | 0.999 | 60 | 5 | 1 |
| engines/validator.py | gate_9_accessorials | 0.998 | 56 | 6 | 8 |
| app.py | team_dashboard | 0.998 | 59 | 5 | 0 |
| ingestion/activity_import.py | import_activity_history | 0.998 | 58 | 3 | 3 |
| web/gap_dashboard.py | enrich_invoice | 0.998 | 58 | 4 | 1 |
| app.py | team_member_profile | 0.996 | 54 | 5 | 1 |
| engines/validator.py | gate_8_fuel | 0.996 | 52 | 4 | 7 |
| web/gap_dashboard.py | _parse_generic_csv | 0.996 | 51 | 7 | 2 |
| web/contracts.py | contracts_list | 0.995 | 52 | 5 | 0 |
| web/gap_dashboard.py | _import_fuel_section | 0.994 | 50 | 5 | 3 |
| web/documents.py | document_extract | 0.993 | 48 | 7 | 2 |
| web/gap_dashboard.py | _import_lanes_section | 0.991 | 48 | 4 | 3 |
| engines/email_generator.py | generate_pricing_ticket | 0.990 | 45 | 6 | 5 |
| app.py | ingest | 0.989 | 46 | 7 | 0 |
| app.py | dispute_brief | 0.989 | 46 | 6 | 1 |
| web/carrier_profiles.py | carrier_import_fuel | 0.989 | 47 | 4 | 1 |
| app.py | debug_export | 0.987 | 45 | 6 | 1 |
| engines/validator.py | validate_invoice | 0.987 | 43 | 8 | 2 |
| engines/carrier_identity.py | detect_merge_candidates | 0.984 | 43 | 6 | 2 |
| app.py | invoices_list | 0.983 | 44 | 5 | 0 |
| web/carrier_profiles.py | carrier_import_accessorials | 0.983 | 43 | 6 | 1 |
| web/gap_dashboard.py | _import_base_rates_section | 0.981 | 43 | 3 | 4 |
| extraction_tracking.py | write_extraction_quality_report | 0.981 | 43 | 4 | 2 |

## Co-Change Patterns (200 pairs)
| File A | File B | Co-changes | Jaccard |
|---|---|---|---|
| PROJECT_STATUS.md | knowledge/research/agent-prompt-feedback.md | 160 | 0.304 |
| knowledge/research/copilot-extraction-quality.md | knowledge/research/validation-quality-summary.md | 33 | 0.868 |
| contract_tables.py | database.py | 18 | 0.234 |
| copilot_prompts.py | web/gap_dashboard.py | 18 | 0.143 |
| knowledge/research/activity-notes-patterns.md | knowledge/research/validation-quality-summary.md | 17 | 0.472 |
| app.py | knowledge/research/agent-prompt-feedback.md | 17 | 0.034 |
| app.py | web/templates/invoice_detail.html | 17 | 0.119 |
| knowledge/research/activity-notes-patterns.md | knowledge/research/copilot-extraction-quality.md | 16 | 0.421 |
| web/templates/contract_fuel.html | web/templates/contract_lanes.html | 15 | 0.455 |
| web/contracts.py | web/gap_dashboard.py | 15 | 0.092 |
| contract_tables.py | knowledge/research/agent-prompt-feedback.md | 14 | 0.032 |
| web/templates/contract_accessorials.html | web/templates/contract_fuel.html | 14 | 0.438 |
| copilot_prompts.py | web/contracts.py | 13 | 0.115 |
| engines/validator.py | web/contracts.py | 13 | 0.108 |
| web/contracts.py | web/templates/contract_dashboard.html | 13 | 0.153 |
| web/templates/contract_accessorials.html | web/templates/contract_lanes.html | 13 | 0.565 |
| web/templates/contract_accessorials.html | web/templates/contract_fak.html | 12 | 0.667 |
| web/templates/contract_billto.html | web/templates/contract_fak.html | 12 | 0.857 |
| app.py | web/templates/dashboard.html | 12 | 0.105 |
| app.py | database.py | 11 | 0.075 |
| knowledge/research/agent-prompt-feedback.md | web/contracts.py | 11 | 0.023 |
| web/contracts.py | web/templates/contract_fuel.html | 11 | 0.112 |
| web/templates/carrier_fuel.html | web/templates/carrier_minimums.html | 11 | 0.733 |
| web/templates/contract_accessorials.html | web/templates/contract_billto.html | 11 | 0.579 |
| web/templates/contract_areas.html | web/templates/contract_fak.html | 11 | 0.786 |
| app.py | ingestion/ingest.py | 10 | 0.086 |
| app.py | engines/validator.py | 10 | 0.067 |
| app.py | validate_batch.py | 10 | 0.083 |
| app.py | web/contracts.py | 10 | 0.057 |
| web/carrier_profiles.py | web/templates/carrier_profile_detail.html | 10 | 0.233 |

## Research Recommendations (1070 deviations across 4 roles)

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

### route_handler (59 deviations)
- **[medium]** `web/action_queue.py::action_queue` -- single_responsibility: Function has 262 lines (threshold: 80)
- **[medium]** `web/action_queue.py::confirm_carrier` -- single_responsibility: Function has 125 lines (threshold: 80)
- **[medium]** `web/action_queue.py::record_response` -- single_responsibility: Function has 165 lines (threshold: 80)
- **[medium]** `web/action_queue.py::_auto_route_after_response` -- single_responsibility: Function has 118 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profiles_list` -- single_responsibility: Function has 142 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::_build_carrier_cards` -- single_responsibility: Function has 246 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profile_detail` -- single_responsibility: Function has 200 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_accessorials` -- single_responsibility: Function has 202 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_fuel` -- single_responsibility: Function has 265 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_minimums` -- single_responsibility: Function has 192 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_validate_contract_json` -- single_responsibility: Function has 226 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_import_contract` -- single_responsibility: Function has 310 lines (threshold: 80)
- **[medium]** `web/contract_import.py::import_contract_json` -- single_responsibility: Function has 199 lines (threshold: 80)
- **[medium]** `web/contract_template_routes.py::template_upload` -- single_responsibility: Function has 112 lines (threshold: 80)
- **[medium]** `web/contract_template_routes.py::template_apply` -- single_responsibility: Function has 87 lines (threshold: 80)

### utility (1000 deviations)
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

## Intent Gaps (15 findings)
| Severity | Signal Type | Title | Diagnostic |
|---|---|---|---|
| MEDIUM | coverage_gap | get_invoice_prompt (copilot_prompts.py) — uncovered high-volatility function | Fix |
| LOW | coverage_gap | get_prompt_for_queue (copilot_prompts.py) — uncovered high-volatility function | Fix |
| LOW | coverage_gap | __init__ (copilot_prompts.py) — uncovered high-volatility method | Fix |
| LOW | coverage_gap | list_prompts (copilot_prompts.py) — uncovered high-volatility function | Fix |
| LOW | coverage_gap | PromptDef (copilot_prompts.py) — uncovered high-volatility class | Fix |
| LOW | coverage_gap | get_all_sections (copilot_prompts.py) — uncovered high-volatility function | Fix |
| HIGH | coupling_hotspot | create_contract_tables (contract_tables.py) — high-coupling node (coupling_score | Architecture check |
| CRITICAL | complexity_hotspot | invoice_detail (app.py) — high cyclomatic complexity (complexity_score=1.00, cyc | Fix |
| HIGH | complexity_hotspot | InvoiceXMLParser (ingestion/xml_parser.py) — high cyclomatic complexity (complex | Fix |
| CRITICAL | complexity_hotspot | _validate_contract_json (web/contract_import.py) — high cyclomatic complexity (c | Fix |
| CRITICAL | complexity_hotspot | rates_grid (web/rates.py) — high cyclomatic complexity (complexity_score=1.00, c | Fix |
| HIGH | complexity_hotspot | _build_dashboard_cards (web/contracts.py) — high cyclomatic complexity (complexi | Fix |
| CRITICAL | complexity_hotspot | contract_fuel_import_combined (web/contracts.py) — high cyclomatic complexity (c | Fix |
| MEDIUM | complexity_hotspot | gate_7_linehaul (engines/validator.py) — high cyclomatic complexity (complexity_ | Fix |
| HIGH | complexity_hotspot | import_contract_setup (web/gap_dashboard.py) — high cyclomatic complexity (compl | Fix |

## Planner Constraints (238 total)

### coverage_required (44)
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.88, no test coverage, volatility 0.92
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.88, no test coverage, volatility 0.92
- **[high]** `web/contracts.py::contract_lanes_bulk` — Composite score 0.83, no test coverage, volatility 0.92
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.82, no test coverage, volatility 0.00
- **[high]** `ingestion/activity_import.py::import_activity_history` — Composite score 0.81, no test coverage, volatility 0.00
- **[high]** `profile_ingestion.py::run_profiled_ingestion` — Composite score 0.81, no test coverage, volatility 0.00
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.81, no test coverage, volatility 0.00
- **[high]** `app.py::invoice_detail` — Composite score 0.80, no test coverage, volatility 0.79
- **[high]** `web/contracts.py::contract_new` — Composite score 0.79, no test coverage, volatility 0.92
- **[high]** `web/contracts.py::contract_edit` — Composite score 0.78, no test coverage, volatility 0.92
- **[high]** `web/contracts.py::_save_contract` — Composite score 0.78, no test coverage, volatility 0.92
- **[high]** `web/contract_import.py::_validate_contract_json` — Composite score 0.78, no test coverage, volatility 0.00
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.78, no test coverage, volatility 0.17
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.78, no test coverage, volatility 0.00
- **[high]** `web/rates.py::rates_grid` — Composite score 0.78, no test coverage, volatility 0.00

### verify_dependents (51)
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.99, 5281 inbound + 51260 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.97, 5754 inbound + 28357 outbound deps
- **[high]** `contract_tables.py::extend_existing_tables` — Coupling score 0.96, 5281 inbound + 16649 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.96, 18708 inbound + 2552 outbound deps
- **[high]** `database.py::init_db` — Coupling score 0.96, 13555 inbound + 6555 outbound deps
- **[high]** `engines/validator.py::validate_invoice` — Coupling score 0.95, 10494 inbound + 9244 outbound deps
- **[high]** `ingestion/ingest.py::_to_float` — Coupling score 0.95, 19342 inbound + 0 outbound deps
- **[high]** `app.py::_table_exists` — Coupling score 0.94, 17464 inbound + 95 outbound deps
- **[high]** `engines/validator.py::add` — Coupling score 0.94, 15906 inbound + 0 outbound deps
- **[high]** `ingestion/activity_import.py::import_activity_history` — Coupling score 0.93, 9976 inbound + 4313 outbound deps
- **[high]** `engines/validator.py::gate_9_accessorials` — Coupling score 0.92, 9280 inbound + 4408 outbound deps
- **[high]** `contract_tables.py::_safe_add_column` — Coupling score 0.92, 13120 inbound + 232 outbound deps
- **[high]** `web/contracts.py::_build_dashboard_cards` — Coupling score 0.92, 6171 inbound + 6575 outbound deps
- **[high]** `engines/validator.py::gate_8_fuel` — Coupling score 0.91, 7664 inbound + 4273 outbound deps
- **[high]** `engines/validator.py::gate_7_linehaul` — Coupling score 0.91, 7056 inbound + 4790 outbound deps

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

### investigation_needed (73)
- **[high]** `app.py::before_request` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `eia_fetcher.py::get_eia_price_for_date` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_dispute_email` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_pricing_ticket` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/action_router.py::_build_summary` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/training.py::_build_discrepancy` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `engines/variance_analyzer.py::_adjust_confidence_by_history` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `extraction_tracking.py::compute_prompt_version` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `extraction_tracking.py::_compute_fields_multi_section` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `ingestion/csv_reader.py::_map_rows` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `ingestion/csv_reader.py::_read_excel` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/conftest.py::app_client` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/conftest.py::_xdist_db_isolation` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_all_routes_modes.py::routes_app` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_base_rates_file_upload.py::test_blank_csv_download_returns_correct_headers` — Staleness score 1.00 — dependencies updated but chunk unchanged

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
- **[medium]** `web/action_queue.py::action_queue` — route_handler deviates from single_responsibility: Function has 262 lines (threshold: 80)
- **[medium]** `web/action_queue.py::confirm_carrier` — route_handler deviates from single_responsibility: Function has 125 lines (threshold: 80)
- **[medium]** `web/action_queue.py::record_response` — route_handler deviates from single_responsibility: Function has 165 lines (threshold: 80)
- **[medium]** `web/action_queue.py::_auto_route_after_response` — route_handler deviates from single_responsibility: Function has 118 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profiles_list` — route_handler deviates from single_responsibility: Function has 142 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::_build_carrier_cards` — route_handler deviates from single_responsibility: Function has 246 lines (threshold: 80)

## Specialist Update Data
- Functions: 1418
- Classes: 504
- Methods: 68
- Test cases: 2185
- Dependencies: 2877792
- Similarity pairs: 9816
- Average health score: 0.2569
- High risk count: 1012
