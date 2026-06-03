# Anvil Cycle Report — invoice-pulse — Cycle 20
**Date:** 2026-06-03

## Executive Summary
- **Total files:** 5213
- **Total chunks:** 4175
- **High risk chunks:** 1047
- **Average composite score:** 0.2558
- **Total findings:** 2057

## Coverage Gaps (34 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/contracts.py | contract_fuel_import_combined | function | 0.878 | 1.00 | 0.92 |
| web/contracts.py | contracts_list | function | 0.869 | 1.00 | 0.92 |
| web/contracts.py | contract_lanes_bulk | function | 0.822 | 1.00 | 0.92 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.814 | 1.00 | 0.00 |
| ingestion/activity_import.py | import_activity_history | function | 0.813 | 1.00 | 0.00 |
| profile_ingestion.py | run_profiled_ingestion | function | 0.810 | 1.00 | 0.00 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.802 | 1.00 | 0.00 |
| app.py | invoice_detail | function | 0.793 | 1.00 | 0.79 |
| web/contracts.py | contract_new | function | 0.781 | 1.00 | 0.92 |
| web/action_queue.py | action_queue | function | 0.776 | 1.00 | 0.17 |
| web/contracts.py | _save_contract | function | 0.776 | 1.00 | 0.92 |
| web/contracts.py | contract_edit | function | 0.775 | 1.00 | 0.92 |
| web/contract_import.py | _validate_contract_json | function | 0.774 | 1.00 | 0.00 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.772 | 1.00 | 0.00 |
| app.py | dispute_brief | function | 0.762 | 1.00 | 0.79 |
| engines/lane_matcher.py | match_lane | function | 0.761 | 1.00 | 0.29 |
| app.py | team_dashboard | function | 0.757 | 1.00 | 0.79 |
| web/contracts.py | contract_fuel_brackets_bulk | function | 0.757 | 1.00 | 0.92 |
| web/documents.py | document_extract | function | 0.756 | 1.00 | 0.00 |
| web/contracts.py | contract_fuel_save | function | 0.755 | 1.00 | 0.92 |
| web/contracts.py | contract_fak_bulk | function | 0.748 | 1.00 | 0.92 |
| web/carrier_profiles.py | carrier_profile_detail | function | 0.738 | 1.00 | 0.00 |
| engines/triangulation.py | get_attestation_requests | function | 0.735 | 1.00 | 0.00 |
| web/contract_import.py | import_contract_json | function | 0.734 | 1.00 | 0.00 |
| app.py | run_validation | function | 0.729 | 1.00 | 0.79 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.725 | 1.00 | 0.00 |
| web/carrier_profiles.py | carrier_profiles_list | function | 0.724 | 1.00 | 0.00 |
| web/contracts.py | contract_merge | function | 0.724 | 1.00 | 0.92 |
| app.py | ingest_xml_paste | function | 0.724 | 1.00 | 0.79 |
| app.py | invoices_list | function | 0.723 | 1.00 | 0.79 |

## Untested Complexity (top-20 by coverage × complexity)
| File | Name | Coverage | Complexity | Cov×Comp | Composite |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 1.000 | 1.000 | 0.793 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 1.000 | 1.000 | 0.608 |
| web/contract_import.py | _validate_contract_json | 1.000 | 1.000 | 1.000 | 0.774 |
| web/contracts.py | contract_fuel_import_combined | 1.000 | 0.999 | 0.999 | 0.878 |
| app.py | team_dashboard | 1.000 | 0.998 | 0.998 | 0.757 |
| ingestion/activity_import.py | import_activity_history | 1.000 | 0.998 | 0.998 | 0.813 |
| web/gap_dashboard.py | enrich_invoice | 1.000 | 0.998 | 0.998 | 0.634 |
| tests/test_xml_validation_enrichment.py | TestScenario1_EnrichmentSucceeds | 1.000 | 0.996 | 0.996 | 0.599 |
| web/gap_dashboard.py | _parse_generic_csv | 1.000 | 0.996 | 0.996 | 0.573 |
| web/contracts.py | contracts_list | 1.000 | 0.995 | 0.995 | 0.869 |
| web/gap_dashboard.py | _import_fuel_section | 1.000 | 0.994 | 0.994 | 0.593 |
| web/documents.py | document_extract | 1.000 | 0.993 | 0.993 | 0.756 |
| web/gap_dashboard.py | _import_lanes_section | 1.000 | 0.991 | 0.991 | 0.641 |
| engines/email_generator.py | generate_pricing_ticket | 1.000 | 0.990 | 0.990 | 0.695 |
| app.py | dispute_brief | 1.000 | 0.989 | 0.989 | 0.762 |
| web/carrier_profiles.py | carrier_import_fuel | 1.000 | 0.989 | 0.989 | 0.814 |
| tests/test_copilot_contract_import.py | TestImport | 1.000 | 0.984 | 0.984 | 0.595 |
| tests/test_validate_batch.py | TestRunBatch | 1.000 | 0.984 | 0.984 | 0.595 |
| engines/carrier_identity.py | detect_merge_candidates | 1.000 | 0.984 | 0.984 | 0.691 |
| app.py | invoices_list | 1.000 | 0.983 | 0.983 | 0.723 |

