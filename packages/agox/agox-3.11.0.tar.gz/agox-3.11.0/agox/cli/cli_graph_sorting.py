import os

import rich_click as click
from ase.io import read, write
from rich import print

from agox.databases.database import Database


class Analysis:
    def __init__(self, descriptor, directories, sample_size, save_data=True, force_reload=False):
        self.descriptor = descriptor
        self.directories = directories
        self.sample_size = sample_size
        self.analysed_directories = []

        self.save_data = save_data
        self.force_reload = force_reload

        self.structures = []

    def analyse_directories(self):
        for idx, directory in enumerate(self.directories):
            self.add_directory(directory, force_reload=self.force_reload)

    def add_directory(self, directory, force_reload=False):
        if directory in self.analysed_directories:
            print("Directory: {} - already been loaded so skipping it".format(directory))

        cwd = os.getcwd()
        full_path = os.path.join(cwd, directory)
        if full_path[-1] != "/":
            full_path += "/"
        data_path = full_path + "GS_data/"

        if os.path.exists(data_path) and not force_reload:
            print("{} has already been analysed.".format(full_path))
            self.structures += read(data_path + "unique.traj", index=":")
            if self.descriptor.template is None:
                template = read(data_path + "template.traj", index="0")
                self.descriptor.template = template

        else:
            # Find database files in this directory:
            structures = []
            print("Loading files from directory: {}".format(directory))
            for f in os.listdir(os.path.join(cwd, directory)):
                if f[-3:] == ".db":
                    db = Database(os.path.join(cwd, directory, f))
                    db.restore_to_memory()
                    structures += db.get_all_candidates()
                    if self.descriptor.template is None:
                        template = structures[0].get_template()
                        self.descriptor.template = template

            unique = self.sort_structures(structures)
            self.structures += unique

            if self.save_data:
                if not os.path.exists(data_path):
                    os.mkdir(data_path)
                write(data_path + "unique.traj", unique)
                write(data_path + "template.traj", self.descriptor.template)

        self.analysed_directories.append(directory)

    def sort_structures(self, structures):
        structures = sorted(structures, key=lambda x: x.get_potential_energy())
        print(f"Total number of structures: {len(structures)}")
        unique = []
        eigen_spectrum = []
        for i, structure in enumerate(structures):
            eigen_values = self.descriptor.create_features(structure)
            if eigen_values not in eigen_spectrum:
                unique.append(structure)
                eigen_spectrum.append(eigen_values)
                print(i, eigen_values)
                if len(unique) == self.sample_size:
                    break
        print(f"Number of unique structures: {len(unique)}")
        return unique


graph_sort_option_groups = {
    "agox graph-sort": [
        {
            "name": "File options",
            "options": ["--directories", "--trajectories", "--save-data", "--force-reload"],
        },
        {
            "name": "Sorting options",
            "options": ["--sample-size", "--covalent-bond-scale-factor"],
        },
        {
            "name": "Voronoi options",
            "options": [
                "--number-of-points",
                "--angle-from-central-atom",
                "--template",
                "--indices",
            ],
        },
    ]
}

click.rich_click.OPTION_GROUPS.update(graph_sort_option_groups)


@click.command("graph-sort")
@click.option(
    "--directories",
    "-d",
    multiple=True,
    help="Directories to analyse.",
    required=False,
    default=[],
)
@click.option(
    "--trajectories",
    "-t",
    multiple=True,
    help="Trajectories to analyse.",
    required=False,
    default=[],
)
@click.option(
    "--save-data",
    "-sd",
    is_flag=True,
    help="Save the data to a file.",
    required=False,
    default=True,
)
@click.option(
    "--force-reload",
    "-f",
    is_flag=True,
    help="Force reload the data.",
    required=False,
    default=False,
)
@click.option(
    "--sample-size",
    "-ss",
    type=int,
    help="Number of structures to sample.",
    required=False,
    default=10,
)
@click.option(
    "--covalent-bond-scale-factor",
    "-cbf",
    type=float,
    help="Covalent bond scale factor.",
    required=False,
    default=1.3,
)
@click.option(
    "--number-of-points",
    "-n",
    type=int,
    help="Number of points in the Voronoi diagram.",
    required=False,
    default=8,
)
@click.option(
    "--angle-from-central-atom",
    "-a",
    type=float,
    help="Angle from the central atom.",
    required=False,
    default=20.0,
)
@click.option("--template", "-tm", type=str, help="Template file.", required=False, default=None)
@click.option(
    "--indices",
    "-i",
    type=str,
    help="Indices to consider.",
    required=False,
    default=None,
)
def cli_graph_sorting(
    directories,
    trajectories,
    save_data,
    force_reload,
    sample_size,
    covalent_bond_scale_factor,
    number_of_points,
    angle_from_central_atom,
    template,
    indices,
):
    """
    Sorts structures according to their Voronoi graphs.
    """
    from agox.models.descriptors.voronoi import Voronoi

    descriptor = Voronoi(
        indices=indices,
        template=template,
        covalent_bond_scale_factor=covalent_bond_scale_factor,
        n_points=number_of_points,
        angle_from_central_atom=angle_from_central_atom,
        environment=None,
    )

    A = Analysis(
        descriptor,
        directories,
        sample_size,
        save_data=save_data,
        force_reload=force_reload,
    )
    if len(directories) != 0:
        A.analyse_directories()

    if len(trajectories) != 0:
        print("Loading structures from trajectories")
        structures = []
        for trajectory in trajectories:
            structures += read(trajectory, index=":")

        A.structures += structures

    if len(directories) == 0 and len(trajectories) == 0:
        print("No directories or trajectories have been provided.")
        return

    print("\nConstructing combined sample from all directories and trajectories.\n")
    A.sample_size = 10000
    combined_unique = A.sort_structures(A.structures)
    write("combined_sample.traj", combined_unique)


if __name__ == "__main__":
    cli_graph_sorting()
