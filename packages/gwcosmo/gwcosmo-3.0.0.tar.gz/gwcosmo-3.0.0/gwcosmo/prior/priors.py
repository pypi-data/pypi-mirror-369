"""
Priors
Ignacio Magana, Rachel Gray, Sergio Vallejo-Peña, Antonio Enea Romano 
"""
from __future__ import absolute_import

import numpy as np

from scipy.interpolate import interp1d
import bilby 
from gwcosmo.utilities.mass_prior_utilities import peaks_sampling_constraint, peaks_grid_constraint

from . import custom_math_priors as _cmp

def pH0(H0, prior='log'):
    """
    Returns p(H0)
    The prior probability of H0

    Parameters
    ----------
    H0 : float or array_like
        Hubble constant value(s) in kms-1Mpc-1
    prior : str, optional
        The choice of prior (default='log')
        if 'log' uses uniform in log prior
        if 'uniform' uses uniform prior

    Returns
    -------
    float or array_like
        p(H0)
    """
    if prior == 'uniform':
        return np.ones(len(H0))
    if prior == 'log':
        return 1./H0
    
def pairing_func(m1, m2, beta):
    """
    Returns simple pairing function

    Parameters
    ----------
    m1, m2 : float or array_like
        primary and secondary mass(es)
    beta: float
        index of mass ratio powerlaw
    """

    q = m2/m1
    toret = q**beta
    toret[q>1] = 0.

    return toret 

def pairing_func_broken(m1, m2, beta1, beta2, mbreak):
    """
    Returns broken pairing function

    Parameters
    ---------
     m1, m2 : float or array_like
        primary and secondary mass(es)
    beta1: float
        index of mass ratio powerlaw before mbreak
    beta2: float
        index of mass ratio powerlaw after mbreak
    mbreak: float 
        secondary mass value at which powerlaw index changes
    
    """

    q = m2/m1
    toret = q**beta1
    toret[m2>=mbreak] = q[m2>=mbreak]**beta2
    toret[q>1] = 0.

    return toret

class distance_distribution(object):
    def __init__(self, name):
        self.name = name

        if self.name == 'BBH-powerlaw':
            dist = PriorDict(conversion_function=constrain_m1m2)
            dist['luminosity_distance'] = PowerLaw(alpha=2, minimum=1, maximum=15000)

        if self.name == 'BNS':
            dist = PriorDict(conversion_function=constrain_m1m2)
            dist['luminosity_distance'] = PowerLaw(alpha=2, minimum=1, maximum=1000)

        if self.name == 'NSBH':
            dist = PriorDict(conversion_function=constrain_m1m2)
            dist['luminosity_distance'] = PowerLaw(alpha=2, minimum=1, maximum=1000)

        if self.name == 'BBH-constant':
            dist = PriorDict()
            dist['luminosity_distance'] = PowerLaw(alpha=2, minimum=1, maximum=15000)

        self.dist = dist

    def sample(self, N_samples):
        samples = self.dist.sample(N_samples)
        return samples['luminosity_distance']

    def prob(self, samples):
        return self.dist['luminosity_distance'].prob(samples)

class m_priors(object):
    """
    Parent class with common methods for managing the priors on source frame masses.
    The prior is factorized as :math:`p(m_1,m_2) \\propto p(m_1)p(m_2|m_1)`
    """

    def __init__(self):
        pass

    def update_parameters(self,param_dict):
        """
        Method to dynamically determine attributes in a mass prior class and use these.
        """
        for key, value in param_dict.items():
            setattr(self, key, value)
        self.update_mass_priors()

    def joint_prob(self, ms1, ms2):
        """
        This method returns the joint probability :math:`p(m_1,m_2)`

        Parameters
        ----------
        ms1: np.array(matrix)
            mass one in solar masses
        ms2: dict
            mass two in solar masses
        """

        to_ret = self.mdis['mass_1'].prob(ms1)*self.mdis['mass_2'].conditioned_prob(ms2,self.mmin*np.ones_like(ms1),np.minimum(ms1,self.mmax2))
        #print('ms1',ms1)
        #print('ms2',ms2)
        #print('mmin',self.mmin)
        #print('mmax2',self.mmax2)
        #print('to_ret',to_ret)

        return to_ret
    
    def log_joint_prob(self,ms1, ms2):
        
        to_ret = np.log(self.joint_prob(ms1, ms2))
        to_ret[np.isnan(to_ret)] = -np.inf

        return to_ret

    def sample(self, Nsample):
        """
        *Not used in O4, due to the use of injections instead of Pdet*
        This method samples from the joint probability :math:`p(m_1,m_2)`

        Parameters
        ----------
        Nsample: int
            Number of samples you want
        """

        vals_m1 = np.random.rand(Nsample)
        vals_m2 = np.random.rand(Nsample)

        m1_trials = np.logspace(np.log10(self.mdis['mass_1'].minimum),np.log10(self.mdis['mass_1'].maximum),10000)
        m2_trials = np.logspace(np.log10(self.mdis['mass_2'].minimum),np.log10(self.mdis['mass_2'].maximum),10000)

        cdf_m1_trials = self.mdis['mass_1'].cdf(m1_trials)
        cdf_m2_trials = self.mdis['mass_2'].cdf(m2_trials)

        m1_trials = np.log10(m1_trials)
        m2_trials = np.log10(m2_trials)

        _,indxm1 = np.unique(cdf_m1_trials,return_index=True)
        _,indxm2 = np.unique(cdf_m2_trials,return_index=True)

        interpo_icdf_m1 = interp1d(cdf_m1_trials[indxm1],m1_trials[indxm1],bounds_error=False,fill_value=(m1_trials[0],m1_trials[-1]))
        interpo_icdf_m2 = interp1d(cdf_m2_trials[indxm2],m2_trials[indxm2],bounds_error=False,fill_value=(m2_trials[0],m2_trials[-1]))

        mass_1_samples = 10**interpo_icdf_m1(vals_m1)
        mass_2_samples = 10**interpo_icdf_m2(vals_m2*self.mdis['mass_2'].cdf(mass_1_samples))

        return mass_1_samples, mass_2_samples
    
    @staticmethod
    def grid_constraint_call(*args):
        pass 

    @staticmethod
    def sampling_constraint_call(prior_dict):
        return prior_dict

