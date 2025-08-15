from typing import Literal
from qtpy.QtWidgets import QApplication, QWidget
from molde import MOLDE_DIR
from molde.colors import color_names


def set_qproperty(widget: QWidget, **kwargs):
    for key, val in kwargs.items():
        widget.setProperty(key, val)
    widget.style().polish(widget)

def get_variables(theme:Literal["light", "dark"] = "light") -> dict:
    variables = {
        "@border-radius": "5px",
    }

    if theme == "light":
        variables.update({
            "@primary-lighter": color_names.BLUE_6.to_hex(),
            "@primary": color_names.BLUE_4.to_hex(),
            "@primary-darker": color_names.BLUE_3.to_hex(),

            "@danger-color-lighter": color_names.RED_5.to_hex(),
            "@danger-color": color_names.RED_4.to_hex(),
            "@danger-color-darker": color_names.RED_2.to_hex(),

            "@warning-color-lighter": color_names.YELLOW_6.to_hex(),
            "@warning-color": color_names.YELLOW_4.to_hex(),
            "@warning-color-darker": color_names.YELLOW_3.to_hex(),

            "@background": color_names.GRAY_9.to_hex(),
            "@background-variant": color_names.GRAY_8.to_hex(),

            "@on-primary": color_names.WHITE.to_hex(),
            "@on-background": color_names.BLACK.to_hex(),

            "@border-color": color_names.GRAY_7.to_hex(),
            "@checkbox-border-color": color_names.GRAY_6.to_hex(),
            "@input-color": color_names.GRAY_8.to_hex(),

            "@disabled-background": color_names.GRAY_8.to_hex(),
            "@disabled-color": color_names.GRAY_7.to_hex(),
            "@alternative-disabled-background" : color_names.GRAY_6.to_hex(),

            "@hover-arrow-color":  color_names.GRAY_8.to_hex(),
            "@arrow-up-image-icon": str(MOLDE_DIR / "icons/arrow_up_light_theme.svg").replace("\\", "/"),
            "@arrow-down-image-icon": str(MOLDE_DIR/ "icons/arrow_down_light_theme.svg").replace("\\", "/"),
            "@arrow-left-image-icon": str(MOLDE_DIR/ "icons/arrow_left_light_theme.svg").replace("\\", "/"),
            "@arrow-right-image-icon": str(MOLDE_DIR/ "icons/arrow_right_light_theme.svg").replace("\\", "/"),
            "@check-box-image-icon": str(MOLDE_DIR / "icons/check_box_image.svg").replace("\\", "/"),
            "@arrow-up-disabled-image-icon" : str(MOLDE_DIR / "icons/arrow_up_disabled_light_theme.svg").replace("\\", "/"),
            "@arrow-down-disabled-image-icon" : str(MOLDE_DIR / "icons/arrow_down_disabled_light_theme.svg").replace("\\", "/"),
        })

    elif theme == "dark":
        variables.update({
            "@primary-lighter": color_names.BLUE_6.to_hex(),
            "@primary": color_names.BLUE_5.to_hex(),
            "@primary-darker": color_names.BLUE_4.to_hex(),

            "@danger-color-lighter": color_names.RED_5.to_hex(),
            "@danger-color": color_names.RED_4.to_hex(),
            "@danger-color-darker": color_names.RED_2.to_hex(),

            "@warning-color-lighter": color_names.YELLOW_6.to_hex(),
            "@warning-color": color_names.YELLOW_4.to_hex(),
            "@warning-color-darker": color_names.YELLOW_3.to_hex(),

            "@background": color_names.GRAY_1.to_hex(),
            "@background-variant": color_names.GRAY_3.to_hex(),

            "@on-background": color_names.WHITE.to_hex(),
            "@on-primary": color_names.WHITE.to_hex(),

            "@border-color": color_names.GRAY_2.to_hex(),
            "@checkbox-border-color": color_names.GRAY_4.to_hex(),
            "@input-color": color_names.GRAY_3.to_hex(),

            "@disabled-background": color_names.GRAY_0.to_hex(),
            "@disabled-color": color_names.GRAY_4.to_hex(),
            "@alternative-disabled-background" : color_names.GRAY_2.to_hex(),

            "@hover-arrow-color": color_names.GRAY_1.to_hex(),
            "@arrow-up-image-icon": str(MOLDE_DIR / "icons/arrow_up_dark_theme.svg").replace("\\", "/"),
            "@arrow-down-image-icon": str(MOLDE_DIR / "icons/arrow_down_dark_theme.svg").replace("\\", "/"),
            "@arrow-left-image-icon": str(MOLDE_DIR/ "icons/arrow_left_dark_theme.svg").replace("\\", "/"),
            "@arrow-right-image-icon": str(MOLDE_DIR/ "icons/arrow_right_dark_theme.svg").replace("\\", "/"),
            "@check-box-image-icon": str(MOLDE_DIR / "icons/check_box_image.svg").replace("\\", "/"),
            "@arrow-up-disabled-image-icon" : str(MOLDE_DIR / "icons/arrow_up_disabled_light_theme.svg").replace("\\", "/"),
            "@arrow-down-disabled-image-icon" : str(MOLDE_DIR / "icons/arrow_down_disabled_light_theme.svg").replace("\\", "/"),
            
        })

    return variables

def get_stylesheet(theme:Literal["light", "dark"] = "light", *, extra_style=""):
    qss_dir = MOLDE_DIR / "stylesheets/"

    all_stylesheets = []
    for path in qss_dir.glob("*.qss"):
        all_stylesheets.append(path.read_text())
    all_stylesheets.append(extra_style)
    stylesheet = "\n\n".join(all_stylesheets)

    # Replace variables by correspondent data
    variable_size = lambda x: len(x[0])
    variables_mapping = sorted(get_variables(theme).items(), 
                               key=variable_size, reverse=True)
    for name, data in variables_mapping:
        stylesheet = stylesheet.replace(name, data)

    return stylesheet

def set_theme(theme=Literal["light", "dark"], *, extra_style=""):

    app: QApplication | None = QApplication.instance()
    if app is None:
        print("Ops")
        return

    stylesheet = get_stylesheet(theme)
    app.setStyleSheet(stylesheet)
