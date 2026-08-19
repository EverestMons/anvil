# Anvil Cycle Report — invoice-pulse — Cycle 21
**Date:** 2026-08-19

## Executive Summary
- **Total files:** 295
- **Total chunks:** 5166
- **High risk chunks:** 1019
- **Average composite score:** 0.2604
- **Total findings:** 3283

## Coverage Gaps (76 findings)
| File | Name | Type | Composite | Coverage | Volatility |
|---|---|---|---|---|---|
| web/contracts.py | contract_fuel_import_combined | function | 0.880 | 1.00 | 0.94 |
| web/contracts.py | contracts_list | function | 0.867 | 1.00 | 0.94 |
| app.py | team_dashboard | function | 0.861 | 1.00 | 0.97 |
| app.py | ingest_xml_paste | function | 0.854 | 1.00 | 0.97 |
| app.py | dispute_brief | function | 0.852 | 1.00 | 0.97 |
| web/contracts.py | contract_lanes_bulk | function | 0.841 | 1.00 | 0.94 |
| app.py | invoice_detail | function | 0.840 | 1.00 | 0.97 |
| web/carrier_profiles.py | carrier_import_fuel | function | 0.840 | 1.00 | 0.17 |
| web/contract_import.py | _validate_contract_json | function | 0.836 | 1.00 | 0.00 |
| app.py | _invoice_list_query_parts | function | 0.835 | 1.00 | 0.97 |
| extraction_tracking.py | write_extraction_quality_report | function | 0.833 | 1.00 | 0.17 |
| engines/action_router.py | dismiss_filled_gap_actions | function | 0.830 | 1.00 | 0.00 |
| engines/triangulation.py | get_attestation_requests | function | 0.827 | 1.00 | 0.00 |
| web/action_queue.py | action_queue | function | 0.824 | 1.00 | 0.00 |
| web/documents.py | document_extract | function | 0.824 | 1.00 | 0.00 |
| web/carrier_profiles.py | carrier_import_accessorials | function | 0.819 | 1.00 | 0.17 |
| web/carrier_profiles.py | carrier_import_minimums | function | 0.807 | 1.00 | 0.17 |
| web/carrier_profiles.py | _build_carrier_cards | function | 0.803 | 1.00 | 0.17 |
| app.py | run_validation | function | 0.800 | 1.00 | 0.97 |
| web/contracts.py | _save_contract | function | 0.796 | 1.00 | 0.94 |
| engines/pattern_learner.py | discover_fuel_patterns | function | 0.794 | 1.00 | 0.00 |
| integrity.py | deep_consistency_check | function | 0.794 | 1.00 | 0.00 |
| web/contract_import.py | import_contract_json | function | 0.794 | 1.00 | 0.00 |
| web/carrier_profiles.py | carrier_profile_detail | function | 0.792 | 1.00 | 0.17 |
| web/reporting.py | _get_dispute_lifecycle | function | 0.790 | 1.00 | 0.17 |
| web/contracts.py | contract_new | function | 0.789 | 1.00 | 0.94 |
| web/contracts.py | contract_fuel_brackets_bulk | function | 0.788 | 1.00 | 0.94 |
| web/contract_import.py | _import_contract | function | 0.786 | 1.00 | 0.00 |
| ingestion/ingest.py | _run_ingestion_rows | function | 0.784 | 1.00 | 0.77 |
| engines/lane_matcher.py | match_lane | function | 0.779 | 1.00 | 0.14 |

