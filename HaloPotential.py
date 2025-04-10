"""
Module for providing a galaxy+NFW+external gravity potential to the cgm_model module
"""

import numpy as np
import scipy
from numpy import log as ln, log10 as log, e, pi, arange, zeros
from astropy import units as un, constants as cons
from astropy.cosmology import Planck15 as cosmo
import cgm_model_interface as CMI

h0=cosmo.H0.value/100
X = 0.75     #hydrogen mass fraction
mu = 4/(3+5*X) #mean molecular weight
mp = cons.m_p.to('g') #proton mass

class PowerLaw(CMI.Potential):
    def __init__(self,m,vc_Rvir,Rvir,R_phi0_to_Rvir=10):
        self.m = m
        self.vc_Rvir = vc_Rvir
        self.Rvir = Rvir
        self.R_phi0 = R_phi0_to_Rvir*Rvir
    def vc(self, r):
        return self.vc_Rvir * (r/self.Rvir)**self.m
    def Phi(self, r):
        if self.m!=0:
            return -self.vc_Rvir**2 / (2*self.m) * ((self.R_phi0/self.Rvir)**(2*self.m) - (r/self.Rvir)**(2*self.m))
        else:
            return -self.vc_Rvir**2 * ln(self.R_phi0/r)
    def dlnvc_dlnR(self, r):
        return self.m

class PowerLaw_with_AngularMomentum(PowerLaw):
    def __init__(self,m,vc_Rvir,Rvir,Rcirc):
        PowerLaw.__init__(self,m,vc_Rvir,Rvir)
        self.Rcirc = Rcirc
    def vc(self, r):
        vc = PowerLaw.vc(self,r)
        return vc * (1-(self.Rcirc/r)**2)**0.5
    def vc(self, r):
        vc = PowerLaw.vc(self,r)
        return vc * (1-(self.Rcirc/r)**2)**0.5
    def dlnvc_dlnR(self,r):
        dlnvc_dlnR = PowerLaw.dlnvc_dlnR(self,r)
        return dlnvc_dlnR + ((r/self.Rcirc)**2-1)**-1.

class NFW(CMI.Potential):	
    def __init__(self,Mvir,z,cvir=None,_fdr = 100.):
        self._fdr = _fdr
        self.Mvir = Mvir
        self.z = z
        if cvir==None:
            self.cvir = 7.85*(self.Mvir/2e12/un.M_sun*h0)**(-0.081)*(1+self.z)**(-0.71) #Duffy et al. 2008
        else:
            self.cvir = cvir
        self.dr = self.r_scale()/self._fdr
        rs = arange(self.dr.value,self.rvir().value,self.dr.value) * un.kpc
        self.rho_scale = (self.Mvir / (4*pi * rs**2 * self.dr * 
                                               self.rho2rho_scale(rs) ).sum() ).to('g/cm**3') 
    def Delta_c(self): #Bryan & Norman 98
        x = cosmo.Om(self.z) - 1
        return 18*pi**2 + 82*x - 39*x**2
    def rvir(self):
        return ((self.Mvir / (4/3.*pi*self.Delta_c()*cosmo.critical_density(self.z)))**(1/3.)).to('kpc')
    def r_ta(self,use200m=False): 
        if not use200m:
            return 2*self.rvir()
        else:
            return 2*self.r200m()
    def r_scale(self):
        return self.rvir() / self.cvir
    def rho2rho_scale(self,r): 
        return 4. / ( (r/self.r_scale()) * (1+r/self.r_scale())**2 ) 
    def rho(self,r):
        return self.rho_scale * self.rho2rho_scale(r)
    def enclosedMass(self,r):
        return (16*pi*self.rho_scale * self.r_scale()**3 * 
                        (ln(1+r/self.r_scale()) - (self.r_scale()/r + 1.)**-1.)).to('Msun')
    def v_vir(self):
        return ((cons.G*self.Mvir / self.rvir())**0.5).to('km/s')
    def vc(self,r):
        Ms = self.enclosedMass(r)
        return ((cons.G*Ms / r)**0.5).to('km/s')
    def mean_enclosed_rho2rhocrit(self,r):
        Ms = self.enclosedMass(r)
        return Ms / (4/3.*pi*r**3) / cosmo.critical_density(self.z)
    def r200(self,delta=200.):
        rs = arange(self.dr.value,2*self.rvir().value,self.dr.value)*un.kpc
        mean_rho2rhocrit = self.mean_enclosed_rho2rhocrit(rs)
        return rs[np.searchsorted(-mean_rho2rhocrit,-delta)]
    def r500(self,delta=500.):
        rs = arange(self.dr.value,2*self.rvir().value,self.dr.value)*un.kpc
        mean_rho2rhocrit = self.mean_enclosed_rho2rhocrit(rs)
        return rs[np.searchsorted(-mean_rho2rhocrit,-delta)]
    def r200m(self,delta=200.):
        rs = arange(self.dr.value,2*self.rvir().value,self.dr.value)*un.kpc
        mean_rho2rhocrit = self.mean_enclosed_rho2rhocrit(rs)
        return rs[np.searchsorted(-mean_rho2rhocrit,-delta*cosmo.Om(self.z))]		
    def r500m(self,delta=500.):
        rs = arange(self.dr.value,2*self.rvir().value,self.dr.value)*un.kpc
        mean_rho2rhocrit = self.mean_enclosed_rho2rhocrit(rs)
        return rs[np.searchsorted(-mean_rho2rhocrit,-delta*cosmo.Om(self.z))]
    def M200(self,delta=200.):
        return self.enclosedMass(self.r200(delta))
    def M200m(self,delta=200.):
        return self.enclosedMass(self.r200m(delta))
    def g(self,r):
        Ms = self.enclosedMass(r)
        return cons.G*Ms / r**2
    def t_ff(self,r):
        return 2**0.5 * r / self.vc(r)
    def T200(self):
        return (0.5*mu*mp*self.vc(self.r200())**2).to('keV')
    def dlnvc_dlnR(self, r):
        #return (ln(1+r/self.r_scale())*(self.r_scale()/r + 1.)**2 - (self.r_scale()/r + 1.))**-1.
        A = self.r_scale()+r
        B = ln(A/self.r_scale())
        return 0.5*(-r**2+A*(-r+A*B)) / (A*(r-A*B))
    def Phi(self,r):
        return -(16*pi*cons.G*self.rho_scale*self.r_scale()**3 / r * ln(1+r/self.r_scale())).to('km**2/s**2')

