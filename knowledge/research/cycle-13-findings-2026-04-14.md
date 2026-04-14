# Anvil Cycle Report — invoice-pulse — Cycle 13
**Date:** 2026-04-14

## Executive Summary
- **Total files:** 4636
- **Total chunks:** 3836
- **High risk chunks:** 739
- **Average composite score:** 0.2632
- **Total findings:** 1958

## Coverage Gaps (58 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.874 | 1.00 | 0.93 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.866 | 1.00 | 0.93 |
| web/contracts.py | contract_fuel_import_combined | function | 0.862 | 1.00 | 0.98 |
| web/contracts.py | contracts_list | function | 0.861 | 1.00 | 0.98 |
| web/action_queue.py | action_queue | function | 0.845 | 1.00 | 0.83 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.841 | 1.00 | 0.93 |
| ingestion/activity_import.py | import_activity_history | function | 0.832 | 1.00 | 0.60 |
| web/contracts.py | contract_lanes_bulk | function | 0.820 | 1.00 | 0.98 |
| web/action_queue.py | record_response | function | 0.811 | 1.00 | 0.83 |
| web/rates.py | rates_grid | function | 0.807 | 1.00 | 0.89 |
| app.py | dispute_brief | function | 0.806 | 1.00 | 1.00 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.805 | 1.00 | 0.90 |
| app.py | team_dashboard | function | 0.801 | 1.00 | 1.00 |
| app.py | invoice_detail | function | 0.793 | 1.00 | 1.00 |
| ingestion/ingest.py | _run_ingestion_rows | function | 0.792 | 1.00 | 0.88 |
| web/contracts.py | contract_edit | function | 0.790 | 1.00 | 0.98 |
| web/carrier_profiles.py | _build_carrier_cards | function | 0.787 | 1.00 | 0.93 |
| web/contract_import.py | _validate_contract_json | function | 0.786 | 1.00 | 0.73 |
| web/contracts.py | contract_fuel_brackets_bulk | function | 0.779 | 1.00 | 0.98 |
| web/carrier_profiles.py | carrier_profile_detail | function | 0.776 | 1.00 | 0.93 |
| contract_tables.py | extend_existing_tables | function | 0.774 | 1.00 | 0.95 |
| app.py | run_validation | function | 0.772 | 1.00 | 1.00 |
| web/email_triage.py | email_archiver | function | 0.772 | 1.00 | 0.86 |
| app.py | ingest_xml_paste | function | 0.769 | 1.00 | 1.00 |
| web/contracts.py | _save_contract | function | 0.768 | 1.00 | 0.98 |
| app.py | invoices_list | function | 0.768 | 1.00 | 1.00 |
| app.py | debug_export | function | 0.764 | 1.00 | 1.00 |
| web/contracts.py | contract_new | function | 0.763 | 1.00 | 0.98 |
| web/contracts.py | contract_fak_bulk | function | 0.763 | 1.00 | 0.98 |
| validate_batch.py | run_batch | function | 0.757 | 1.00 | 0.85 |

