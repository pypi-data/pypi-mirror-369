from molde import MOLDE_DIR
from molde.utils import nested_dict
from molde.colors import color_names


colors_by_name = nested_dict()
for full_name, color in color_names.__dict__.items():
    try:
        name, level = full_name.split("_")
        level = int(level)
        colors_by_name[name][level] = color.to_hex()
    except:
        continue

page_body_list = []
for color_name, color_data in colors_by_name.items():
    color_data: dict
    palette_header = ""
    html_palette_list = []
    for color_level, color_code in sorted(color_data.items(), reverse=True):
        if color_level == 4:
            palette_header = (
                f'<div class="colorblock" style="color:#ffffff; background:{color_code}">'
                    f'<b>{color_name.title()}</b>'
                    f'<b>{color_code}</b>'
                '</div>'
            )
        txt_color = "#000000" if color_level >= 5 else "#FFFFFF" 
        block = (
            f'<div class="colorblock" style="color:{txt_color}; background:{color_code}">'
                f'<b>{color_level}</b>'
                f'<b>{color_code}</b>'
            '</div>'
        )
        html_palette_list.append(block)

    html_palette_list = [palette_header] + html_palette_list
    page_body_list.append("\n".join(html_palette_list))

page_header = '''<html>
<title>Molde Colors</title>
<style>
body{
  font-family: sans-serif;
  background-color: #000000;
}
div.colorblock {
  display:flex;
  justify-content:space-between;
  padding: 0.75rem 1.5rem;
}
</style>

'''

page_body = "\n\n&nbsp;\n\n".join(page_body_list)

page_footer = "\n\n</html>"

path = MOLDE_DIR.parent / "docs/index.html"
path.write_text(page_header + page_body + page_footer)