## Untested Complexity (top-20 by coverage × complexity)
| File | Name | Coverage | Complexity | Cov×Comp | Composite |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 1.000 | 1.000 | 0.840 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 1.000 | 1.000 | 0.620 |
| migrate_fuel_ceilings_floor_only_20260719.py | run_migration | 1.000 | 1.000 | 1.000 | 0.689 |
| web/contract_import.py | _validate_contract_json | 1.000 | 1.000 | 1.000 | 0.836 |
| web/contracts.py | contract_fuel_import_combined | 1.000 | 1.000 | 1.000 | 0.880 |
| web/contracts.py | contracts_list | 1.000 | 0.999 | 0.999 | 0.867 |
| web/gap_dashboard.py | enrich_invoice | 1.000 | 0.998 | 0.998 | 0.642 |
| repair_fuel_sentinel_20260716.py | run_repair | 1.000 | 0.998 | 0.998 | 0.686 |
| web/documents.py | document_extract | 1.000 | 0.997 | 0.997 | 0.824 |
| web/gap_dashboard.py | _import_fuel_section | 1.000 | 0.997 | 0.997 | 0.600 |
| ingestion/activity_import.py | import_activity_history | 1.000 | 0.996 | 0.996 | 0.779 |
| tests/test_xml_validation_enrichment.py | TestScenario1_EnrichmentSucceeds | 1.000 | 0.996 | 0.996 | 0.599 |
| web/gap_dashboard.py | _parse_generic_csv | 1.000 | 0.996 | 0.996 | 0.578 |
| app.py | team_dashboard | 1.000 | 0.995 | 0.995 | 0.861 |
| web/carrier_profiles.py | carrier_import_fuel | 1.000 | 0.992 | 0.992 | 0.840 |
| web/gap_dashboard.py | _import_lanes_section | 1.000 | 0.991 | 0.991 | 0.650 |
| engines/email_generator.py | generate_pricing_ticket | 1.000 | 0.990 | 0.990 | 0.705 |
| app.py | dispute_brief | 1.000 | 0.989 | 0.989 | 0.852 |
| tests/test_copilot_contract_import.py | TestImport | 1.000 | 0.984 | 0.984 | 0.595 |
| tests/test_validate_batch.py | TestRunBatch | 1.000 | 0.984 | 0.984 | 0.595 |

## Coupling Hotspots (73 findings)
| File | Name | Coupling | Inbound | Outbound | Composite |
|---|---|---|---|---|---|
| dedup_xml_data.py | execute | 0.995 | 98592 | 19 | 0.365 |
| contract_tables.py | create_contract_tables | 0.993 | 6387 | 67020 | 0.481 |
| database.py | _create_tables | 0.981 | 6935 | 37047 | 0.627 |
| contract_tables.py | extend_existing_tables | 0.972 | 6387 | 22051 | 0.538 |
| engines/triangulation.py | triangulate | 0.970 | 24219 | 3333 | 0.707 |
| database.py | init_db | 0.968 | 17690 | 8846 | 0.566 |
| ingestion/ingest.py | _to_float | 0.967 | 25072 | 0 | 0.625 |
| engines/validator.py | validate_invoice | 0.965 | 12798 | 12095 | 0.504 |
| engines/validator.py | add | 0.956 | 20592 | 0 | 0.327 |
| ingestion/activity_import.py | import_activity_history | 0.951 | 12954 | 5595 | 0.779 |
| engines/validator.py | gate_9_accessorials | 0.946 | 12042 | 5758 | 0.437 |
| contract_tables.py | _safe_add_column | 0.944 | 17268 | 303 | 0.596 |
| web/contracts.py | _build_dashboard_cards | 0.940 | 7262 | 8549 | 0.639 |
| engines/validator.py | gate_8_fuel | 0.939 | 10025 | 5647 | 0.460 |
| engines/validator.py | gate_7_linehaul | 0.937 | 9135 | 6390 | 0.435 |
| engines/exit_interview.py | run_pro_exit_interviews | 0.933 | 13215 | 1208 | 0.377 |
| engines/action_router.py | route_actions | 0.932 | 9887 | 4214 | 0.740 |
| ingestion/ingest.py | _insert_charge | 0.930 | 13557 | 301 | 0.678 |
| web/carrier_profiles.py | _float_or_none | 0.925 | 13228 | 0 | 0.566 |
| extraction_tracking.py | write_extraction_quality_report | 0.923 | 7802 | 4242 | 0.833 |
| ingestion/ingest.py | enrich_invoice_xml | 0.921 | 10545 | 1204 | 0.607 |
| web/utils.py | normalize_zip | 0.919 | 11373 | 0 | 0.567 |
| ingestion/xml_parser.py | parse | 0.917 | 11080 | 0 | 0.233 |
| web/data_hygiene.py | data_hygiene_page | 0.914 | 0 | 10831 | 0.592 |
| extraction_tracking.py | record_extraction_result | 0.912 | 10511 | 303 | 0.632 |
| backup.py | main | 0.910 | 9086 | 1515 | 0.323 |
| web/contract_import.py | _import_contract | 0.909 | 303 | 10238 | 0.786 |
| web/utils.py | flash_safe_error | 0.907 | 10370 | 0 | 0.551 |
| engines/confidence.py | record_evidence | 0.905 | 9050 | 1212 | 0.756 |
| engines/variance_analyzer.py | analyze_invoice_variance | 0.903 | 7877 | 2120 | 0.584 |

