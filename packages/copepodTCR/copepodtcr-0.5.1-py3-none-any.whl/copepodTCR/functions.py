#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import numpy as np
from itertools import combinations
import math
import random
from collections import Counter
import trimesh
import sys
from io import StringIO
import zipfile
from io import BytesIO
import pymc as pm
import arviz as az

import seaborn as sn
from matplotlib import pyplot as plt

import plotly.graph_objects as go
import plotly.io as pio


# # Setting seed
def set_seed(seed: int):
    """
    Sets the seed for both Python's random module and NumPy's random number generator.
    Call this once before running any stochastic functions for reproducibility.
    """
    random.seed(seed)
    np.random.seed(seed)


# # Functions for ITERS search

def factorial(num: "int") -> "int":

    """
    Returns factorial of the number.
    Used in function(combination).
    """

    if num == 0:
        return 1
    else:
        return num * factorial(num-1)

def combination(n: "int", k: "int") -> "int":

    """
    Returns number of possible combinations.
    Is dependent on function(factorial)
    Used in function(find_possible_k_values).
    """

    return factorial(n) // (factorial(k) * factorial(n - k))

def find_possible_k_values(n: "int", l: "int") -> "list[int]":

    """
    Returns possible iters given number of peptides (l) and number of pools (n).
    Is dependent on function(combination).
    """

    k_values = []
    k = 0
    
    while k <= n:
        c = combination(n, k)
        if c >= l:
            break
        k += 1

    while k <= n:
        if combination(n, k) >= l:
            k_values.append(k)
        else:
            break
        k += 1

    return k_values


# # Peptide overlap

def peptide_generation(
    protein: "str | list[str]",
    peptide_length: "int",
    peptide_shift: "int",
    protein_end: "bool" = False
) -> "list[str]":
    
    """
    Takes a protein or a list of proteins.
    Returns list with peptides generated from this protein with required parameters (length and shift length = peptide length - overlap length).
    """

    peptide_lst = []

    if isinstance(protein, str):
        for i in range(0, len(protein), peptide_shift):
            ps = protein[i:i+peptide_length]
            if len(ps) == peptide_length:
                peptide_lst.append(ps)
            else:
                if protein_end == True:
                    diff = peptide_length - len(ps)
                    ps = protein[i-diff:i-diff+peptide_length]
                    if peptide_lst[-1] != ps:
                        peptide_lst.append(ps)

    elif isinstance(protein, list):
        for pr in protein:
            for i in range(0, len(pr), peptide_shift):
                ps = pr[i:i+peptide_length]
                if len(ps) == peptide_length:
                    peptide_lst.append(ps)
                else:
                    if protein_end == True:
                        diff = peptide_length - len(ps)
                        ps = pr[i-diff:i-diff+peptide_length]
                        if peptide_lst[-1] != ps:
                            peptide_lst.append(ps)
    return peptide_lst


def string_overlap(str1: "str", str2: "str") -> "int":
    
    """
    Takes two peptides, returns length of their overlap.
    """
    
    overlap_len = 0
    for i in range(1, min(len(str1), len(str2)) + 1):
        if str1[-i:] == str2[:i]:
            overlap_len = i
    return overlap_len

def all_overlaps(strings: "list[str]") -> "Counter[int]":
    
    """
    Takes list of peptides, returns occurence of overlap of different lengths.
    """
    
    overlaps = []
    for i in range(len(strings) - 1):
        overlaps.append(string_overlap(strings[i], strings[i+1]))

    return Counter(overlaps)

def find_pair_with_overlap(strings: "list[str]", target_overlap: "int") -> "list[list[str]]":
    
    """
    Takes list of peptides and overlap length.
    Returns peptides with this overlap.
    """
    
    target = []
    for i in range(len(strings) - 1):  
        if string_overlap(strings[i], strings[i+1]) == target_overlap:
            target.append([strings[i], strings[i+1]])
    return target

def how_many_peptides(lst: "list[str]", ep_length: "int") -> "tuple[Counter[int], dict[str, int]]":
    """
    Takes list of peptides and expected epitope length.
    Returns 1) Counter object with number of epitopes shared across number of peptides;
    2) dictionary with all possible epitopes as keys and in how many peptides thet are present as values.
    """

    sequence_counts = dict()
    counts = []

    for peptide in lst:
        for i in range(0, len(peptide) - ep_length + 1):
            sequence = peptide[i:i+ep_length]
            if sequence in sequence_counts.keys():
                sequence_counts[sequence] += 1
            else:
                sequence_counts[sequence] = 1

    for key in sequence_counts.keys():
        counts.append(sequence_counts[key])
    counts = Counter(counts)

    return counts, sequence_counts


