import pytest
from biotite.structure.io import pdbx

from atomworks.io.parser import parse
from atomworks.io.utils import io_utils
from atomworks.io.utils.testing import assert_same_atom_array
from tests.io.conftest import get_pdb_path

MULTIPLE_ASSEMBLY_TEST_CASES = [
    {"pdbid": "1a7j", "n_assemblies": 3},
    {"pdbid": "5vos", "n_assemblies": 1},
]

ASSEMBLY_ATOM_COORDINATES_TEST_CASES = ["1A8O", "1RXZ", "4NDZ", "5XNL", "6DMG", "2E2H"]


@pytest.mark.parametrize("test_case", MULTIPLE_ASSEMBLY_TEST_CASES)
def test_assembly_counts(test_case: dict):
    # unpack test case
    pdbid = test_case["pdbid"]
    n_assemblies = test_case["n_assemblies"]

    # parse the file
    filename = get_pdb_path(pdbid)

    # test the different build_assembly options
    out_no_assembly = parse(filename=filename, build_assembly=None, remove_ccds=[])
    assert len(out_no_assembly["assemblies"]) == 0

    out_first = parse(filename=filename, build_assembly="first", remove_ccds=[])
    assert len(out_first["assemblies"]) == 1

    out_all = parse(filename=filename, build_assembly="all", remove_ccds=[])
    assert len(out_all["assemblies"]) == n_assemblies


@pytest.mark.parametrize("pdb_id", ASSEMBLY_ATOM_COORDINATES_TEST_CASES)
def test_assembly_atom_coordinates(pdb_id: str):
    path = get_pdb_path(pdb_id)

    # Biotite
    file = io_utils.read_any(path)
    biotite_assembly = pdbx.get_assembly(
        file,
        assembly_id="1",
        use_author_fields=False,
        altloc="first",
        extra_fields=[
            "atom_id",
            "occupancy",
        ],
        model=1,
    )
    resolved_biotite_assembly = biotite_assembly[(biotite_assembly.occupancy > 0) & (biotite_assembly.element != "H")]

    assembly = parse(
        filename=path,
        build_assembly="first",
        fix_arginines=False,
        remove_waters=False,
        hydrogen_policy="remove",
        remove_ccds=[],  # Do not remove crystallization solvents
        ccd_mirror_path=None,  # Use Biotite's CCD mirror
    )["assemblies"]["1"][0]
    resolved_assembly = assembly[assembly.occupancy > 0]

    assert_same_atom_array(
        resolved_biotite_assembly,
        resolved_assembly,
        annotations_to_compare=["chain_id", "res_name", "atom_name"],
        compare_bonds=False,
        # NOTE: We do not compare res_id as waters don't match in the res_id and elements as we turn elements into integers
    )