## Clone Candidates (730 pairs)
| File A | Name A | File B | Name B | Similarity |
|---|---|---|---|---|
| database.py | __init__ | tests/test_remaining_pipeline_qa.py | __init__ | 1.000 |
| database.py | __getitem__ | tests/test_remaining_pipeline_qa.py | __getitem__ | 1.000 |
| tests/test_accessorial_aliases.py | _make_db | tests/test_zip_5digit.py | _make_db | 1.000 |
| tests/test_action_queue_aggregation.py | _insert_action | tests/test_aggregated_queue_customer_display.py | _insert_action | 1.000 |
| tests/test_aggregated_queue_customer_display.py | TestCustomerDisplayMultiCustomer | tests/test_aggregated_queue_customer_display.py | test_three_customers_joined_by_middle_dot | 1.000 |
| tests/test_backtest_removal_validation.py | _get_app_db | tests/test_template_apply_updated_at.py | _get_app_db | 1.000 |
| tests/test_backtest_removal_validation.py | _get_app_db | tests/test_validations_stale_bump.py | _get_app_db | 1.000 |
| tests/test_backtest_removal_validation.py | _get_app_db | tests/test_base_rates_file_upload.py | _get_app_db | 1.000 |
| tests/test_backtest_removal_validation.py | _seed | tests/test_base_rates_file_upload.py | _seed | 1.000 |
| tests/test_backtest_removal_validation.py | _query_one | tests/test_base_rates_file_upload.py | _query_one | 1.000 |
| tests/test_backtest_removal_validation.py | _get_contract_updated_at | tests/test_validations_stale_bump.py | _get_contract_updated_at | 1.000 |
| tests/test_base_rates_file_upload.py | _get_app_db | tests/test_template_apply_updated_at.py | _get_app_db | 1.000 |
| tests/test_base_rates_file_upload.py | _get_app_db | tests/test_validations_stale_bump.py | _get_app_db | 1.000 |
| tests/test_fuel_inference_endpoints.py | TestApplyWritesFields | tests/test_fuel_inference_endpoints.py | test_apply_writes_and_materializes | 1.000 |
| tests/test_fuel_pattern_inference.py | TestGapDetected | tests/test_fuel_pattern_inference.py | test_missing_bracket | 1.000 |
| tests/test_integration.py | get_db | tests/test_training.py | get_db | 1.000 |
| tests/test_team_analytics.py | TestFactionGrouping | tests/test_team_analytics.py | test_users_grouped_by_department | 1.000 |
| tests/test_team_analytics.py | TestTrendingSections | tests/test_team_analytics.py | test_top_task_codes_from_status_history | 1.000 |
| tests/test_template_apply_updated_at.py | _get_app_db | tests/test_validations_stale_bump.py | _get_app_db | 1.000 |
| web/action_queue.py | _get_db | web/team.py | _get_db | 1.000 |
| web/action_queue.py | _get_db | web/contract_import.py | _get_db | 1.000 |
| web/action_queue.py | _get_db | web/reporting.py | _get_db | 1.000 |
| web/action_queue.py | _get_db | web/prompts.py | _get_db | 1.000 |
| web/action_queue.py | _get_db | web/activity_codes.py | _get_db | 1.000 |
| web/action_queue.py | _get_db | web/gap_dashboard.py | _get_db | 1.000 |
| web/action_queue.py | _get_db | web/eia.py | _get_db | 1.000 |
| web/action_queue.py | _get_db | web/rates.py | _get_db | 1.000 |
| web/activity_codes.py | _get_db | web/team.py | _get_db | 1.000 |
| web/activity_codes.py | _get_db | web/contract_import.py | _get_db | 1.000 |
| web/activity_codes.py | _get_db | web/reporting.py | _get_db | 1.000 |