# # Pooling


### Bad addresses search
def bad_address_predictor(all_ns: "list[list[int]]") -> "list[list[int]]":
    
    """
    Takes list of addresses, searches for three consecutive addresses with the same union, removes the middle one.
    Returns list of addresses.
    """
    
    wb = all_ns.copy()
    
    for i in range(len(wb)-1, 1, -1):
        n1 = wb[i]
        n2 = wb[i-1]
        n3 = wb[i-2]
        if set(n1 + n2) == set(n2 + n3) or set(n1 + n2) == set(n1 + n3):
            wb.remove(n2)
    return wb

### Pooling
def pooling(
    lst: "list[str]",
    addresses: "list[list[int]]",
    n_pools: "int"
) -> "tuple[dict[int, list[str]], dict[str, list[int]]]":
    
    """
    Takes list of peptides, list of addresses, number of pools.
    Returns pools - list of peptides for each pool, and peptide_address - for each peptide its address.
    """
    
    pools = {key: [] for key in range(n_pools)}
    peptide_address = dict()

    for i in range(len(lst)):
        peptide = lst[i]
        peptide_pools = addresses[i]
        peptide_address[peptide] = peptide_pools
        for item in peptide_pools:
            pools[item].append(peptide)
    return pools, peptide_address


### Pools activation
def pools_activation(
    pools: "dict[int, list[str]]",
    epitope: "str"
) -> "list[int]":
    
    """
    Takes peptide pooling scheme (pools) and epitope.
    Returns which pools will be activated given this epitope.
    Is used in function(run_experiment).
    """
    
    activated_pools = []
    for key in pools.keys():
        for item in pools[key]:
            if epitope in item:
                activated_pools.append(key)
                    
    activated_pools = list(set(activated_pools))              
    return activated_pools


### Epitope - activated pools table
def epitope_pools_activation(
    peptide_address: "dict[str, list[int]]",
    lst: "list[str]",
    ep_length: "int"
) -> "dict[str, list[str]]":
    
    """
    Takes dictionary of peptide_addresses, list of peptides, epitope length.
    Returns activated pools for each possible epitope from peptides.
    Is used in function(run_experiment).
    """
    
    epitopes = []
    act_profile = dict()
    for item in lst:
        for i in range(len(item)):
            if len(item[i:i+ep_length]) == ep_length and item[i:i+ep_length] not in epitopes:
                epitopes.append(item[i:i+ep_length])
    for ep in epitopes:
        act = []
        for peptide in peptide_address.keys():
            if ep in peptide:
                act = act + list(peptide_address[peptide])
        act = sorted(list(set(act)))
        str_act = str(act)
        if str_act not in act_profile.keys():
            act_profile[str_act] = [ep]
        else:
            act_profile[str_act].append(ep)
    return act_profile

### Peptide determination

def peptide_search(
    lst: "list[str]",
    act_profile: "dict[str, list[str]]",
    act_pools: "list[int]",
    iters: "int",
    n_pools: "int",
    regime: "str"
) -> "tuple[list[str], list[str]] | None":
    
    """
    Takes activated pools and returns peptides and epitopes which led to their activation.
    Has two regimes: with and without dropouts.
    Is used in function(run_experiment).
    """
    
    if regime == 'without dropouts':
        act = str(sorted(list(act_pools)))
        epitopes = act_profile.get(act)
        if epitopes is not None:
            peptides = []
            for peptide in lst:
                if all(epitope in peptide for epitope in epitopes):
                    peptides.append(peptide)
            return peptides, epitopes
    elif regime == 'with dropouts':
        act = str(sorted(list(act_pools)))
        epitopes = act_profile.get(act)
        if len(act) == iters +1 and epitopes is not None:
            peptides = []
            for peptide in lst:
                if all(epitope in peptide for epitope in epitopes):
                    peptides.append(peptide)
            return peptides, epitopes
        else:
            rest = list(set(range(n_pools)) - set(act_pools))
            r = iters + 1 - len(act_pools)
            if r < 0:
                r = 0
            options = list(combinations(rest, r))
            possible_peptides = []
            possible_epitopes = []
            
            for option in options:
                act_try = act_pools + list(option)
                act_try = str(sorted(list(act_try)))
                epitopes = act_profile.get(act_try)
                if epitopes is not None:
                    possible_epitopes = possible_epitopes + epitopes
                    peptides = []
                    for peptide in lst:
                        if all(epitope in peptide for epitope in epitopes):
                            peptides.append(peptide)
                    possible_peptides = possible_peptides + peptides
            return list(set(possible_peptides)), list(set(possible_epitopes))