## Coupling Hotspots (44 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| contract_tables.py | create_contract_tables | 0.991 | 3187 | 26591 | 0.744 |
| database.py | _create_tables | 0.974 | 3504 | 14731 | 0.738 |
| contract_tables.py | extend_existing_tables | 0.960 | 3187 | 8431 | 0.774 |
| engines/triangulation.py | triangulate | 0.957 | 9819 | 1331 | 0.486 |
| database.py | init_db | 0.954 | 7073 | 3187 | 0.575 |
| ingestion/ingest.py | _to_float | 0.951 | 10033 | 0 | 0.643 |
| engines/validator.py | validate_invoice | 0.946 | 4941 | 4810 | 0.620 |
| app.py | _table_exists | 0.937 | 9232 | 65 | 0.559 |
| engines/validator.py | add | 0.929 | 8172 | 0 | 0.462 |
| ingestion/activity_import.py | import_activity_history | 0.923 | 5203 | 2234 | 0.832 |
| engines/validator.py | gate_9_accessorials | 0.917 | 4840 | 2299 | 0.446 |
| contract_tables.py | _safe_add_column | 0.914 | 6734 | 121 | 0.722 |
| engines/validator.py | gate_8_fuel | 0.906 | 3993 | 2200 | 0.549 |
| web/contracts.py | _build_dashboard_cards | 0.903 | 2751 | 3410 | 0.641 |
| engines/validator.py | gate_7_linehaul | 0.900 | 3597 | 2417 | 0.548 |
| engines/exit_interview.py | run_pro_exit_interviews | 0.891 | 5324 | 484 | 0.353 |
| engines/action_router.py | route_actions | 0.889 | 3937 | 1694 | 0.750 |
| ingestion/ingest.py | _insert_charge | 0.886 | 5445 | 121 | 0.616 |
| web/carrier_profiles.py | _float_or_none | 0.874 | 5302 | 0 | 0.645 |
| extraction_tracking.py | write_extraction_quality_report | 0.871 | 3146 | 1694 | 0.805 |
| web/utils.py | normalize_zip | 0.869 | 4785 | 0 | 0.609 |
| ingestion/ingest.py | enrich_invoice_xml | 0.866 | 4235 | 484 | 0.618 |
| ingestion/xml_parser.py | parse | 0.863 | 4458 | 0 | 0.493 |
| extraction_tracking.py | record_extraction_result | 0.857 | 4235 | 121 | 0.554 |
| web/data_hygiene.py | data_hygiene_page | 0.857 | 0 | 4356 | 0.524 |
| web/utils.py | flash_safe_error | 0.854 | 4327 | 0 | 0.593 |
| web/contract_import.py | _import_contract | 0.851 | 121 | 4114 | 0.711 |
| backup.py | main | 0.849 | 3609 | 605 | 0.316 |
| system_logger.py | log_event | 0.846 | 3946 | 242 | 0.586 |
| engines/confidence.py | record_evidence | 0.843 | 3630 | 484 | 0.533 |

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
| engines/backtest.py | _table_exists | web/reporting.py | _table_exists | 1.000 |

## Staleness Alerts (62 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.500 |
| engines/action_router.py | _build_dispute_email | 1.000 | 0.644 |
| engines/action_router.py | _build_pricing_ticket | 1.000 | 0.650 |
| engines/action_router.py | _build_summary | 1.000 | 0.722 |
| engines/email_matcher.py | match_pros_to_invoices | 1.000 | 0.573 |
| engines/training.py | _build_discrepancy | 1.000 | 0.455 |
| engines/variance_analyzer.py | _adjust_confidence_by_history | 1.000 | 0.466 |
| extraction_tracking.py | compute_prompt_version | 1.000 | 0.605 |
| extraction_tracking.py | _compute_fields_multi_section | 1.000 | 0.704 |
| ingestion/csv_reader.py | _map_rows | 1.000 | 0.471 |
| ingestion/csv_reader.py | _read_excel | 1.000 | 0.472 |
| tests/conftest.py | app_client | 1.000 | 0.449 |
| tests/test_base_rates_file_upload.py | test_blank_csv_download_returns_correct_headers | 1.000 | 0.258 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_auto_links_contract | 1.000 | 0.251 |
| tests/test_base_rates_file_upload.py | test_csv_file_upload_rejects_mismatch | 1.000 | 0.247 |
| tests/test_base_rates_file_upload.py | test_csv_upload_rejects_invalid_extension | 1.000 | 0.247 |
| tests/test_base_rates_file_upload.py | test_csv_upload_with_missing_columns | 1.000 | 0.247 |
| tests/test_contract_display_label.py | test_label_none_contract | 1.000 | 0.190 |
| tests/test_contract_rates_paste.py | test_invoice_detail_rates_url_targets_import_section | 1.000 | 0.338 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_standard | 1.000 | 0.253 |
| tests/test_coverage_batch1.py | test_reshape_for_apply_empty | 1.000 | 0.220 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_valid | 1.000 | 0.229 |
| tests/test_coverage_batch1.py | test_parse_charge_csv_none_safety | 1.000 | 0.220 |
| tests/test_csv_parsers.py | test_contract_setup_happy_path | 1.000 | 0.227 |
| tests/test_csv_parsers.py | test_lanes_combined_format | 1.000 | 0.224 |
| tests/test_csv_parsers.py | test_fuel_float_parsing | 1.000 | 0.224 |
| tests/test_csv_parsers.py | test_empty_csv_returns_error | 1.000 | 0.221 |
| tests/test_csv_parsers.py | test_unknown_section_type_returns_error | 1.000 | 0.219 |
| tests/test_eia_padd_regions.py | test_env | 1.000 | 0.197 |
| tests/test_email_archiver_scope.py | test_resolved_with_dispute_appears | 1.000 | 0.197 |