## Coupling Hotspots (44 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| contract_tables.py | create_contract_tables | 0.991 | 5665 | 56162 | 0.635 |
| database.py | _create_tables | 0.971 | 6164 | 31062 | 0.700 |
| contract_tables.py | extend_existing_tables | 0.956 | 5665 | 18306 | 0.665 |
| engines/triangulation.py | triangulate | 0.953 | 20466 | 2794 | 0.575 |
| database.py | init_db | 0.950 | 14864 | 7248 | 0.537 |
| engines/validator.py | validate_invoice | 0.948 | 11640 | 10126 | 0.494 |
| ingestion/ingest.py | _to_float | 0.945 | 21191 | 0 | 0.566 |
| engines/validator.py | add | 0.930 | 17447 | 0 | 0.386 |
| ingestion/activity_import.py | import_activity_history | 0.924 | 10922 | 4726 | 0.813 |
| engines/validator.py | gate_9_accessorials | 0.915 | 10160 | 4826 | 0.370 |
| contract_tables.py | _safe_add_column | 0.912 | 14398 | 254 | 0.613 |
| web/contracts.py | _build_dashboard_cards | 0.910 | 6894 | 7204 | 0.630 |
| engines/validator.py | gate_8_fuel | 0.904 | 8406 | 4694 | 0.368 |
| engines/validator.py | gate_7_linehaul | 0.901 | 7754 | 5278 | 0.472 |
| engines/exit_interview.py | run_pro_exit_interviews | 0.895 | 11176 | 1016 | 0.291 |
| engines/action_router.py | route_actions | 0.889 | 8270 | 3556 | 0.696 |
| ingestion/ingest.py | _insert_charge | 0.886 | 11430 | 254 | 0.540 |
| web/carrier_profiles.py | _float_or_none | 0.878 | 11134 | 0 | 0.559 |
| extraction_tracking.py | write_extraction_quality_report | 0.875 | 6604 | 3556 | 0.725 |
| ingestion/ingest.py | enrich_invoice_xml | 0.872 | 8890 | 1016 | 0.543 |
| web/utils.py | normalize_zip | 0.869 | 9678 | 0 | 0.559 |
| ingestion/xml_parser.py | parse | 0.866 | 9365 | 0 | 0.550 |
| extraction_tracking.py | record_extraction_result | 0.860 | 8890 | 254 | 0.474 |
| web/data_hygiene.py | data_hygiene_page | 0.860 | 0 | 9144 | 0.550 |
| backup.py | main | 0.857 | 7724 | 1270 | 0.352 |
| web/contract_import.py | _import_contract | 0.854 | 254 | 8636 | 0.666 |
| web/utils.py | flash_safe_error | 0.851 | 8818 | 0 | 0.543 |
| engines/email_matcher.py | extract_pro_numbers | 0.848 | 7426 | 1270 | 0.633 |
| engines/confidence.py | record_evidence | 0.846 | 7620 | 1016 | 0.544 |
| system_logger.py | log_event | 0.843 | 7978 | 508 | 0.531 |

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
| engines/backtest.py | _table_exists | web/reporting.py | _table_exists | 1.000 |