### Resulting table
def run_experiment(
    lst: "list[str]",
    peptide_address: "dict[str, list[int]]",
    ep_length: "int",
    pools: "dict[int, list[str]]",
    iters: "int",
    n_pools: "int",
    regime: "str"
) -> "pd.DataFrame":
    
    """
    Imitates experiment. Has two regimes: with and without dropouts.
    Takes list of peptides and runs experiment for every possible epitope.
    Returns activated pools, predicted peptides based on these activated pools.
    With dropouts imitates dropouts and returns number of possible peptides given each possible dropout combination.
    Is dependent on function(pools_activation), function(peptide_search), function(epitope_pools_activation).
    """
    
    act_profile = epitope_pools_activation(peptide_address, lst, ep_length)
    
    check_results = pd.DataFrame(columns = ['Peptide', 'Address', 'Epitope', 'Act Pools',
                                        '# of pools', '# of epitopes', '# of peptides', 'Remained', '# of lost',
                                           'Right peptide', 'Right epitope'])
    for peptide in lst:
        for i in range(len(peptide)):
            ep = peptide[i:i+ep_length]
            if len(ep) == ep_length:
                act = pools_activation(pools, ep)
                if regime == 'without dropouts':
                    peps, eps = peptide_search(lst=lst, act_profile=act_profile,
                                           act_pools = act,
                                           iters = iters, n_pools = n_pools,
                                           regime = 'without dropouts')
                    right_pep = str(peptide in peps)
                    right_ep = str(ep in eps)
                    row = {'Peptide':peptide, 'Address':str(peptide_address[peptide]), 'Epitope':ep,
                           'Act Pools':str(sorted(list(act))), '# of pools':len(act),
                           '# of epitopes':len(eps), '# of peptides':len(peps), 'Remained':'-', '# of lost':0,
                           'Right peptide':right_pep, 'Right epitope':right_ep}
                    check_results = pd.concat([check_results, pd.DataFrame(row, index = [0])])
                elif regime == 'with dropouts':
                    l = len(act)
                    for i in range(1, l+1):
                        lost = len(act) - i
                        lost_combs = list(combinations(act, i))
                        for lost_comb in lost_combs:
                            peps, eps = peptide_search(lst=lst, act_profile=act_profile,
                                           act_pools = list(lost_comb),
                                           iters = iters, n_pools = n_pools,
                                           regime = 'with dropouts')
                            right_pep = str(peptide in peps)
                            right_ep = str(ep in eps)
                
                            row = {'Peptide':peptide, 'Address':str(peptide_address[peptide]), 'Epitope':ep,
                                   'Act Pools':str(sorted(list(act))), '# of pools':len(act),
                                   '# of epitopes':len(eps), '# of peptides':len(peps),
                                   'Remained':str(list(lost_comb)), '# of lost':lost,
                                   'Right peptide':right_pep, 'Right epitope':right_ep}
                            check_results = pd.concat([check_results, pd.DataFrame(row, index = [0])])
    return check_results

## Functions for .stl files

def pick_engine():
    import trimesh.boolean

    # default engine is manifold3d
    try:
        import manifold3d  # noqa: F401
        return "manifold"
    except ImportError:
        pass

    # Other available engines
    available = set(trimesh.boolean._engines.keys())

    if "blender" in available:
        return "blender"

    raise RuntimeError(
        f"No boolean backend available. Install manifold3d or Blender."
        f"Available engines: {available}"
    )


