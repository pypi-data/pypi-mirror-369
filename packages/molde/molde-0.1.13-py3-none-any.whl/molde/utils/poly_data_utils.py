from pathlib import Path

from vtkmodules.vtkCommonCore import vtkUnsignedCharArray, vtkUnsignedIntArray
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
from vtkmodules.vtkIOGeometry import vtkOBJReader, vtkSTLReader


def set_polydata_colors(data: vtkPolyData, color: tuple) -> vtkUnsignedCharArray:
    n_cells = data.GetNumberOfCells()
    cell_colors = vtkUnsignedCharArray()
    cell_colors.SetName("colors")
    cell_colors.SetNumberOfComponents(3)
    cell_colors.SetNumberOfTuples(n_cells)
    cell_colors.FillComponent(0, color[0])
    cell_colors.FillComponent(1, color[1])
    cell_colors.FillComponent(2, color[2])
    data.GetCellData().SetScalars(cell_colors)
    return cell_colors


def set_polydata_property(
    data: vtkPolyData, property_data: int, property_name: str
) -> vtkUnsignedIntArray:
    n_cells = data.GetNumberOfCells()
    cell_identifier = vtkUnsignedIntArray()
    cell_identifier.SetName(property_name)
    cell_identifier.SetNumberOfTuples(n_cells)
    cell_identifier.Fill(property_data)
    data.GetCellData().AddArray(cell_identifier)
    return cell_identifier


def read_obj_file(path: str | Path) -> vtkPolyData:
    reader = vtkOBJReader()
    reader.SetFileName(str(path))
    reader.Update()
    return reader.GetOutput()


def read_stl_file(path: str | Path) -> vtkPolyData:
    reader = vtkSTLReader()
    reader.SetFileName(str(path))
    reader.Update()
    return reader.GetOutput()


def transform_polydata(
    polydata: vtkPolyData,
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    scale=(1, 1, 1),
) -> vtkPolyData:
    transform = vtkTransform()
    transform.Translate(position)
    transform.Scale(scale)
    transform.RotateX(rotation[0])
    transform.RotateY(rotation[1])
    transform.RotateZ(rotation[2])
    transform.Update()
    transformation = vtkTransformPolyDataFilter()
    transformation.SetTransform(transform)
    transformation.SetInputData(polydata)
    transformation.Update()
    return transformation.GetOutput()
