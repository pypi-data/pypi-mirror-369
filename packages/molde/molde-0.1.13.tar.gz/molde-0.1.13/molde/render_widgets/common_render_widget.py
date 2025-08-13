from pathlib import Path
from threading import Lock
from typing import Literal

from PIL import Image
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QFrame, QStackedLayout
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.util.numpy_support import vtk_to_numpy
from vtkmodules.vtkCommonCore import VTK_FONT_FILE, vtkLookupTable
from vtkmodules.vtkInteractionWidgets import (
    vtkLogoRepresentation,
    vtkOrientationMarkerWidget,
)
from vtkmodules.vtkIOImage import vtkPNGReader
from vtkmodules.vtkRenderingAnnotation import (
    vtkAxesActor,
    vtkLegendScaleActor,
    vtkScalarBarActor,
)
from vtkmodules.vtkRenderingCore import (
    vtkLight,
    vtkActor,
    vtkRenderer,
    vtkTextActor,
    vtkInteractorStyle,
    vtkTextProperty,
    vtkWindowToImageFilter,
)

from molde import MOLDE_DIR
from molde.colors import Color
from molde.interactor_styles import ArcballCameraInteractorStyle


class CommonRenderWidget(QFrame):
    """
    This class is needed to show vtk renderers in pyqt.

    A vtk widget must always have a renderer, even if it is empty.
    """

    left_clicked = Signal(int, int)
    left_released = Signal(int, int)
    right_clicked = Signal(int, int)
    right_released = Signal(int, int)

    def __init__(self, parent=None, *, theme="dark"):
        super().__init__(parent)

        self.renderer = vtkRenderer()
        self.interactor_style = ArcballCameraInteractorStyle()
        self.render_interactor = QVTKRenderWindowInteractor(self)

        self.render_interactor.Initialize()
        self.render_interactor.GetRenderWindow().AddRenderer(self.renderer)
        self.render_interactor.SetInteractorStyle(self.interactor_style)

        self.renderer.ResetCamera()

        self.render_interactor.AddObserver("LeftButtonPressEvent", self.left_click_press_event)
        self.render_interactor.AddObserver("LeftButtonReleaseEvent", self.left_click_release_event)
        self.render_interactor.AddObserver("RightButtonPressEvent", self.right_click_press_event)
        self.render_interactor.AddObserver("RightButtonReleaseEvent", self.right_click_release_event)

        layout = QStackedLayout()
        layout.addWidget(self.render_interactor)
        self.setLayout(layout)

        self._current_theme = theme
        self._widget_actors = list()
        self.update_lock = Lock()

        self.create_info_text()
        self.set_theme(self._current_theme)

    def update_plot(self):
        raise NotImplementedError("The function update_plot was not implemented")

    def add_actors(self, *actors: vtkActor):
        for actor in actors:
            self.renderer.AddActor(actor)
            if actor not in self._widget_actors:
                self._widget_actors.append(actor)

    def remove_actors(self, *actors: vtkActor):
        for actor in actors:
            self.renderer.RemoveActor(actor)
            try:
                self._widget_actors.remove(actor)
            except ValueError:
                continue

    def remove_all_actors(self):
        self.remove_actors(*self.get_widget_actors())

    def remove_all_props(self):
        self.renderer.RemoveAllViewProps()

    def get_widget_actors(self):
        return [i for i in self._widget_actors]

    def set_interactor_style(self, interactor_style: vtkInteractorStyle):
        self.interactor_style = interactor_style
        self.render_interactor.SetInteractorStyle(interactor_style)

    def get_interactor_style(self) -> vtkInteractorStyle:
        return self.render_interactor.GetInteractorStyle()

    def update(self):
        if self.update_lock.locked():
            return

        ren_win = self.render_interactor.GetRenderWindow()
        if ren_win is not None:
            self.renderer.ResetCameraClippingRange()
            ren_win.Render()

    def left_click_press_event(self, obj, event):
        x, y, *_ = self.render_interactor.GetEventPosition()
        self.left_clicked.emit(x, y)

    def left_click_release_event(self, obj, event):
        x, y, *_ = self.render_interactor.GetEventPosition()
        self.left_released.emit(x, y)

    def right_click_press_event(self, obj, event):
        x, y, *_ = self.render_interactor.GetEventPosition()
        self.right_clicked.emit(x, y)

    def right_click_release_event(self, obj, event):
        x, y, *_ = self.render_interactor.GetEventPosition()
        self.right_released.emit(x, y)

    def get_screenshot(self) -> Image.Image:
        image_filter = vtkWindowToImageFilter()
        image_filter.SetInput(self.render_interactor.GetRenderWindow())
        image_filter.Update()

        vtk_image = image_filter.GetOutput()
        width, height, _ = vtk_image.GetDimensions()
        vtk_array = vtk_image.GetPointData().GetScalars()
        components = vtk_array.GetNumberOfComponents()

        array = vtk_to_numpy(vtk_array).reshape(height, width, components)
        image = Image.fromarray(array).transpose(Image.FLIP_TOP_BOTTOM)
        return image

    def get_thumbnail(self) -> Image.Image:
        image = self.get_screenshot()
        w, h = image.size
        s = min(w, h)
        box = (
            (w - s) // 2,
            (h - s) // 2,
            (w + s) // 2,
            (h + s) // 2,
        )
        return image.crop(box).resize((512, 512))

    def save_image(self, path: str | Path):
        """
        Saves the render as an image.
        Supported formats are JPEG, JPG, PNG, BMP, ICO, TIFF, PPM and others.
        """
        image = self.get_screenshot()
        with open(path, "wb") as file:
            image.save(file)

    def create_axes(self):
        axes_actor = vtkAxesActor()

        axes_actor.SetXAxisLabelText(" X")
        axes_actor.SetYAxisLabelText(" Y")
        axes_actor.SetZAxisLabelText(" Z")

        axes_actor.GetXAxisShaftProperty().LightingOff()
        axes_actor.GetYAxisShaftProperty().LightingOff()
        axes_actor.GetZAxisShaftProperty().LightingOff()
        axes_actor.GetXAxisTipProperty().LightingOff()
        axes_actor.GetYAxisTipProperty().LightingOff()
        axes_actor.GetZAxisTipProperty().LightingOff()

        x_property = axes_actor.GetXAxisCaptionActor2D().GetCaptionTextProperty()
        y_property = axes_actor.GetYAxisCaptionActor2D().GetCaptionTextProperty()
        z_property = axes_actor.GetZAxisCaptionActor2D().GetCaptionTextProperty()

        for text_property in [x_property, y_property, z_property]:
            text_property: vtkTextProperty
            text_property.ItalicOff()
            text_property.BoldOn()

        self.axes = vtkOrientationMarkerWidget()
        self.axes.SetViewport(0, 0, 0.18, 0.18)
        self.axes.SetOrientationMarker(axes_actor)
        self.axes.SetInteractor(self.render_interactor)
        self.axes.EnabledOn()
        self.axes.InteractiveOff()

    def create_scale_bar(self):
        self.scale_bar_actor = vtkLegendScaleActor()
        self.scale_bar_actor.AllAxesOff()
        self.renderer.AddActor(self.scale_bar_actor)

        font_file = MOLDE_DIR / "fonts/IBMPlexMono-Regular.ttf"

        title_property: vtkTextProperty
        title_property = self.scale_bar_actor.GetLegendTitleProperty()
        title_property.SetFontSize(16)
        title_property.ShadowOff()
        title_property.ItalicOff()
        title_property.BoldOn()
        title_property.SetLineOffset(-55)
        title_property.SetVerticalJustificationToTop()
        title_property.SetFontFamily(VTK_FONT_FILE)
        title_property.SetFontFile(font_file)

        label_property: vtkTextProperty
        label_property = self.scale_bar_actor.GetLegendLabelProperty()
        label_property.SetFontSize(16)
        label_property.SetColor((0.8, 0.8, 0.8))
        label_property.ShadowOff()
        label_property.ItalicOff()
        label_property.BoldOff()
        label_property.SetLineOffset(-35)
        label_property.SetFontFamily(VTK_FONT_FILE)
        label_property.SetFontFile(font_file)

        # set the text color based on current theme
        self.set_theme(self._current_theme)

    def create_color_bar(self, lookup_table=None):
        if lookup_table is None:
            lookup_table = vtkLookupTable()
            lookup_table.Build()

        font_file = MOLDE_DIR / "fonts/IBMPlexMono-Regular.ttf"

        self.colorbar_actor = vtkScalarBarActor()
        self.colorbar_actor.SetLabelFormat("%1.0e ")
        self.colorbar_actor.SetLookupTable(lookup_table)
        self.colorbar_actor.SetWidth(0.02)
        self.colorbar_actor.SetPosition(0.94, 0.17)
        self.colorbar_actor.SetHeight(0.7)
        self.colorbar_actor.SetMaximumNumberOfColors(400)
        self.colorbar_actor.SetVerticalTitleSeparation(20)
        self.colorbar_actor.UnconstrainedFontSizeOn()
        self.colorbar_actor.SetTextPositionToPrecedeScalarBar()
        self.renderer.AddActor(self.colorbar_actor)

        colorbar_title: vtkTextProperty = self.colorbar_actor.GetTitleTextProperty()
        colorbar_title.ShadowOff()
        colorbar_title.ItalicOff()
        colorbar_title.BoldOn()
        colorbar_title.SetFontSize(16)
        colorbar_title.SetJustificationToLeft()
        colorbar_title.SetFontFamily(VTK_FONT_FILE)
        colorbar_title.SetFontFile(font_file)

        colorbar_label: vtkTextProperty = self.colorbar_actor.GetLabelTextProperty()
        colorbar_label.ShadowOff()
        colorbar_label.ItalicOff()
        colorbar_label.BoldOn()
        colorbar_label.SetFontSize(16)
        colorbar_label.SetJustificationToLeft()
        colorbar_label.SetFontFamily(VTK_FONT_FILE)
        colorbar_label.SetFontFile(font_file)

        # set the text color based on current theme
        self.set_theme(self._current_theme)

    def create_info_text(self):
        font_file = MOLDE_DIR / "fonts/IBMPlexMono-Bold.ttf"

        self.text_actor = vtkTextActor()
        self.renderer.AddActor2D(self.text_actor)

        info_text_property = self.text_actor.GetTextProperty()
        info_text_property.SetFontSize(14)
        info_text_property.SetVerticalJustificationToTop()
        info_text_property.SetColor((0.2, 0.2, 0.2))
        info_text_property.SetLineSpacing(1.3)
        info_text_property.SetFontFamilyToTimes()
        info_text_property.SetFontFamily(VTK_FONT_FILE)
        info_text_property.SetFontFile(font_file)

        coord = self.text_actor.GetPositionCoordinate()
        coord.SetCoordinateSystemToNormalizedViewport()
        coord.SetValue(0.01, 0.98)

        # set the text color based on current theme
        self.set_theme(self._current_theme)

    def create_logo(self, path: str | Path) -> vtkLogoRepresentation:
        path = Path(path)

        image_reader = vtkPNGReader()
        image_reader.SetFileName(path)
        image_reader.Update()

        logo = vtkLogoRepresentation()
        logo.SetImage(image_reader.GetOutput())
        logo.ProportionalResizeOn()
        logo.GetImageProperty().SetOpacity(0.9)
        logo.GetImageProperty().SetDisplayLocationToBackground()

        self.renderer.AddViewProp(logo)
        logo.SetRenderer(self.renderer)
        return logo

    def create_camera_light(self, offset_x=0, offset_y=0):
        light = vtkLight()
        light.SetLightTypeToCameraLight()
        light.SetPosition(offset_x, offset_y, 1)
        self.renderer.AddLight(light)

    def set_colorbar_unit(self, text):
        if not hasattr(self, "colorbar_actor"):
            return
        self.colorbar_actor.SetTitle(text)

    def set_info_text(self, text):
        self.text_actor.SetInput(text)

    def set_theme(self, theme: Literal["dark", "light", "custom"], **kwargs):
        self._current_theme = theme

        if theme == "dark":
            bkg_1 = Color("#0b0f17")
            bkg_2 = Color("#3e424d")
            font_color = Color("#CCCCCC")

        elif theme == "light":
            bkg_1 = Color("#8092A6")
            bkg_2 = Color("#EEF2F3")
            font_color = Color("#111111")

        elif theme == "custom":
            bkg_1 = kwargs.get("bkg_1")
            bkg_2 = kwargs.get("bkg_2")
            font_color = kwargs.get("font_color")

            if bkg_1 is None:
                raise ValueError('Missing value "bkg_1"')
            if bkg_2 is None:
                raise ValueError('Missing value "bkg_2"')
            if font_color is None:
                raise ValueError('Missing value "font_color"')

        else:
            return

        self.renderer.GradientBackgroundOn()
        self.renderer.SetBackground(bkg_1.to_rgb_f())
        self.renderer.SetBackground2(bkg_2.to_rgb_f())

        if hasattr(self, "text_actor"):
            self.text_actor.GetTextProperty().SetColor(font_color.to_rgb_f())

        if hasattr(self, "colorbar_actor"):
            self.colorbar_actor.GetTitleTextProperty().SetColor(font_color.to_rgb_f())
            self.colorbar_actor.GetLabelTextProperty().SetColor(font_color.to_rgb_f())

        if hasattr(self, "scale_bar_actor"):
            self.scale_bar_actor.GetLegendTitleProperty().SetColor(font_color.to_rgb_f())
            self.scale_bar_actor.GetLegendLabelProperty().SetColor(font_color.to_rgb_f())

    #
    def set_custom_view(self, position, view_up):
        self.renderer.GetActiveCamera().SetPosition(position)
        self.renderer.GetActiveCamera().SetViewUp(view_up)
        self.renderer.GetActiveCamera().SetParallelProjection(True)
        self.renderer.ResetCamera(*self.renderer.ComputeVisiblePropBounds())
        self.update()

    def set_top_view(self):
        x, y, z = self.renderer.GetActiveCamera().GetFocalPoint()
        position = (x, y + 1, z)
        view_up = (0, 0, -1)
        self.set_custom_view(position, view_up)

    def set_bottom_view(self):
        x, y, z = self.renderer.GetActiveCamera().GetFocalPoint()
        position = (x, y - 1, z)
        view_up = (0, 0, 1)
        self.set_custom_view(position, view_up)

    def set_left_view(self):
        x, y, z = self.renderer.GetActiveCamera().GetFocalPoint()
        position = (x - 1, y, z)
        view_up = (0, 1, 0)
        self.set_custom_view(position, view_up)

    def set_right_view(self):
        x, y, z = self.renderer.GetActiveCamera().GetFocalPoint()
        position = (x + 1, y, z)
        view_up = (0, 1, 0)
        self.set_custom_view(position, view_up)

    def set_front_view(self):
        x, y, z = self.renderer.GetActiveCamera().GetFocalPoint()
        position = (x, y, z + 1)
        view_up = (0, 1, 0)
        self.set_custom_view(position, view_up)

    def set_back_view(self):
        x, y, z = self.renderer.GetActiveCamera().GetFocalPoint()
        position = (x, y, z - 1)
        view_up = (0, 1, 0)
        self.set_custom_view(position, view_up)

    def set_isometric_view(self):
        x, y, z = self.renderer.GetActiveCamera().GetFocalPoint()
        position = (x + 1, y + 1, z + 1)
        view_up = (0, 1, 0)
        self.set_custom_view(position, view_up)

    def copy_camera_from(self, other):
        if isinstance(other, CommonRenderWidget):
            other_camera = other.renderer.GetActiveCamera()
        elif isinstance(other, vtkRenderer):
            other_camera = other.GetActiveCamera()
        else:
            return

        self.renderer.GetActiveCamera().DeepCopy(other_camera)
        self.renderer.ResetCameraClippingRange()
        self.renderer.GetActiveCamera().Modified()
        self.update()