def stl_generator(
    rows: "int",
    cols: "int",
    length: "float",
    width: "float",
    thickness: "float",
    hole_radius: "float",
    x_offset: "float",
    y_offset: "float",
    well_spacing: "float",
    coordinates: "list[tuple[int, int]]",
    engine: "str",
    marks: "int | bool" = False
) -> "Trimesh":
    """
    Returns a Trimesh of a 3D plate with holes at given coordinates.
    """

    hole_height = thickness + 2

    # Base plate
    plate_mesh = trimesh.creation.box(extents=[length, width, thickness])
    plate_mesh.apply_translation([length / 2, width / 2, thickness / 2])

    # Batch parameters
    batch_size = 40
    coordinate_batches = [coordinates[i:i + batch_size]
                          for i in range(0, len(coordinates), batch_size)]

    for batch in coordinate_batches:
        # Build all cylinders for this batch first
        cylinders = []
        for r, c in batch:
            i, j = r - 1, c - 1
            hole_x = x_offset + j * well_spacing
            hole_y = y_offset + i * well_spacing
            cyl = trimesh.creation.cylinder(radius=hole_radius, height=hole_height)
            cyl.apply_translation([hole_x, hole_y, thickness / 2])
            cylinders.append(cyl)

        # Union of cylinders in one call
        if len(cylinders) == 1:
            batch_mesh = cylinders[0]
        else:
            batch_mesh = trimesh.boolean.union(
                cylinders, engine=engine, check_volume=False
            )

        # Subtract the batch from the plate (one call)
        plate_mesh = plate_mesh.difference(
            batch_mesh, engine=engine, check_volume=False
        )

    # Optional marks: build once, subtract once
    if marks:
        mark_meshes = []
        mark_space = 0
        for i in range(marks):
            y = well_spacing * 0.5
            x = well_spacing * 0.5 + i + mark_space
            mark_space += 1
            mark = trimesh.creation.box(extents=[1, 1, hole_height / 3])
            mark.apply_translation([x, y, thickness / 3])
            mark_meshes.append(mark)

        if mark_meshes:
            if len(mark_meshes) == 1:
                marks_union = mark_meshes[0]
            else:
                marks_union = trimesh.boolean.union(
                    mark_meshes, engine=engine, check_volume=False
                )
            plate_mesh = plate_mesh.difference(
                marks_union, engine=engine, check_volume=False
            )

    return plate_mesh

def pools_stl(
    peptides_table: "pd.DataFrame",
    pools: "pd.DataFrame",
    engine: "str",
    rows: "int" = 16,
    cols: "int" = 24,
    length: "float" = 122.10,
    width: "float" = 79.97,
    thickness: "float" = 1.5,
    hole_radius: "float" = 4.0 / 2,
    x_offset: "float" = 9.05,
    y_offset: "float" = 6.20,
    well_spacing: "float" = 4.5,
    hole16: "bool" = False
) -> "dict[str, Trimesh]":
    
    """
    Takes peptide pooling scheme.
    Returns dictionary with mesh objects (3D plate with holes), where one plate is one value, and its key is a pool index.
    Is dependent on function(stl_generator).
    """

    meshes_list = dict()

    for pool_N in set(pools.index):
        coordinates = []
        for peptide in pools['Peptides'].iloc[pool_N].split(';'):
            row_value = int([(x, peptides_table.columns[y]) for x, y in zip(*np.where(peptides_table.values == peptide))][0][0]+1)
            column_value = int([(x, peptides_table.columns[y]) for x, y in zip(*np.where(peptides_table.values == peptide))][0][1])
            coordinates.append([row_value, column_value])
        if hole16:
            coordinates = coordinates + [[16, 24]]
        
        name = 'pool' + str(pool_N+1)
        
        m = stl_generator(rows, cols, length, width, thickness, hole_radius, x_offset, y_offset, well_spacing,
                 coordinates, marks = pool_N+1, engine = engine)
        meshes_list[name] = m
    return meshes_list

def zip_meshes_export(
    meshes_list: "dict[str, Trimesh]"
) -> "None":

    """
    Takes a dictionary with mesh objects.
    Exports a .zip file with stl files generated from these mesh objects.
    """

    zip_filename = 'Pools_stl.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for key in meshes_list.keys():
            stl_filename = f'{key}.stl'
            meshes_list[key].export(stl_filename)
            zipf.write(stl_filename)
            
def zip_meshes(
    meshes_list: "dict[str, Trimesh]"
) -> "BytesIO":

    """
    Takes a dictionary with mesh objects.
    Returns a .zip file with stl files generated from these mesh objects.
    """

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for key in meshes_list.keys():
            stl_buffer = BytesIO()
            meshes_list[key].export(stl_buffer, file_type='stl')
            stl_buffer.seek(0)
            zipf.writestr(f'{key}.stl', stl_buffer.read())
    zip_buffer.seek(0)
    return zip_buffer


# # Bayesian Model

