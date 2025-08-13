from dataclasses import dataclass
from typing import Callable

from vtkmodules.vtkCommonCore import (
    vtkDoubleArray,
    vtkIntArray,
    vtkPoints,
    vtkUnsignedCharArray,
)
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDistanceToCamera,
    vtkGlyph3DMapper,
    vtkRenderer,
)

from molde import Color

Triple = tuple[float, float, float]


@dataclass
class Symbol:
    shape_function: Callable
    position: Triple
    orientation: Triple
    color: Color
    scale: float


class CommonSymbolsActor(vtkActor):
    def __init__(self, *args, **kwargs):
        self._symbols: list[Symbol] = list()

    def add_symbol(
        self,
        shape_function: Callable,
        position: Triple,
        orientation: Triple,
        color: Triple,
        scale: float = 1,
    ):
        symbol = Symbol(
            shape_function,
            position,
            orientation,
            color,
            scale,
        )
        self._symbols.append(symbol)

    def clear_symbols(self):
        self._symbols.clear()

    def common_build(self):
        self.data = vtkPolyData()
        points = vtkPoints()

        self.mapper: vtkGlyph3DMapper = vtkGlyph3DMapper()
        self.SetMapper(self.mapper)

        sources = vtkIntArray()
        sources.SetName("sources")

        rotations = vtkDoubleArray()
        rotations.SetNumberOfComponents(3)
        rotations.SetName("rotations")

        scales = vtkDoubleArray()
        scales.SetName("scales")

        colors = vtkUnsignedCharArray()
        colors.SetNumberOfComponents(4)
        colors.SetName("colors")

        shape_function_to_index = dict()
        for symbol in self._symbols:
            if symbol.shape_function not in shape_function_to_index:
                index = len(shape_function_to_index)
                shape_function_to_index[symbol.shape_function] = index
                self.mapper.SetSourceData(index, symbol.shape_function())

            points.InsertNextPoint(symbol.position)
            rotations.InsertNextTuple(symbol.orientation)
            colors.InsertNextTuple(symbol.color.to_rgba())
            scales.InsertNextValue(symbol.scale)
            sources.InsertNextValue(shape_function_to_index[symbol.shape_function])

        self.data.SetPoints(points)
        self.data.GetPointData().AddArray(sources)
        self.data.GetPointData().AddArray(rotations)
        self.data.GetPointData().AddArray(scales)
        self.data.GetPointData().SetScalars(colors)

    def set_zbuffer_offsets(self, factor: float, units: float):
        """
        This functions is usefull to make a object appear in front of the others.
        If the object should never be hidden, the parameters should be set to
        factor = 1 and offset = -66000.
        """
        self.mapper.SetResolveCoincidentTopologyToPolygonOffset()
        self.mapper.SetRelativeCoincidentTopologyLineOffsetParameters(factor, units)
        self.mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(factor, units)
        self.mapper.SetRelativeCoincidentTopologyPointOffsetParameter(units)
        self.mapper.Update()


class CommonSymbolsActorFixedSize(CommonSymbolsActor):
    def build(self):
        self.common_build()

        self.mapper.SetInputData(self.data)
        self.mapper.SetSourceIndexArray("sources")
        self.mapper.SetOrientationArray("rotations")
        self.mapper.SetScaleArray("scales")
        self.mapper.SourceIndexingOn()
        self.mapper.ScalarVisibilityOn()
        self.mapper.SetScaleModeToScaleByMagnitude()
        self.mapper.SetScalarModeToUsePointData()
        self.mapper.SetOrientationModeToDirection()
        self.mapper.Update()


class CommonSymbolsActorVariableSize(CommonSymbolsActor):
    def __init__(self, renderer: vtkRenderer):
        super().__init__()
        self.renderer = renderer

    def build(self):
        self.common_build()

        distance_to_camera = vtkDistanceToCamera()
        distance_to_camera.SetInputData(self.data)
        distance_to_camera.SetScreenSize(40)
        distance_to_camera.SetRenderer(self.renderer)

        self.mapper.SetInputConnection(distance_to_camera.GetOutputPort())
        self.mapper.SetSourceIndexArray("sources")
        self.mapper.SetOrientationArray("rotations")
        self.mapper.SetScaleArray("DistanceToCamera")
        self.mapper.SourceIndexingOn()
        self.mapper.ScalarVisibilityOn()
        self.mapper.SetScaleModeToScaleByMagnitude()
        self.mapper.SetScalarModeToUsePointData()
        self.mapper.SetOrientationModeToDirection()

        self.mapper.Update()