class BBH_powerlaw(m_priors):
    """
    Child class for BBH power law distribution.
    
    Parameters
    -------------
    mminbh: Minimum mass of the PL component of the black hole mass distribution
    mmaxbh: Maximum mass of the PL component of the black hole mass distribution
    alpha: Spectral index for the PL of the primary mass distribution
    beta: Spectral index for the PL of the mass ratio distribution

    The default values of the parameters are set to the corresponding median values in the uniform priors reported in 2111.03604

    ************
    NOTE: The spectral indices passed to PowerLaw_math are alpha=-self.alpha, and alpha=self.beta, according to eqs. A8,A10 in 2111.03604
    ************
    
    The method m_priors.update_parameters is used  in the constructor to initialize the objects
    """
    def __init__(self,mminbh=6.0,mmaxbh=125.0,alpha=6.75,beta=4.0):
        super().__init__()

        self.update_parameters(param_dict={'alpha':alpha, 'beta':beta, 'mminbh':mminbh, 'mmaxbh':mmaxbh})               
              
    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects. 
        It sets the maximum value of the primary mass distribution mmax to mmaxbh, 
        the minimum value of the secondary mass distribution mmin to mminbh, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxbh.
        It's called by update_paratemters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''

        self.mmax = self.mmaxbh #Maximum value of m1, used in injections.Injections.update_VT (m_prior.mmax)
        self.mmin = self.mminbh #Minimum value of m2, used in self.joint_prob and in injections.Injections.update_VT (m_prior.mmin) 
        self.mmax2 = self.mmaxbh #Maximum value of m2, used in self.joint_prob

        self.mdis={'mass_1':_cmp.PowerLaw_math(alpha=-self.alpha,min_pl=self.mminbh,max_pl=self.mmaxbh),
                     'mass_2':_cmp.PowerLaw_math(alpha=self.beta,min_pl=self.mminbh,max_pl=self.mmaxbh)}
        

class NSBH_powerlaw(m_priors):
    """
    Child class for NS-BH power law distribution.
    
    Parameters
    -------------
    mminbh: Minimum mass of the PL component of the black hole mass distribution
    mmaxbh: Maximum mass of the PL component of the black hole mass distribution
    alpha: Spectral index for the PL of the primary mass distribution
    mminns: Minimum mass of the neutron star distribution
    mmaxns: Maximum mass of the neutron star distribution
    alphans: Spectral index for the PL of the neutron star mass distribution

    The default values of the black hole mass distribution parameters are set to the corresponding median values in the uniform priors reported in 2111.03604
    The default values of the neutron star mass distribution parameters are set to the corresponding values reported in section 4.2 (page 23) in 2111.03604

    ************
    NOTE: The spectral indices passed to PowerLaw_math are alpha=-self.alpha, and alpha=-self.alphans, according to eq. A10 in 2111.03604
    *************   

    The method m_priors.update_parameters is used in the constructor to initialize the objects
    """
    def __init__(self,mminbh=6.0,mmaxbh=125.0,alpha=6.75,mminns=1.0,mmaxns=3.0,alphans=0.0):
        super().__init__()

        self.update_parameters(param_dict={'alpha':alpha, 'mminbh':mminbh, 'mmaxbh':mmaxbh, 'alphans':alphans, 'mminns':mminns, 'mmaxns':mmaxns})
        
    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to mmaxbh, 
        the minimum value of the secondary mass distribution mmin to mminns, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxns.
        It's called by update_paratemters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''

        self.mmax=self.mmaxbh
        self.mmin=self.mminns        
        self.mmax2=self.mmaxns

        self.mdis={'mass_1':_cmp.PowerLaw_math(alpha=-self.alpha,min_pl=self.mminbh,max_pl=self.mmaxbh),
                     'mass_2':_cmp.PowerLaw_math(alpha=-self.alphans,min_pl=self.mminns,max_pl=self.mmaxns)}
   
class BBH_powerlaw_gaussian(m_priors):
    """
    Child class for BBH power law gaussian distribution.
    
    Parameters
    -------------
    mminbh: Minimum mass of the PL component of the black hole mass distribution
    mmaxbh: Maximum mass of the PL component of the black hole mass distribution
    alpha: Spectral index for the PL of the primary mass distribution    
    mu_g: Mean of the Gaussian component in the primary mass distribution
    sigma_g: Width of the Gaussian component in the primary mass distribution
    lambda_g: Fraction of the model in the Gaussian component
    delta_m: Range of mass tapering on the lower end of the mass distribution
    beta: Spectral index for the PL of the mass ratio distribution

    The default values of the parameters are set to the corresponding values reported in section 4.2 (page 23) in 2111.03604

    ************
    NOTE: The spectral indices passed to PowerLawGaussian_math, and PowerLaw_math, are alpha=-self.alpha, and alpha=self.beta, according to eqs. A8,A11 in 2111.03604
    *************   

    The method m_priors.update_parameters is used in the constructor to initialize the objects.
    """
    def __init__(self,mminbh=4.98,mmaxbh=112.5,alpha=3.78,mu_g=32.27,sigma_g=3.88,lambda_g=0.03,delta_m=4.8,beta=0.81):
        super().__init__()
        
        self.update_parameters(param_dict={'alpha':alpha, 'beta':beta, 'mminbh':mminbh, 'mmaxbh':mmaxbh, 'mu_g':mu_g, 'sigma_g':sigma_g, 'lambda_g':lambda_g, 'delta_m':delta_m})

    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to self.mdis['mass_1'].maximum, 
        the minimum value of the secondary mass distribution mmin to mminbh, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxbh.
        It's called by update_paratemters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''
                       
        self.m1pr = _cmp.PowerLawGaussian_math(alpha=-self.alpha,min_pl=self.mminbh,max_pl=self.mmaxbh,lambda_g=self.lambda_g
                    ,mu_g=self.mu_g,sigma_g=self.sigma_g,min_g=self.mminbh,max_g=self.mu_g+5*self.sigma_g)

        # The max of the secondary mass is adapted to the primary mass maximum which is decided by the Gaussian and PL
        self.m2pr = _cmp.PowerLaw_math(alpha=self.beta,min_pl=self.mminbh,max_pl=np.max([self.mu_g+5*self.sigma_g,self.mmaxbh]))

        self.mdis={'mass_1': _cmp.SmoothedProb(origin_prob=self.m1pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m),
                      'mass_2':_cmp.SmoothedProb(origin_prob=self.m2pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m)}
       
        # TO DO Add a check on the mu_g - 5 sigma of the gaussian to not overlap with mmin, print a warning
        #if (mu_g - 5*sigma_g)<=mmin:
        #print('Warning, your mean (minuse 5 sigma) of the gaussian component is too close to the minimum mass')

        self.mmax = self.mdis['mass_1'].maximum 
        self.mmin = self.mminbh  
        self.mmax2 = self.mmaxbh

