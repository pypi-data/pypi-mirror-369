import numpy as np
import massfunc as mf
import astropy.units as u
from scipy.interpolate import interp1d
from scipy.integrate import quad,quad_vec
from scipy.optimize import fsolve,root_scalar
from . import PowerSpectrum as ps

cosmo = mf.SFRD()
m_H = (cosmo.mHu.to(u.M_sun)).value #M_sun
omega_b = cosmo.omegab
omega_m = cosmo.omegam
rhom = cosmo.rhom

class Barrier:

    def __init__(self,fesc=0.2, qion=7000.0,z_v=10.0,nrec=3,xi=10.0,A2byA1=0.1,kMpc_trans=420,alpha=2.0,beta=0.0):
        self.fesc = fesc
        self.qion = qion
        self.z = z_v
        self.nrec = nrec
        self.xi = xi
        self.M_min = cosmo.M_vir(0.61,1e4,self.z)  # Minimum halo mass for ionization
        self.M_J = cosmo.M_Jeans(self.z,20.0,1.22)
        self.Nion_interp_func = []  
        self.Mv_list = []
        self.N_xi_interp_func = []  
        self.N_xi_Mv = []  
        self.powspec = ps.MassFunctions(A2byA1=A2byA1,kMpc_trans=kMpc_trans,alpha=alpha,beta=beta)
        self.ratio = self.Modify_Ratio()  # Ratio for partial ionization

    # Interpolation for Nion
    def Nion_interp_ini(self, Mv):
        deltaR = np.concatenate((np.linspace(-0.999,2,1000), np.linspace(2.001,25,1000)))
        self.Nion_interp_Mv = interp1d(deltaR, self.Nion(Mv, deltaR), kind='cubic')
        return self.Nion_interp_Mv

    def Nion_interp(self, Mv, deltaR):
        if f"{Mv:.3f}" not in self.Mv_list:
            self.Mv_list.append(f"{Mv:.3f}")
            self.Nion_interp_func.append(self.Nion_interp_ini(Mv))
            return self.Nion_interp_func[-1](deltaR)
        else:
            index = self.Mv_list.index(f"{Mv:.3f}")
            return self.Nion_interp_func[index](deltaR)

    # Interpolation for N_xi
    def N_xi_interp_ini(self, Mv):
        deltaR = np.concatenate((np.linspace(-0.999,2,1000), np.linspace(2.001,25,1000)))
        self.N_xi_interp_Mv = interp1d(deltaR, self.N_xi(Mv, deltaR), kind='cubic')
        return self.N_xi_interp_Mv

    def N_xi_interp(self, Mv, deltaR):
        if f"{Mv:.3f}" not in self.N_xi_Mv:
            self.N_xi_Mv.append(f"{Mv:.3f}")
            self.N_xi_interp_func.append(self.N_xi_interp_ini(Mv))
            return self.N_xi_interp_func[-1](deltaR)
        else:
            index = self.N_xi_Mv.index(f"{Mv:.3f}")
            return self.N_xi_interp_func[index](deltaR)

    #patch
    def Nion_ST(self):
        def Nion_ST_diff(m):
            fstar = cosmo.fstar(m)
            return (self.fesc * self.qion / m_H * fstar * omega_b / omega_m * m * self.powspec.dndmst(m, self.z))
        mslice = np.logspace(np.log10(self.M_min), np.log10(cosmo.M_vir(0.61,1e8,self.z)), 20)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nion_ST_diff, mslice[i], mslice[i+1], epsrel=1e-5)[0]
        return ans

    def Nion_PS(self):
        def Nion_PS_diff(m):
            fstar = cosmo.fstar(m)
            return (self.fesc * self.qion / m_H * fstar * omega_b / omega_m * m * self.powspec.dndmps(m, self.z))
        mslice = np.logspace(np.log10(self.M_min), np.log10(cosmo.M_vir(0.61,1e8,self.z)), 20)
        ans = 0
        for i in range(len(mslice)-1):
            ans += quad(Nion_PS_diff, mslice[i], mslice[i+1], epsrel=1e-5)[0]
        return ans

    def Modify_Ratio(self):
        return self.Nion_ST() / self.Nion_PS()

    def delta_L(self, deltar):
        return (1.68647 - 1.35 / (1 + deltar) ** (2 / 3) - 1.12431 / (1 + deltar) ** (1 / 2) + 0.78785 / (1 + deltar) ** (0.58661)) / cosmo.Dz(self.z)
    
    def dndmeps(self,M,Mr,deltar,z):
        deltaL = self.delta_L(deltar)
        sig1 = self.powspec.sigma2_interp(M) - self.powspec.sigma2_interp(Mr)
        del1 = cosmo.deltac(z) - deltaL
        return cosmo.rhom * (1 + deltar) / M / np.sqrt(2 * np.pi) * abs(self.powspec.dsigma2_dm_interp(M)) * del1 / sig1 ** (3 / 2) * np.exp(-del1 ** 2 / (2 * sig1))

    def Nion_diff(self,m,Mv,deltaR):
        fstar = cosmo.fstar(m)
        return self.fesc*self.qion/m_H *fstar* omega_b/omega_m *m*self.dndmeps(m,Mv,deltaR,self.z)

    def Nion(self,Mv,delta_R):
        return quad_vec(self.Nion_diff, self.M_min, Mv, args=(Mv,delta_R),epsrel=1e-5)[0]

    def N_H(self,deltaR):
        return 1/m_H * omega_b/omega_m * rhom *(1+deltaR) 

    def N_xi_diff(self,M,Mv,deltaR):
        return self.xi/m_H * omega_b/omega_m *M*self.dndmeps(M,Mv,deltaR,self.z)
    
    def N_xi(self,Mv,delta_R):
        return quad_vec(self.N_xi_diff, self.M_J,self.M_min, args=(Mv,delta_R),epsrel=1e-5)[0]
    
    def Calcul_deltaVM_EQ(self,deltaR,Mv):
        return self.ratio *self.Nion(Mv,deltaR) - (1+self.nrec)*self.N_H(deltaR)

    def Calcul_deltaVM(self,Mv):
        result = root_scalar(self.Calcul_deltaVM_EQ, args=(Mv,), bracket=[-0.99, 1.5], method='bisect')
        return result.root
    
    def Calcul_deltaVM_Minihalo_EQ(self,deltaR,Mv):
        return self.ratio *self.Nion(Mv,deltaR) - (1+self.nrec)*self.N_H(deltaR) - self.ratio * self.N_xi(Mv,deltaR)

    def Calcul_deltaVM_Minihalo(self,Mv):
        result = root_scalar(self.Calcul_deltaVM_Minihalo_EQ, args=(Mv,), bracket=[-0.99, 1.67], method='bisect')
        return result.root
    