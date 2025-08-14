"""
Custom functions for handling implementation of range of mass 
prior distributions.

Alexander Papadopoulos
"""
import os
import gwcosmo
import sys
import importlib.util
import bilby
import numpy as np
import gwcosmo.prior.priors as priors



def extract_parameters_from_instance(instance):
    # Get the __init__ method of the class
    init_method = instance.__init__

    # Get the names of parameters from the __init__ method
    parameter_names = list(init_method.__code__.co_varnames[1:])

    # Create a dictionary of parameters and their values
    parameters = {name: getattr(instance, name) for name in parameter_names}

    return parameters

def multipeak_constrained_parameters(params):
    # Shallow copy of param dictionary
    converted_params = params.copy()

    # Define dummy constraint prior
    converted_params['peak_constraint'] = params['mu_g_high'] - params['mu_g_low']
    
    return converted_params


def mass_model_selector(model, parser):

    # Assign mass model from paser output or return error
    if model == 'BBH-powerlaw':
        mass_priors = priors.BBH_powerlaw()
    elif model == 'NSBH-powerlaw':
        mass_priors = priors.NSBH_powerlaw()
    elif model == 'BBH-powerlaw-gaussian':
        mass_priors = priors.BBH_powerlaw_gaussian()
    elif model == 'NSBH-powerlaw-gaussian':
        mass_priors = priors.NSBH_powerlaw_gaussian()
    elif model == 'BBH-broken-powerlaw':
        mass_priors = priors.BBH_broken_powerlaw()
    elif model == 'NSBH-broken-powerlaw':
        mass_priors = priors.NSBH_broken_powerlaw()
    elif model == 'BBH-multi-peak-gaussian':
        mass_priors = priors.BBH_multi_peak_gaussian()
    elif model == 'NSBH-multi-peak-gaussian':
        mass_priors = priors.NSBH_multi_peak_gaussian()
    elif model == 'BBH-broken-powerlaw-multi-peak-gaussian':
        mass_priors = priors.BBH_broken_powerlaw_multi_peak_gaussian()
    elif model == 'NSBH-broken-powerlaw-multi-peak-gaussian':
        mass_priors = priors.NSBH_broken_powerlaw_multi_peak_gaussian()
    elif model == 'BNS':
        mass_priors = priors.BNS()
    elif model == 'multipopulation_pairing':
        mass_priors = priors.multipopulation_pairing_func()
    elif model == 'multipopulation_pairing_broken':
        mass_priors = priors.multipopulation_pairing_func_broken()
    else:
        parser.error('Unrecognized mass model')

    return mass_priors

def peaks_sampling_constraint(prior_dict):

    """
    Function to set up constraint prior dictionary for multi-peak mass prior in sampling method
    """

    # constraint for mu_g_low sampling and mu_g_high fixed
    if (type(prior_dict['mu_g_low']) in {bilby.core.prior.Uniform,bilby.core.prior.Gaussian,bilby.core.prior.LogUniform}) & (type(prior_dict['mu_g_high']) == float):
        if prior_dict['mu_g_low'].maximum > prior_dict['mu_g_high']:
            raise ValueError(f"Value for maximum lower peak {prior_dict['mu_g_low'].maximum} is greater than fixed upper peak {prior_dict['mu_g_high']}.")
    # constraint for mu_g_low fixed and mu_g_high sampling
    elif (type(prior_dict['mu_g_high']) in {bilby.core.prior.Uniform,bilby.core.prior.Gaussian,bilby.core.prior.LogUniform}) & (type(prior_dict['mu_g_low']) == float):
        if prior_dict['mu_g_low'] > prior_dict['mu_g_high'].minimum:
            raise ValueError(f"Value for minimum upper peak {prior_dict['mu_g_high'].minimum} is lower than fixed lower peak {prior_dict['mu_g_low']}.")
    # constraint for mu_g_low fixed and mu_g_high fixed
    elif(type(prior_dict['mu_g_high']) == float) & (type(prior_dict['mu_g_low']) == float): 
        if prior_dict['mu_g_low'] > prior_dict['mu_g_high']:
            raise ValueError(f"Value for lower peak {prior_dict['mu_g_low']} is greater than upper peak {prior_dict['mu_g_high']}.")
    # constraint for mu_g_low sampling and mu_g_high sampling with constrained prior
    else :
        prior_dict = bilby.core.prior.PriorDict(prior_dict, conversion_function = multipeak_constrained_parameters)
        prior_dict['peak_constraint'] = bilby.core.prior.Constraint(minimum = 0, maximum = 5000)

    return prior_dict

    
def peaks_grid_constraint(constraint_grid, values, parameter_grid, fixed_params):
        """
        Function to remove parameter space that does not follow constraint for multi-peak mass prior in gridded method
        """
        
        # constraint for mu_g_low sampling and mu_g_high fixed
        if ('mu_g_low' in parameter_grid.keys()) & ('mu_g_high' in fixed_params.keys()):
            if np.max(parameter_grid['mu_g_low']) > fixed_params['mu_g_high']:
                raise ValueError(f"Value for maximum lower peak {np.max(parameter_grid['mu_g_low'])} is greater than fixed upper peak {fixed_params['mu_g_high']}.")
        # constraint for mu_g_low fixed and mu_g_high sampling
        elif ('mu_g_high' in parameter_grid.keys()) & ('mu_g_low' in fixed_params.keys()):
            if np.min(parameter_grid['mu_g_high']) < fixed_params['mu_g_low']:
                raise ValueError(f"Value for minimum upper peak {np.min(parameter_grid['mu_g_high'])} is less than fixed lower peak {fixed_params['mu_g_low']}.")
        # constraint for mu_g_low fixed and mu_g_high fixed
        elif ('mu_g_low' in fixed_params.keys()) & ('mu_g_high' in fixed_params.keys()): 
            if fixed_params['mu_g_low'] > fixed_params['mu_g_high']:
                raise ValueError(f"Value for lower peak {fixed_params['mu_g_low']} is greater than upper peak {fixed_params['mu_g_high']}.")
        else:
            names  = list(parameter_grid.keys())
            idx_low = names.index('mu_g_low')
            idx_high = names.index('mu_g_high')
            mask = [x[idx_high] < x[idx_low] for x in values]
            shape = constraint_grid.shape
            reshaped_mask = np.array(mask).reshape(shape)
            constraint_grid[reshaped_mask] = -np.inf

        return constraint_grid
