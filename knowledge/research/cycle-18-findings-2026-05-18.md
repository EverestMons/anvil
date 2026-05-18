# Anvil Cycle Report — invoice-pulse — Cycle 18
**Date:** 2026-05-18

## Executive Summary
- **Total files:** 4960
- **Total chunks:** 3956
- **High risk chunks:** 966
- **Average composite score:** 0.2580
- **Total findings:** 1976

## Coverage Gaps (32 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/action_queue.py | action_queue | function | 0.850 | 1.00 | 1.00 |
| ingestion/activity_import.py | import_activity_history | function | 0.813 | 1.00 | 0.00 |
| profile_ingestion.py | run_profiled_ingestion | function | 0.812 | 1.00 | 0.00 |
| web/contracts.py | contracts_list | function | 0.810 | 1.00 | 0.60 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.806 | 1.00 | 0.00 |
| web/contracts.py | contract_fuel_import_combined | function | 0.803 | 1.00 | 0.60 |
| web/action_queue.py | record_response | function | 0.799 | 1.00 | 1.00 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.798 | 1.00 | 0.00 |
| web/contract_import.py | _validate_contract_json | function | 0.779 | 1.00 | 0.00 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.776 | 1.00 | 0.00 |
| engines/lane_matcher.py | match_lane | function | 0.766 | 1.00 | 0.20 |
| web/training.py | training_batch_apply | function | 0.765 | 1.00 | 0.00 |
| web/contracts.py | contract_lanes_bulk | function | 0.764 | 1.00 | 0.60 |
| web/documents.py | document_extract | function | 0.760 | 1.00 | 0.00 |
| web/rates.py | rates_grid | function | 0.749 | 1.00 | 0.00 |
| app.py | invoice_detail | function | 0.737 | 1.00 | 0.10 |
| web/contracts.py | contract_edit | function | 0.737 | 1.00 | 0.60 |
| web/email_triage.py | email_archiver | function | 0.737 | 1.00 | 0.00 |
| engines/triangulation.py | get_attestation_requests | function | 0.737 | 1.00 | 0.00 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.726 | 1.00 | 0.00 |
| web/contracts.py | contract_new | function | 0.725 | 1.00 | 0.60 |
| web/contract_import.py | import_contract_json | function | 0.723 | 1.00 | 0.00 |
| web/contracts.py | contract_fuel_brackets_bulk | function | 0.719 | 1.00 | 0.60 |
| ingestion/ingest.py | _run_ingestion_rows | function | 0.719 | 1.00 | 0.00 |
| web/carrier_profiles.py | carrier_profile_detail | function | 0.717 | 1.00 | 0.00 |
| web/contracts.py | contract_merge | function | 0.716 | 1.00 | 0.60 |
| web/contracts.py | contract_fak_bulk | function | 0.716 | 1.00 | 0.60 |
| app.py | dispute_brief | function | 0.708 | 1.00 | 0.10 |
| engines/exit_interview.py | _capture_pro_exit_interview | function | 0.704 | 1.00 | 0.00 |
| app.py | team_dashboard | function | 0.704 | 1.00 | 0.10 |

## Untested Complexity (top-20 by coverage × complexity)
| File | Name | Coverage | Complexity | Cov×Comp | Composite |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 1.000 | 1.000 | 0.737 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 1.000 | 1.000 | 0.611 |
| web/contract_import.py | _validate_contract_json | 1.000 | 1.000 | 1.000 | 0.779 |
| web/rates.py | rates_grid | 1.000 | 1.000 | 1.000 | 0.749 |
| web/contracts.py | contract_fuel_import_combined | 1.000 | 0.999 | 0.999 | 0.803 |
| web/gap_dashboard.py | import_contract_setup | 1.000 | 0.999 | 0.999 | 0.638 |
| app.py | team_dashboard | 1.000 | 0.998 | 0.998 | 0.704 |
| ingestion/activity_import.py | import_activity_history | 1.000 | 0.998 | 0.998 | 0.813 |
| web/gap_dashboard.py | enrich_invoice | 1.000 | 0.998 | 0.998 | 0.675 |
| tests/test_xml_validation_enrichment.py | TestScenario1_EnrichmentSucceeds | 1.000 | 0.996 | 0.996 | 0.599 |
| web/gap_dashboard.py | _parse_generic_csv | 1.000 | 0.996 | 0.996 | 0.601 |
| web/contracts.py | contracts_list | 1.000 | 0.995 | 0.995 | 0.810 |
| web/gap_dashboard.py | _import_fuel_section | 1.000 | 0.993 | 0.993 | 0.631 |
| web/documents.py | document_extract | 1.000 | 0.993 | 0.993 | 0.760 |
| web/gap_dashboard.py | _import_lanes_section | 1.000 | 0.991 | 0.991 | 0.681 |
| engines/email_generator.py | generate_pricing_ticket | 1.000 | 0.990 | 0.990 | 0.697 |
| app.py | dispute_brief | 1.000 | 0.989 | 0.989 | 0.708 |
| web/carrier_profiles.py | carrier_import_fuel | 1.000 | 0.989 | 0.989 | 0.798 |
| app.py | debug_export | 1.000 | 0.987 | 0.987 | 0.659 |
| tests/test_copilot_contract_import.py | TestImport | 1.000 | 0.984 | 0.984 | 0.595 |

