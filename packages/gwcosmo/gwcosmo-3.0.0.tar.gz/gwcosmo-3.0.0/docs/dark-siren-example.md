
# Dark siren example

We provide here the complete command line for a dark siren analysis of a few CBCs detected and selected during O1-O2-O3. The information used for this analysis is the mass distribution of the set of CBCs together with their 3D location on the sky (right ascension, declination and luminosity distance).
We will assume you have a login at the CIT cluster of the form `albert.einstein`. All paths are relative to this cluster. The analysis runs the code `gwcosmo_dark_siren_posterior` and it assumes that `gwcosmo` was installed inside a `conda` environment in `/home/albert.einstein/.conda/envs/gwcosmo/`.

Glossary:

- approximant: or waveform approximant, this is the name of the GW model used to analyse a single event. For instance, IMRPhenomXPHM, IMRPhenomPv2...
- PE: means Parameter Estimation. It is the analysis performed on each single event and leads to the production of posterior samples of the event's characteristics (m1, m2, luminosity distance, spins...)
- PE samples: the posterior samples computed by the PE analysis
- injections: this term corresponds to fake GW events injected in the noise streams of the interferometers, in realistic conditions (noise levels, uptimes, duty cycles...). Those injections are needed to compute the selection effect, allowing an unbiased analysis
- spectral analysis: we assume that the redshifts of the GW sources follow a uniform-in-comoving-volume distribution. It's a non-informative prior choice
- dark sirens analysis: we assume that the redshifts of the GW sources follow a redshift distribution informed by the GLADE+ catalog in the K-band. At high redshifts, when the catalog does not contain any galaxy, a uniform-in-comoving-volume distribution is assumed, like in the spectral case
- LOS: Line Of Sight redshift prior. This is the prior quantity $p(z|\Omega_j)$ used in the analysis, where $\Omega_j$ denotes the Healpix pixel $j$ and $z$ is the redshift. In a spectral analysis, the function $p(z|\Omega_j)$ provides a uniform-in-comoving-volume distribution. In a dark siren analysis, $p(z|\Omega_j)$ contains the GLADE+ information.

The script `job.sub` below must be given to `condor` with the command `condor_submit job.sub`. In the script we define the variable `environment`: careful, its definition can vary according to the cluster on which you are running the analysis. The version here runs well at CIT as of 20250731.

``` console
universe = vanilla
environment = "HOME=/home/albert.einstein/ PATH=/home/albert.einstein/.conda/envs/gwcosmo/bin OMP_NUM_THREADS=1"

executable = run.sh
arguments =

output = condor.out
error = condor.err
log = condor.log

accounting_group = ligo.prod.o4.cbc.hubble.gwcosmo
accounting_group_user = albert.einstein
request_cpus   = 1 
request_memory = 60 gb
request_disk   = 5 gb
batch_name = example

queue
```

In this example, `condor` will execute the bash script `run.sh` that actually starts the gwcosmo analysis. In this first example, we start a gridded analysis (i.e. all hyper parameters are fixed and the posteriors are computed on a H0 grid) and we use the following script `run.sh`:

``` console
#!/bin/bash

exe=gwcosmo_dark_siren_posterior

LOS=GLADE+_Kband.hdf5
injections=inj_SNR9_det_frame_2e6_IFAR_minus_1.h5
posterior=events.json

# CBC
params=bpl_dip_dict_fixed.json
mass_model=multipopulation_pairing_broken
gravity_model=GR
method=gridded

name=gwcosmo3_example
ifar=4 # IFAR cut for the selection effect
snr=10 # SNR cut for the selection effect

cmd="${exe} --method ${method} \
        --posterior_samples ${posterior} \
        --LOS_catalog ${LOS} \
        --injections ${injections} \
        --parameter_dict ${params} \
        --mass_model ${mass_model} \
        --gravity_model ${gravity_model} \
        --redshift_evolution Madau \
        --snr ${snr} \
        --ifar ${ifar} \
        --min_pixels 25 \
        --outputfile pH0_${method}_${name}"

echo ${cmd}
echo "Executing command..."
echo ${cmd} | /bin/bash
```

In case you want to run a full run with a nested sampler (here we use `nessai`), you should set the number of CPUs to a higher value in file `job.sub`, for instance `request_cpus = 16`. Then you need to run this script `run.sh`:

``` console
#!/bin/bash

exe=gwcosmo_dark_siren_posterior

LOS=GLADE+_Kband.hdf5
injections=inj_SNR9_det_frame_2e6_IFAR_minus_1.h5
posterior=events.json

params=bpl_dip_dict.json
mass_model=multipopulation_pairing_broken
gravity_model=GR
method=sampling

name=gwcosmo3_example
ifar=4 # IFAR cut for the selection effect
snr=10 # SNR cut for the selection effect

cmd="${exe} --method ${method} \
        --posterior_samples ${posterior} \
        --LOS_catalog ${LOS} \
        --injections ${injections} \
        --parameter_dict ${params} \
        --mass_model ${mass_model} \
        --gravity_model ${gravity_model} \
        --redshift_evolution Madau \
        --snr ${snr} \
        --ifar ${ifar} \
        --min_pixels 25 \
        --outputfile pH0_${method}_${name} \
        --sampler nessai --nlive 1000 --dlogz 0.1 --npool 16"

echo ${cmd}
echo "Executing command..."
echo ${cmd} | /bin/bash
```

