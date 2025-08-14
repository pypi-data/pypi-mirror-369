from iccore.test_utils import get_test_output_dir

from icplot.geometry import Quad, Annulus, Circle, Cylinder
from icplot.mesh import (
    vtk,
    mesh_rectangle,
    mesh_annulus,
    mesh_circle,
    mesh_extrude,
    mesh_cylinder_basic,
    mesh_compound_cylinder,
)


def test_mesh_rectangle():

    output_dir = get_test_output_dir()

    rect = Quad(width=5.0, height=5.0)
    mesh = mesh_rectangle(rect, 5, 5)

    vtk.write_unstructured_grid(mesh, output_dir / "rectangle.vtk")


def test_annulus():

    output_dir = get_test_output_dir()

    shape = Annulus(outer_radius=1.0, inner_radius=0.5, angle=360)
    mesh = mesh_annulus(shape, 2, 8)

    vtk.write_unstructured_grid(mesh, output_dir / "annulus.vtk")
    vtk.write_unstructured_grid(
        mesh_extrude(mesh, 5, 5), output_dir / "annulus_extruded.vtk"
    )


def test_circle():

    output_dir = get_test_output_dir()

    shape = Circle(radius=1.0)
    mesh = mesh_circle(shape, 0.7, 4, 24)

    vtk.write_unstructured_grid(mesh, output_dir / "circle.vtk")


def test_extrude():

    output_dir = get_test_output_dir()

    rect = Quad(width=5.0, height=5.0)
    mesh = mesh_rectangle(rect, 5, 5)

    extruded_mesh = mesh_extrude(mesh, 5, 5)

    vtk.write_unstructured_grid(extruded_mesh, output_dir / "extrude.vtk")


def test_cylinder():

    output_dir = get_test_output_dir()

    shape = Cylinder(diameter=2.0, length=5.0)
    mesh = mesh_cylinder_basic(shape, 0.5, 2, 16, 5)

    vtk.write_unstructured_grid(mesh, output_dir / "cylinder.vtk")


def xtest_compound_cylinder():

    output_dir = get_test_output_dir()

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
