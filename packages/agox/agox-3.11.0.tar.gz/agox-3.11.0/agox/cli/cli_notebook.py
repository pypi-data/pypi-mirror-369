import rich_click as click


@click.command("notebook")
@click.argument("directories", nargs=-1, type=str)
@click.option("--auto-open", is_flag=True, help="Open the notebook in VS-code after creation.")
@click.option("--name", type=str, help="Name of the notebook file.")
def cli_notebook(directories, auto_open, name) -> None:
    """
    Create a jupyter notebook for analysis.
    """
    import pathlib
    import subprocess

    import nbformat as nbf

    # Need to massage the input of directories a little bit:
    for i in range(len(directories)):
        directories[i] = "'" + directories[i] + "'"

    # Convenience settings:
    figsize = "figsize = (7, 7)"

    # Create notebook object
    nb = nbf.v4.new_notebook()

    # Add functions:
    markdown = nbf.v4.new_markdown_cell
    code = nbf.v4.new_code_cell

    # List to hold cell contents
    cells = nb["cells"] = []

    def add_cell(content_string, add_function):
        cells.append(add_function(content_string))

    # Create initial text
    this_file = pathlib.Path(__file__).absolute()
    headline = """
# Automagic AGOX Analysis
This is an automatically generated AGOX analysis notebook.\n 
Notebook generation is defined in this file: {}
    """.format(this_file)
    # cells.append(markdown(headline))
    add_cell(headline, markdown)

    # Import statements % basic settings
    import_block = """import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt
from agox.utils.batch_analysis import Analysis
from agox.utils.jupyter_interactive import InteractiveStructureHistogram, InteractiveSuccessStats, InteractiveEnergy, sorted_species"""
    # cells.append(code(import_block))
    add_cell(import_block, code)

    # Load block:
    load_headline = """## Scan and read db-files in the directories and calculate CDF.
This is the block that takes the most times, avoid rerunning unless changes have been made that require re-reading the 
directories, such as adding additional ones. """
    add_cell(load_headline, markdown)

    load_block = """
analysis = Analysis()
force_reload = False
"""
    for directory in directories:
        load_block += "analysis.add_directory({}, force_reload=force_reload)\n".format(directory)
    load_block += "analysis.compile_information()\n"
    load_block += "analysis.calculate_CDF()"

    # cells.append(code(load_block))
    add_cell(load_block, code)

    # Success statistics block:
    succes_headline = """
## Analysis
    """
    add_cell(succes_headline, markdown)

    success_block = """ISS = InteractiveSuccessStats(analysis)
out = widgets.interactive_output(ISS.update_plot, ISS.widget_dict)
widgets.HBox([widgets.VBox(ISS.widget_list), out])""".format()
    add_cell(success_block, code)

    energy_int_block = """IE = InteractiveEnergy(analysis)
out = widgets.interactive_output(IE.update_plot, IE.widget_dict)
widgets.HBox([widgets.VBox(IE.widget_list), out])"""
    add_cell(energy_int_block, code)

    interactive_struct_hist = """ISH = InteractiveStructureHistogram(analysis)
num_structures = np.sum(analysis.restarts)
index = widgets.IntSlider(min=0, max=num_structures-1, value=0, description='Index')
widgets.interactive(ISH.update_plot, index=index)"""
    add_cell(interactive_struct_hist, code)

    structure_viewer = """from ase.visualize import view
structures, energies = analysis.get_best_structures()
structures = [sorted_species(atoms) for atoms in structures]
view(structures, viewer='ngl')"""
    add_cell(structure_viewer, code)

    # Write notebook:
    notebook_path = name + ".ipynb"
    nbf.write(nb, notebook_path)

    # This will only work with appropriately configured VS-code installation.
    if auto_open:
        subprocess.run("code {}".format(notebook_path), shell=True)
