from dataclasses import dataclass
from pathlib import Path
from functools import cmp_to_key

from icplot.geometry import Point
from icplot.mesh import Vertex, Mesh, get_hex_faces

from .foamfile import read_foamfile, FoamFile, write_header


@dataclass(frozen=True)
class Face:
    """
    A mesh face, which is a sequence of vertices
    """

    vertices: tuple[int, ...]
    id: int = -1
    owner: int = -1
    neighbour: int = -1

    def get_centre(self, mesh: Mesh) -> Point:
        x = sum(mesh.vertices[idx].x for idx in self.vertices)
        y = sum(mesh.vertices[idx].y for idx in self.vertices)
        z = sum(mesh.vertices[idx].z for idx in self.vertices)
        return Point(
            x / len(self.vertices), y / len(self.vertices), z / len(self.vertices)
        )


@dataclass(frozen=True)
class Cell:
    """
    A mesh cell, which is a squence of faces
    """

    faces: tuple[int, ...]
    id: int = -1


@dataclass(frozen=True)
class Polymesh:
    """
    The polymesh
    """

    vertices: tuple[Vertex, ...]
    faces: tuple[Face, ...]
    cells: tuple[Cell, ...]


@dataclass(frozen=True)
class PolymeshPatch:
    name: str
    faces: tuple[Face, ...]
    startFace: int
    type: str = "patch"

    def has_face(self, face: Face) -> bool:
        for f in self.faces:
            if f.id == face.id:
                return True
        return False


def read_polymesh(path: Path) -> Polymesh:

    points_file = read_foamfile(path / "points")
    # faces_file = read_foamfile(path / "faces")
    print(points_file)
    # print(faces_file)
    return Polymesh((), (), ())


def _write_points(vertices: tuple[Vertex, ...]) -> str:

    # Write file header
    header = FoamFile(
        location="constant/polyMesh", foam_object="points", foam_class="vectorField"
    )
    ret = write_header(header)

    ret += f"{len(vertices)}\n(\n"
    for v in vertices:
        ret += f"({v.x} {v.y} {v.z})\n"
    ret += ")\n"
    return ret


def _write_faces(internal_faces: tuple[Face, ...], patches: list[PolymeshPatch]) -> str:
    header = FoamFile(
        location="constant/polyMesh", foam_object="faces", foam_class="faceList"
    )
    ret = write_header(header)

    num_patch_faces = sum(len(p.faces) for p in patches)
    num_faces = len(internal_faces) + num_patch_faces

    ret += f"{num_faces}\n(\n"
    for f in internal_faces:
        verts = f.vertices
        ret += f"{len(verts)}({verts[0]} {verts[1]} {verts[2]} {verts[3]})\n"

    for p in patches:
        for f in p.faces:
            verts = f.vertices
            ret += f"{len(verts)}({verts[0]} {verts[1]} {verts[2]} {verts[3]})\n"
    ret += ")\n"
    return ret


def _write_owners(
    internal_faces: tuple[Face, ...], patches: list[PolymeshPatch]
) -> str:
    header = FoamFile(
        location="constant/polyMesh", foam_object="owner", foam_class="labelList"
    )
    ret = write_header(header)

    num_patch_faces = sum(len(p.faces) for p in patches)
    num_faces = len(internal_faces) + num_patch_faces

    ret += f"{num_faces}\n(\n"
    for f in internal_faces:
        ret += f"{f.owner}\n"
    for p in patches:
        for f in p.faces:
            ret += f"{f.owner}\n"
    ret += ")\n"
    return ret


def _write_neighbours(
    internal_faces: tuple[Face, ...], patches: list[PolymeshPatch]
) -> str:
    header = FoamFile(
        location="constant/polyMesh", foam_object="neighbour", foam_class="labelList"
    )
    ret = write_header(header)

    num_patch_faces = sum(len(p.faces) for p in patches)
    num_faces = len(internal_faces) + num_patch_faces

    ret += f"{num_faces}\n(\n"
    for f in internal_faces:
        ret += f"{f.neighbour}\n"
    for p in patches:
        for f in p.faces:
            ret += f"{f.neighbour}\n"
    ret += ")\n"
    return ret