class NSBH_powerlaw_gaussian(m_priors):
    """
    Child class for NS-BH power law gaussian distribution.
    
    Parameters
    -------------
    mminbh: Minimum mass of the PL component of the black hole mass distribution
    mmaxbh: Maximum mass of the PL component of the black hole mass distribution
    alpha: Spectral index for the PL of the primary mass distribution    
    mu_g: Mean of the Gaussian component in the primary mass distribution
    sigma_g: Width of the Gaussian component in the primary mass distribution
    lambda_g: Fraction of the model in the Gaussian component    
    delta_m: Range of mass tapering on the lower end of the mass distribution
    mminns: Minimum mass of the neutron star distribution
    mmaxns: Maximum mass of the neutron star distribution
    alphans: Spectral index for the PL of the neutron star mass distribution

    The default values of the parameters are set to the corresponding values reported in section 4.2 (page 23) in 2111.03604

    ************
    NOTE: The spectral indices passed to PowerLawGaussian_math, and PowerLaw_math, are alpha=-self.alpha, and alpha=-self.alphans, according to eqs. A10,A11 in 2111.03604
    *************
        
    The method m_priors.update_parameters is used in the constructor to initialize the objects.
    """
    def __init__(self,mminbh=4.98,mmaxbh=112.5,alpha=3.78,mu_g=32.27,sigma_g=3.88,lambda_g=0.03,delta_m=4.8,mminns=1.0,mmaxns=3.0,alphans=0.0):
        super().__init__()

        self.update_parameters(param_dict={'alpha':alpha, 'mminbh':mminbh, 'mmaxbh':mmaxbh, 'mu_g':mu_g, 'sigma_g':sigma_g, 'lambda_g':lambda_g, 'delta_m':delta_m, 'alphans':alphans, 'mminns':mminns, 'mmaxns':mmaxns})

    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to self.mdis['mass_1'].maximum, 
        the minimum value of the secondary mass distribution mmin to mminns, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxns.
        It's called by update_paratemters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''
                
        self.m1pr = _cmp.PowerLawGaussian_math(alpha=-self.alpha,min_pl=self.mminbh,max_pl=self.mmaxbh,lambda_g=self.lambda_g
                    ,mu_g=self.mu_g,sigma_g=self.sigma_g,min_g=self.mminbh,max_g=self.mu_g+5*self.sigma_g)

        # The max of the secondary mass is adapted to the primary mass maximum which is decided by the Gaussian and PL
        self.m2pr = _cmp.PowerLaw_math(alpha=-self.alphans,min_pl=self.mminns,max_pl=self.mmaxns)

        self.mdis={'mass_1': _cmp.SmoothedProb(origin_prob=self.m1pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m),
                      'mass_2':self.m2pr}

        self.mmax = self.mdis['mass_1'].maximum 
        self.mmin = self.mminns  
        self.mmax2 = self.mmaxns

class BBH_broken_powerlaw(m_priors):
    """
    Child class for BBH broken power law distribution.

    Parameters
    -------------
    mminbh: Minimum mass of the PL component of the black hole mass distribution
    mmaxbh: Maximum mass of the PL component of the black hole mass distribution
    alpha_1: PL slope of the primary mass distribution for masses below mbreak 
    alpha_2: PL slope for the primary mass distribution for masses above mbreak 
    b: The fraction of the way between mminbh and mmaxbh at which the primary mass distribution breaks
    delta_m: Range of mass tapering on the lower end of the mass distribution
    beta: Spectral index for the PL of the mass ratio distribution

    The default values of the parameters are set to the corresponding median values in the uniform priors reported in 2111.03604
    
    ************
    NOTE: The spectral indices passed to BrokenPowerLaw_math, and PowerLaw_math, are alpha_1=-self.alpha_1, alpha_2=-self.alpha_2, and alpha=self.beta, according to eqs. A8,A12 in 2111.03604
    ************

    The method m_priors.update_parameters is used in the constructor to initialize the objects.
    """
    def __init__(self,mminbh=26,mmaxbh=125,alpha_1=6.75,alpha_2=6.75,b=0.5,delta_m=5,beta=4):
        super().__init__()

        self.update_parameters(param_dict={'alpha_1':alpha_1, 'alpha_2':alpha_2, 'beta':beta, 'mminbh':mminbh, 'mmaxbh':mmaxbh, 'b':b, 'delta_m':delta_m})

    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects. 
        It sets the maximum value of the primary mass distribution mmax to mmaxbh, 
        the minimum value of the secondary mass distribution mmin to mminbh, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxbh.
        It's called by update_paratemters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''

        self.mmax = self.mmaxbh 
        self.mmin = self.mminbh  
        self.mmax2 = self.mmaxbh
                
        self.m1pr = _cmp.BrokenPowerLaw_math(alpha_1=-self.alpha_1,alpha_2=-self.alpha_2,min_pl=self.mminbh,max_pl=self.mmaxbh,b=self.b)
        self.m2pr = _cmp.PowerLaw_math(alpha=self.beta,min_pl=self.mminbh,max_pl=self.mmaxbh)

        self.mdis={'mass_1': _cmp.SmoothedProb(origin_prob=self.m1pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m),
                      'mass_2':_cmp.SmoothedProb(origin_prob=self.m2pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m)}