## Coupling Hotspots (47 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| contract_tables.py | create_contract_tables | 0.992 | 4907 | 46584 | 0.610 |
| database.py | _create_tables | 0.973 | 5354 | 25776 | 0.650 |
| contract_tables.py | extend_existing_tables | 0.960 | 4907 | 15076 | 0.641 |
| engines/triangulation.py | triangulate | 0.957 | 17029 | 2321 | 0.576 |
| database.py | init_db | 0.954 | 12318 | 5902 | 0.288 |
| engines/validator.py | validate_invoice | 0.952 | 9411 | 8403 | 0.515 |
| ingestion/ingest.py | _to_float | 0.949 | 17578 | 0 | 0.567 |
| app.py | _table_exists | 0.941 | 15912 | 90 | 0.460 |
| engines/validator.py | add | 0.933 | 14437 | 0 | 0.399 |
| ingestion/activity_import.py | import_activity_history | 0.927 | 9073 | 3919 | 0.813 |
| engines/validator.py | gate_9_accessorials | 0.919 | 8440 | 4009 | 0.383 |
| contract_tables.py | _safe_add_column | 0.916 | 11904 | 211 | 0.589 |
| web/contracts.py | _build_dashboard_cards | 0.911 | 5492 | 5975 | 0.567 |
| engines/validator.py | gate_8_fuel | 0.908 | 6963 | 3874 | 0.486 |
| engines/validator.py | gate_7_linehaul | 0.906 | 6393 | 4329 | 0.486 |
| engines/exit_interview.py | run_pro_exit_interviews | 0.900 | 9284 | 844 | 0.292 |
| engines/action_router.py | route_actions | 0.895 | 6842 | 2954 | 0.697 |
| ingestion/ingest.py | _insert_charge | 0.892 | 9495 | 211 | 0.541 |
| web/carrier_profiles.py | _float_or_none | 0.884 | 9232 | 0 | 0.560 |
| extraction_tracking.py | write_extraction_quality_report | 0.881 | 5486 | 2954 | 0.726 |
| ingestion/ingest.py | enrich_invoice_xml | 0.879 | 7385 | 844 | 0.544 |
| web/utils.py | normalize_zip | 0.876 | 8115 | 0 | 0.560 |
| ingestion/xml_parser.py | parse | 0.873 | 7778 | 0 | 0.551 |
| extraction_tracking.py | record_extraction_result | 0.868 | 7385 | 211 | 0.475 |
| web/data_hygiene.py | data_hygiene_page | 0.868 | 0 | 7596 | 0.552 |
| backup.py | main | 0.865 | 6380 | 1055 | 0.330 |
| web/contract_import.py | _import_contract | 0.863 | 211 | 7174 | 0.667 |
| web/utils.py | flash_safe_error | 0.860 | 7379 | 0 | 0.544 |
| engines/confidence.py | record_evidence | 0.857 | 6330 | 844 | 0.547 |
| engines/email_matcher.py | extract_pro_numbers | 0.857 | 6119 | 1055 | 0.572 |

## Clone Candidates (500 pairs)
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

