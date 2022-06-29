import pathlib


def get_model_path(name: str) -> pathlib.Path:
    """Return absolute path to the specified model.

    Args:
        name: Filename of the model.

    Returns:
        Path to the model file.

    Raises:
        FileNotFoundError: If the model does not exist.
    """
    here = pathlib.Path(__file__).parent
    model_path = here / name

    if not model_path.is_file():
        raise FileNotFoundError("Model {} not found".format(name))

    return model_path