### Activation model
def activation_model(
    obs: "list[float] | np.ndarray",
    n_pools: "int",
    inds: "list[int] | np.ndarray",
    neg_control=None,
    neg_share=None,
    cores=1
):

    """
    Takes a list with observed data (obs), number of pools (n_pools), and indices for the observed data (inds).
    Optionally, takes also negative control data (neg_control) and the expected share of negative pools (neg_share).
    Builds a Bayesian mixture model with two components (positive, negative).
    Fits the model to the data using MCMC sampling (PyMC).
    
    Returns:
    - model: PyMC model object.
    - fig: posterior predictive plot generated via ArviZ.
    - probs: dataframe with posterior mean probability of each pool being negative.
    - n_c: normalized control values used for model training.
    - idata_alt: full posterior sampling trace (InferenceData object).
    - [p_mean, n_mean]: posterior means of the offset and negative component.
    """
    
    coords = dict(pool=range(n_pools), component=("positive", "negative"))
    if neg_share is None:
        neg_share = 0.5
    if neg_control is None:
        neg_control = sorted(obs)[:inds.count(0)]
    if np.min(neg_control) > np.max(obs):
        obs = obs/np.max(neg_control)
        neg_control = neg_control/np.max(neg_control)
    else:
        neg_control = neg_control/np.max(obs)
        obs = obs/np.max(obs)

    with pm.Model(coords=coords) as model:
    
        negative = pm.TruncatedNormal(
            "negative",
            mu=0,
            sigma=1,
            lower=0.0,
            upper=1.0,
        )

        negative_obs = pm.TruncatedNormal(
            "negative_obs",
            mu=negative,
            sigma=0.1,
            lower=0.0,
            upper=1.0,
            observed=neg_control,
        )

        # Offset such that negative + offset <= 1
        offset_proportion = pm.Beta("offset_proportion", alpha=5, beta=2)
        offset = pm.Deterministic("offset", (1 - negative) * offset_proportion)
        #offset = pm.TruncatedNormal('offset', mu = 0.6, sigma = 0.1, upper = 1, lower = 0)

        #positive = pm.Deterministic("positive", negative + offset, upper = 0, lower = 1)
        positive = pm.Deterministic("positive", negative + offset)
    
        p = pm.Beta("p", alpha=neg_share * 100, beta=(1 - neg_share) * 100)
        component = pm.Bernoulli("assign", p, dims="pool")

        mu_pool = negative * component + positive * (1 - component)
    
        sigma_neg = pm.HalfNormal("sigma_neg", 0.5)
        #sigma_delta = pm.Exponential("sigma_delta", 0.5)
        sigma_pos = pm.HalfNormal("sigm_pos", 0.2)
        sigma_pool = sigma_pos * (1 - component) + sigma_neg * component
        
        pool_dist = pm.TruncatedNormal(
            "pool_dist",
            mu=mu_pool,
            sigma = sigma_pool,
            lower=0.0,
            upper=1.0,
            dims="pool",
        )
    
        # Likelihood, where the data indices pick out the relevant pool from pool
        sigma_data = pm.Exponential("sigma_data", 1.0)
        pm.TruncatedNormal(
            "lik", mu=pool_dist[inds], sigma=sigma_data, observed=obs, lower=0.0, upper=1.0
        )

        idata_alt = pm.sample(cores = cores)

    with model:
        posterior_predictive = pm.sample_posterior_predictive(idata_alt)

    ax = az.plot_ppc(posterior_predictive, num_pp_samples=100, colors = ['#015396', '#FFA500', '#000000'])

    posterior = az.extract(idata_alt)
    n_mean = float(posterior["negative"].mean(dim="sample"))
    p_mean = float(posterior["offset"].mean(dim="sample"))

    posterior_p_mean = posterior["p"].mean(dim="sample").item()
    print(f"Posterior mean of p: {posterior_p_mean:.3f}")

    probs = posterior["assign"].mean(dim="sample").to_dataframe()

    ## only probs are important
    return model, ax, probs, neg_control, idata_alt, [p_mean, n_mean]