## Staleness Alerts (60 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.489 |
| engines/action_router.py | _build_dispute_email | 1.000 | 0.592 |
| engines/action_router.py | _build_pricing_ticket | 1.000 | 0.598 |
| engines/action_router.py | _build_summary | 1.000 | 0.669 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.702 |
| engines/training.py | _build_discrepancy | 1.000 | 0.523 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.562 |
| extraction_tracking.py | compute_prompt_version | 1.000 | 0.542 |
| extraction_tracking.py | _compute_fields_multi_section | 1.000 | 0.633 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.597 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.598 |
| tests/test_base_rates_file_upload.py | test_blank_csv_download_returns_correct_headers | 1.000 | 0.185 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_auto_links_contract | 1.000 | 0.181 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_rejects_mismatch | 1.000 | 0.174 |
| tests/test_base_rates_file_upload.py | test_csv_upload_rejects_invalid_extension | 1.000 | 0.174 |
| tests/test_base_rates_file_upload.py | test_csv_upload_with_missing_columns | 1.000 | 0.174 |
| tests/test_contract_display_label.py | test_label_none_contract | 1.000 | 0.176 |
| tests/test_contract_rates_paste.py | test_invoice_detail_rates_url_targets_import_section | 1.000 | 0.175 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_standard | 1.000 | 0.207 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_empty | 1.000 | 0.175 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_valid | 1.000 | 0.184 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_none_safety | 1.000 | 0.175 |
| tests/test_csv_parsers.py | test_contract_setup_happy_path | 1.000 | 0.182 |
| tests/test_csv_parsers.py | test_lanes_combined_format | 1.000 | 0.179 |
| tests/test_csv_parsers.py | test_fuel_float_parsing | 1.000 | 0.179 |
| tests/test_csv_parsers.py | test_empty_csv_returns_error | 1.000 | 0.176 |
| tests/test_csv_parsers.py | test_unknown_section_type_returns_error | 1.000 | 0.173 |
| tests/test_eia_padd_regions.py | test_env | 1.000 | 0.175 |
| tests/test_email_archiver_scope.py | test_resolved_with_dispute_appears | 1.000 | 0.194 |
| tests/test_email_archiver_scope.py | test_resolved_without_dispute_excluded | 1.000 | 0.191 |

## Complexity Hotspots (121 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 86 | 5 | 1 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 91 | 4 | 0 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/rates.py | rates_grid | 1.000 | 69 | 4 | 0 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 65 | 3 | 6 |
| engines/validator.py | gate_7_linehaul | 0.999 | 62 | 4 | 6 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 62 | 5 | 1 |
| web/gap_dashboard.py | import_contract_setup | 0.999 | 60 | 5 | 1 |
| engines/validator.py | gate_9_accessorials | 0.998 | 56 | 6 | 8 |
| app.py | team_dashboard | 0.998 | 59 | 5 | 0 |
| ingestion/activity_import.py | import_activity_history | 0.998 | 58 | 3 | 3 |
| web/gap_dashboard.py | enrich_invoice | 0.998 | 58 | 4 | 1 |
| app.py | team_member_profile | 0.996 | 54 | 5 | 1 |
| web/gap_dashboard.py | _parse_generic_csv | 0.996 | 51 | 7 | 2 |
| web/contracts.py | contracts_list | 0.995 | 52 | 5 | 0 |
| engines/validator.py | gate_8_fuel | 0.994 | 49 | 4 | 7 |
| web/gap_dashboard.py | _import_fuel_section | 0.993 | 49 | 5 | 3 |
| web/documents.py | document_extract | 0.993 | 48 | 7 | 2 |
| web/gap_dashboard.py | _import_lanes_section | 0.991 | 48 | 4 | 3 |
| engines/email_generator.py | generate_pricing_ticket | 0.990 | 45 | 6 | 5 |
| app.py | dispute_brief | 0.989 | 46 | 6 | 1 |
| web/carrier_profiles.py | carrier_import_fuel | 0.989 | 47 | 4 | 1 |
| app.py | debug_export | 0.987 | 45 | 6 | 1 |
| engines/validator.py | validate_invoice | 0.987 | 43 | 8 | 2 |
| engines/carrier_identity.py | detect_merge_candidates | 0.984 | 43 | 6 | 2 |
| app.py | invoices_list | 0.983 | 44 | 5 | 0 |
| web/carrier_profiles.py | carrier_import_accessorials | 0.983 | 43 | 6 | 1 |
| web/gap_dashboard.py | _import_base_rates_section | 0.981 | 43 | 3 | 4 |
| extraction_tracking.py | write_extraction_quality_report | 0.981 | 43 | 4 | 2 |
| engines/exit_interview.py | _capture_pro_exit_interview | 0.976 | 41 | 5 | 2 |

