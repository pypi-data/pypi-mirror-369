import numpy as np

from icplot.geometry import (
    Point,
    Quad,
    Annulus,
    Transform,
    Circle,
    Cuboid,
    Vector,
    Cylinder,
)

from .mesh import Mesh
from .vertex import Vertex, find_closest
from .cell import Cell, HexCell

from .operations import map_radial, close_mesh, merge_meshes, mesh_extrude


def mesh_rectangle(rect: Quad, num_width: int = 10, num_height: int = 10) -> Mesh:

    # Generate verts
    verts: list[Vertex] = []

    delta_w = rect.width / float(num_width)
    delta_h = rect.height / float(num_height)
    count = 0
    for idx in range(num_height + 1):
        for jdx in range(num_width + 1):
            verts.append(
                Vertex(x=float(jdx) * delta_w, y=float(idx) * delta_h, id=count)
            )
            count += 1

    # Generate cells
    cells: list[Cell] = []
    for idx in range(num_height):
        for jdx in range(num_width):
            v0 = jdx + (num_width + 1) * idx
            v1 = v0 + 1
            v2 = jdx + (num_width + 1) * (idx + 1) + 1
            v3 = v2 - 1

            cells.append(Cell(type="quad", vertices=(v0, v1, v2, v3)))

    return Mesh(vertices=tuple(verts), cells=tuple(cells)).apply_transform(
        rect.transform
    )


def mesh_annulus(
    annulus: Annulus, num_radial: int = 2, num_circumferential: int = 8
) -> Mesh:

    angle_rad = annulus.angle * np.pi / 180

    rect_mesh = mesh_rectangle(
        Quad(
            width=angle_rad * annulus.outer_radius,
            height=annulus.outer_radius - annulus.inner_radius,
            transform=Transform(location=Point(0.0, annulus.inner_radius)),
        ),
        num_width=num_circumferential,
        num_height=num_radial,
    )
    radial_mesh = map_radial(rect_mesh, annulus.angle).flip_normals()

    if annulus.angle == 360:
        return close_mesh(radial_mesh)
    return radial_mesh


def _rotate_list(lst, n):
    return lst[n:] + lst[:n]


def _close_circle(inner_mesh: Mesh, outer_mesh: Mesh, num_circumferential: int) -> Mesh:

    num_side = int(num_circumferential / 4)
    inner_verts = []

    # Base
    for idx in range(num_side + 1):
        inner_verts.append(idx)

    # RHS
    for idx in range(1, num_side + 1):
        inner_verts.append((idx + 1) * (num_side + 1) - 1)

    # Top
    for idx in range(2, num_side + 2):
        inner_verts.append((num_side + 1) * (num_side + 1) - idx)

    # Left
    for idx in range(2, num_side + 1):
        inner_verts.append((num_side + 1) * (num_side + 1 - idx))

    inner_verts = _rotate_list(inner_verts, num_side + 1 + int((num_side + 1) / 2) - 1)

    new_nodes = []
    new_cells = []
    count = 0
    for idx in range(num_circumferential):

        next_id = idx + 1
        if next_id == num_circumferential:
            next_id = 0

        outer_next = outer_mesh.vertices[next_id]
        nearest_next = inner_mesh.vertices[inner_verts[next_id]]

        if idx == 0:
            outer = outer_mesh.vertices[idx]
            nearest = inner_mesh.vertices[inner_verts[idx]]

            new_nodes.append(Vertex(x=nearest.x, y=nearest.y, z=nearest.z, id=count))
            new_nodes.append(Vertex(x=outer.x, y=outer.y, z=outer.z, id=count + 1))
            count += 2

        new_nodes.append(
            Vertex(x=nearest_next.x, y=nearest_next.y, z=nearest_next.z, id=count)
        )
        new_nodes.append(
            Vertex(x=outer_next.x, y=outer_next.y, z=outer_next.z, id=count + 1)
        )
        count += 2
        new_cells.append(
            Cell(type="quad", vertices=(count - 2, count - 4, count - 3, count - 1))
        )

    # Create mesh interface layer
    mesh_interface = Mesh(cells=tuple(new_cells), vertices=tuple(new_nodes))
    mesh_interface = close_mesh(mesh_interface)

    # Merge mesh interface layer
    inner_merged = merge_meshes(inner_mesh, mesh_interface)
    return merge_meshes(inner_merged, outer_mesh)


def mesh_circle(
    circle: Circle,
    boundary_frac: float = 0.5,
    num_radial: int = 2,
    num_circumferential: int = 8,
) -> Mesh:

    annulus_mesh = mesh_annulus(
        Annulus(outer_radius=circle.radius, inner_radius=circle.radius * boundary_frac),
        num_radial=num_radial,
        num_circumferential=num_circumferential,
    )

    inner_radius = circle.radius * boundary_frac
    inner_mesh = mesh_rectangle(
        Quad(
            width=inner_radius,
            height=inner_radius,
            transform=Transform(
                location=Point(-inner_radius / 2.0, -inner_radius / 2.0)
            ),
        ),
        num_width=int(num_circumferential / 4),
        num_height=int(num_circumferential / 4),
    )

    return _close_circle(inner_mesh, annulus_mesh, num_circumferential)