## Staleness Alerts (481 findings)
| File | Name | Staleness | Composite |
|---|---|---|---|
| app.py | before_request | 1.000 | 0.584 |
| app.py | ingest_panel_needs_activity | 1.000 | 0.568 |
| app.py | _invoice_list_query_parts | 1.000 | 0.835 |
| copilot_prompts.py | get_invoice_prompt | 1.000 | 0.528 |
| czar_entry.py | insert_rates | 1.000 | 0.585 |
| czar_entry.py | coverage_report | 1.000 | 0.555 |
| delete_not_xml.py | materialize_targets | 1.000 | 0.480 |
| delete_not_xml.py | _count_rows | 1.000 | 0.483 |
| delete_not_xml.py | _financial_stats | 1.000 | 0.488 |
| delete_not_xml.py | _export_backup | 1.000 | 0.499 |
| diagnose_contract.py | diagnose_invoice | 1.000 | 0.737 |
| diagnose_contract.py | show_recent_failures | 1.000 | 0.517 |
| eia_fetcher.py | store_prices | 1.000 | 0.607 |
| eia_fetcher.py | check_freshness | 1.000 | 0.580 |
| eia_fetcher.py | manual_entry | 1.000 | 0.578 |
| eia_fetcher.py | get_eia_price_for_date | 1.000 | 0.498 |
| engines/action_router.py | _build_dispute_email | 1.000 | 0.603 |
| engines/action_router.py | _build_fill_gap | 1.000 | 0.778 |
| engines/action_router.py | _build_pricing_ticket | 1.000 | 0.609 |
| engines/action_router.py | _build_flag_duplicate | 1.000 | 0.609 |
| engines/action_router.py | _build_register_contract | 1.000 | 0.365 |
| engines/action_router.py | _build_record_resolution | 1.000 | 0.614 |
| engines/action_router.py | _check_follow_ups | 1.000 | 0.689 |
| engines/action_router.py | _check_contract_renewals | 1.000 | 0.630 |
| engines/action_router.py | _build_summary | 1.000 | 0.680 |
| engines/action_router.py | dismiss_filled_gap_actions | 1.000 | 0.830 |
| engines/activity_analytics.py | get_anomalies | 1.000 | 0.652 |
| engines/activity_analytics.py | get_note_patterns | 1.000 | 0.532 |
| engines/activity_analytics.py | get_pipeline_flow | 1.000 | 0.534 |
| engines/activity_analytics.py | get_stale_invoices | 1.000 | 0.569 |

