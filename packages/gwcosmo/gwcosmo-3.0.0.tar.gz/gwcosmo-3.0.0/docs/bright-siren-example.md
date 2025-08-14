# Bright siren example

We provide here the complete command line for a bright siren analysis of the BNS GW170817 detected during the run O2.
We will assume you have a login at the CIT cluster of the form `albert.einstein`. All paths are relative to this cluster. The analysis runs the code `gwcosmo_dark_siren_posterior` and it assumes that `gwcosmo` was installed inside a `conda` environment in `/home/albert.einstein/.conda/envs/gwcosmo/`.

The script `job.sub` below must be given to `condor` with the command `condor_submit job.sub`. In the script we define the variable `environment`: careful, its definition can vary according to the cluster on which you are running the analysis. The version here runs well at CIT as of 20250731. The detail of the arguments are given in the documentation for the dark sirens analysis

```
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

exe=gwcosmo_bright_siren_posterior

injections=inj_SNR9_det_frame_2e6_IFAR_minus_1.h5
posterior=event.json
params=params_BNS.json

method=gridded

mass_model=BNS

name=bright_GW170817
snrthr=10
ifarthr=4

cmd="${exe} --method ${method} \
        --posterior_samples ${posterior} \
        --injections ${injections} \
        --parameter_dict ${params} \
        --mass_model ${mass_model} \
        --redshift_evolution Madau \
        --snr ${snrthr} \
        --ifar ${ifarthr} \
        --outputfile pH0_${method}_${name}"
echo ${cmd}
echo "Executing command..."
echo ${cmd} | /bin/bash
```

For this analysis, the posterior file `event.json` is:

``` json
{
    "GW170817_124104": {
        "PEprior_kind": "m1d_m2d_uniform_dL_square_PE_priors",
        "posterior_file_path": "GW170817_GWTC-1.hdf5",
        "samples_field": "", 
        "use_event": "True",
        "counterpart_velocity": [3017, 166],
        "counterpart_ra_dec": [3.44602385, -0.40813555]
    }   
}
```


The PE file `GW170817_GWTC-1.hdf5` can be found at this [public LVK URL](https://dcc.ligo.org/public/0157/P1800370/005/GW170817_GWTC-1.hdf5). You don't need to set the `samples_field` field to any particular value as gwcosmo is using specificaly for this event `IMRPhenomPv2NRT_lowSpin_posterior`. If you want to run the analysis for the highSpin case, you will need to extract the PE samples for this approximant as a `.dat` file and run gwcosmo with this one. You also note that you must provide the PE priors used for this event as the PE file does not contains explicitely the prior. The **cosmological** redshift is provided in the json file with `counterpart_velocity` as z=velocity/c, the velocity being expressed in km/s. We provide the mean value and its 1 sigma uncertainty, assuming a gaussian distribution. We also set the sky position of the event, corresponding the the position of NGC4993.