def peptide_probabilities(sim: "pd.DataFrame", probs: "pd.DataFrame") -> "pd.DataFrame":

    """
    Takes a dataframe with probabilities (generated by function(activation_model)) and simulation without drop-outs (generated by function(run_experiment)).
    Returns a probability of each peptide in a DataFrame.
    """

    sim_add = sim[['Peptide', 'Address', 'Act Pools']]
    sim_add = sim_add.drop_duplicates()
    
    for i in range(len(sim_add)):
        sim_add.iloc[i, 1] = [int(i) for i in sim_add['Address'].iloc[i][1:-1].split(',')]
        sim_add.iloc[i, 2] = [int(i) for i in sim_add['Act Pools'].iloc[i][1:-1].split(',')]
    sim_add['Probability'] = 0.0
    sim_add['Activated'] = 0
    sim_add['Non-Activated'] = 0
    
    for i in range(len(sim_add)):
        ad = sim_add.iloc[i, 2]
        mul = []
        act = []
        non_act = []
        for y in range(len(probs)):
            p = probs['assign'].iloc[y]
            if y not in ad:
                mul.append(p)
            else:
                mul.append(1-p)
                if p <= 0.5:
                    act.append(y)
                else:
                    non_act.append(y)
        probability = np.prod(mul)
        sim_add.iloc[i, 3] = probability
        sim_add.iloc[i, 4] = len(act)
        sim_add.iloc[i, 5] = len(non_act)
    sim_add['Probability'] = sim_add['Probability']/sum(sim_add['Probability'])
    #sim_add = sim_add.sort_values(by = 'Probability', ascending = False)
    return sim_add

def results_analysis(
    peptide_probs: "pd.DataFrame",
    probs: "pd.DataFrame",
    sim: "pd.DataFrame"
) -> "tuple[int, str, list[str] | str, list[str]]":

    """
    Takes a dataframe with probabilities (generated by function(activation_model)), simulation without drop-outs (generated by function(run_experiment)), and probabilities for each peptide generated by function(peptide_probabilities).
    Returns resulting peptides.
    """
    
    ep_length = len(sim['Epitope'].iloc[0])
    all_lst = list(peptide_probs['Peptide'].drop_duplicates())
    c, _ = how_many_peptides(all_lst, ep_length)
    normal = max(c, key=c.get)
    
    act_pools = []
    for i in range(len(probs)):
        if probs['assign'].iloc[i] < 0.5:
            act_pools.append(i)

    end_peptides = [peptide_probs['Peptide'].iloc[0], peptide_probs['Peptide'].iloc[-1]]
    peptide_probs = peptide_probs.sort_values(by = 'Probability', ascending=False)

     ## Whether top Normal peptides share an epitope
    topNormal = list(set(list(peptide_probs['Peptide'])[:normal]))
    epitope_check = [False]*(len(topNormal)-1)
    for i in range(len(topNormal[0])):
        check = topNormal[0][i:i+ep_length]
        for y in range(len(topNormal[1:])):
            if len(check) == ep_length and check in topNormal[1:][y]:
                epitope_check[y] = True
    epitope_check = all(epitope_check)
    
    ## Whether top Normal results do not have drop outs
    drop_check = [True]*len(topNormal)
    for i in range(len(topNormal)):
        check = peptide_probs['Non-Activated'][peptide_probs['Peptide'] == topNormal[i]].values[0]
        if check == 0:
            drop_check[i] = False
    drop_check = all(drop_check)

    ## Whether top Normal peptides are located at the end of the protein:
    end_check = [False]
    for p in topNormal:
        if p in end_peptides:
            end_check[0] = True
            end_check.append(p)

    peptide_address = dict()
    for p in all_lst:
        address = peptide_probs['Address'][peptide_probs['Peptide'] == p].iloc[0]
        peptide_address[p] = address

    ## If all pools are marked as activated, then the results are compromised
    if len(act_pools) == len(probs):
        notification = 'All pools were activated'
        return len(act_pools), notification, [], []

    ## If zero pools are marked as activated, then the results are negative
    elif len(act_pools) == 0:
        notification = 'Zero pools were activated'
        return len(act_pools), notification, [], []

    ## If both checks hold:
    elif epitope_check == True and drop_check == False:
        notification = 'No drop-outs were detected'
        return len(act_pools), notification, topNormal, topNormal

    ## If both checks do not hold:
    elif epitope_check == False and drop_check == True:
        act_profile = epitope_pools_activation(peptide_address, all_lst, ep_length)
        iters = len(peptide_probs['Address'].iloc[0])
        n_pools = len(probs)
        act_number = iters + normal -1
        peptides, epitopes = peptide_search(all_lst, act_profile, act_pools, iters, n_pools, 'with dropouts')
        if end_check[0] == True:
            notification = 'Cognate peptide is located at one of the ends of the list'
            return len(act_pools), notification, end_check[-1], peptides
        else:
            notification = 'Cognate peptides are not found'
            return len(act_pools), notification, [], peptides
        
    ## If epitope is shared, but drop-outs are detected
    elif epitope_check == True and drop_check == True:
        act_profile = epitope_pools_activation(peptide_address, all_lst, ep_length)
        iters = len(peptide_probs['Address'].iloc[0])
        n_pools = len(probs)
        act_number = iters + normal -1
        if act_number > len(act_pools):
            notification = 'Drop-out was detected'
            peptides, epitopes = peptide_search(all_lst, act_profile, act_pools, iters, n_pools, 'with dropouts')
            return len(act_pools), notification, topNormal, peptides
        else:
            notification = 'False positive was detected'
            return len(act_pools), notification, [], []

    ## If epitope is not shared, but drop-outs are not detected
    elif epitope_check == False and drop_check == False:
        act_profile = epitope_pools_activation(peptide_address, all_lst, ep_length)
        iters = len(peptide_probs['Address'].iloc[0])
        n_pools = len(probs)
        act_number = iters + normal -1
        peptides, epitopes = peptide_search(all_lst, act_profile, act_pools, iters, n_pools, 'with dropouts')
        ## if peptide is first or last one in the list:
        if end_check[0] == True:
            notification = 'Cognate peptide is located at one of the ends of the list'
            return len(act_pools), notification, end_check[-1], peptides
        else:
            notification = 'No drop-outs were detected'
            return len(act_pools), notification, topNormal, peptides
    else:
        notification = 'Analysis error'
        return len(act_pools), notification, [], []


