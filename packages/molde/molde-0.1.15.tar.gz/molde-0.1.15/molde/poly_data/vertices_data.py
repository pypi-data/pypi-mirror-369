from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import VTK_VERTEX, vtkPolyData


class VerticesData(vtkPolyData):
    """
    This class describes a polydata composed by a set of points.
    """

    def __init__(self, points_list: list[tuple[int, int, int]]) -> None:
        super().__init__()

        self.points_list = points_list
        self.build()

    def build(self):
        points = vtkPoints()
        self.Allocate(len(self.points_list))

        for i, (x, y, z) in enumerate(self.points_list):
            points.InsertNextPoint(x, y, z)
            self.InsertNextCell(VTK_VERTEX, 1, [i])

        self.SetPoints(points)