class NSBH_broken_powerlaw(m_priors):
    """
    Child class for NS-BH broken power law distribution.
    
    Parameters
    -------------
    mminbh: Minimum mass of the PL component of the black hole mass distribution
    mmaxbh: Maximum mass of the black hole mass distribution
    alpha_1: PL slope of the primary mass distribution for masses below mbreak 
    alpha_2: PL slope for the primary mass distribution for masses above mbreak 
    b: The fraction of the way between mminbh and mmaxbh at which the primary mass distribution breaks
    delta_m: Range of mass tapering on the lower end of the mass distribution
    mminns: Minimum mass of the neutron star distribution
    mmaxns: Maximum mass of the neutron star distribution
    alphans: Spectral index for the PL of the neutron star mass distribution

    The default values of the black hole mass distribution parameters are set to the corresponding median values in the uniform priors reported in 2111.03604
    The default values of the neutron star mass distribution parameters are set to the corresponding values reported in section 4.2 (page 23) in 2111.03604

    ************
    NOTE: The spectral indices passed to BrokenPowerLaw_math, and PowerLaw_math, are alpha_1=-self.alpha_1, alpha_2=-self.alpha_2, and alpha=-self.alphans, according to eqs. A10,A12 in 2111.03604
    ************
    
    The method m_priors.update_parameters is used in the constructor to initialize the objects.
    """
    def __init__(self,mminbh=26,mmaxbh=125,alpha_1=6.75,alpha_2=6.75,b=0.5,delta_m=5,mminns=1.0,mmaxns=3.0,alphans=0.0):
        super().__init__()

        self.update_parameters(param_dict={'alpha_1':alpha_1, 'alpha_2':alpha_2, 'mminbh':mminbh, 'mmaxbh':mmaxbh, 'b':b, 'delta_m':delta_m, 'alphans':alphans, 'mminns':mminns, 'mmaxns':mmaxns})

    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to mmaxbh, 
        the minimum value of the secondary mass distribution mmin to mminns, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxns.
        It's called by update_paratemters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''
        
        self.mmax=self.mmaxbh
        self.mmin=self.mminns        
        self.mmax2=self.mmaxns
                
        self.m1pr = _cmp.BrokenPowerLaw_math(alpha_1=-self.alpha_1,alpha_2=-self.alpha_2,min_pl=self.mminbh,max_pl=self.mmaxbh,b=self.b)
        self.m2pr = _cmp.PowerLaw_math(alpha=-self.alphans,min_pl=self.mminns,max_pl=self.mmaxns)

        self.mdis={'mass_1': _cmp.SmoothedProb(origin_prob=self.m1pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m),
                      'mass_2':self.m2pr}
             

class BBH_multi_peak_gaussian(m_priors):
    """
    Child class for BBH with powerlaw component and two gaussian peaks.

    Parameters
    -------------
    mminbh: Minimum mass of the PL component of the black hole mass distribution
    mmaxbh: Maximum mass of the PL component of the black hole mass distribution
    alpha: Spectral index for the PL of the primary mass distribution    
    mu_g_low: Mean of the lower mass Gaussian component in the primary mass distribution
    sigma_g_low: Width of the lower mass Gaussian component in the primary mass distribution
    mu_g_high: Mean of the higher mass Gaussian component in the primary mass distribution
    sigma_g_high: Width of the higher mass Gaussian component in the primary mass distribution
    lambda_g: Fraction of the model in the Gaussian component
    lambda_g_low: Fraction of the Gaussian component in the lower mass peak
    delta_m: Range of mass tapering on the lower end of the mass distribution
    beta: Spectral index for the PL of the mass ratio distribution

    ************
    NOTE: The spectral indices passed to PowerLawDoubleGaussian_math, and PowerLaw_math, are alpha=-self.alpha, and alpha=self.beta, according to eqs. A8,A11 in 2111.03604
    ************* 
    
    The method m_priors.update_parameters is used in the constructor to initialize the objects.
    """
    def __init__(self,alpha=3.78,beta=0.8,mminbh=4.98,mmaxbh=112.5,lambda_g=0.03,lambda_g_low= 0.5,mu_g_low=10.5,sigma_g_low=3.88,mu_g_high=32.27,sigma_g_high=5,delta_m=5):
        super().__init__()

        self.update_parameters(param_dict={'alpha':alpha,'beta':beta,'mminbh':mminbh,'mmaxbh':mmaxbh,'lambda_g':lambda_g,'lambda_g_low':lambda_g_low,'mu_g_low':mu_g_low,'sigma_g_low':sigma_g_low,'mu_g_high':mu_g_high,'sigma_g_high':sigma_g_high,'delta_m':delta_m})

    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to self.mdis['mass_1'].maximum, 
        the minimum value of the secondary mass distribution mmin to mminbh, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxbh.
        It's called by update_parameters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''

        self.m1pr =_cmp.PowerLawDoubleGaussian_math(alpha=-self.alpha,min_pl=self.mminbh,max_pl=self.mmaxbh,lambda_g=self.lambda_g,lambda_g_low=self.lambda_g_low,
                                                    mu_g_low=self.mu_g_low,sigma_g_low=self.sigma_g_low,mu_g_high=self.mu_g_high,sigma_g_high=self.sigma_g_high,min_g=self.mminbh,max_g=self.mu_g_high+5*self.sigma_g_high)
        

        self.m2pr =_cmp.PowerLaw_math(alpha=self.beta,min_pl=self.mminbh,max_pl=np.max([self.mu_g_low+5*self.sigma_g_low,self.mmaxbh]))

        self.mdis={'mass_1': _cmp.SmoothedProb(origin_prob=self.m1pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m),
                      'mass_2':_cmp.SmoothedProb(origin_prob=self.m2pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m)}

        self.mmax = self.mdis['mass_1'].maximum
        self.mmin = self.mminbh
        self.mmax2 = self.mmaxbh

    @staticmethod
    def grid_constraint_call(constraint_grid, values, parameter_grid, fixed_params):
        new_grid = peaks_grid_constraint(constraint_grid, values, parameter_grid, fixed_params)
        return new_grid

    @staticmethod
    def sampling_constraint_call(prior_dict):
        new_dict = peaks_sampling_constraint(prior_dict)
        return new_dict