# # Simulated data

###Peptides generation
def random_amino_acid_sequence(length: "int") -> "str":
    '''
    Takes the length (integer).
    Returns random amino acid sequence of desired length.
    '''
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
    return ''.join(random.choice(amino_acids) for _ in range(length))

### Simulation
def simulation(
    mu_off: "float",
    sigma_off: "float",
    mu_n: "float",
    sigma_n: "float",
    r: "int",
    sigma_p_r: "float",
    sigma_n_r: "float",
    n_pools: "int",
    p_shape: "int",
    pl_shape: "int",
    low_offset: "float",
    cores: "int" = 1
) -> "tuple[list[float], list[float], list[float], list[float], list[float]]":
    """
    Takes parameters for offset, positive/negative signal distributions, number of pools,
    replication count (r), and simulation noise levels.
    Returns simulated measurement values for positive, low-positive, and negative pools (with replicates),
    control measurements, and the posterior means of the offset and negative baseline.
    """

    n_shape = n_pools-p_shape-pl_shape
    with pm.Model() as simulation:
        # offset
        offset = pm.TruncatedNormal("offset", mu=mu_off, sigma=sigma_off, lower=0, upper=100)
    
        # Negative
        n = pm.TruncatedNormal('n', mu=mu_n, sigma=sigma_n, lower=0, upper=100)
        # Positive
        raw_p = n + offset
        p = pm.Deterministic("p", pm.math.clip(raw_p, 0, 100))
        # Low positive
        p_low = pm.Deterministic("p_low", p*low_offset)

        # Negative pools
        n_pools = pm.TruncatedNormal('n_pools', mu=n, sigma=sigma_n, lower=0, upper=100, shape = n_shape)
        inds_n = list(range(n_shape))*r
        n_shape_r = n_shape*r

        # Positive pools
        p_pools = pm.TruncatedNormal('p_pools', mu=p, sigma=sigma_off, lower=0, upper=100, shape = p_shape)
        inds_p = list(range(p_shape))*r
        p_shape_r = p_shape*r

        # Low positive pools
        pl_pools = pm.TruncatedNormal('pl_pools', mu=p_low, sigma=sigma_off, lower=0, upper=100, shape = pl_shape)
        inds_pl = list(range(pl_shape))*r
        pl_shape_r = pl_shape*r

        # With replicas
        p_pools_r = pm.TruncatedNormal('p_pools_r', mu=p_pools[inds_p], sigma=sigma_p_r, lower=0, upper=100, shape=p_shape_r)
        pl_pools_r = pm.TruncatedNormal('pl_pools_r', mu=pl_pools[inds_pl], sigma=sigma_p_r, lower=0, upper=100, shape=pl_shape_r)
        n_pools_r = pm.TruncatedNormal('n_pools_r', mu=n_pools[inds_n], sigma=sigma_n_r, lower=0, upper=100, shape=n_shape_r)

        # negative control
        n_control = pm.TruncatedNormal('n_control', mu=n, sigma=sigma_n, lower=0, upper=100, shape=r)

        trace = pm.sample(draws=1, cores = cores)
        
    p_results = trace.posterior.p_pools_r.mean(dim="chain").values.tolist()[0]
    pl_results = trace.posterior.pl_pools_r.mean(dim="chain").values.tolist()[0]
    n_results = trace.posterior.n_pools_r.mean(dim="chain").values.tolist()[0]
    n_control = trace.posterior.n_control.mean(dim="chain").values.tolist()[0]

    n_mean = float(trace.posterior.n.mean())
    p_mean = float(trace.posterior.offset.mean())

    return p_results, pl_results, n_results, n_control, [p_mean, n_mean]