## Staleness Alerts (70 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| app.py | before_request | 1.000 | 0.540 |
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.489 |
| engines/action_router.py | _build_dispute_email | 1.000 | 0.592 |
| engines/action_router.py | _build_pricing_ticket | 1.000 | 0.598 |
| engines/action_router.py | _build_summary | 1.000 | 0.670 |
| engines/training.py | _build_discrepancy | 1.000 | 0.519 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.555 |
| extraction_tracking.py | compute_prompt_version | 1.000 | 0.540 |
| extraction_tracking.py | _compute_fields_multi_section | 1.000 | 0.635 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.594 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.595 |
| tests/conftest.py | app_client | 1.000 | 0.493 |
| tests/conftest.py | _xdist_db_isolation | 1.000 | 0.468 |
| tests/test_all_routes_modes.py | routes_app | 1.000 | 0.468 |
| tests/test_base_rates_file_upload.py | test_blank_csv_download_returns_correct_headers | 1.000 | 0.190 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_auto_links_contract | 1.000 | 0.185 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_rejects_mismatch | 1.000 | 0.179 |
| tests/test_base_rates_file_upload.py | test_csv_upload_rejects_invalid_extension | 1.000 | 0.179 |
| tests/test_base_rates_file_upload.py | test_csv_upload_with_missing_columns | 1.000 | 0.179 |
| tests/test_contract_display_label.py | test_label_none_contract | 1.000 | 0.178 |
| tests/test_contract_rates_paste.py | test_invoice_detail_rates_url_targets_import_section | 1.000 | 0.181 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_standard | 1.000 | 0.213 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_empty | 1.000 | 0.180 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_valid | 1.000 | 0.190 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_none_safety | 1.000 | 0.180 |
| tests/test_csv_parsers.py | test_contract_setup_happy_path | 1.000 | 0.187 |
| tests/test_csv_parsers.py | test_lanes_combined_format | 1.000 | 0.184 |
| tests/test_csv_parsers.py | test_fuel_float_parsing | 1.000 | 0.184 |
| tests/test_csv_parsers.py | test_empty_csv_returns_error | 1.000 | 0.181 |
| tests/test_csv_parsers.py | test_unknown_section_type_returns_error | 1.000 | 0.178 |