class NSBH_multi_peak_gaussian(m_priors):
    """
    Child class for NS-BH with powerlaw component and two gaussian peaks.

    Parameters
    -------------
    mminbh: Minimum mass of the PL component of the black hole mass distribution
    mmaxbh: Maximum mass of the PL component of the black hole mass distribution
    alpha: Spectral index for the PL of the primary mass distribution    
    mu_g_low: Mean of the lower mass Gaussian component in the primary mass distribution
    sigma_g_low: Width of the lower mass Gaussian component in the primary mass distribution
    mu_g_high: Mean of the higher mass Gaussian component in the primary mass distribution
    sigma_g_high: Width of the higher mass Gaussian component in the primary mass distribution
    lambda_g: Fraction of the model in the Gaussian component
    lambda_g_low: Fraction of the Gaussian component in the lower mass peak
    delta_m: Range of mass tapering on the lower end of the mass distribution
    mminns: Minimum mass of the neutron star distribution
    mmaxns: Maximum mass of the neutron star distribution
    alphans: Spectral index for the PL of the neutron star mass distribution

    ************
    NOTE: The spectral indices passed to PowerLawDoubleGaussian_math, and PowerLaw_math, are alpha=-self.alpha, and alpha=-self.alphans, according to eqs. A10,A11 in 2111.03604
    *************
    
    The method m_priors.update_parameters is used in the constructor to initialize the objects.
    """

    def __init__(self,alpha=3.78,mminbh=4.98,mmaxbh=112.5,lambda_g=0.03,lambda_g_low= 0.5,mu_g_low=10.5,sigma_g_low=3.88,mu_g_high=32.27,sigma_g_high=5,delta_m=5,mminns=1.0,mmaxns=3.0,alphans=0):
        super().__init__()

        self.update_parameters(param_dict={'alpha':alpha,'mminbh':mminbh,'mmaxbh':mmaxbh,'lambda_g':lambda_g,'lambda_g_low':lambda_g_low,'mu_g_low':mu_g_low,'sigma_g_low':sigma_g_low,'mu_g_high':mu_g_high,'sigma_g_high':sigma_g_high,'delta_m':delta_m,'mminns':mminns,'mmaxns':mmaxns,'alphans':alphans})

    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to self.mdis['mass_1'].maximum, 
        the minimum value of the secondary mass distribution mmin to mminns, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxns.
        It's called by update_parameters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''


        self.m1pr =_cmp.PowerLawDoubleGaussian_math(alpha=-self.alpha,min_pl=self.mminbh,max_pl=self.mmaxbh,lambda_g=self.lambda_g,lambda_g_low=self.lambda_g_low,
                                                    mu_g_low=self.mu_g_low,sigma_g_low=self.sigma_g_low,mu_g_high=self.mu_g_high,sigma_g_high=self.sigma_g_high,min_g=self.mminbh,max_g=self.mu_g_high+5*self.sigma_g_high)
        

        self.m2pr = _cmp.PowerLaw_math(alpha=-self.alphans,min_pl=self.mminns,max_pl=self.mmaxns)

        self.mdis={'mass_1': _cmp.SmoothedProb(origin_prob=self.m1pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m),
                      'mass_2': self.m2pr}

        self.mmax = self.mdis['mass_1'].maximum
        self.mmin = self.mminns
        self.mmax2 = self.mmaxns

    @staticmethod
    def grid_constraint_call(constraint_grid, values, parameter_grid, fixed_params):
        new_grid = peaks_grid_constraint(constraint_grid, values, parameter_grid, fixed_params)
        return new_grid
    
    @staticmethod
    def sampling_constraint_call(prior_dict):
        new_dict = peaks_sampling_constraint(prior_dict)
        return new_dict
    
class BBH_broken_powerlaw_multi_peak_gaussian(m_priors):

    def __init__(self,alpha_1=6.75,alpha_2=6.75,b=0.5,beta=0.8,mminbh=4.98,mmaxbh=112.5,lambda_g=0.03,lambda_g_low= 0.5,mu_g_low=10.5,sigma_g_low=3.88,mu_g_high=32.27,sigma_g_high=5,delta_m=5):
        super().__init__()

        self.update_parameters(param_dict={'alpha_1':alpha_1,'alpha_2':alpha_2,'b':b,'beta':beta,'mminbh':mminbh,'mmaxbh':mmaxbh,
                                           'lambda_g':lambda_g,'lambda_g_low':lambda_g_low,'mu_g_low':mu_g_low,'sigma_g_low':sigma_g_low,'mu_g_high':mu_g_high,'sigma_g_high':sigma_g_high,'delta_m':delta_m})
    
    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to self.mdis['mass_1'].maximum, 
        the minimum value of the secondary mass distribution mmin to mminns, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxns.
        It's called by update_parameters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''

        self.break_point = self.mminbh+self.b*(self.mmaxbh-self.mminbh)
        self.m1pr =_cmp.BrokenPowerLawDoubleGaussian_math(min_pl=self.mminbh,max_pl=self.mmaxbh,lambda_g=self.lambda_g,lambda_g_low=self.lambda_g_low,
                                                    mu_g_low=self.mu_g_low,sigma_g_low=self.sigma_g_low,mu_g_high=self.mu_g_high,
                                                    sigma_g_high=self.sigma_g_high,min_g=self.mminbh,max_g=self.mu_g_high+5*self.sigma_g_high,
                                                    alpha_1=-self.alpha_1,alpha_2=-self.alpha_2,break_point=self.break_point)
        

        self.m2pr = _cmp.PowerLaw_math(alpha=self.beta,min_pl=self.mminbh,max_pl=np.max([self.mu_g_low+5*self.sigma_g_low,self.mmaxbh]))

        self.mdis={'mass_1': _cmp.SmoothedProb(origin_prob=self.m1pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m),
                      'mass_2': _cmp.SmoothedProb(origin_prob=self.m2pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m)}

        self.mmax = self.mdis['mass_1'].maximum
        self.mmin = self.mminbh
        self.mmax2 = self.mmaxbh

    @staticmethod
    def grid_constraint_call(constraint_grid, values, parameter_grid, fixed_params):
        new_grid = peaks_grid_constraint(constraint_grid, values, parameter_grid, fixed_params)
        return new_grid
    
    @staticmethod
    def sampling_constraint_call(prior_dict):
        new_dict = peaks_sampling_constraint(prior_dict)
        return new_dict
    
