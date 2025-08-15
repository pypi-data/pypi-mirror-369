"""
Schema Command

Adds `vlite-cli schema` command that parses parameters, performs minimal rules
file validation (single-table only, no jsonschema), and prints placeholder
output aligned with the existing CLI style.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast

import click

from cli.core.data_validator import DataValidator
from cli.core.source_parser import SourceParser
from shared.enums import RuleAction, RuleCategory, RuleType, SeverityLevel
from shared.enums.data_types import DataType
from shared.schema.base import RuleTarget, TargetEntity
from shared.schema.rule_schema import RuleSchema
from shared.utils.console import safe_echo
from shared.utils.datetime_utils import now as _now
from shared.utils.logger import get_logger

logger = get_logger(__name__)


_ALLOWED_TYPE_NAMES: set[str] = {
    "string",
    "integer",
    "float",
    "boolean",
    "date",
    "datetime",
}


def _validate_rules_payload(payload: Any) -> Tuple[List[str], int]:
    """Validate the minimal structure of the schema rules file.

    This performs non-jsonschema checks:
    - Top-level must be an object with a `rules` array
    - Warn and ignore top-level `table` if present
    - Validate each rule item fields and types:
      - field: required str
      - type: optional str in allowed set
      - required: optional bool
      - enum: optional list
      - min/max: optional numeric (int or float)

    Returns:
        warnings, rules_count

    Raises:
        click.UsageError: if structure or types are invalid
    """
    warnings: List[str] = []

    if not isinstance(payload, dict):
        raise click.UsageError("Rules file must be a JSON object with a 'rules' array")

    if "table" in payload:
        warnings.append(
            "Top-level 'table' is ignored; table is derived from data-source"
        )

    if "tables" in payload:
        # Explicitly reject multi-table format in v1
        raise click.UsageError(
            "'tables' is not supported in v1; use single-table 'rules' only"
        )

    rules = payload.get("rules")
    if not isinstance(rules, list):
        raise click.UsageError("'rules' must be an array")

    for idx, item in enumerate(rules):
        if not isinstance(item, dict):
            raise click.UsageError(f"rules[{idx}] must be an object")

        # field
        field_name = item.get("field")
        if not isinstance(field_name, str) or not field_name:
            raise click.UsageError(f"rules[{idx}].field must be a non-empty string")

        # type
        if "type" in item:
            type_name = item["type"]
            if not isinstance(type_name, str):
                raise click.UsageError(
                    f"rules[{idx}].type must be a string when provided"
                )
            if type_name.lower() not in _ALLOWED_TYPE_NAMES:
                allowed = ", ".join(sorted(_ALLOWED_TYPE_NAMES))
                raise click.UsageError(
                    f"rules[{idx}].type '{type_name}' is not supported. "
                    f"Allowed: {allowed}"
                )

        # required
        if "required" in item and not isinstance(item["required"], bool):
            raise click.UsageError(
                f"rules[{idx}].required must be a boolean when provided"
            )

        # enum
        if "enum" in item and not isinstance(item["enum"], list):
            raise click.UsageError(f"rules[{idx}].enum must be an array when provided")

        # min/max
        for bound_key in ("min", "max"):
            if bound_key in item:
                value = item[bound_key]
                if not isinstance(value, (int, float)):
                    raise click.UsageError(
                        f"rules[{idx}].{bound_key} must be numeric when provided"
                    )

    return warnings, len(rules)


def _map_type_name_to_datatype(type_name: str) -> DataType:
    """Map user-provided type string to DataType enum.

    Args:
        type_name: Input type name (case-insensitive), e.g. "string".

    Returns:
        DataType enum.

    Raises:
        click.UsageError: When the value is unsupported.
    """
    normalized = str(type_name).strip().lower()
    mapping: Dict[str, DataType] = {
        "string": DataType.STRING,
        "integer": DataType.INTEGER,
        "float": DataType.FLOAT,
        "boolean": DataType.BOOLEAN,
        "date": DataType.DATE,
        "datetime": DataType.DATETIME,
    }
    if normalized not in mapping:
        allowed = ", ".join(sorted(_ALLOWED_TYPE_NAMES))
        raise click.UsageError(f"Unsupported type '{type_name}'. Allowed: {allowed}")
    return mapping[normalized]


def _derive_category(rule_type: RuleType) -> RuleCategory:
    """Derive category from rule type per design mapping."""
    if rule_type == RuleType.SCHEMA:
        return RuleCategory.VALIDITY
    if rule_type == RuleType.NOT_NULL:
        return RuleCategory.COMPLETENESS
    if rule_type == RuleType.UNIQUE:
        return RuleCategory.UNIQUENESS
    # RANGE, LENGTH, ENUM, REGEX, DATE_FORMAT -> VALIDITY in v1
    return RuleCategory.VALIDITY


def _create_rule_schema(
    *,
    name: str,
    rule_type: RuleType,
    column: str | None,
    parameters: Dict[str, Any],
    description: str | None = None,
    severity: SeverityLevel = SeverityLevel.MEDIUM,
    action: RuleAction = RuleAction.ALERT,
) -> RuleSchema:
    """Create a `RuleSchema` with an empty target that will be completed later.

    The database and table will be filled by the validator based on the source.
    """
    target = RuleTarget(
        entities=[
            TargetEntity(
                database="", table="", column=column, connection_id=None, alias=None
            )
        ],
        relationship_type="single_table",
    )
    return RuleSchema(
        name=name,
        description=description,
        type=rule_type,
        target=target,
        parameters=parameters,
        cross_db_config=None,
        threshold=0.0,
        category=_derive_category(rule_type),
        severity=severity,
        action=action,
        is_active=True,
        tags=[],
        template_id=None,
        validation_error=None,
    )


def _decompose_to_atomic_rules(payload: Dict[str, Any]) -> List[RuleSchema]:
    """Decompose schema JSON payload into atomic RuleSchema objects.

    Rules per item:
    - type -> contributes to table-level SCHEMA columns mapping
    - required -> NOT_NULL(column)
    - min/max -> RANGE(column, min_value/max_value)
    - enum -> ENUM(column, allowed_values)
    """
    rules_arr = payload.get("rules", [])

    # Build SCHEMA columns mapping first
    columns_map: Dict[str, Dict[str, Any]] = {}
    atomic_rules: List[RuleSchema] = []

    for item in rules_arr:
        field_name = item.get("field")
        if not isinstance(field_name, str) or not field_name:
            # Should have been validated earlier; keep defensive check
            raise click.UsageError("Each rule item must have a non-empty 'field'")

        # SCHEMA: type contributes expected_type
        if "type" in item and item["type"] is not None:
            dt = _map_type_name_to_datatype(str(item["type"]))
            columns_map[field_name] = {"expected_type": dt.value}

        # NOT_NULL
        if bool(item.get("required", False)):
            atomic_rules.append(
                _create_rule_schema(
                    name=f"not_null_{field_name}",
                    rule_type=RuleType.NOT_NULL,
                    column=field_name,
                    parameters={},
                    description=f"CLI: required non-null for {field_name}",
                )
            )

        # RANGE
        has_min = "min" in item and isinstance(item.get("min"), (int, float))
        has_max = "max" in item and isinstance(item.get("max"), (int, float))
        if has_min or has_max:
            params: Dict[str, Any] = {}
            if has_min:
                params["min_value"] = item["min"]
            if has_max:
                params["max_value"] = item["max"]
            atomic_rules.append(
                _create_rule_schema(
                    name=f"range_{field_name}",
                    rule_type=RuleType.RANGE,
                    column=field_name,
                    parameters=params,
                    description=f"CLI: range for {field_name}",
                )
            )

        # ENUM
        if "enum" in item:
            values = item.get("enum")
            if not isinstance(values, list) or len(values) == 0:
                raise click.UsageError("'enum' must be a non-empty array when provided")
            atomic_rules.append(
                _create_rule_schema(
                    name=f"enum_{field_name}",
                    rule_type=RuleType.ENUM,
                    column=field_name,
                    parameters={"allowed_values": values},
                    description=f"CLI: enum for {field_name}",
                )
            )

    # Create one table-level SCHEMA rule if any columns were declared
    if columns_map:
        schema_params: Dict[str, Any] = {"columns": columns_map}
        # Optional switches at top-level
        if isinstance(payload.get("strict_mode"), bool):
            schema_params["strict_mode"] = payload["strict_mode"]
        if isinstance(payload.get("case_insensitive"), bool):
            schema_params["case_insensitive"] = payload["case_insensitive"]

        atomic_rules.insert(
            0,
            _create_rule_schema(
                name="schema",
                rule_type=RuleType.SCHEMA,
                column=None,
                parameters=schema_params,
                description="CLI: table schema existence+type",
            ),
        )

    return atomic_rules


def _build_prioritized_atomic_status(
    *,
    schema_result: Dict[str, Any] | None,
    atomic_rules: List[RuleSchema],
) -> Dict[str, Dict[str, str]]:
    """Return a mapping rule_id -> {status, skip_reason} applying prioritization.

    Prioritization per column:
      1) If field missing → mark SCHEMA for that field as FAILED (implicit) and all
         dependent rules (NOT_NULL/RANGE/ENUM) as SKIPPED (reason FIELD_MISSING).
      2) If type mismatch → mark dependent rules as SKIPPED (reason TYPE_MISMATCH).
      3) Otherwise, leave dependent rules to their engine-evaluated status.

    We infer per-column status from schema_result.execution_plan.schema_details.
    """
    mapping: Dict[str, Dict[str, str]] = {}

    # Build per-column guard from SCHEMA details
    column_guard: Dict[str, str] = {}  # column -> NONE|FIELD_MISSING|TYPE_MISMATCH
    if schema_result:
        details = (
            schema_result.get("execution_plan", {})
            .get("schema_details", {})
            .get("field_results", [])
        )
        for item in details:
            col = str(item.get("column"))
            code = str(item.get("failure_code", "NONE"))
            column_guard[col] = code

    # Apply skip to dependent rules
    for r in atomic_rules:
        if r.type == RuleType.SCHEMA:
            continue
        column = r.get_target_column() or ""
        guard = column_guard.get(column, "NONE")
        if guard == "FIELD_MISSING":
            mapping[r.id] = {"status": "SKIPPED", "skip_reason": "FIELD_MISSING"}
        elif guard == "TYPE_MISMATCH":
            mapping[r.id] = {"status": "SKIPPED", "skip_reason": "TYPE_MISMATCH"}

    return mapping


def _safe_echo(text: str, *, err: bool = False) -> None:
    """Compatibility shim; delegate to shared safe_echo."""
    safe_echo(text, err=err)


def _maybe_echo_analyzing(source: str, output: str) -> None:
    """Emit analyzing line unless JSON output."""
    if str(output).lower() != "json":
        _safe_echo(f"🔍 Analyzing source: {source}", err=True)


def _guard_empty_source_file(source: str) -> None:
    """Raise a ClickException if a provided file source is empty."""
    potential_path = Path(source)
    if potential_path.exists() and potential_path.is_file():
        if potential_path.stat().st_size == 0:
            raise click.ClickException(
                f"Error: Source file '{source}' is empty – nothing to validate."
            )


def _read_rules_payload(rules_file: str) -> Dict[str, Any]:
    """Read and parse JSON rules file, raising UsageError on invalid JSON."""
    try:
        with open(rules_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as e:
        raise click.UsageError(f"Invalid JSON in rules file: {rules_file}") from e
    return cast(Dict[str, Any], payload)


def _emit_warnings(warnings: List[str]) -> None:
    for msg in warnings:
        _safe_echo(f"⚠️ Warning: {msg}", err=True)


def _early_exit_when_no_rules(
    *, source: str, rules_file: str, output: str, fail_on_error: bool
) -> None:
    """Emit minimal output and exit when no rules are present."""
    if output.lower() == "json":
        payload = {
            "status": "ok",
            "source": source,
            "rules_file": rules_file,
            "rules_count": 0,
            "summary": {
                "total_rules": 0,
                "passed_rules": 0,
                "failed_rules": 0,
                "skipped_rules": 0,
                "total_failed_records": 0,
                "execution_time_s": 0.0,
            },
            "results": [],
            "fields": [],
        }
        _safe_echo(json.dumps(payload, default=str))
        raise click.exceptions.Exit(1 if fail_on_error else 0)
    else:
        _safe_echo(f"✓ Checking {source} (0 records)")
        raise click.exceptions.Exit(1 if fail_on_error else 0)


def _create_validator(
    *,
    source_config: Any,
    atomic_rules: List[RuleSchema] | List[Dict[str, Any]],
    core_config: Any,
    cli_config: Any,
) -> Any:
    try:
        return DataValidator(
            source_config=source_config,
            rules=cast(List[RuleSchema | Dict[str, Any]], atomic_rules),
            core_config=core_config,
            cli_config=cli_config,
        )
    except TypeError:
        return DataValidator()  # type: ignore[call-arg]


def _run_validation(validator: Any) -> Tuple[List[Any], float]:
    import asyncio

    start = _now()
    results = asyncio.run(validator.validate())
    exec_seconds = (_now() - start).total_seconds()
    return results, exec_seconds


def _extract_schema_result_dict(
    *, atomic_rules: List[RuleSchema], results: List[Any]
) -> Dict[str, Any] | None:
    try:
        schema_rule = next(
            (rule for rule in atomic_rules if rule.type == RuleType.SCHEMA), None
        )
        if not schema_rule:
            return None
        for r in results:
            rid = ""
            if hasattr(r, "rule_id"):
                try:
                    rid = str(getattr(r, "rule_id"))
                except Exception:
                    rid = ""
            elif isinstance(r, dict):
                rid = str(r.get("rule_id", ""))
            if rid == str(schema_rule.id):
                return (
                    r.model_dump()
                    if hasattr(r, "model_dump")
                    else cast(Dict[str, Any], r)
                )
        return None
    except Exception:
        return None


def _compute_skip_map(
    *, atomic_rules: List[RuleSchema], schema_result_dict: Dict[str, Any] | None
) -> Dict[str, Dict[str, str]]:
    try:
        return _build_prioritized_atomic_status(
            schema_result=schema_result_dict, atomic_rules=atomic_rules
        )
    except Exception:
        return {}


def _emit_json_output(
    *,
    source: str,
    rules_file: str,
    atomic_rules: List[RuleSchema],
    results: List[Any],
    skip_map: Dict[str, Dict[str, str]],
    schema_result_dict: Dict[str, Any] | None,
    exec_seconds: float,
) -> None:
    enriched_results: List[Dict[str, Any]] = []
    for r in results:
        rd: Dict[str, Any]
        if hasattr(r, "model_dump"):
            try:
                rd = cast(Dict[str, Any], r.model_dump())
            except Exception:
                rd = {}
        elif isinstance(r, dict):
            rd = r
        else:
            rd = {}
        rule_id = str(rd.get("rule_id", ""))
        if rule_id in skip_map:
            rd["status"] = skip_map[rule_id]["status"]
            rd["skip_reason"] = skip_map[rule_id]["skip_reason"]
        enriched_results.append(rd)

    rule_map: Dict[str, RuleSchema] = {str(rule.id): rule for rule in atomic_rules}

    def _failed_records_of(res: Dict[str, Any]) -> int:
        if "failed_records" in res and isinstance(res.get("failed_records"), int):
            return int(res.get("failed_records") or 0)
        dm = res.get("dataset_metrics") or []
        total = 0
        for m in dm:
            if hasattr(m, "failed_records"):
                total += int(getattr(m, "failed_records", 0) or 0)
            elif isinstance(m, dict):
                total += int(m.get("failed_records", 0) or 0)
        return total

    fields: List[Dict[str, Any]] = []
    schema_fields_index: Dict[str, Dict[str, Any]] = {}

    if schema_result_dict:
        schema_plan = (schema_result_dict or {}).get("execution_plan", {}) or {}
        schema_details = schema_plan.get("schema_details", {}) or {}
        field_results = schema_details.get("field_results", []) or []
        for item in field_results:
            col_name = str(item.get("column"))
            entry: Dict[str, Any] = {
                "column": col_name,
                "checks": {
                    "existence": {
                        "status": item.get("existence", "UNKNOWN"),
                        "failure_code": item.get("failure_code", "NONE"),
                    },
                    "type": {
                        "status": item.get("type", "UNKNOWN"),
                        "failure_code": item.get("failure_code", "NONE"),
                    },
                },
            }
            fields.append(entry)
            schema_fields_index[col_name] = entry

    schema_rule = next(
        (rule for rule in atomic_rules if rule.type == RuleType.SCHEMA), None
    )
    if schema_rule:
        params = schema_rule.parameters or {}
        declared_cols = (params.get("columns") or {}).keys()
        for col in declared_cols:
            if str(col) not in schema_fields_index:
                entry = {
                    "column": str(col),
                    "checks": {
                        "existence": {"status": "UNKNOWN", "failure_code": "NONE"},
                        "type": {"status": "UNKNOWN", "failure_code": "NONE"},
                    },
                }
                fields.append(entry)
                schema_fields_index[str(col)] = entry

    def _ensure_check(entry: Dict[str, Any], name: str) -> Dict[str, Any]:
        checks: Dict[str, Dict[str, Any]] = entry.setdefault("checks", {})
        if name not in checks:
            checks[name] = {
                "status": (
                    "SKIPPED"
                    if name in {"not_null", "range", "enum", "regex", "date_format"}
                    else "UNKNOWN"
                )
            }
        return checks[name]

    for rd in enriched_results:
        rule_id = str(rd.get("rule_id", ""))
        rule = rule_map.get(rule_id)
        if not rule or rule.type == RuleType.SCHEMA:
            continue
        column_name = rule.get_target_column() or ""
        if not column_name:
            continue
        l_entry = schema_fields_index.get(column_name)
        if not l_entry:
            l_entry = {"column": column_name, "checks": {}}
            fields.append(l_entry)
            schema_fields_index[column_name] = l_entry
        t = rule.type
        if t == RuleType.NOT_NULL:
            key = "not_null"
        elif t == RuleType.RANGE:
            key = "range"
        elif t == RuleType.ENUM:
            key = "enum"
        elif t == RuleType.REGEX:
            key = "regex"
        elif t == RuleType.DATE_FORMAT:
            key = "date_format"
        else:
            key = t.value.lower()
        check = _ensure_check(l_entry, key)
        check["status"] = str(rd.get("status", "UNKNOWN"))
        if rule_id in skip_map:
            check["status"] = skip_map[rule_id]["status"]
            check["skip_reason"] = skip_map[rule_id]["skip_reason"]
        fr = _failed_records_of(rd)
        if fr:
            check["failed_records"] = fr

    total_rules = len(enriched_results)
    passed_rules = sum(
        1 for r in enriched_results if str(r.get("status", "")).upper() == "PASSED"
    )
    failed_rules = sum(
        1 for r in enriched_results if str(r.get("status", "")).upper() == "FAILED"
    )
    skipped_rules = sum(
        1 for r in enriched_results if str(r.get("status", "")).upper() == "SKIPPED"
    )
    total_failed_records = sum(_failed_records_of(r) for r in enriched_results)

    schema_extras: List[str] = []
    if schema_result_dict:
        try:
            extras = (
                (schema_result_dict.get("execution_plan") or {}).get(
                    "schema_details", {}
                )
                or {}
            ).get("extras", [])
            if isinstance(extras, list):
                schema_extras = [str(x) for x in extras]
        except Exception:
            schema_extras = []

    payload: Dict[str, Any] = {
        "status": "ok",
        "source": source,
        "rules_file": rules_file,
        "rules_count": len(atomic_rules),
        "summary": {
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "skipped_rules": skipped_rules,
            "total_failed_records": total_failed_records,
            "execution_time_s": round(exec_seconds, 3),
        },
        "results": enriched_results,
        "fields": fields,
    }
    if schema_extras:
        payload["schema_extras"] = sorted(schema_extras)
    _safe_echo(json.dumps(payload, default=str))


def _emit_table_output(
    *,
    source: str,
    atomic_rules: List[RuleSchema],
    results: List[Any],
    skip_map: Dict[str, Dict[str, str]],
    schema_result_dict: Dict[str, Any] | None,
    exec_seconds: float,
) -> None:
    rule_map = {str(rule.id): rule for rule in atomic_rules}

    table_results: List[Dict[str, Any]] = []

    def _dataset_total(res: Dict[str, Any]) -> int:
        if isinstance(res.get("total_records"), int):
            return int(res.get("total_records") or 0)
        dm = res.get("dataset_metrics") or []
        total = 0
        for m in dm:
            if hasattr(m, "total_records"):
                total = max(total, int(getattr(m, "total_records", 0) or 0))
            elif isinstance(m, dict):
                total = max(total, int(m.get("total_records", 0) or 0))
        return total

    for r in results:
        rd: Dict[str, Any]
        if hasattr(r, "model_dump"):
            try:
                rd = cast(Dict[str, Any], r.model_dump())
            except Exception:
                rd = {}
        elif isinstance(r, dict):
            rd = r
        else:
            rd = {}
        rid = str(rd.get("rule_id", ""))
        rule = rule_map.get(rid)
        if rule is not None:
            rd["rule_type"] = rule.type.value
            rd["column_name"] = rule.get_target_column()
            rd.setdefault("rule_name", rule.name)
        if rid in skip_map:
            rd["status"] = skip_map[rid]["status"]
            rd["skip_reason"] = skip_map[rid]["skip_reason"]
        table_results.append(rd)

    header_total_records = 0
    for rd in table_results:
        header_total_records = max(header_total_records, _dataset_total(rd))

    def _calc_failed(res: Dict[str, Any]) -> int:
        if isinstance(res.get("failed_records"), int):
            return int(res.get("failed_records") or 0)
        dm = res.get("dataset_metrics") or []
        total = 0
        for m in dm:
            if hasattr(m, "failed_records"):
                total += int(getattr(m, "failed_records", 0) or 0)
            elif isinstance(m, dict):
                total += int(m.get("failed_records", 0) or 0)
        return total

    for rd in table_results:
        if "failed_records" not in rd:
            rd["failed_records"] = _calc_failed(rd)
        if "total_records" not in rd:
            rd["total_records"] = _dataset_total(rd)

    column_guard: Dict[str, str] = {}
    if schema_result_dict:
        details = (
            schema_result_dict.get("execution_plan", {})
            .get("schema_details", {})
            .get("field_results", [])
        )
        for item in details:
            col = str(item.get("column"))
            column_guard[col] = str(item.get("failure_code", "NONE"))

    grouped: Dict[str, Dict[str, Any]] = {}
    schema_rule = next((r for r in atomic_rules if r.type == RuleType.SCHEMA), None)
    declared_cols: List[str] = []
    if schema_rule:
        params = schema_rule.parameters or {}
        declared_cols = list((params.get("columns") or {}).keys())
        for col in declared_cols:
            grouped[str(col)] = {"column": str(col), "issues": []}

    for rd in table_results:
        rid = str(rd.get("rule_id", ""))
        rule = rule_map.get(rid)
        if not rule or rule.type == RuleType.SCHEMA:
            continue
        col = rule.get_target_column() or ""
        if not col:
            continue
        entry = grouped.setdefault(col, {"column": col, "issues": []})
        status = str(rd.get("status", "UNKNOWN"))
        if rule.type == RuleType.NOT_NULL:
            key = "not_null"
        elif rule.type == RuleType.RANGE:
            key = "range"
        elif rule.type == RuleType.ENUM:
            key = "enum"
        elif rule.type == RuleType.REGEX:
            key = "regex"
        elif rule.type == RuleType.DATE_FORMAT:
            key = "date_format"
        else:
            key = rule.type.value.lower()
        if column_guard.get(col) == "FIELD_MISSING":
            continue
        if column_guard.get(col) == "TYPE_MISMATCH" and key in {
            "not_null",
            "range",
            "enum",
            "regex",
            "date_format",
        }:
            continue
        if status in {"FAILED", "ERROR", "SKIPPED"}:
            entry["issues"].append(
                {
                    "check": key,
                    "status": status,
                    "failed_records": int(rd.get("failed_records", 0) or 0),
                    "skip_reason": skip_map.get(rid, {}).get("skip_reason"),
                }
            )

    lines: List[str] = []
    lines.append(f"✓ Checking {source} ({header_total_records:,} records)")

    total_failed_records = sum(
        int(r.get("failed_records", 0) or 0) for r in table_results
    )

    for col in sorted(grouped.keys()):
        guard = column_guard.get(col, "NONE")
        if guard == "FIELD_MISSING":
            lines.append(f"✗ {col}: missing (skipped dependent checks)")
            continue
        if guard == "TYPE_MISMATCH":
            lines.append(f"✗ {col}: type mismatch (skipped dependent checks)")
            continue
        issues = grouped[col]["issues"]
        critical = [i for i in issues if i["status"] in {"FAILED", "ERROR"}]
        if not critical:
            lines.append(f"✓ {col}: OK")
        else:
            for i in critical:
                fr = i.get("failed_records") or 0
                if i["status"] == "ERROR":
                    lines.append(f"✗ {col}: {i['check']} error")
                else:
                    lines.append(f"✗ {col}: {i['check']} failed ({fr} failures)")

    total_columns = len(grouped)
    passed_columns = sum(
        1
        for col in grouped
        if column_guard.get(col, "NONE") == "NONE"
        and not [
            i for i in grouped[col]["issues"] if i["status"] in {"FAILED", "ERROR"}
        ]
    )
    failed_columns = total_columns - passed_columns
    overall_error_rate = (
        0.0
        if header_total_records == 0
        else (total_failed_records / max(header_total_records, 1)) * 100
    )
    lines.append(
        f"\nSummary: {passed_columns} passed, {failed_columns} failed"
        f" ({overall_error_rate:.2f}% overall error rate)"
    )
    lines.append(f"Time: {exec_seconds:.2f}s")

    _safe_echo("\n".join(lines))


@click.command("schema")
@click.argument("source", required=True)
@click.option(
    "--rules",
    "rules_file",
    type=click.Path(exists=True, readable=True),
    required=True,
    help="Path to schema rules file (JSON)",
)
@click.option(
    "--output",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    show_default=True,
    help="Output format",
)
@click.option(
    "--fail-on-error",
    is_flag=True,
    default=False,
    help="Return exit code 1 if any error occurs during skeleton execution",
)
@click.option(
    "--max-errors",
    type=int,
    default=100,
    show_default=True,
    help="Maximum number of errors to collect (reserved; not used in skeleton)",
)
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output")
def schema_command(
    source: str,
    rules_file: str,
    output: str,
    fail_on_error: bool,
    max_errors: int,
    verbose: bool,
) -> None:
    """Schema validation command with minimal rules file validation.

    Decomposition and execution are added in subsequent tasks.
    """

    from cli.core.config import get_cli_config
    from core.config import get_core_config

    # start_time = now()
    try:
        _maybe_echo_analyzing(source, output)
        _guard_empty_source_file(source)

        source_config = SourceParser().parse_source(source)

        rules_payload = _read_rules_payload(rules_file)

        warnings, rules_count = _validate_rules_payload(rules_payload)
        _emit_warnings(warnings)

        # Decompose into atomic rules per design
        atomic_rules = _decompose_to_atomic_rules(rules_payload)

        # Fast-path: no rules → emit minimal payload and exit cleanly
        if len(atomic_rules) == 0:
            _early_exit_when_no_rules(
                source=source,
                rules_file=rules_file,
                output=output,
                fail_on_error=fail_on_error,
            )

        # Execute via core engine using DataValidator
        core_config = get_core_config()
        cli_config = get_cli_config()
        validator = _create_validator(
            source_config=source_config,
            atomic_rules=atomic_rules,
            core_config=core_config,
            cli_config=cli_config,
        )
        results, exec_seconds = _run_validation(validator)

        # Aggregation and prioritization
        schema_result_dict: Dict[str, Any] | None = _extract_schema_result_dict(
            atomic_rules=atomic_rules, results=results
        )
        skip_map = _compute_skip_map(
            atomic_rules=atomic_rules, schema_result_dict=schema_result_dict
        )

        # Apply skip map to JSON output only; table mode stays concise by design
        if output.lower() == "json":
            _emit_json_output(
                source=source,
                rules_file=rules_file,
                atomic_rules=atomic_rules,
                results=results,
                skip_map=skip_map,
                schema_result_dict=schema_result_dict,
                exec_seconds=exec_seconds,
            )
        else:
            _emit_table_output(
                source=source,
                atomic_rules=atomic_rules,
                results=results,
                skip_map=skip_map,
                schema_result_dict=schema_result_dict,
                exec_seconds=exec_seconds,
            )

        # Exit code: fail if any rule failed (support both model objects and dicts)
        def _status_of(item: Any) -> str:
            if hasattr(item, "status"):
                try:
                    return str(getattr(item, "status") or "").upper()
                except Exception:
                    return ""
            if isinstance(item, dict):
                return str(item.get("status", "") or "").upper()
            return ""

        any_failed = any(_status_of(r) == "FAILED" for r in results)
        import click as _click

        raise _click.exceptions.Exit(1 if any_failed or fail_on_error else 0)

    except click.UsageError:
        # Propagate Click usage errors for standard exit code (typically 2)
        raise
    except click.exceptions.Exit:
        # Allow Click's explicit Exit (with code) to propagate unchanged
        raise
    except Exception as e:  # Fallback: print concise error and return generic failure
        logger.error(f"Schema command error: {str(e)}")
        _safe_echo(f"❌ Error: {str(e)}", err=True)
        import click as _click

        raise _click.exceptions.Exit(1)
