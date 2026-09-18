"""Reference and documentation audits for the local lookup-table cleanup."""

import ast
import itertools
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "rubikscubennnsolver"
LOOKUP_DIR = ROOT / "lookup-tables"
SOLVER_MODULES = tuple(PACKAGE / f"RubiksCube{size}.py" for size in (555, 666, 777))
LOOKUP_NAME = re.compile(r"lookup-table-[A-Za-z0-9_.+-]+")
STICKER_LINE = re.compile(r"^\s*(?:[.xULFRBD-]\s+){2,}[.xULFRBD-]\s*$")
ARTIFACT_SUFFIXES = (".bin", ".json", ".txt", ".state_index")


class _Unknown:
    pass


UNKNOWN = _Unknown()


def _assign(target, value, env):
    if isinstance(target, ast.Name):
        env[target.id] = value
    elif isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, (tuple, list)):
        for child, item in zip(target.elts, value):
            _assign(child, item, env)


def _truth(value):
    return value is not UNKNOWN and bool(value)


def _eval(node, env):
    """Evaluate the small, side-effect-free expression subset used by filename specs."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id, UNKNOWN)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        values = [_eval(item, env) for item in node.elts]
        if UNKNOWN in values:
            return UNKNOWN
        constructor = tuple if isinstance(node, ast.Tuple) else list if isinstance(node, ast.List) else set
        return constructor(values)
    if isinstance(node, ast.Dict):
        keys = [_eval(item, env) for item in node.keys]
        values = [_eval(item, env) for item in node.values]
        return UNKNOWN if UNKNOWN in keys + values else dict(zip(keys, values))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _eval(node.left, env), _eval(node.right, env)
        if left is UNKNOWN or right is UNKNOWN:
            return UNKNOWN
        try:
            return left + right
        except TypeError:
            return UNKNOWN
    if isinstance(node, ast.JoinedStr):
        result = []
        for part in node.values:
            if isinstance(part, ast.Constant):
                result.append(str(part.value))
            elif isinstance(part, ast.FormattedValue):
                value = _eval(part.value, env)
                if value is UNKNOWN:
                    return UNKNOWN
                result.append(str(value))
            else:
                return UNKNOWN
        return "".join(result)
    if isinstance(node, ast.Subscript):
        value, key = _eval(node.value, env), _eval(node.slice, env)
        if value is UNKNOWN or key is UNKNOWN:
            return UNKNOWN
        try:
            return value[key]
        except (KeyError, IndexError, TypeError):
            return UNKNOWN
    if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators) == 1:
        left, right = _eval(node.left, env), _eval(node.comparators[0], env)
        if left is UNKNOWN or right is UNKNOWN:
            return UNKNOWN
        op = node.ops[0]
        if isinstance(op, ast.In):
            return left in right
        if isinstance(op, ast.NotIn):
            return left not in right
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right
        return UNKNOWN
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in {"tuple", "list", "set", "frozenset"}:
            value = _eval(node.args[0], env) if node.args else ()
            if value is UNKNOWN:
                return UNKNOWN
            return {"tuple": tuple, "list": list, "set": set, "frozenset": frozenset}[node.func.id](value)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in {"lower", "upper"}
            and not node.args
            and not node.keywords
        ):
            value = _eval(node.func.value, env)
            return getattr(value, node.func.attr)() if isinstance(value, str) else UNKNOWN
        return UNKNOWN
    if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
        results = []

        def visit_generator(index, local_env):
            if index == len(node.generators):
                results.append(_eval(node.elt, local_env))
                return
            generator = node.generators[index]
            values = _eval(generator.iter, local_env)
            if values is UNKNOWN:
                results.append(UNKNOWN)
                return
            for value in values:
                child_env = dict(local_env)
                _assign(generator.target, value, child_env)
                if all(_truth(_eval(condition, child_env)) for condition in generator.ifs):
                    visit_generator(index + 1, child_env)

        visit_generator(0, dict(env))
        if UNKNOWN in results:
            return UNKNOWN
        if isinstance(node, ast.GeneratorExp):
            return iter(results)
        return results if isinstance(node, ast.ListComp) else set(results)
    return UNKNOWN


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in itertools.chain(value.keys(), value.values()):
            yield from _strings(item)
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            yield from _strings(item)


def _python_lookup_references(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    env = {}
    references = set()
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            value = _eval(statement.value, env)
            for target in statement.targets:
                _assign(target, value, env)
            references.update(_strings(value))
        elif isinstance(statement, ast.AnnAssign):
            value = _eval(statement.value, env)
            _assign(statement.target, value, env)
            references.update(_strings(value))

    # Literal defaults and class-local filenames are references too.
    references.update(
        node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)
    )
    return {
        Path(match.group(0)).name
        for value in references
        for match in LOOKUP_NAME.finditer(value)
        if match.group(0).endswith(ARTIFACT_SUFFIXES)
    }


def _c_lookup_references(path):
    text = path.read_text(encoding="utf-8")
    return {
        Path(match.group(0)).name for match in LOOKUP_NAME.finditer(text) if match.group(0).endswith(ARTIFACT_SUFFIXES)
    }


def _production_artifact_basenames():
    referenced = set()
    for path in PACKAGE.glob("*.py"):
        referenced.update(_python_lookup_references(path))
    for path in itertools.chain(PACKAGE.glob("*.c"), PACKAGE.glob("*.h")):
        referenced.update(_c_lookup_references(path))

    # Ranked builders emit metadata beside a cost file. Metadata is valid only
    # for a production-referenced binary; arbitrary orphan JSON remains rejected.
    sidecars = {f"{name}.json" for name in referenced if name.endswith(".bin")}
    return referenced | sidecars


def _is_allowed_local_artifact(name, allowed):
    return name in allowed


def test_local_lookup_artifacts_are_all_referenced_by_production():
    allowed = _production_artifact_basenames()
    local = {path.name for path in LOOKUP_DIR.iterdir() if path.is_file()}
    obsolete = sorted(local - allowed)
    assert not obsolete, "obsolete or orphan lookup-table artifacts returned:\n" + "\n".join(obsolete)

    orphan_sidecars = sorted(
        name for name in local if name.endswith(".bin.json") and name[: -len(".json")] not in local
    )
    assert not orphan_sidecars, "lookup-table metadata has no local binary:\n" + "\n".join(orphan_sidecars)


def test_live_777_leave_one_out_fallback_set_is_preserved():
    expected = {
        f"lookup-table-7x7x7-daisy-{axis}-without-{orbit}-centers.cost-only.bin"
        for axis in ("UD", "LR", "FB")
        for orbit in ("left-oblique", "middle-oblique", "right-oblique", "inner-t", "inner-x")
    }
    allowed = _production_artifact_basenames()
    local = {path.name for path in LOOKUP_DIR.iterdir() if path.is_file()}
    assert expected <= allowed
    assert expected <= local


def test_symmetry_indexes_and_required_metadata_are_allowed():
    allowed = _production_artifact_basenames()
    required_indexes = {
        "lookup-table-4x4x4-step12-all-centers-stage-symmetry.cost-only.bin.symmetry-index.bin",
        "lookup-table-7x7x7-daisy-perfect-centers.cost-only.bin.symmetry-index.bin",
        "lookup-table-7x7x7-solve-perfect-centers.cost-only.bin.symmetry-index.bin",
    }
    assert required_indexes <= allowed
    for path in LOOKUP_DIR.glob("*.bin.json"):
        assert path.name in allowed


@pytest.mark.parametrize(
    "obsolete",
    (
        "lookup-table-5x5x5-old.bin",
        "lookup-table-5x5x5-old.state_index",
        "lookup-table-5x5x5-old.txt",
        "lookup-table-7x7x7-perfect-hash.bin",
        "lookup-table-6x6x6-orphan.cost-only.bin.json",
    ),
)
def test_classic_obsolete_artifact_names_are_rejected(obsolete):
    assert not _is_allowed_local_artifact(obsolete, _production_artifact_basenames())


def _class_artifact_references(node, module_env):
    names = set()
    for item in ast.walk(node):
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            names.update(match.group(0) for match in LOOKUP_NAME.finditer(item.value))
        elif isinstance(item, ast.Name):
            names.update(
                match.group(0)
                for value in _strings(module_env.get(item.id, UNKNOWN))
                for match in LOOKUP_NAME.finditer(value)
            )
    return {Path(name).name for name in names if name.endswith(".bin")}


def _module_env(tree):
    env = {}
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            value = _eval(statement.value, env)
            for target in statement.targets:
                _assign(target, value, env)
    return env


def _assigns_self_filename(node):
    return any(
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "self"
        and target.attr == "filename"
        for assignment in ast.walk(node)
        if isinstance(assignment, (ast.Assign, ast.AnnAssign))
        for target in (assignment.targets if isinstance(assignment, ast.Assign) else (assignment.target,))
    )


def _passes_filename_to_table_base(node):
    return any(
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "__init__"
        and any(
            (isinstance(arg, ast.Constant) and isinstance(arg.value, str) and "lookup-table-" in arg.value)
            or (isinstance(arg, ast.Name) and "TABLE" in arg.id)
            for arg in call.args
        )
        for call in ast.walk(node)
        if isinstance(call, ast.Call)
    )


def _has_diagram(doc):
    return sum(bool(STICKER_LINE.match(line)) for line in doc.splitlines()) >= 3


def _documentation_cases():
    one_table = []
    wrappers = []
    for path in SOLVER_MODULES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        env = _module_env(tree)
        for node in (item for item in tree.body if isinstance(item, ast.ClassDef)):
            refs = _class_artifact_references(node, env)
            if (
                not node.name.startswith("LookupTableIDA")
                and len(refs) == 1
                and (_assigns_self_filename(node) or _passes_filename_to_table_base(node))
            ):
                one_table.append(pytest.param(path, node, id=f"{path.stem}.{node.name}"))
            elif (
                refs
                and node.name.startswith("LookupTableIDA")
                and any(
                    isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and "solve" in item.name
                    for item in node.body
                )
            ):
                wrappers.append(pytest.param(path, node, id=f"{path.stem}.{node.name}"))
    return tuple(one_table), tuple(wrappers)


ONE_TABLE_CASES, WRAPPER_CASES = _documentation_cases()


@pytest.mark.parametrize("path,node", ONE_TABLE_CASES)
def test_concrete_one_table_classes_document_their_coordinate(path, node):
    doc = ast.get_docstring(node, clean=True) or ""
    assert _has_diagram(doc), (
        f"{path.name}:{node.lineno} {node.name} must document its one-table coordinate " "with a cube diagram"
    )


@pytest.mark.parametrize("path,node", WRAPPER_CASES)
def test_ida_wrappers_document_components_and_heuristic(path, node):
    doc = (ast.get_docstring(node, clean=True) or "").lower()
    missing = []
    if "table" not in doc:
        missing.append("table components")
    if not re.search(r"\b(?:heuristic|cost|prune)\w*\b", doc):
        missing.append("heuristic/cost combination")
    assert not missing, f"{path.name}:{node.lineno} {node.name} docstring is missing " + " and ".join(missing)
