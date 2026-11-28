"""A missing lookup table tells the caller which make target builds it."""

# standard libraries
import pytest

# rubiks cube libraries
from rubikscubennnsolver.LookupTable import download_file_if_needed


def test_existing_table_is_kept(tmp_path):
    table = tmp_path / "lookup-table-4x4x4-already-there.cost-only.bin"
    table.write_bytes(b"kept")
    download_file_if_needed(str(table))
    assert table.read_bytes() == b"kept"


def test_missing_table_exits_with_make_target(tmp_path, capsys):
    table = tmp_path / "lookup-table-4x4x4-missing.cost-only.bin"
    with pytest.raises(SystemExit) as caught:
        download_file_if_needed(str(table))
    assert caught.value.code == 1
    error = capsys.readouterr().err
    assert "lookup-table-4x4x4-missing.cost-only.bin" in error
    assert "make 444-tables" in error


def test_missing_table_target_follows_cube_size(tmp_path, capsys):
    table = tmp_path / "lookup-table-7x7x7-phase9-ud-axis-centers.cost-only.bin"
    with pytest.raises(SystemExit) as caught:
        download_file_if_needed(str(table))
    assert caught.value.code == 1
    assert "make 777-tables" in capsys.readouterr().err


def test_missing_joint_table_names_its_own_target(tmp_path, capsys):
    table = tmp_path / "lookup-table-5x5x5-step13-LR-t-x-centers-joint.sym-nibble.bin"
    with pytest.raises(SystemExit) as caught:
        download_file_if_needed(str(table))
    assert caught.value.code == 1
    error = capsys.readouterr().err
    assert "make 555-lr-joint" in error
    assert "make 555-tables" not in error
