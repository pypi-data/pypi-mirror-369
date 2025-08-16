import rich_click as click


def convert_database_to_traj(database_path):
    import os

    from agox.databases import Database

    """
    Convert database to list of ASE Atoms objects. 

    Currently assumes that the database can be read using the standard database 
    class (agox/modules/databases/database.py).

    Parameters
    -----------
    database_path: str
        Path to database on disk. 

    Returns
    --------
    list
        List of ASE Atoms objects. 
    """

    if os.path.exists(database_path):
        database = Database(database_path, initialize=False)
    else:
        print(f"Trajectory not found: {database_path}")
        return []

    trajectory = database.restore_to_trajectory()

    return trajectory


def find_file_types(paths):
    """
    Find file extension of given paths.

    Parameters
    -----------
    paths: list of str
        Paths to check

    Returns
    --------
    list:
        List of strs indicating of the file types (extensions) of the given paths.
    """
    file_types = []
    for path in paths:
        file_types.append(path.split(".")[-1])
    return file_types


@click.command(name="convert")
@click.argument("files", nargs=-1)
@click.option("--name", "-n", default=None, type=str, help="Name of the output trajectory file.")
def cli_convert(files, name=None):
    """
    Convert database files to trajectory files.
    """
    import numpy as np
    from ase.io import write

    # Determine the file extension & ensure all paths have the same extension.
    file_types = find_file_types(files)
    assert np.array([file_type == file_types[0] for file_type in file_types]).all()
    file_type = file_types[0]

    # If database files - convert to trajectory.
    trajectory = []
    if file_type == "db":
        for path in files:
            print(f"Converting: {path}")
            trajectory += convert_database_to_traj(path)

        # Naming:
        if name is None:
            name = "converted_db.traj"

        # Save:
        print(f"Saving trajectory file {name}")
        write(name, trajectory)


if __name__ == "__main__":
    cli_convert()