## Co-Change Patterns (194 pairs)
| File A | File B | Co-changes | Jaccard |
|---|---|---|---|
| PROJECT_STATUS.md | knowledge/research/agent-prompt-feedback.md | 146 | 0.324 |
| knowledge/research/copilot-extraction-quality.md | knowledge/research/validation-quality-summary.md | 33 | 0.868 |
| knowledge/research/activity-notes-patterns.md | knowledge/research/validation-quality-summary.md | 17 | 0.472 |
| app.py | web/templates/invoice_detail.html | 17 | 0.122 |
| contract_tables.py | database.py | 17 | 0.236 |
| copilot_prompts.py | web/gap_dashboard.py | 17 | 0.142 |
| knowledge/research/activity-notes-patterns.md | knowledge/research/copilot-extraction-quality.md | 16 | 0.421 |
| app.py | knowledge/research/agent-prompt-feedback.md | 16 | 0.036 |
| web/templates/contract_fuel.html | web/templates/contract_lanes.html | 15 | 0.500 |
| web/contracts.py | web/gap_dashboard.py | 15 | 0.096 |
| web/templates/contract_accessorials.html | web/templates/contract_fuel.html | 14 | 0.483 |
| engines/validator.py | web/contracts.py | 13 | 0.114 |
| web/contracts.py | web/templates/contract_dashboard.html | 13 | 0.163 |
| web/templates/contract_accessorials.html | web/templates/contract_lanes.html | 13 | 0.565 |
| contract_tables.py | knowledge/research/agent-prompt-feedback.md | 12 | 0.031 |
| copilot_prompts.py | web/contracts.py | 12 | 0.115 |
| web/templates/contract_accessorials.html | web/templates/contract_fak.html | 12 | 0.667 |
| web/templates/contract_billto.html | web/templates/contract_fak.html | 12 | 0.857 |
| app.py | web/templates/dashboard.html | 12 | 0.109 |
| web/templates/carrier_fuel.html | web/templates/carrier_minimums.html | 11 | 0.733 |
| web/templates/contract_accessorials.html | web/templates/contract_billto.html | 11 | 0.579 |
| web/templates/contract_areas.html | web/templates/contract_fak.html | 11 | 0.786 |
| app.py | ingestion/ingest.py | 10 | 0.089 |
| app.py | engines/validator.py | 10 | 0.069 |
| app.py | web/contracts.py | 10 | 0.059 |
| web/carrier_profiles.py | web/templates/carrier_profile_detail.html | 10 | 0.233 |
| web/contracts.py | web/templates/contract_fuel.html | 10 | 0.110 |
| web/templates/carrier_accessorials.html | web/templates/carrier_fuel.html | 10 | 0.625 |
| web/templates/carrier_accessorials.html | web/templates/carrier_minimums.html | 10 | 0.833 |
| web/templates/carrier_accessorials.html | web/templates/carrier_remote_access.html | 10 | 0.909 |

## Research Recommendations (1008 deviations across 4 roles)

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

### utility (940 deviations)
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