## Complexity Hotspots (87 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 86 | 5 | 1 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 91 | 4 | 0 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 65 | 3 | 6 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 65 | 5 | 1 |
| engines/validator.py | gate_7_linehaul | 0.999 | 62 | 4 | 6 |
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
| engines/validator.py | validate_invoice | 0.987 | 43 | 8 | 2 |
| engines/carrier_identity.py | detect_merge_candidates | 0.984 | 43 | 6 | 2 |
| app.py | invoices_list | 0.983 | 44 | 5 | 0 |
| web/carrier_profiles.py | carrier_import_accessorials | 0.983 | 43 | 6 | 1 |
| web/gap_dashboard.py | _import_base_rates_section | 0.981 | 43 | 3 | 4 |
| extraction_tracking.py | write_extraction_quality_report | 0.981 | 43 | 4 | 2 |
| engines/exit_interview.py | _capture_pro_exit_interview | 0.976 | 41 | 5 | 2 |
| engines/email_generator.py | _build_rate_comparison | 0.953 | 37 | 3 | 3 |
| extraction_tracking.py | generate_followup_prompt | 0.951 | 36 | 5 | 2 |

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
| LOW | coverage_gap | __init__ (copilot_prompts.py) — uncovered high-volatility method | Fix |
| LOW | coverage_gap | get_prompt_for_queue (copilot_prompts.py) — uncovered high-volatility function | Fix |
| LOW | coverage_gap | list_prompts (copilot_prompts.py) — uncovered high-volatility function | Fix |
| LOW | coverage_gap | PromptDef (copilot_prompts.py) — uncovered high-volatility class | Fix |
| LOW | coverage_gap | get_all_sections (copilot_prompts.py) — uncovered high-volatility function | Fix |
| HIGH | coupling_hotspot | create_contract_tables (contract_tables.py) — high-coupling node (coupling_score | Architecture check |
| CRITICAL | complexity_hotspot | invoice_detail (app.py) — high cyclomatic complexity (complexity_score=1.00, cyc | Fix |
| HIGH | complexity_hotspot | InvoiceXMLParser (ingestion/xml_parser.py) — high cyclomatic complexity (complex | Fix |
| CRITICAL | complexity_hotspot | _validate_contract_json (web/contract_import.py) — high cyclomatic complexity (c | Fix |
| HIGH | complexity_hotspot | _build_dashboard_cards (web/contracts.py) — high cyclomatic complexity (complexi | Fix |
| CRITICAL | complexity_hotspot | contract_fuel_import_combined (web/contracts.py) — high cyclomatic complexity (c | Fix |
| MEDIUM | complexity_hotspot | gate_7_linehaul (engines/validator.py) — high cyclomatic complexity (complexity_ | Fix |
| LOW | complexity_hotspot | gate_9_accessorials (engines/validator.py) — high cyclomatic complexity (complex | Fix |
| CRITICAL | complexity_hotspot | team_dashboard (app.py) — high cyclomatic complexity (complexity_score=1.00, cyc | Fix |

## Planner Constraints (218 total)

### coverage_required (34)
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.88, no test coverage, volatility 0.92
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.87, no test coverage, volatility 0.92
- **[high]** `web/contracts.py::contract_lanes_bulk` — Composite score 0.82, no test coverage, volatility 0.92
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.81, no test coverage, volatility 0.00
- **[high]** `ingestion/activity_import.py::import_activity_history` — Composite score 0.81, no test coverage, volatility 0.00
- **[high]** `profile_ingestion.py::run_profiled_ingestion` — Composite score 0.81, no test coverage, volatility 0.00
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.80, no test coverage, volatility 0.00
- **[high]** `app.py::invoice_detail` — Composite score 0.79, no test coverage, volatility 0.79
- **[high]** `web/contracts.py::contract_new` — Composite score 0.78, no test coverage, volatility 0.92
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.78, no test coverage, volatility 0.17
- **[high]** `web/contracts.py::_save_contract` — Composite score 0.78, no test coverage, volatility 0.92
- **[high]** `web/contracts.py::contract_edit` — Composite score 0.78, no test coverage, volatility 0.92
- **[high]** `web/contract_import.py::_validate_contract_json` — Composite score 0.77, no test coverage, volatility 0.00
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.77, no test coverage, volatility 0.00
- **[high]** `app.py::dispute_brief` — Composite score 0.76, no test coverage, volatility 0.79

### verify_dependents (44)
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.99, 5665 inbound + 56162 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.97, 6164 inbound + 31062 outbound deps
- **[high]** `contract_tables.py::extend_existing_tables` — Coupling score 0.96, 5665 inbound + 18306 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.95, 20466 inbound + 2794 outbound deps
- **[high]** `database.py::init_db` — Coupling score 0.95, 14864 inbound + 7248 outbound deps
- **[high]** `engines/validator.py::validate_invoice` — Coupling score 0.95, 11640 inbound + 10126 outbound deps
- **[high]** `ingestion/ingest.py::_to_float` — Coupling score 0.94, 21191 inbound + 0 outbound deps
- **[high]** `engines/validator.py::add` — Coupling score 0.93, 17447 inbound + 0 outbound deps
- **[high]** `ingestion/activity_import.py::import_activity_history` — Coupling score 0.92, 10922 inbound + 4726 outbound deps
- **[high]** `engines/validator.py::gate_9_accessorials` — Coupling score 0.92, 10160 inbound + 4826 outbound deps
- **[high]** `contract_tables.py::_safe_add_column` — Coupling score 0.91, 14398 inbound + 254 outbound deps
- **[high]** `web/contracts.py::_build_dashboard_cards` — Coupling score 0.91, 6894 inbound + 7204 outbound deps
- **[high]** `engines/validator.py::gate_8_fuel` — Coupling score 0.90, 8406 inbound + 4694 outbound deps
- **[high]** `engines/validator.py::gate_7_linehaul` — Coupling score 0.90, 7754 inbound + 5278 outbound deps
- **[high]** `engines/exit_interview.py::run_pro_exit_interviews` — Coupling score 0.90, 11176 inbound + 1016 outbound deps

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

### investigation_needed (70)
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
- Dependencies: 3158992
- Similarity pairs: 10353
- Average health score: 0.2558
- High risk count: 1047