Several input files are needed for the analysis.

## The posteriors of the GW events (`--posterior_samples`)


The file `events.json` contains all is needed about the events used in the analysis. The json structure is a list of each event characteristics:

``` json
"GW190814_211039": {
        "posterior_file_path": "GW190814_211039.h5",
        "PEprior_kind": "m1d_m2d_uniform_dL_square_PE_priors",      
        "samples_field": "C01:IMRPhenomXPHM",
        "skymap_path": "GW190814_211039_C01:IMRPhenomXPHM.fits",
        "use_event": "True"
    },
"GW191105_143521": {...
```

For each event, there are several **mandatory** fields:

- `posterior_file_path`: it provides the path to the file containing the PE samples of the events In this file, samples may be available for different choices of waveform approximants
- `skymap_path`: it provides the path to the `fits` file containing probability skymap of the event
- `samples_field`: it tells gwcosmo to use a specific waveform approximant as for most of the events, the posterior file contains samples corresponding to different waveforms: in this case, the posterior file is a multi-analysis file. When using a single-analysis file, this json field is ignored and the analysis will run with the samples in the file.

and **optional** fields:

- `PEprior_kind`: this field tells gwcosmo which PE prior was used in the PE analysis. gwcosmo needs this information for the likelihood computation. If this field is not provided, gwcosmo checks the PE file with the requested approximant as in principle, the PE prior is also provided in the PE file. If no prior is found, the code stops and you will have to provide the information: see [section PE prior](#The-PE-prior)
- `use_event`: set this field to "False" if you want to skip this event in the analysis


### The PE prior

In the case there is no PE prior object in the PE file, corresponding to the approximant you requested, you need to tell gwcosmo how to correct for the PE prior used in the PE analysis. Note that **gwcosmo needs the PE prior on the detector-frame masses m1, m2 and luminosity distance**. You need to know what prior was used. gwcosmo has some pre-defined PE priors, that you can use by setting the field `PEprior_kind` to the name of the PE prior. The priors available in gwcosmo are:
- `m1d_m2d_uniform_dL_square_PE_priors`: if the PE samples used a 2D uniform distribution for both masses and $p(D_L) \propto D_L^2$
- `chirp_det_frame_q_uniform_dL_square_PE_priors`: if the PE samples used a 2D uniform distribution in detector-frame chirp mass and mass ratio, and $p(D_L) \propto D_L^2$
- `chirp_det_frame_q_uniform_dL_LogUniform_PE_priors`: if the PE samples used a 2D uniform distribution in detector-frame chirp mass and mass ratio, and $p(D_L) \propto 1/D_L$
- `m1d_m2d_uniform_dL_uniform_merger_rate_in_source_comoving_frame_PE_priors`: if the PE samples used a 2D uniform distribution for both masses and $p(D_L)\propto |\partial z/\partial D_L|\frac{\mathrm{d}V_c}{\mathrm{d}z}\frac{1}{1+z}$. The underlying cosmology is a flat $\Lambda$CDM with $H_0=67.9$ km/s/Mpc and $\Omega_m=0.3065$. If you want to use another cosmology, you will have to modify this part of the code (posterior_samples.py) or to provide a PE prior file (see below)

As an example, you can see that in file `events.json`, the event `GW190814_211039` will be analysed assuming a 2D uniform (m1,m2) and $p(D_L)\propto D_L^2$ as we have set `"PEprior_kind": "m1d_m2d_uniform_dL_square_PE_priors"`.

In the case the event you want to use in a gwcosmo analysis, has PE samples obtained with another type of PE prior, you have to provide a python file to gwcosmo. This file has to declare a class called `PE_priors`. For example, you have PE samples obtained with uniform priors in (Mc_det,q) and $p(D_L)\propto D_L^2$. You need to compute the probability for $p(m1_det,m2_det,D_L)$ from $p(Mc_det,q,D_L)$ as gwcosmo computes the likelihood in terms of variables $m1_det,m2_det,D_L$. Your class `PE_priors` must have a function returning the probability $p(m1_det,m2_det,D_L)$, so basically, you have to computed the jacobian of the transformation. In our example, here is the file `PE_prior.py` you need to perform the analysis:

``` python
class PE_priors(object):
    """
    the name of the class must always be "PE_priors"
    the class must have a member function 
    called get_prior(self,m1d,m2d,dL) that returns a floating value (or an array)
    """    
    def __init__(self):        
        self.name = "chirp_det_ratio:uniform --- dL:square"

    def get_prior_m1d_m2d_dL(self,m1d,m2d,dL):
        """
        This function returns something proportional to p(m1d,m2d,dL)
        """
        mc = (m1d*m2d)**(3./5)/(m1d+m2d)**(1./5)
        return dL**2 * mc/m1d**2
```

You finally have to set the field appropriately in the json file `events.json`: `"PEprior_kind": "PE_prior.py"`. The class will be loaded at run time.


## The LOS redshift prior file (`--LOS_catalog`)

The file: `GLADE+_Kband.hdf5` contains the line-of-sight redshift prior. The data stored in this hdf5 file are the values of $p(z|\Omega_j)$ (see Eq. 2.22 of arXiv:2308.02281) for each pixel and the summation over all pixels.


## The selection effect (`--injections`)

The denominator of Eq. 2.2 (see arXiv:2308.02281) takes properly into account the selection effect, i.e. the bias due to the fact that the events you have selected for the analysis were obtained after a cut on their SNR or their IFAR. In gwcosmo, the selection effect is computed using a logical condition `(SNR>SNRthr) | (IFAR>IFARthr)`. This allows to use the official LVK injections file in which:
- for O1 and O2 injections, the SNR value is provided (and the FAR is set to 0)
- for O3 and O4a injections, the FAR value is provided (and the SNR is set to 0)
Note that LVK injections provide the FAR values, in units of inverse years: False Alarm Rate, and gwcosmo needs the IFAR values in units of years, Inverse of the FAR.

The LVK injections file needs to be modified for two reasons. First, gwcosmo needs the IFAR and not the FAR. Also, when only the SNR is known, the default IFAR value is set to `-1` so that the selection condition `(SNR>SNRthr) | (IFAR>IFARthr)` is correctly applied, assuming `IFARthr>-1`. Second, we need to marginalise injections over the spin model. Indeed, the priors on the simulated CBC parameters in the LVK injections file are not always separable in terms of masses, distance and spins. gwcosmo makes the analysis assuming population models depending on masses and distance only, disregarding the spins. So we need to marginalise those injections over the same spin model than the one considered in the PE analysis, to have a consistent treatment.

For details on the computation of the selection effect, refer to section 2.3 of arXiv:2308.02281. We compute this effect using a large set of 'injections' i.e. simulated compact binaries signals that would be detected in the same instrumental configuration than the one existing to create your actual dataset. For more details, please refer to the dedicated documentation page for Injections.

Note that the injections file `inj_SNR9_det_frame_2e6_IFAR_minus_1.h5` used in this example has only SNR values for O1-O2-O3 runs. The corresponding IFAR value is set to `-1` for all injections. This file is not as accurate as the official LVK injections that takes into account in a much more precise way the uptimes, duty cycles and sensitivities of the interferometers.

## The parameters you want to estimate (`--parameter_dict`)

The parameters you want to constrain in the gwcosmo analysis must be provided as a json file. In this example, the file `bpl_dip_dict.json` contains the configuration of the parameters for the multipopulation analysis (BBHs, NSBHs, BNSs). The name of the parameters must be the same than the ones used in the assumed population model (mass and rates). The expected format is:

``` json
{

    "H0": {
        "value" : [10, 200, 100],
        "description" : "The Hubble constant (km s-1 Mpc-1). [start, stop [, bins]] or single value",
        "prior" : "Uniform",
        "label" : "$H_0$"
    },
    "gamma": {
        "value" : [0, 12, 100],
        "description" : "Powerlaw slope (PowerLaw), or low-z slope (Madau) for merger rate evolution with redshift.",
        "prior" : "Uniform",
        "label" : "$\\gamma$"
    },
    "Madau_zp": {
        "value": [0, 4, 100],
        "description" : "Break-point for merger rate evolution with redshift (Madau).",
        ...
```

In case you want to fix some parameters, you simply have to write in the json file:

``` json
    "mu_g": {
        "value": 32.27,
        "description" : "Mean of the gaussian peak of the primary powerlaw-gaussian BH mass distribution.",
        "prior" : "Uniform",
        "label" : "$\\mu_g$"
    },
```

## The mass model (`--mass_model`)

This argument of the command line must be a mass model that will be considered in gwcosmo. Possible values for this argument are:
- 'BBH-powerlaw': used in the cosmology-GWTC4 publication, as PLP (Power-Law plus Peak)
- 'NSBH-powerlaw'
- 'BBH-powerlaw-gaussian': 
- 'NSBH-powerlaw-gaussian'
- 'BBH-broken-powerlaw'
- 'NSBH-broken-powerlaw'
- 'BBH-multi-peak-gaussian': used in the cosmology-GWTC4 publication, as MLTP (Multi-Peak)
- 'NSBH-multi-peak-gaussian'
- 'BBH-broken-powerlaw-multi-peak-gaussian'
- 'NSBH-broken-powerlaw-multi-peak-gaussian'
- 'BNS'
- 'multipopulation_pairing'
- 'multipopulation_pairing_broken': used in the cosmology-GWTC4 publication, as FullPop-4.0

Note that the names of the parameters describing those laws must be the same than the ones appearing in the json file providing the parameters (argument `--parameter_dict`).

## The gravity model (`--gravity_model`)

If this argument is not provided, the analysis is performed assuming general relativity as the gravity model. Possible values for this argument are:
- `GR`: general relativity
- `Xi0_n`: modified gravity, phenomenological departure from GR
- `cM`: modified gravity, running Planck mass, Horndeski gravity