## Complexity Hotspots (101 findings)
| File | Name | Score | Cyclomatic | Depth | Params |
|---|---|---|---|---|---|
| app.py | invoice_detail | 1.000 | 132 | 5 | 1 |
| ingestion/xml_parser.py | InvoiceXMLParser | 1.000 | 91 | 4 | 0 |
| migrate_fuel_ceilings_floor_only_20260719.py | run_migration | 1.000 | 91 | 5 | 2 |
| web/contract_import.py | _validate_contract_json | 1.000 | 78 | 4 | 2 |
| web/contracts.py | contract_fuel_import_combined | 1.000 | 67 | 5 | 1 |
| web/contracts.py | _build_dashboard_cards | 0.999 | 65 | 3 | 6 |
| web/contracts.py | contracts_list | 0.999 | 65 | 5 | 0 |
| engines/validator.py | gate_7_linehaul | 0.999 | 62 | 4 | 6 |
| engines/validator.py | gate_9_accessorials | 0.998 | 56 | 6 | 8 |
| web/gap_dashboard.py | enrich_invoice | 0.998 | 58 | 4 | 1 |
| repair_fuel_sentinel_20260716.py | run_repair | 0.998 | 58 | 3 | 2 |
| web/documents.py | document_extract | 0.997 | 54 | 7 | 2 |
| web/gap_dashboard.py | _import_fuel_section | 0.997 | 54 | 5 | 3 |
| check_l5c_shift.py | main | 0.996 | 53 | 7 | 0 |
| engines/validator.py | gate_8_fuel | 0.996 | 52 | 4 | 7 |
| ingestion/activity_import.py | import_activity_history | 0.996 | 54 | 3 | 3 |
| web/gap_dashboard.py | _parse_generic_csv | 0.996 | 51 | 7 | 2 |
| app.py | team_dashboard | 0.995 | 52 | 5 | 0 |
| web/carrier_profiles.py | carrier_import_fuel | 0.992 | 49 | 4 | 1 |
| web/gap_dashboard.py | _import_lanes_section | 0.991 | 48 | 4 | 3 |
| engines/email_generator.py | generate_pricing_ticket | 0.990 | 45 | 6 | 5 |
| app.py | dispute_brief | 0.989 | 46 | 6 | 1 |
| engines/validator.py | validate_invoice | 0.987 | 43 | 8 | 2 |
| web/carrier_profiles.py | carrier_import_accessorials | 0.983 | 43 | 6 | 1 |
| extraction_tracking.py | write_extraction_quality_report | 0.981 | 43 | 4 | 2 |
| web/contracts.py | adjudicate_cell | 0.977 | 41 | 6 | 1 |
| engines/exit_interview.py | _capture_pro_exit_interview | 0.976 | 41 | 5 | 2 |
| web/gap_dashboard.py | _import_base_rates_section | 0.975 | 41 | 3 | 4 |
| app.py | _invoice_list_query_parts | 0.965 | 38 | 5 | 3 |
| engines/email_generator.py | _build_rate_comparison | 0.953 | 37 | 3 | 3 |

## Co-Change Patterns (228 pairs)
| File A | File B | Co-changes | Jaccard |
|---|---|---|---|
| PROJECT_STATUS.md | knowledge/research/agent-prompt-feedback.md | 160 | 0.291 |
| knowledge/research/copilot-extraction-quality.md | knowledge/research/validation-quality-summary.md | 35 | 0.854 |
| contract_tables.py | database.py | 19 | 0.224 |
| app.py | web/templates/invoice_detail.html | 18 | 0.115 |
| copilot_prompts.py | web/gap_dashboard.py | 18 | 0.141 |
| knowledge/research/activity-notes-patterns.md | knowledge/research/validation-quality-summary.md | 17 | 0.436 |
| app.py | knowledge/research/agent-prompt-feedback.md | 17 | 0.032 |
| app.py | web/templates/ingest.html | 17 | 0.136 |
| knowledge/research/activity-notes-patterns.md | knowledge/research/copilot-extraction-quality.md | 16 | 0.400 |
| web/templates/contract_fuel.html | web/templates/contract_lanes.html | 16 | 0.471 |
| web/templates/contract_accessorials.html | web/templates/contract_fuel.html | 15 | 0.455 |
| web/contracts.py | web/gap_dashboard.py | 15 | 0.086 |
| app.py | database.py | 14 | 0.086 |
| contract_tables.py | knowledge/research/agent-prompt-feedback.md | 14 | 0.030 |
| web/contracts.py | web/templates/contract_dashboard.html | 14 | 0.149 |
| web/templates/contract_accessorials.html | web/templates/contract_lanes.html | 14 | 0.583 |
| copilot_prompts.py | web/contracts.py | 13 | 0.107 |
| engines/validator.py | web/contracts.py | 13 | 0.101 |
| web/templates/contract_accessorials.html | web/templates/contract_fak.html | 13 | 0.684 |
| web/contracts.py | web/templates/contracts_list.html | 13 | 0.141 |
| web/contracts.py | web/templates/contract_fuel.html | 12 | 0.112 |
| web/templates/contract_billto.html | web/templates/contract_fak.html | 12 | 0.800 |
| app.py | web/templates/dashboard.html | 12 | 0.095 |
| app.py | ingestion/ingest.py | 11 | 0.083 |
| app.py | validate_batch.py | 11 | 0.083 |
| knowledge/research/agent-prompt-feedback.md | web/contracts.py | 11 | 0.022 |
| web/carrier_profiles.py | web/templates/carrier_profile_detail.html | 11 | 0.250 |
| web/templates/carrier_fuel.html | web/templates/carrier_minimums.html | 11 | 0.733 |
| web/templates/contract_accessorials.html | web/templates/contract_billto.html | 11 | 0.550 |
| web/templates/contract_areas.html | web/templates/contract_fak.html | 11 | 0.733 |

