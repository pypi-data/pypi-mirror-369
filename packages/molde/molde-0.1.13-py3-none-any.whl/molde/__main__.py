import os, sys
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QLineEdit, QTableWidgetItem, QPushButton, QLabel, QSlider
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt
from time import time

from vtkmodules.vtkFiltersSources import vtkCylinderSource
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor

from molde import MOLDE_DIR, load_ui
from molde import stylesheets
from molde.render_widgets.common_render_widget import CommonRenderWidget


class Example(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__()
        load_ui(MOLDE_DIR / "stylesheets/mainwindow.ui", self, MOLDE_DIR / "stylesheets")
        self.current_theme = "light"

        self.change_theme_button.clicked.connect(self.change_theme)
        # self.render_widget: CommonRenderWidget
        # self.render_widget.create_axes()
        # self.render_widget.create_scale_bar()
        # self.render_widget.create_color_bar()
        # self.render_widget.set_info_text("Hola\nque\ntal?")

        cylinder = vtkCylinderSource()
        cylinder.SetResolution(8)
        cylinder_mapper = vtkPolyDataMapper()
        cylinder_mapper.SetInputConnection(cylinder.GetOutputPort())
        cylinder_actor = vtkActor()
        cylinder_actor.SetMapper(cylinder_mapper)
        # self.render_widget.add_actors(cylinder_actor)

        self.botao1 = QPushButton()
        self.label = QLabel("Olha o sapooo")
        self.label.setProperty("type", "logo")
        # font = QFont()
        # font.setFamily("Bauhaus 93")
        # self.label.setFont(font)
        print(self.label.fontInfo().family())

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setValue(50)
        self.botao1.setText("Olha a faca")
        self.toolbar_2.addWidget(self.label)
        self.toolbar_2.setDisabled(False)

        item = QTableWidgetItem("fr")
        item.setBackground(QColor("#FF0000"))  
        self.tableWidget.setItem(0, 0, item) 
        self.show()
        
    def change_theme(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        
        # self.render_widget.set_theme(self.current_theme)
        stylesheets.set_theme(self.current_theme)
    
    def closeEvent(self, event):
        close = QMessageBox.question(
            self, 
            "QUIT", 
            "Would you like to close the application?", 
            QMessageBox.Yes | QMessageBox.No
        )
        QApplication.quit()


if __name__ == "__main__":
    # Make the window scale evenly for every monitor
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    e = Example()
    e.change_theme()
    sys.exit(app.exec())
