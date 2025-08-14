from pathlib import Path
import shutil

from icplot.mesh.openfoam import polymesh
from icplot.mesh import (
    mesh_cylinder_basic,
    mesh_compound_cylinder,
    mesh_rectangle,
    mesh_extrude,
    vtk,
)
from icplot.geometry import Cylinder, Point, Quad

from iccore.test_utils import get_test_data_dir, get_test_output_dir


def xtest_read_polymesh():

    data_dir = get_test_data_dir()

    mesh = polymesh.read_polymesh(data_dir / "openfoam/polymesh/basic")
    print(mesh)


def inlet_func(face_centre: Point):
    return face_centre.z == 0.0


def outlet_func(face_centre: Point):
    return face_centre.z == 5.0


def test_polymesh_cube():

    output_dir = get_test_output_dir()
    polymesh_dir = output_dir / "constant/polyMesh"
    polymesh_dir.mkdir(parents=True, exist_ok=True)

    system_dir = output_dir / "system"
    system_dir.mkdir(parents=True, exist_ok=True)

    control_path = Path(__file__).parent.parent / "src/icplot/mesh/openfoam/controlDict"
    shutil.copy(control_path, system_dir)

    shape = Quad(width=1.0, height=1.0)
    mesh = mesh_rectangle(shape, 2, 2)
    mesh = mesh_extrude(mesh, 5.0, 2)

    vtk.write_unstructured_grid(mesh, output_dir / "cube.vtk")

    polymesh.write_polymesh(
        polymesh_dir, mesh, {"inlet": inlet_func, "outlet": outlet_func}
    )


def test_polymesh_cylinder():

    output_dir = get_test_output_dir()
    polymesh_dir = output_dir / "constant/polyMesh"
    polymesh_dir.mkdir(parents=True, exist_ok=True)

    system_dir = output_dir / "system"
    system_dir.mkdir(parents=True, exist_ok=True)

    control_path = Path(__file__).parent.parent / "src/icplot/mesh/openfoam/controlDict"
    shutil.copy(control_path, system_dir)

    shape = Cylinder(diameter=2.0, length=5.0)
    mesh = mesh_cylinder_basic(shape, 0.5, 2, 8, 2)

    vtk.write_unstructured_grid(mesh, output_dir / "cylinder.vtk")

    polymesh.write_polymesh(
        polymesh_dir, mesh, {"inlet": inlet_func, "outlet": outlet_func}
    )


def compound_inlet_func(face_centre: Point):
    return face_centre.z == 0.0


def compound_outlet_func(face_centre: Point):
    return face_centre.z == 7.0


def xtest_polymesh_compound_cylinder():

    output_dir = get_test_output_dir()
    polymesh_dir = output_dir / "constant/polyMesh"
    polymesh_dir.mkdir(parents=True, exist_ok=True)

    system_dir = output_dir / "system"
    system_dir.mkdir(parents=True, exist_ok=True)

    control_path = Path(__file__).parent.parent / "src/icplot/mesh/openfoam/controlDict"
    shutil.copy(control_path, system_dir)

    inlet_radius = 0.5
    inlet_height = 1.0
    radius = 2.0
    height = 5.0
    boundary_fraction = 0.5
    num_circumferential = 16
    num_radial = 4
    num_height = 4

    mesh = mesh_compound_cylinder(
        inlet_radius,
        inlet_height,
        radius,
        height,
        boundary_fraction,
        num_circumferential,
        num_radial,
        num_height,
    )

    vtk.write_unstructured_grid(mesh, output_dir / "compound_cylinder.vtk")

    polymesh.write_polymesh(
        polymesh_dir,
        mesh,
        {"inlet": compound_inlet_func, "outlet": compound_outlet_func},
    )
