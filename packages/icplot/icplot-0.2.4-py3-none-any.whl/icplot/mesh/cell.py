from dataclasses import dataclass


@dataclass(frozen=True)
class Cell:
    """
    A mesh cell
    """

    vertices: tuple[int, ...]
    type: str = ""

    def get_edges(self) -> tuple:
        raise NotImplementedError()


def flip_normals(cell: Cell) -> Cell:
    if cell.type == "quad":
        return Cell(type=cell.type, vertices=tuple(reversed(cell.vertices)))
    else:
        raise RuntimeError("Not implemented for this cell type")


def get_hex_faces(cell: Cell) -> tuple[tuple[int, ...], ...]:
    if cell.type != "hex":
        raise RuntimeError("Can only get hex faces for hex cells")

    return (
        (cell.vertices[0], cell.vertices[1], cell.vertices[5], cell.vertices[4]),
        (cell.vertices[1], cell.vertices[2], cell.vertices[6], cell.vertices[5]),
        (cell.vertices[2], cell.vertices[3], cell.vertices[7], cell.vertices[6]),
        (cell.vertices[3], cell.vertices[0], cell.vertices[4], cell.vertices[7]),
        (cell.vertices[0], cell.vertices[3], cell.vertices[2], cell.vertices[1]),
        (cell.vertices[4], cell.vertices[5], cell.vertices[6], cell.vertices[7]),
    )


@dataclass(frozen=True)
class HexCell(Cell):
    """
    A hex mesh element - used in openfoam meshing
    """

    cell_counts: tuple[int, ...] = (1, 1, 1)
    grading: str = "simpleGrading"
    grading_ratios: tuple[int, ...] = (1, 1, 1)
    type = "hex"

    def get_top_edges(self) -> tuple:
        return (
            (self.vertices[0], self.vertices[1]),
            (self.vertices[1], self.vertices[2]),
            (self.vertices[2], self.vertices[3]),
            (self.vertices[3], self.vertices[0]),
        )

    def get_bottom_edges(self) -> tuple:
        return (
            (self.vertices[4], self.vertices[5]),
            (self.vertices[5], self.vertices[6]),
            (self.vertices[6], self.vertices[7]),
            (self.vertices[7], self.vertices[4]),
        )

    def get_side_edges(self) -> tuple:
        return (
            (self.vertices[0], self.vertices[4]),
            (self.vertices[1], self.vertices[5]),
            (self.vertices[2], self.vertices[6]),
            (self.vertices[3], self.vertices[7]),
        )

    def get_edges(self) -> tuple:
        return self.get_bottom_edges() + self.get_top_edges() + self.get_side_edges()