## Research Recommendations (1578 deviations across 4 roles)

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

### route_handler (46 deviations)
- **[medium]** `web/action_queue.py::action_queue` -- single_responsibility: Function has 262 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profiles_list` -- single_responsibility: Function has 114 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::_build_carrier_cards` -- single_responsibility: Function has 204 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profile_detail` -- single_responsibility: Function has 205 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_accessorials` -- single_responsibility: Function has 202 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_fuel` -- single_responsibility: Function has 269 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_minimums` -- single_responsibility: Function has 192 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_stub_contracts_panel` -- single_responsibility: Function has 84 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_validate_contract_json` -- single_responsibility: Function has 226 lines (threshold: 80)
- **[medium]** `web/contract_import.py::_import_contract` -- single_responsibility: Function has 330 lines (threshold: 80)
- **[medium]** `web/contract_import.py::import_contract_json` -- single_responsibility: Function has 199 lines (threshold: 80)
- **[medium]** `web/contract_template_routes.py::template_upload` -- single_responsibility: Function has 112 lines (threshold: 80)
- **[medium]** `web/contract_template_routes.py::template_apply` -- single_responsibility: Function has 95 lines (threshold: 80)
- **[medium]** `web/contract_templates.py::parse_csv` -- single_responsibility: Function has 87 lines (threshold: 80)
- **[medium]** `web/contract_templates.py::compute_diff` -- single_responsibility: Function has 111 lines (threshold: 80)

### utility (1522 deviations)
- **[medium]** `app.py::handle_csrf_error` -- no_domain_logic: Domain-specific term found in utility function
- **[medium]** `app.py::ingest` -- pure_functions: File I/O found in utility function
- **[medium]** `app.py::ingest` -- no_domain_logic: Domain-specific term found in utility function
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
- **[medium]** `app.py::run_validation` -- pure_functions: Database connection parameter found in utility function

### validation_gate (1 deviations)
- **[medium]** `engines/validator.py::_feed_confidence_system` -- deterministic_output: datetime.now() used in gate function