class NSBH_broken_powerlaw_multi_peak_gaussian(m_priors):

    def __init__(self,alpha_1=6.75,alpha_2=6.75,b=0.5,mminbh=4.98,mmaxbh=112.5,lambda_g=0.03,lambda_g_low= 0.5,mu_g_low=10.5,sigma_g_low=3.88,mu_g_high=32.27,sigma_g_high=5,delta_m=5,mminns=1,mmaxns=5,alphans=0):
        super().__init__()

        self.update_parameters(param_dict={'alpha_1':alpha_1,'alpha_2':alpha_2,'b':b,'mminbh':mminbh,'mmaxbh':mmaxbh,
                                           'lambda_g':lambda_g,'lambda_g_low':lambda_g_low,'mu_g_low':mu_g_low,'sigma_g_low':sigma_g_low,'mu_g_high':mu_g_high,'sigma_g_high':sigma_g_high,'delta_m':delta_m,
                                           'mmins':mminns,'mmaxns':mmaxns,'alphans':alphans})
    
    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to self.mdis['mass_1'].maximum, 
        the minimum value of the secondary mass distribution mmin to mminns, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxns.
        It's called by update_parameters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''
        self.break_point = self.mminbh+self.b*(self.mmaxbh-self.mminbh)

        self.m1pr =_cmp.BrokenPowerLawDoubleGaussian_math(min_pl=self.mminbh,max_pl=self.mmaxbh,lambda_g=self.lambda_g,lambda_g_low=self.lambda_g_low,
                                                    mu_g_low=self.mu_g_low,sigma_g_low=self.sigma_g_low,mu_g_high=self.mu_g_high,
                                                    sigma_g_high=self.sigma_g_high,min_g=self.mminbh,max_g=self.mu_g_high+5*self.sigma_g_high,
                                                    alpha_1=-self.alpha_1,alpha_2=-self.alpha_2,break_point=self.break_point)
        

        self.m2pr = _cmp.PowerLaw_math(alpha=-self.alphans,min_pl=self.mminns,max_pl=self.mmaxns)

        self.mdis={'mass_1': _cmp.SmoothedProb(origin_prob=self.m1pr,high_pass_min=self.mminbh,high_pass_smooth=self.delta_m),
                      'mass_2': self.m2pr}

        self.mmax = self.mdis['mass_1'].maximum
        self.mmin = self.mminns
        self.mmax2 = self.mmaxns

    @staticmethod
    def grid_constraint_call(constraint_grid, values, parameter_grid, fixed_params):
        new_grid = peaks_grid_constraint(constraint_grid, values, parameter_grid, fixed_params)
        return new_grid
    
    @staticmethod
    def sampling_constraint_call(prior_dict):
        new_dict = peaks_sampling_constraint(prior_dict)
        return new_dict
    