"""
def _write_face_zones(zones: list[FaceZone]) -> str:

    header = FoamFile(
        location="constant/polyMesh",
        foam_object="faceZones",
        foam_class="regIOobject",
        meta={"names": tuple(zone.name for zone in zones)},
    )
    ret = write_header(header)

    ret += f"{len(zones)}\n( "
    for zone in zones:
        ret += f"{zone.name}\n{{"
        ret += "\ttype\tfaceZone;\n\tfaceLabels\tList<label>\n"
        ret += f"{len(zone.faces)}\n("
        for face in zone.faces:
            ret += f"{face}\n"
        ret += ");\n"
        ret += "\tflipMap\tList<bool>\n"
        ret += f"{len(zone.faces)}\n("
        for face in zone.faces:
            ret += "0\n"
        ret += ");\n"
        ret += "}\n\n"
    ret += ")"
    return ret
"""


def _write_boundaries(patches: list[PolymeshPatch]):

    header = FoamFile(
        location="constant/polyMesh",
        foam_object="boundary",
        foam_class="polyBoundaryMesh",
    )
    ret = write_header(header)

    ret += f"{len(patches)}(\n"
    for p in patches:
        ret += f"{p.name}\n{{"
        ret += f"\ttype\t{p.type};\n"
        ret += f"\tnFaces\t{len(p.faces)};\n"
        ret += f"\tstartFace\t{p.startFace};\n"
        ret += "}\n\n"
    ret += ")"
    return ret


def _faces_equal(f0, f1):
    return set(f0) == set(f1)


def _compare_faces(f0: Face, f1: Face):
    if f0.owner == f1.owner:
        if f0.neighbour == f1.neighbour:
            return 0
        elif f0.neighbour > f1.neighbour:
            return 1
        else:
            return -1
    else:
        if f0.owner > f1.owner:
            return 1
        else:
            return -1


def _build_faces(mesh: Mesh) -> list[Face]:
    faces: list[Face] = []

    count = 0
    for idx, cell in enumerate(mesh.cells):
        hex_faces = get_hex_faces(cell)
        for hex_face in hex_faces:
            found = False
            for face in faces:
                if _faces_equal(hex_face, face.vertices):
                    if idx < face.owner:
                        faces[face.id] = Face(
                            vertices=tuple(list(reversed(face.vertices))),
                            owner=idx,
                            id=face.id,
                            neighbour=face.owner,
                        )
                    else:
                        faces[face.id] = Face(
                            vertices=face.vertices,
                            owner=face.owner,
                            id=face.id,
                            neighbour=idx,
                        )
                    found = True
                    break
            if not found:
                faces.append(Face(id=count, vertices=hex_face, owner=idx, neighbour=-1))
                count += 1

    faces.sort(key=cmp_to_key(_compare_faces))
    return faces


def _get_external_faces(faces: tuple[Face, ...]) -> tuple[Face, ...]:
    return tuple(f for f in faces if f.neighbour == -1)


def _get_internal_faces(faces: tuple[Face, ...]) -> tuple[Face, ...]:
    return tuple(f for f in faces if f.neighbour != -1)


def write_polymesh(path: Path, mesh: Mesh, patch_funcs: dict):

    # Write points
    with open(path / "points", "w", encoding="utf-8") as f:
        f.write(_write_points(mesh.vertices))

    # Prepare faces, owners and neighbours
    faces = _build_faces(mesh)

    internal_faces = _get_internal_faces(tuple(faces))
    external_faces = _get_external_faces(tuple(faces))

    # Get patches
    count = len(internal_faces)
    patches = []
    for name, func in patch_funcs.items():
        patch_faces = tuple(f for f in external_faces if func(f.get_centre(mesh)))
        patches.append(PolymeshPatch(name=name, faces=patch_faces, startFace=count))
        count += len(patch_faces)

    # Add a default wall patch
    wall_faces = []
    for face in external_faces:
        found = False
        for patch in patches:
            if patch.has_face(face):
                found = True
                break
        if not found:
            wall_faces.append(face)
    patches.append(
        PolymeshPatch(
            name="wall",
            type="wall",
            faces=tuple(f for f in wall_faces),
            startFace=count,
        )
    )

    with open(path / "faces", "w", encoding="utf-8") as f:
        f.write(_write_faces(internal_faces, patches))

    with open(path / "owner", "w", encoding="utf-8") as f:
        f.write(_write_owners(internal_faces, patches))

    with open(path / "neighbour", "w", encoding="utf-8") as f:
        f.write(_write_neighbours(internal_faces, patches))

    # Write boundaries
    with open(path / "boundary", "w", encoding="utf-8") as f:
        f.write(_write_boundaries(patches))
