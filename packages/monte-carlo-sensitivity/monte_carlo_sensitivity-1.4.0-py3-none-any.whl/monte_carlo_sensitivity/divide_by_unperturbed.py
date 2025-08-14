import numpy as np

def divide_by_unperturbed(perterbations: np.array, unperturbed_values: np.array) -> np.array:
    """
    Normalize perturbations by dividing them by unperturbed values.

    This function takes two arrays: `perterbations` and `unperturbed_values`. 
    It ensures that the `unperturbed_values` array is converted to a float64 type 
    and handles edge cases such as infinite or zero values by replacing them with NaN. 
    The function then divides the `perterbations` array by the processed `unperturbed_values` 
    to compute the normalized values.

    Parameters:
        perterbations (np.array): Array of perturbed values.
        unperturbed_values (np.array): Array of unperturbed baseline values.

    Returns:
        np.array: Array of normalized values, where each element is the result of 
                  dividing the corresponding element in `perterbations` by the 
                  corresponding element in `unperturbed_values`. NaN is returned 
                  for divisions involving invalid unperturbed values (e.g., zero or infinity).
    """
    # Ensure unperturbed_values is a NumPy array of type float64 for numerical stability
    unperturbed_values = np.array(unperturbed_values).astype(np.float64)
    
    # Replace infinite values in unperturbed_values with NaN to avoid invalid divisions
    unperturbed_values = np.where(np.isinf(unperturbed_values), np.nan, unperturbed_values)
    
    # Replace zero values in unperturbed_values with NaN to avoid division by zero
    unperturbed_values = np.where(unperturbed_values == 0, np.nan, unperturbed_values)
    
    # Perform element-wise division of perterbations by unperturbed_values
    normalized_values = perterbations / unperturbed_values

    return normalized_values