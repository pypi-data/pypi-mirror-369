import numpy as np
import inspect

def propagate(func, *args):

    # Get the names of the function's arguments so we know how many inputs it expects
    arg_names = list(inspect.signature(func).parameters.keys())

    # Make sure we got both a value and an error for every argument
    if len(args) != 2 * len(arg_names):
        raise ValueError(f"Expected value/error for each of {len(arg_names)} args, got {len(args)}")
    
    # Split into lists of values and errors, making sure they’re arrays
    vals_list = [np.atleast_1d(a) for a in args[0::2]]
    errs_list = [np.atleast_1d(e) for e in args[1::2]]
    
    # Number of data points (must be the same for all inputs)
    n = vals_list[0].size
    values = np.empty(n)
    errors = np.empty(n)

    # Small relative step for finite difference derivative
    delta_factor = 1e-8

    for i in range(n):

        # Get the i-th set of variable values (one from each input array)
        base_vals = [vals[i] for vals in vals_list]
        # Evaluate the function at this set of values
        f0 = func(*base_vals)
        # Store the result in the output array
        values[i] = f0
         
        # Start with zero total error
        err_sq = 0.0

        # Loop through each variable and its uncertainty for this data point
        for j, (val, sigma) in enumerate(zip(base_vals, [errs[i] for errs in errs_list])):
            if sigma == 0:
                continue # Skip if this variable has no uncertainty

            # Small step size for numerical derivative (scaled to variable size)
            h = delta_factor * max(abs(val), 1.0)

            # Create "plus" and "minus" versions of the variable to compute derivative
            plus_args = base_vals.copy()
            minus_args = base_vals.copy()
            plus_args[j] += h
            minus_args[j] -= h

            # Central difference: (f(x+h) - f(x-h)) / (2h)
            deriv = (func(*plus_args) - func(*minus_args)) / (2 * h)

            # Add the squared contribution from this variable
            err_sq += (deriv * sigma) ** 2
            
        # Final combined uncertainty
        errors[i] = np.sqrt(err_sq)

    return values, errors