class BNS(m_priors):
    """
    Child class for BNS distribution.
    
    Parameters
    -----------
    mminns: Minimum mass of the neutron star distribution
    mmaxns: Maximum mass of the neutron star distribution
    alphans: Spectral index for the PL of the neutron star mass distribution

    The default values of the parameters are set to the corresponding values reported in section 4.2 (page 23) in 2111.03604

    ************
    NOTE: The spectral index passed to PowerLaw_math is alpha=-self.alphans according to eq. A10 in 2111.03604
    ************
    
    The method m_priors.update_parameters is used in the constructor to initialize the objects.
    """
    def __init__(self,mminns=1.0,mmaxns=3.0,alphans=0.0):
        super().__init__()

        self.update_parameters(param_dict={'alphans':alphans, 'mminns':mminns, 'mmaxns':mmaxns})
                    
    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to mmaxns, 
        and the minimum value of the secondary mass distribution mmin to mminns.
        It's called by update_paratemters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax and mmin definitions depend on the mass prior model.          
        '''

        self.mmax = self.mmaxns
        self.mmin = self.mminns        

        self.mdis={'mass_1':_cmp.PowerLaw_math(alpha=-self.alphans,min_pl=self.mminns,max_pl=self.mmaxns),
                  'mass_2':_cmp.PowerLaw_math(alpha=-self.alphans,min_pl=self.mminns,max_pl=self.mmaxns)}
        
    
    def joint_prob(self, ms1, ms2):
        """ 
        This method returns the joint probability :math:`p(m_1,m_2)`

        Parameters
        ----------
        ms1: np.array(matrix)
            mass one in solar masses
        ms2: dict
            mass two in solar masses
        """

        to_ret =self.mdis['mass_1'].prob(ms1)*self.mdis['mass_2'].prob(ms2)

        return to_ret
    

    def sample(self, Nsample):
        """
        This method samples from the joint probability :math:`p(m_1,m_2)`

        Parameters
        ----------
        Nsample: int
            Number of samples you want
        """

        vals_m1 = np.random.rand(Nsample)
        vals_m2 = np.random.rand(Nsample)

        m1_trials = np.logspace(np.log10(self.mdis['mass_1'].minimum),np.log10(self.mdis['mass_1'].maximum),10000)
        m2_trials = np.logspace(np.log10(self.mdis['mass_2'].minimum),np.log10(self.mdis['mass_2'].maximum),10000)

        cdf_m1_trials = self.mdis['mass_1'].cdf(m1_trials)
        cdf_m2_trials = self.mdis['mass_2'].cdf(m2_trials)

        m1_trials = np.log10(m1_trials)
        m2_trials = np.log10(m2_trials)

        _,indxm1 = np.unique(cdf_m1_trials,return_index=True)
        _,indxm2 = np.unique(cdf_m2_trials,return_index=True)

        interpo_icdf_m1 = interp1d(cdf_m1_trials[indxm1],m1_trials[indxm1],bounds_error=False,fill_value=(m1_trials[0],m1_trials[-1]))
        interpo_icdf_m2 = interp1d(cdf_m2_trials[indxm2],m2_trials[indxm2],bounds_error=False,fill_value=(m2_trials[0],m2_trials[-1]))

        mass_1_samples = 10**interpo_icdf_m1(vals_m1)
        mass_2_samples = 10**interpo_icdf_m2(vals_m2)

        indx = np.where(mass_2_samples>mass_1_samples)[0]
        mass_1_samples[indx],mass_2_samples[indx] = mass_2_samples[indx],mass_1_samples[indx]

        return mass_1_samples, mass_2_samples
    

class multipopulation_broken_powerlaw_multi_peak_gaussian(m_priors):
    """
    Child class which builds a multipopulation model covering whole CBC range. This has two identical distribtuions in m1 and m2,
    with both being BPL+2G+Dip with smoothing.

    This cannot be directly specified as a mass model in the command line.

    Parameters
    ----------
    alpha_1 : float
        Slope of the power law for masses below the break point.
    alpha_2 : float
        Slope of the power law for masses above the break point.
    mmin : float
        Minimum mass of the distribution.
    mmax : float
        Maximum mass of the distribution.
    lambda_g : float
        Scaling parameter for the overall Gaussian component.
    lambda_g_low : float
        Scaling parameter for the low mass Gaussian peak.
    mu_g_low : float
        Mean of the low mass Gaussian peak.
    sigma_g_low : float
        Standard deviation of the low mass Gaussian peak.
    mu_g_high : float
        Mean of the high mass Gaussian peak.
    sigma_g_high : float
        Standard deviation of the high mass Gaussian peak.
    delta_m_low_pass : float
        Smoothing parameter for the high mass end of distribution.
    delta_m_high_pass : float
        Smoothing parameter for the low mass end of distribution.
    A : float
        Amplitude of the notch feature.
    notch_left : float
        Left boundary of the notch region.
    notch_right : float
        Right boundary of the notch region.
    notch_smooth_left : float
        Smoothing factor on the left side of the notch.
    notch_smooth_right : float
        Smoothing factor on the right side of the notch.
    """

    def __init__(self, alpha_1=1.0, alpha_2=3.0, mmin=1.0, mmax=112.5, lambda_g=0.3,
                  lambda_g_low=0.4, mu_g_low=15.0, sigma_g_low=3.88, mu_g_high=32.27, sigma_g_high=3.88, 
                  delta_m_low_pass=1, delta_m_high_pass=0.1, A=0, notch_left=3.0, notch_right=5.0, 
                  notch_smooth_left=1, notch_smooth_right=0.5):
        super().__init__()

        self.update_parameters(param_dict={'alpha_1':alpha_1,'alpha_2':alpha_2,'mmin':mmin,'mmax':mmax,'lambda_g':lambda_g,'lambda_g_low':lambda_g_low,'mu_g_low':mu_g_low,'sigma_g_low':sigma_g_low,
                                           'mu_g_high':mu_g_high,'sigma_g_high':sigma_g_high,'delta_m_low_pass':delta_m_low_pass,'delta_m_high_pass':delta_m_high_pass,
                                           'A':A,'notch_left':notch_left,'notch_right':notch_right,'notch_smooth_left':notch_smooth_left,'notch_smooth_right':notch_smooth_right})
    
    def update_mass_priors(self):
        ''' 
        This method creates a dictionary of mass distributions objects.         
        It sets the maximum value of the primary mass distribution mmax to self.mdis['mass_1'].maximum, 
        the minimum value of the secondary mass distribution mmin to mminns, 
        and the maximum value of the secondary mass distribution mmax2 to mmaxns.
        It's called by update_parameters everytime the mass priors parameters are changed.
        Every mass priors model has a different implementation because the distributions are different,
        and mmax, mmin and mmax2 definitions depend on the mass prior model.          
        '''

        self.break_point = 0.5*(self.notch_left+self.notch_right+self.notch_smooth_left-self.notch_smooth_right)


        self.m1pr =_cmp.BrokenPowerLawDoubleGaussian_math(min_pl=self.mmin,max_pl=self.mmax,lambda_g=self.lambda_g,lambda_g_low=self.lambda_g_low,
                                                    mu_g_low=self.mu_g_low,sigma_g_low=self.sigma_g_low,mu_g_high=self.mu_g_high,
                                                    sigma_g_high=self.sigma_g_high,min_g=self.mmin,max_g=self.mu_g_high+5*self.sigma_g_high,
                                                    alpha_1=-self.alpha_1,alpha_2=-self.alpha_2,break_point=self.break_point)
        self.m2pr = _cmp.BrokenPowerLawDoubleGaussian_math(min_pl=self.mmin,max_pl=self.mmax,lambda_g=self.lambda_g,lambda_g_low=self.lambda_g_low,
                                                    mu_g_low=self.mu_g_low,sigma_g_low=self.sigma_g_low,mu_g_high=self.mu_g_high,
                                                    sigma_g_high=self.sigma_g_high,min_g=self.mmin,max_g=self.mu_g_high+5*self.sigma_g_high,
                                                    alpha_1=-self.alpha_1,alpha_2=-self.alpha_2,break_point=self.break_point)

        self.mdis={'mass_1': _cmp.SmoothedDipProb(origin_prob=self.m1pr,right_smooth=self.delta_m_high_pass,
                                                  left_smooth=self.delta_m_low_pass,A=self.A,notch_lower=self.notch_left,
                                                  notch_lower_smooth=self.notch_smooth_left,notch_upper=self.notch_right,notch_upper_smooth=self.notch_smooth_right),
                      'mass_2': _cmp.SmoothedDipProb(origin_prob=self.m2pr,right_smooth=self.delta_m_high_pass,
                                                  left_smooth=self.delta_m_low_pass,A=self.A,notch_lower=self.notch_left,
                                                  notch_lower_smooth=self.notch_smooth_left,notch_upper=self.notch_right,notch_upper_smooth=self.notch_smooth_right)}
        
        self.mmax = self.mdis['mass_1'].maximum
        self.mmin = self.mmin
        self.mmax2 = self.mmax

        # generate samples for normalisation 
        self.m1_samp, self.m2_samp = self.sample(10000)
        
    @staticmethod
    def grid_constraint_call(constraint_grid, values, parameter_grid, fixed_params):
        new_grid = peaks_grid_constraint(constraint_grid, values, parameter_grid, fixed_params)
        return new_grid
    
    @staticmethod
    def sampling_constraint_call(prior_dict):
        new_dict = peaks_sampling_constraint(prior_dict)
        return new_dict

    def sample(self, Nsample):
        '''
        Samples from the probability distribution. Assumes m1 and m2 are independent for use with pairing function.
        
        Parameters
        ----------
        Nsample: int
            Number of samples to generate
        
        Returns
        -------
        Samples: array_like
        '''
        sarray_1 =np.linspace(self.mdis['mass_1'].minimum,self.mdis['mass_1'].maximum,10000)
        sarray_2 =np.linspace(self.mdis['mass_2'].minimum,self.mdis['mass_2'].maximum,10000)

        cdfeval_1=self.mdis['mass_1'].cdf(sarray_1)
        cdfeval_2=self.mdis['mass_2'].cdf(sarray_2)

        randomcdf_1=np.random.rand(Nsample)
        randomcdf_2=np.random.rand(Nsample)

        return np.interp(randomcdf_1,cdfeval_1,sarray_1), np.interp(randomcdf_2,cdfeval_2,sarray_2)     
    
class multipopulation_pairing_func(multipopulation_broken_powerlaw_multi_peak_gaussian):
    """
    Child class of multipopulation_broken_powerlaw_multi_peak_gaussian which also inherits from m_priors.
    
    Adds a simple powerlaw pairing function to the distribution, with index beta

    Parameters
    ----------
    beta: float
        powerlaw index for pairing function
    """

    def __init__(self, alpha_1=1.0, alpha_2=3.0, beta=0.81, mmin=1.0, mmax=112.5, lambda_g=0.3,
                  lambda_g_low=0.4, mu_g_low=15.0, sigma_g_low=3.88, mu_g_high=32.27, sigma_g_high=3.88, 
                  delta_m_low_pass=1, delta_m_high_pass=0.1, A=0, notch_left=3.0, notch_right=5.0, 
                  notch_smooth_left=1, notch_smooth_right=0.5):
        super().__init__(alpha_1, alpha_2, mmin, mmax, lambda_g, lambda_g_low, mu_g_low, sigma_g_low, 
                         mu_g_high, sigma_g_high, delta_m_low_pass, delta_m_high_pass, A, notch_left, notch_right, notch_smooth_left, notch_smooth_right)
        
        self.update_parameters(param_dict={'alpha_1':alpha_1,'alpha_2':alpha_2,'beta':beta,'mmin':mmin,'mmax':mmax,'lambda_g':lambda_g,'lambda_g_low':lambda_g_low,'mu_g_low':mu_g_low,'sigma_g_low':sigma_g_low,
                                           'mu_g_high':mu_g_high,'sigma_g_high':sigma_g_high,'delta_m_low_pass':delta_m_low_pass,'delta_m_high_pass':delta_m_high_pass,
                                           'A':A,'notch_left':notch_left,'notch_right':notch_right,'notch_smooth_left':notch_smooth_left,'notch_smooth_right':notch_smooth_right})

    def pairing_wrapper(self,ms1,ms2):
        """
        Wrapper function for pairing function
        """
        return pairing_func(ms1, ms2, self.beta)

    def joint_prob(self, ms1, ms2):
        """
        Calculates the joint probability of the masses according to the pairing function. Replaces parent joint probability method.
        Parent joint probability:
        :math: `p(m_1,m_2) = p(m_1)p(m_2|m_1)
        Pairing function joint probability:
        :math: `p(m_1,m_2) = p(m_1)p(m_2)Q(m_1,m_2)`
        Where Q(m_1,m_2) denotes the pairing function.

        Parameters
        ----------
        ms1 : array_like
            Primary mass samples.
        ms2 : array_like
            Secondary mass samples.

        Returns
        -------
        array_like
            Joint probability of the masses.
        """
       
        self.paired_dist = _cmp.PairingFunc(self.mdis,self.pairing_wrapper, self.m1_samp,self.m2_samp)

        return self.paired_dist.prob(ms1,ms2)
    

class multipopulation_pairing_func_broken(multipopulation_broken_powerlaw_multi_peak_gaussian):
    """
    Child class of multipopulation_broken_powerlaw_multi_peak_gaussian which also inherits from m_priors.
    
    Adds a broken powerlaw pairing function to the distribution, with indices beta_1 and beta_2

    Parameters
    ----------
    beta_1: float
        powerlaw index for pairing function below break point
    beta_2: float
        powerlaw index for pairing function above break point
    """

    def __init__(self, alpha_1=1.0, alpha_2=3.0, beta_1=0.81, beta_2=1.11, mmin=1.0, mmax=112.5, lambda_g=0.3,
                  lambda_g_low=0.4, mu_g_low=15.0, sigma_g_low=3.88, mu_g_high=32.27, sigma_g_high=3.88, 
                  delta_m_low_pass=1, delta_m_high_pass=0.1, A=0, notch_left=3.0, notch_right=5.0, 
                  notch_smooth_left=1, notch_smooth_right=0.5):
        super().__init__(alpha_1, alpha_2, mmin, mmax, lambda_g, lambda_g_low, mu_g_low, sigma_g_low, 
                         mu_g_high, sigma_g_high, delta_m_low_pass, delta_m_high_pass, A, notch_left, notch_right, notch_smooth_left, notch_smooth_right)
        
        self.update_parameters(param_dict={'alpha_1':alpha_1,'alpha_2':alpha_2,'beta_1':beta_1,'beta_2':beta_2,'mmin':mmin,'mmax':mmax,'lambda_g':lambda_g,'lambda_g_low':lambda_g_low,'mu_g_low':mu_g_low,'sigma_g_low':sigma_g_low,
                                           'mu_g_high':mu_g_high,'sigma_g_high':sigma_g_high,'delta_m_low_pass':delta_m_low_pass,'delta_m_high_pass':delta_m_high_pass,
                                           'A':A,'notch_left':notch_left,'notch_right':notch_right,'notch_smooth_left':notch_smooth_left,'notch_smooth_right':notch_smooth_right})

    def pairing_wrapper(self,ms1,ms2):
        """
        Wrapper function for pairing function
        """
        return pairing_func_broken(ms1, ms2, self.beta_1, self.beta_2, self.break_point)
    
    def joint_prob(self, ms1, ms2):
       
        """
        Calculates the joint probability of the masses according to the pairing function. Replaces parent joint probability method.
        Parent joint probability:
        :math: `p(m_1,m_2) = p(m_1)p(m_2|m_1)
        Pairing function joint probability:
        :math: `p(m_1,m_2) = p(m_1)p(m_2)Q(m_1,m_2)`
        Where Q(m_1,m_2) denotes the pairing function.

        Parameters
        ----------
        ms1 : array_like
            Primary mass samples.
        ms2 : array_like
            Secondary mass samples.

        Returns
        -------
        array_like
            Joint probability of the masses.
        """
        self.paired_dist = _cmp.PairingFunc(self.mdis, self.pairing_wrapper, self.m1_samp,self.m2_samp)

        return self.paired_dist.prob(ms1,ms2)