## Intent Gaps (16 findings)
| Severity | Signal Type | Title | Diagnostic |
|---|---|---|---|
| CRITICAL | coverage_gap | team_dashboard (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | ingest_xml_paste (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | dispute_brief (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | invoice_detail (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | _invoice_list_query_parts (app.py) — uncovered high-volatility function | Fix |
| CRITICAL | coverage_gap | run_validation (app.py) — uncovered high-volatility function | Fix |
| LOW | coupling_hotspot | execute (dedup_xml_data.py) — high-coupling node (coupling_score=0.99) | Architecture check |
| MEDIUM | coupling_hotspot | create_contract_tables (contract_tables.py) — high-coupling node (coupling_score | Architecture check |
| CRITICAL | complexity_hotspot | invoice_detail (app.py) — high cyclomatic complexity (complexity_score=1.00, cyc | Fix |
| HIGH | complexity_hotspot | InvoiceXMLParser (ingestion/xml_parser.py) — high cyclomatic complexity (complex | Fix |
| HIGH | complexity_hotspot | run_migration (migrate_fuel_ceilings_floor_only_20260719.py) — high cyclomatic c | Fix |
| CRITICAL | complexity_hotspot | _validate_contract_json (web/contract_import.py) — high cyclomatic complexity (c | Fix |
| CRITICAL | complexity_hotspot | contract_fuel_import_combined (web/contracts.py) — high cyclomatic complexity (c | Fix |
| HIGH | complexity_hotspot | _build_dashboard_cards (web/contracts.py) — high cyclomatic complexity (complexi | Fix |
| CRITICAL | complexity_hotspot | contracts_list (web/contracts.py) — high cyclomatic complexity (complexity_score | Fix |
| LOW | complexity_hotspot | gate_7_linehaul (engines/validator.py) — high cyclomatic complexity (complexity_ | Fix |

## Planner Constraints (700 total)

### coverage_required (76)
- **[high]** `web/contracts.py::contract_fuel_import_combined` — Composite score 0.88, no test coverage, volatility 0.94
- **[high]** `web/contracts.py::contracts_list` — Composite score 0.87, no test coverage, volatility 0.94
- **[high]** `app.py::team_dashboard` — Composite score 0.86, no test coverage, volatility 0.97
- **[high]** `app.py::ingest_xml_paste` — Composite score 0.85, no test coverage, volatility 0.97
- **[high]** `app.py::dispute_brief` — Composite score 0.85, no test coverage, volatility 0.97
- **[high]** `web/contracts.py::contract_lanes_bulk` — Composite score 0.84, no test coverage, volatility 0.94
- **[high]** `app.py::invoice_detail` — Composite score 0.84, no test coverage, volatility 0.97
- **[high]** `web/carrier_profiles.py::carrier_import_fuel` — Composite score 0.84, no test coverage, volatility 0.17
- **[high]** `web/contract_import.py::_validate_contract_json` — Composite score 0.84, no test coverage, volatility 0.00
- **[high]** `app.py::_invoice_list_query_parts` — Composite score 0.83, no test coverage, volatility 0.97
- **[high]** `extraction_tracking.py::write_extraction_quality_report` — Composite score 0.83, no test coverage, volatility 0.17
- **[high]** `engines/action_router.py::dismiss_filled_gap_actions` — Composite score 0.83, no test coverage, volatility 0.00
- **[high]** `engines/triangulation.py::get_attestation_requests` — Composite score 0.83, no test coverage, volatility 0.00
- **[high]** `web/action_queue.py::action_queue` — Composite score 0.82, no test coverage, volatility 0.00
- **[high]** `web/documents.py::document_extract` — Composite score 0.82, no test coverage, volatility 0.00

### verify_dependents (73)
- **[high]** `dedup_xml_data.py::execute` — Coupling score 0.99, 98592 inbound + 19 outbound deps
- **[high]** `contract_tables.py::create_contract_tables` — Coupling score 0.99, 6387 inbound + 67020 outbound deps
- **[high]** `database.py::_create_tables` — Coupling score 0.98, 6935 inbound + 37047 outbound deps
- **[high]** `contract_tables.py::extend_existing_tables` — Coupling score 0.97, 6387 inbound + 22051 outbound deps
- **[high]** `engines/triangulation.py::triangulate` — Coupling score 0.97, 24219 inbound + 3333 outbound deps
- **[high]** `database.py::init_db` — Coupling score 0.97, 17690 inbound + 8846 outbound deps
- **[high]** `ingestion/ingest.py::_to_float` — Coupling score 0.97, 25072 inbound + 0 outbound deps
- **[high]** `engines/validator.py::validate_invoice` — Coupling score 0.96, 12798 inbound + 12095 outbound deps
- **[high]** `engines/validator.py::add` — Coupling score 0.96, 20592 inbound + 0 outbound deps
- **[high]** `ingestion/activity_import.py::import_activity_history` — Coupling score 0.95, 12954 inbound + 5595 outbound deps
- **[high]** `engines/validator.py::gate_9_accessorials` — Coupling score 0.95, 12042 inbound + 5758 outbound deps
- **[high]** `contract_tables.py::_safe_add_column` — Coupling score 0.94, 17268 inbound + 303 outbound deps
- **[high]** `web/contracts.py::_build_dashboard_cards` — Coupling score 0.94, 7262 inbound + 8549 outbound deps
- **[high]** `engines/validator.py::gate_8_fuel` — Coupling score 0.94, 10025 inbound + 5647 outbound deps
- **[high]** `engines/validator.py::gate_7_linehaul` — Coupling score 0.94, 9135 inbound + 6390 outbound deps

### refactor_candidate (40)
- **[medium]** `database.py::__init__ ↔ tests/test_remaining_pipeline_qa.py::__init__` — Similarity 1.00 — potential duplicate
- **[medium]** `database.py::__getitem__ ↔ tests/test_remaining_pipeline_qa.py::__getitem__` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_accessorial_aliases.py::_make_db ↔ tests/test_zip_5digit.py::_make_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_action_queue_aggregation.py::_insert_action ↔ tests/test_aggregated_queue_customer_display.py::_insert_action` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_aggregated_queue_customer_display.py::TestCustomerDisplayMultiCustomer ↔ tests/test_aggregated_queue_customer_display.py::test_three_customers_joined_by_middle_dot` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_backtest_removal_validation.py::_get_app_db ↔ tests/test_template_apply_updated_at.py::_get_app_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_backtest_removal_validation.py::_get_app_db ↔ tests/test_validations_stale_bump.py::_get_app_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_backtest_removal_validation.py::_get_app_db ↔ tests/test_base_rates_file_upload.py::_get_app_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_backtest_removal_validation.py::_seed ↔ tests/test_base_rates_file_upload.py::_seed` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_backtest_removal_validation.py::_query_one ↔ tests/test_base_rates_file_upload.py::_query_one` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_backtest_removal_validation.py::_get_contract_updated_at ↔ tests/test_validations_stale_bump.py::_get_contract_updated_at` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_base_rates_file_upload.py::_get_app_db ↔ tests/test_template_apply_updated_at.py::_get_app_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_base_rates_file_upload.py::_get_app_db ↔ tests/test_validations_stale_bump.py::_get_app_db` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_fuel_inference_endpoints.py::TestApplyWritesFields ↔ tests/test_fuel_inference_endpoints.py::test_apply_writes_and_materializes` — Similarity 1.00 — potential duplicate
- **[medium]** `tests/test_fuel_pattern_inference.py::TestGapDetected ↔ tests/test_fuel_pattern_inference.py::test_missing_bracket` — Similarity 1.00 — potential duplicate

### investigation_needed (481)
- **[high]** `app.py::before_request` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `app.py::ingest_panel_needs_activity` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `app.py::_invoice_list_query_parts` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `copilot_prompts.py::get_invoice_prompt` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `czar_entry.py::insert_rates` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `czar_entry.py::coverage_report` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `delete_not_xml.py::materialize_targets` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `delete_not_xml.py::_count_rows` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `delete_not_xml.py::_financial_stats` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `delete_not_xml.py::_export_backup` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `diagnose_contract.py::diagnose_invoice` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `diagnose_contract.py::show_recent_failures` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `eia_fetcher.py::store_prices` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `eia_fetcher.py::check_freshness` — Staleness score 1.00 — dependencies updated but chunk unchanged
- **[high]** `eia_fetcher.py::manual_entry` — Staleness score 1.00 — dependencies updated but chunk unchanged

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
- **[medium]** `web/carrier_profiles.py::carrier_profiles_list` — route_handler deviates from single_responsibility: Function has 114 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::_build_carrier_cards` — route_handler deviates from single_responsibility: Function has 204 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_profile_detail` — route_handler deviates from single_responsibility: Function has 205 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_accessorials` — route_handler deviates from single_responsibility: Function has 202 lines (threshold: 80)
- **[medium]** `web/carrier_profiles.py::carrier_import_fuel` — route_handler deviates from single_responsibility: Function has 269 lines (threshold: 80)

## Specialist Update Data
- Functions: 1544
- Classes: 711
- Methods: 77
- Test cases: 2834
- Dependencies: 3269889
- Similarity pairs: 3757
- Average health score: 0.2604
- High risk count: 1019
