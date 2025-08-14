import numpy as np


def divide_by_std(perterbations: np.array, unperturbed_values: np.array) -> np.array:
    """
    Divides the perturbations by the standard deviation of the unperturbed values.

    Parameters:
    perterbations (np.array): Array of perturbation values.
    unperturbed_values (np.array): Array of unperturbed values.

    Returns:
    np.array: Array of perturbations normalized by the standard deviation of the unperturbed values.
    """
    return perterbations / np.nanstd(unperturbed_values)