## Intent Gaps (14 findings)
| Severity | Signal Type | Title | Diagnostic |
|---|---|---|---|
| CRITICAL | coverage_gap | action_queue (web/action_queue.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | record_response (web/action_queue.py) — uncovered high-volatility function | Fix |
| HIGH | coverage_gap | _auto_route_after_response (web/action_queue.py) — uncovered high-volatility fun | Fix |
| HIGH | coverage_gap | confirm_carrier (web/action_queue.py) — uncovered high-volatility function | Fix |
| HIGH | coverage_gap | _get_catchup_data (web/action_queue.py) — uncovered high-volatility function | Fix |
| HIGH | coupling_hotspot | create_contract_tables (contract_tables.py) — high-coupling node (coupling_score | Architecture check |
| HIGH | complexity_hotspot | invoice_detail (app.py) — high cyclomatic complexity (complexity_score=1.00, cyc | Fix |
| HIGH | complexity_hotspot | InvoiceXMLParser (ingestion/xml_parser.py) — high cyclomatic complexity (complex | Fix |
| CRITICAL | complexity_hotspot | _validate_contract_json (web/contract_import.py) — high cyclomatic complexity (c | Fix |
| HIGH | complexity_hotspot | rates_grid (web/rates.py) — high cyclomatic complexity (complexity_score=1.00, c | Fix |
| MEDIUM | complexity_hotspot | _build_dashboard_cards (web/contracts.py) — high cyclomatic complexity (complexi | Fix |
| MEDIUM | complexity_hotspot | gate_7_linehaul (engines/validator.py) — high cyclomatic complexity (complexity_ | Fix |
| CRITICAL | complexity_hotspot | contract_fuel_import_combined (web/contracts.py) — high cyclomatic complexity (c | Fix |
| HIGH | complexity_hotspot | import_contract_setup (web/gap_dashboard.py) — high cyclomatic complexity (compl | Fix |

## Planner Constraints (209 total)

### coverage_required (32)
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.85, no test coverage, volatility 1.00
- **[high]** `ingestion/activity_import.py::import_activity_history` — Composite score 0.81, no test coverage, volatility 0.00
- **[high]** `profile_ingestion.py::run_profiled_ingestion` — Composite score 0.81, no test coverage, volatility 0.00
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.81, no test coverage, volatility 0.60
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.81, no test coverage, volatility 0.00
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.80, no test coverage, volatility 0.60
- **[high]** `web/action_queue.py::record_response` — Composite score 0.80, no test coverage, volatility 1.00
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.80, no test coverage, volatility 0.00
- **[high]** `web/contract_import.py::_validate_contract_json` — Composite score 0.78, no test coverage, volatility 0.00
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.78, no test coverage, volatility 0.00
- **[high]** `engines/lane_matcher.py::match_lane` — Composite score 0.77, no test coverage, volatility 0.20
- **[high]** `web/training.py::training_batch_apply` — Composite score 0.77, no test coverage, volatility 0.00
- **[high]** `web/contracts.py::contract_lanes_bulk` — Composite score 0.76, no test coverage, volatility 0.60
- **[high]** `web/documents.py::document_extract` — Composite score 0.76, no test coverage, volatility 0.00
- **[high]** `web/rates.py::rates_grid` — Composite score 0.75, no test coverage, volatility 0.00

### verify_dependents (47)
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.99, 4907 inbound + 46584 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.97, 5354 inbound + 25776 outbound deps
- **[high]** `contract_tables.py::extend_existing_tables` — Coupling score 0.96, 4907 inbound + 15076 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.96, 17029 inbound + 2321 outbound deps
- **[high]** `database.py::init_db` — Coupling score 0.95, 12318 inbound + 5902 outbound deps
- **[high]** `engines/validator.py::validate_invoice` — Coupling score 0.95, 9411 inbound + 8403 outbound deps
- **[high]** `ingestion/ingest.py::_to_float` — Coupling score 0.95, 17578 inbound + 0 outbound deps
- **[high]** `app.py::_table_exists` — Coupling score 0.94, 15912 inbound + 90 outbound deps
- **[high]** `engines/validator.py::add` — Coupling score 0.93, 14437 inbound + 0 outbound deps
- **[high]** `ingestion/activity_import.py::import_activity_history` — Coupling score 0.93, 9073 inbound + 3919 outbound deps
- **[high]** `engines/validator.py::gate_9_accessorials` — Coupling score 0.92, 8440 inbound + 4009 outbound deps
- **[high]** `contract_tables.py::_safe_add_column` — Coupling score 0.92, 11904 inbound + 211 outbound deps
- **[high]** `web/contracts.py::_build_dashboard_cards` — Coupling score 0.91, 5492 inbound + 5975 outbound deps
- **[high]** `engines/validator.py::gate_8_fuel` — Coupling score 0.91, 6963 inbound + 3874 outbound deps
- **[high]** `engines/validator.py::gate_7_linehaul` — Coupling score 0.91, 6393 inbound + 4329 outbound deps

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

### investigation_needed (60)
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
- **[high]** `tests/test_base_rates_file_upload.py::test_blank_csv_download_returns_correct_headers` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_base_rates_file_upload.py::test_csv_file_upload_auto_links_contract` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_base_rates_file_upload.py::test_csv_file_upload_rejects_mismatch` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `tests/test_base_rates_file_upload.py::test_csv_upload_rejects_invalid_extension` — Staleness score 1.00 — dependencies updated but chunk unchanged

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
- Functions: 1382
- Classes: 450
- Methods: 68
- Test cases: 2056
- Dependencies: 2610709
- Similarity pairs: 9279
- Average health score: 0.2580
- High risk count: 966