## Complexity Hotspots (120 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 86 | 5 | 1 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 91 | 4 | 0 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/rates.py | rates_grid | 1.000 | 69 | 4 | 0 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 65 | 3 | 6 |
| engines/validator.py | gate_7_linehaul | 0.999 | 62 | 4 | 6 |
| web/contracts.py | contract_fuel_import_combined | 0.999 | 63 | 5 | 1 |
| web/gap_dashboard.py | import_contract_setup | 0.999 | 60 | 5 | 1 |
| engines/validator.py | gate_9_accessorials | 0.998 | 56 | 6 | 8 |
| app.py | team_dashboard | 0.998 | 59 | 5 | 0 |
| ingestion/activity_import.py | import_activity_history | 0.998 | 58 | 3 | 3 |
| web/gap_dashboard.py | enrich_invoice | 0.998 | 58 | 4 | 1 |
| app.py | team_member_profile | 0.996 | 54 | 5 | 1 |
| web/action_queue.py | action_queue | 0.996 | 52 | 8 | 0 |
| web/contracts.py | contracts_list | 0.995 | 52 | 5 | 0 |
| engines/validator.py | gate_8_fuel | 0.994 | 49 | 4 | 7 |
| web/documents.py | document_extract | 0.993 | 48 | 7 | 2 |
| web/gap_dashboard.py | _import_lanes_section | 0.991 | 48 | 4 | 3 |
| web/gap_dashboard.py | _parse_generic_csv | 0.991 | 46 | 7 | 2 |
| web/carrier_profiles.py | carrier_import_fuel | 0.990 | 48 | 4 | 1 |
| engines/email_generator.py | generate_pricing_ticket | 0.990 | 45 | 6 | 5 |
| app.py | dispute_brief | 0.989 | 46 | 6 | 1 |
| app.py | debug_export | 0.987 | 45 | 6 | 1 |
| engines/validator.py | validate_invoice | 0.987 | 43 | 8 | 2 |
| engines/carrier_identity.py | detect_merge_candidates | 0.984 | 43 | 6 | 2 |
| app.py | invoices_list | 0.983 | 44 | 5 | 0 |
| web/carrier_profiles.py | carrier_import_accessorials | 0.983 | 43 | 6 | 1 |
| web/gap_dashboard.py | _import_base_rates_section | 0.981 | 43 | 3 | 4 |
| extraction_tracking.py | write_extraction_quality_report | 0.981 | 43 | 4 | 2 |
| engines/exit_interview.py | _capture_pro_exit_interview | 0.976 | 41 | 5 | 2 |

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