class NFW_withGalaxy(NFW):
    def __init__(self,Mvir,z,cvir=None,_fdr = 100.,Mgalaxy=6e10*un.Msun,scale_length=2.5*un.kpc):
        super().__init__(Mvir,z,cvir,_fdr)
        self.Mgalaxy=Mgalaxy
        self.Rd = scale_length
    def enclosedMass_galaxy(self,r):
        """disk galaxy mass distribution"""
        factor =  1-np.e**-(r/self.Rd)*(self.Rd+r)/self.Rd
        return factor * self.Mgalaxy 
    def enclosedMass(self, r):
        return super().enclosedMass(r) + self.enclosedMass_galaxy(r)
    def dlnvc_dlnR(self,r):
        vc2_halo = (cons.G*super().enclosedMass(r)/r).to('km**2/s**2')
        AA = vc2_halo/self.vc(r)**2
        A = super().dlnvc_dlnR(r)
        dvc2_glx_dr = ((cons.G*self.Mgalaxy / r).to('km**2/s**2')/r * 
                       (np.e**(-r/self.Rd)*(r**2+self.Rd**2+r*self.Rd)/self.Rd**2 - 1))
        vc2_galaxy = (cons.G*self.enclosedMass_galaxy(r)/r).to('km**2/s**2')
        B = 0.5 * r*dvc2_glx_dr/vc2_galaxy
        BB = vc2_galaxy/self.vc(r)**2
        print(vc2_halo[20]**0.5,AA[20],A[20],vc2_galaxy[20]**0.5,BB[20],B[20])
        return A*AA+B*BB
    def Phi(self,r):        
        return super().Phi(r) + cons.G*self.Mgalaxy*(np.e**-(r/self.Rd)-1)/r
    def mean_enclosed_rho2rhocrit(self,r): 
        """does not include galaxy"""
        Ms = super().enclosedMass(r)
        return Ms / (4/3.*pi*r**3) / cosmo.critical_density(self.z)
    def M200(self,delta=200.):
        """does not include galaxy"""
        return super().enclosedMass(self.r200(delta))
    def M200m(self,delta=200.):
        """does not include galaxy"""
        return super().enclosedMass(self.r200m(delta))