def mesh_cylinder_basic(
    cylinder: Cylinder,
    boundary_frac: float = 0.5,
    num_radial: int = 2,
    num_circumferential: int = 8,
    num_height=5,
) -> Mesh:

    return mesh_extrude(
        mesh_circle(
            Circle(radius=cylinder.diameter / 2),
            boundary_frac,
            num_radial,
            num_circumferential,
        ),
        cylinder.length,
        num_height,
    )


def mesh_compound_cylinder(
    inlet_radius,
    inlet_height,
    radius,
    height,
    boundary_fraction,
    num_circumferential,
    num_radial,
    num_height,
) -> Mesh:

    inner = mesh_cylinder_basic(
        Cylinder(diameter=inlet_radius * 2, length=2 * inlet_height + height),
        boundary_fraction,
        num_radial,
        num_circumferential,
        num_height * int(height / inlet_height) + 2 * num_height,
    )

    main_body = mesh_annulus(
        Annulus(outer_radius=radius, inner_radius=inlet_radius),
        num_radial=num_radial,
        num_circumferential=num_circumferential,
    )
    main_body = mesh_extrude(
        main_body, height, num_cells=num_height * int(height / inlet_height)
    )

    main_body = main_body.move_by(0.0, 0.0, inlet_height)
    return merge_meshes(main_body, inner)


def mesh_cuboid(cuboid: Cuboid, elements_per_dim: int = 5) -> Mesh:

    verts = tuple(Vertex.from_point(p) for p in cuboid.points)

    cell_counts = (elements_per_dim, elements_per_dim, elements_per_dim)
    cells = (HexCell(vertices=tuple(range(len(verts))), cell_counts=cell_counts),)
    return Mesh(verts, cells)


def mesh_cuboids(
    cuboids: list[Cuboid], elements_per_dim: int = 5, merge_tolerance: float = 1.0e-4
) -> Mesh:

    verts: list = []
    block_vert_ids: list = []
    for cuboid in cuboids:
        vert_ids = []
        for p in cuboid.points:

            if not verts:
                verts.append(Vertex.from_point(p, 0))
                vert_ids.append(0)
                continue

            nearest_id = find_closest(verts, p)
            if verts[nearest_id].get_distance(p) <= merge_tolerance:
                vert_ids.append(nearest_id)
            else:
                end_id = len(verts)
                verts.append(Vertex.from_point(p, end_id))
                vert_ids.append(end_id)
        block_vert_ids.append(vert_ids)

    cell_counts = (elements_per_dim, elements_per_dim, elements_per_dim)
    cells = tuple(HexCell(tuple(b), cell_counts=cell_counts) for b in block_vert_ids)
    return Mesh(vertices=tuple(verts), cells=cells)


def mesh_cylinder(cylinder: Cylinder, boundary_frac: float = 0.66) -> Mesh:

    inner_cube_side = cylinder.diameter * boundary_frac / np.sqrt(2)
    outer_cube_x = cylinder.diameter / np.sqrt(2)
    outer_cube_z = cylinder.diameter * (1.0 - boundary_frac) / (2.0 * np.sqrt(2))

    cuboids = [
        Cuboid(
            Transform(Point(0.0, 0.0, -inner_cube_side / 2.0 - outer_cube_z / 2.0)),
            width=outer_cube_x,
            height=cylinder.length,
            depth=outer_cube_z,
            top_width_scale=boundary_frac,
        ),
        Cuboid(
            Transform(
                Point(0.0, 0.0, inner_cube_side / 2.0 + outer_cube_z / 2.0),
                normal=Vector(0.0, 0.0, -1.0),
            ),
            width=outer_cube_x,
            height=cylinder.length,
            depth=outer_cube_z,
            top_width_scale=boundary_frac,
        ),
        Cuboid(
            Transform(
                Point(-outer_cube_x / 2.0, 0.0, 0.0), normal=Vector(-1.0, 0.0, 0.0)
            ),
            width=outer_cube_x,
            height=cylinder.length,
            depth=outer_cube_z,
            top_width_scale=boundary_frac,
        ),
        Cuboid(
            Transform(
                Point(outer_cube_x / 2.0, 0.0, 0.0), normal=Vector(-1.0, 0.0, 0.0)
            ),
            width=outer_cube_x,
            height=cylinder.length,
            depth=outer_cube_z,
            top_width_scale=boundary_frac,
        ),
        Cuboid(
            Transform(Point(0.0, 0.0, 0.0)),
            width=inner_cube_side,
            height=cylinder.length,
            depth=inner_cube_side,
        ),
    ]

    mesh = mesh_cuboids(cuboids)

    """
    top_front_edge = mesh.get_closest_edge(
        Point(0.0, -cylinder.length / 2.0, cylinder.diameter + depth / 2.0)
    )
    top_front_arc = Point(
        0.0, -cylinder.length / 2.0, cylinder.diameter + depth / 2.0 + 0.15
    )

    # edges = (Edge(top_front_edge[0], top_front_edge[1], "arc", (top_front_arc,)),)
    """

    return Mesh(mesh.vertices, mesh.cells)