## Intent Gaps (15 findings)
| Severity | Signal Type | Title | Diagnostic |
|---|---|---|---|
| CRITICAL | coverage_gap | dispute_brief (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | team_dashboard (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | invoice_detail (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | run_validation (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | ingest_xml_paste (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | invoices_list (app.py) — uncovered high-volatility function | Fix |
| HIGH | coupling_hotspot | create_contract_tables (contract_tables.py) — high-coupling node (coupling_score | Architecture check |
| CRITICAL | complexity_hotspot | invoice_detail (app.py) — high cyclomatic complexity (complexity_score=1.00, cyc | Fix |
| MEDIUM | complexity_hotspot | InvoiceXMLParser (ingestion/xml_parser.py) — high cyclomatic complexity (complex | Fix |
| CRITICAL | complexity_hotspot | _validate_contract_json (web/contract_import.py) — high cyclomatic complexity (c | Fix |
| CRITICAL | complexity_hotspot | rates_grid (web/rates.py) — high cyclomatic complexity (complexity_score=1.00, c | Fix |
| HIGH | complexity_hotspot | _build_dashboard_cards (web/contracts.py) — high cyclomatic complexity (complexi | Fix |
| MEDIUM | complexity_hotspot | gate_7_linehaul (engines/validator.py) — high cyclomatic complexity (complexity_ | Fix |
| CRITICAL | complexity_hotspot | contract_fuel_import_combined (web/contracts.py) — high cyclomatic complexity (c | Fix |
| HIGH | complexity_hotspot | import_contract_setup (web/gap_dashboard.py) — high cyclomatic complexity (compl | Fix |

## Planner Constraints (234 total)

### coverage_required (58)
- **[high]** `web/carrier_profiles.py::carrier_import_accessorials` — Composite score 0.87, no test coverage, volatility 0.93
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.87, no test coverage, volatility 0.93
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.86, no test coverage, volatility 0.98
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.86, no test coverage, volatility 0.98
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.84, no test coverage, volatility 0.83
- **[high]** `web/carrier_profiles.py::carrier_import_minimums` — Composite score 0.84, no test coverage, volatility 0.93
- **[high]** `ingestion/activity_import.py::import_activity_history` — Composite score 0.83, no test coverage, volatility 0.60
- **[high]** `web/contracts.py::contract_lanes_bulk` — Composite score 0.82, no test coverage, volatility 0.98
- **[high]** `web/action_queue.py::record_response` — Composite score 0.81, no test coverage, volatility 0.83
- **[high]** `web/rates.py::rates_grid` — Composite score 0.81, no test coverage, volatility 0.89
- **[high]** `app.py::dispute_brief` — Composite score 0.81, no test coverage, volatility 1.00
- **[high]** `extraction_tracking.py::write_extraction_quality_report` — Composite score 0.81, no test coverage, volatility 0.90
- **[high]** `app.py::team_dashboard` — Composite score 0.80, no test coverage, volatility 1.00
- **[high]** `app.py::invoice_detail` — Composite score 0.79, no test coverage, volatility 1.00
- **[high]** `ingestion/ingest.py::_run_ingestion_rows` — Composite score 0.79, no test coverage, volatility 0.88

### verify_dependents (44)
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.99, 3187 inbound + 26591 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.97, 3504 inbound + 14731 outbound deps
- **[high]** `contract_tables.py::extend_existing_tables` — Coupling score 0.96, 3187 inbound + 8431 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.96, 9819 inbound + 1331 outbound deps
- **[high]** `database.py::init_db` — Coupling score 0.95, 7073 inbound + 3187 outbound deps
- **[high]** `ingestion/ingest.py::_to_float` — Coupling score 0.95, 10033 inbound + 0 outbound deps
- **[high]** `engines/validator.py::validate_invoice` — Coupling score 0.95, 4941 inbound + 4810 outbound deps
- **[high]** `app.py::_table_exists` — Coupling score 0.94, 9232 inbound + 65 outbound deps
- **[high]** `engines/validator.py::add` — Coupling score 0.93, 8172 inbound + 0 outbound deps
- **[high]** `ingestion/activity_import.py::import_activity_history` — Coupling score 0.92, 5203 inbound + 2234 outbound deps
- **[high]** `engines/validator.py::gate_9_accessorials` — Coupling score 0.92, 4840 inbound + 2299 outbound deps
- **[high]** `contract_tables.py::_safe_add_column` — Coupling score 0.91, 6734 inbound + 121 outbound deps
- **[high]** `engines/validator.py::gate_8_fuel` — Coupling score 0.91, 3993 inbound + 2200 outbound deps
- **[high]** `web/contracts.py::_build_dashboard_cards` — Coupling score 0.90, 2751 inbound + 3410 outbound deps
- **[high]** `engines/validator.py::gate_7_linehaul` — Coupling score 0.90, 3597 inbound + 2417 outbound deps

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
- Dependencies: 1479820
- Similarity pairs: 6809
- Average health score: 0.2632
- High risk count: 739