# # Plotting results

def poolplot(probs: "pd.DataFrame", cells: "list[float]", inds: "list[int]", most: "list[str]"):

    """
    Returns a scatterplot with pool indices on X axis and log10 of percentage of activated T cells on Y axis.
    Activated pools (according to the model results) are plotted green, others are gray.
    """

    plt.figure(figsize=(8, 4))
    
    # Activated pools with probabilty <0.5
    inds_act = set(probs[probs['assign'] < 0.5].index)
    labels = ['act' if ind in inds_act else 'non-act' for ind in inds]
    palette = {'act': '#00A000', 'non-act': '#C1C1CA'}
    edgecolors = ['#00A000' if ind in inds_act else '#C1C1CA' for ind in inds]

    ax = sn.scatterplot(y=np.log10(cells), x=inds, s=100, hue=labels,
                        alpha=0.5, legend=False, palette=palette, edgecolors = edgecolors)
    
    if len(most) == 2:
        ax.set_title(f"{most[0]} or {most[1]}", fontsize=8)
    ax.set_ylabel("Log10 of activated T cell percentage", fontsize=8)
    ax.set_xlabel("Pools", fontsize=14)
    plt.xticks(inds)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    plt.tight_layout()

def bubbleplot(df: "pd.DataFrame"):

    """
    Returns a bubbleplot with each peptide plotted as one bubble, its size = # of activated pools - # of non-activated pools in its address.
    Position of the peptide in the protein is plotted along the X axis, its probability is along the Y axis.
    """

    df['s'] = (df['Activated'] - df['Non-Activated'])
    df = df[df['s'] > 0]
    
    plt.figure(figsize=(12, 4))
    jitter_strength = 0.2
    x_j = list(df.reset_index().index/5) + np.random.normal(0, jitter_strength, len(list(df.index/5)))
    plt.scatter(x_j, (df['Probability']), s=df['s']*100, alpha=0.5, color = '#00A000')
    #plt.ylim(-0.05)
    plt.ylim(-0.05, max(df['Probability'])+0.1)
    plt.xlabel('Peptide position in the protein')
    plt.ylabel('Peptide probability')
    plt.tight_layout()

def hover_bubbleplot(df: "pd.DataFrame"):

    """
    Returns interactive version of the bubbleplot.
    """

    df["s"] = df["Activated"].astype(float) - df["Non-Activated"].astype(float)
    df = df[df["s"] > 0].reset_index(drop=True)

    n = len(df)
    jitter_strength = 0.2
    x_j = np.arange(n) / 5.0 + np.random.normal(0, jitter_strength, n)

    sizes = (df["s"] * 10.0).to_numpy()
    y = df["Probability"].astype(float).to_numpy()

    # Prepare custom data for hover
    # Address may be list-like; stringify for stable display
    peptide = df["Peptide"].astype(str).to_numpy()
    address = df["Address"].apply(lambda v: str(v)).to_numpy()
    custom = np.column_stack([peptide, address])

    fig = go.Figure(
        data=[
            go.Scatter(
                x=x_j,
                y=y,
                mode="markers",
                marker=dict(size=sizes, opacity=0.5, color="#00A000"),
                customdata=custom,
                hovertemplate=(
                    "Peptide: %{customdata[0]}<br>"
                    "Address: %{customdata[1]}<br>"
                    "Probability: %{y:.4f}<br>"
                    "<extra></extra>"
                ),
            )
        ]
    )

    fig.update_layout(
        width=1000,
        height=350,
        xaxis_title="Peptide position in the protein",
        yaxis_title="Peptide probability",
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=10, b=40),
        xaxis=dict(
        showline=True,
        linecolor="black",
        linewidth=1,
        showgrid=False,
        zeroline=False
        ),
        yaxis=dict(
        showline=True,
        linecolor="black",
        linewidth=1,
        showgrid=False,
        zeroline=False
        )
    )
    fig.update_yaxes(range=[-0.05, float(df["Probability"].max()) + 0.1])

    return fig