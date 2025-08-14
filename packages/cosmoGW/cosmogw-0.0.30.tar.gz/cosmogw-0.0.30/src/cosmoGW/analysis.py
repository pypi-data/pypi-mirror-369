"""
analysis.py is a Python routine that contains functions used in the analyses of potential
detection of GW signals by space-based GW detector LISA.

Currently part of the cosmoGW code:

Author:  Alberto Roper Pol
Created: 01/12/2021
Updated: 23/07/2025 (release of the cosmoGW code)

Main references are:

RoperPol:2022iel - A. Roper Pol, C. Caprini, A. Neronov, D. Semikoz,
"The gravitational wave signal from primordial magnetic fields in the
Pulsar Timing Array frequency band," Phys. Rev. D 105, 123502 (2022),
arXiv:2201.05630

RoperPol:2023bqa - A. Roper Pol, A. Neronov, C. Caprini, T. Boyer,
D. Semikoz, "LISA and γ-ray telescopes as multi-messenger probes of a
first-order cosmological phase transition," arXiv:2307.10744 (2023)
"""

import numpy  as np
import pandas as pd
import matplotlib.pyplot as plt
import cosmoGW.hydro_bubbles  as hb
import cosmoGW.GW_templates   as tmp
import cosmoGW.GW_models      as mod
import cosmoGW.interferometry as inte
import cosmoGW.cosmology      as co
import cosmoGW.GW_back        as cGW
import astropy.units          as u

### Reference values

mins_ref = -3        # minimum frequency for analysis (default is 1e-3)
maxs_ref = 4         # maximum frequency for analysis (default is 1e4)
Nss_ref  = 1000      # number of frequency points (default is 1000)

def analysis_LISA_alphabeta(alphas, betas, vws, TTs, epsturb=1, turb=True, mins=mins_ref,
                            cs2=hb.cs2_ref, quiet=False,
                            maxs=maxs_ref, Nss=Nss_ref,interf='LISA', Nturb=mod.N_turb,
                            TDI=True, chan='A', expansion=True, Nsh=1.,
                            a_sw=tmp.a_sw_ref, b_sw=tmp.b_sw_ref, c_sw=tmp.c_sw_ref,
                            alp1_sw=0, alp2_sw=0, corrRs=True, model_efficiency='fixed_value',
                            OmGW_tilde=tmp.OmGW_sw_ref, bs_HL_eff=20, model_K0='Espinosa',
                            bs_k1HL=40, model_decay='sound_waves', interpolate_HL_decay=True,
                            b=0, model_shape='sw_HL', strength='weak', interpolate_HL_shape=False,
                            a_turb=tmp.a_turb, b_turb=tmp.b_turb, alp_turb=tmp.alp_turb,
                            tdecay=tmp.tdecay_ref, alpPi=tmp.alpPi, fPi=tmp.fPi, bPi=tmp.bPi_vort,
                            interpolate_HL_n3=False, h0=1., Neff=co.Neff_ref, Tobs=4):
                
    '''
    Function that analyzes the GW signal produced by sound waves and turbulence
    for a range of phase transition parameters (alpha, beta, vw, T, epsturb)
    and returns the SNR for each parameter.

    It uses the sound waves and turbulence templates in GW_templates.

    Arguments:
        alphas  -- strength of the phase transition
        betas   -- rate of nucleation of the phase transition
        vws     -- array of wall velocities
        TTs     -- array of temperature scales in GeV
        epsturb -- array of values of the fraction of turbulent
                   energy density
    '''

    s = np.logspace(mins, maxs, Nss)

    _ = co.check_temperature_MeV(TTs,
                func='analysis_LISA_alphabeta of analysis.py')
    TTs = TTs.to(u.GeV)

    mult_alphas  = isinstance(alphas,    (list, tuple, np.ndarray))
    mult_betas   = isinstance(betas,     (list, tuple, np.ndarray))
    mult_vws     = isinstance(vws,       (list, tuple, np.ndarray))
    mult_TT      = isinstance(TTs.value, (list, tuple, np.ndarray))
    mult_epsturb = isinstance(epsturb,   (list, tuple, np.ndarray))

    if not mult_alphas:  alphas   = np.array([alphas])
    if not mult_betas:   betas    = np.array([betas])
    if not mult_vws:     vws      = np.array([vws])
    if not mult_TT:      TTs      = np.array([TTs])
    if not mult_epsturb: epsturb  = np.array([epsturb])
    
    # relativistic and adiabatic degrees of freedom
    g  = co.thermal_g(T=TTs, s=0, file=True, Neff=co.Neff_ref)
    gS = co.thermal_g(T=TTs, s=1, file=True, Neff=co.Neff_ref)

    # LISA sensitivity
    f_LISA, OmLISA, _ = inte.read_sens(interf=interf, Xi=False, TDI=TDI, chan=chan)

    SNR = np.zeros((len(epsturb), len(TTs), len(vws), len(alphas), len(betas)))

    if not turb: epsturb = [0]

    # Spectrum from sound waves using fit (default is the one based on HL simulations
    # of RoperPol:2023bqa, Jinno:2022mie)

    freqs_sw, OmGWs_sw = \
            tmp.OmGW_spec_sw(s, alphas, betas, vws=vws, cs2=cs2, quiet=True, a_sw=a_sw,
                 b_sw=b_sw, c_sw=c_sw, alp1_sw=alp1_sw, alp2_sw=alp2_sw, corrRs=corrRs,
                 expansion=expansion, Nsh=Nsh, model_efficiency=model_efficiency,
                 OmGW_tilde=OmGW_tilde, bs_HL_eff=bs_HL_eff, model_K0=model_K0, bs_k1HL=bs_k1HL,
                 model_decay=model_decay, interpolate_HL_decay=interpolate_HL_decay, b=b,
                 model_shape=model_shape, strength=strength, interpolate_HL_shape=interpolate_HL_shape,
                 interpolate_HL_n3=interpolate_HL_n3, redshift=False)

    freqs_turb = np.zeros((len(s), len(vws), len(betas)))
    OmGWs_turb = np.zeros((len(epsturb), len(s), len(vws), len(alphas), len(betas)))

    if turb:

        for p in range(0, len(epsturb)):
            
            if not quiet: print('Computing spectra for eps_turb = %.1f'%epsturb[p])
            # Spectrum from MHD turbulence based on the constant-in-time model
            # (RoperPol:2023bqa, RoperPol:2022iel)
            _, OmGWs_turb[p] = tmp.OmGW_spec_turb_alphabeta(s, alphas, betas, vws=vws, eps_turb=epsturb[p],
                                 model_K0=model_K0, bs_HL_eff=bs_HL_eff, N=Nturb,
                                 cs2=cs2, corrRs=corrRs, quiet=True, a_turb=a_turb, b_turb=b_turb,
                                 alp=alp_turb, expansion=expansion, tdecay=tdecay, tp='both', alpPi=alpPi,
                                 fPi=fPi, bPi=bPi, redshift=False)

    for i in range(0, len(TTs)):

        if not quiet: print('Redshifting spectra for T = %.e GeV'%TTs[i].value)

        freqs_sw_red, OmGWs_sw_red = \
                cGW.shift_OmGW_today(freqs_sw, OmGWs_sw, g=g[i], gS=gS[i],
                                     T=TTs[i], h0=h0, Neff=Neff)

        for p in range(0, len(epsturb)):
        
            if not quiet:
                print('Redshifting spectra for eps_turb = %.1f and computing SNR'%epsturb[p])
            
            freqs_turb_red, OmGWs_turb_red = \
                    cGW.shift_OmGW_today(freqs_turb[p], OmGWs_turb[p], g=g[i], gS=gS[i],
                                         T=TTs[i], h0=h0, Neff=Neff)

            OmGWs_sum = OmGWs_sw_red + OmGWs_turb_red
               
            for m in range(0, len(vws)):
                for l in range(0, len(betas)):
                    for j in range(0, len(alphas)):
                        SNR[p, i, m, j, l] = \
                            inte.SNR(freqs_sw_red[:, m, l], OmGWs_sum[:, m, j, l], f_LISA, OmLISA, T=Tobs)

    if not turb: SNR = SNR[0, :, :, :, :]
                
    return SNR

def analysis_LISA_alphabeta_Ts_vws(ss, TTs, vws, alphas, betas, cs2=1/3, pr_vw=True, pr_T=True, Omgwtilde=1e-2,
                                   a2_hl=.6, a1_hl=1.5, eps_turb=1., a_turb=4, b_turb=5/3, alpha_turb=6/17,
                                   alpPi=2.15, fPi=2.2, N_turb=2, SNR=10, T=4, save=True, ne=2, ret=False):
    
    '''
    Function that analyzes the detectability of a GW signal compared to the LISA
    PLS that is given for a range of alphas and betas (corresponding to the thermodynamic
    parameters of a first-order phase transition) each for a range of wall speeds (xiw) and
    temperatures.
    
    Can be used to analyze GW signals from sound waves, turbulence, or a combination of both.
    
    OmGW has to be 3d with OmGW[f, beta, alpha].
    Note that the output pos is defined with inverted indices: pos[alpha, beta].
    '''
    
    gs = np.zeros(len(TTs))
    Hs = np.zeros(len(TTs))*u.Hz
    FGW0 = np.zeros(len(TTs))
    for i in range(0, len(TTs)):
        g = cosmoGW.thermal_g(T=TTs[i]*u.GeV)
        Hs[i], FGW0[i] = cosmoGW.shift_OmGW_today(2*np.pi, 1, g=g,
                                                  T=TTs[i]*u.GeV, d=1, h0=1)
    
    pos_SSM = np.zeros((len(TTs), len(vws), len(alphas), len(betas))) + False
    pos_hl = np.zeros((len(TTs), len(vws), len(alphas), len(betas))) + False
    min_alpha_hl = np.zeros((len(TTs), len(vws), len(betas))) + 1e30
    min_alpha_SSM = np.zeros((len(TTs), len(vws), len(betas))) + 1e30

    lfs = GW_fopt.beta_Rs(betas, xiw=vws, cs2=cs2, multi=True)

    for j in range(0, len(vws)):

        if pr_vw: print('computing vw = %.2f (%i/%i) \n'%(vws[j], j + 1, len(vws)))

        OmGW_sw_SSM, OmGW_sw_hl = GW_fopt.OmGW_sws(ss, alphas, betas, xiw=vws[j], cs2=cs2,
                                                   tilOmGW=Omgwtilde, a2_hl=a2_hl, a1_hl=a1_hl, multi_ab=True)
        
        if eps_turb > 0:
            OmGW_mhd = GW_fopt.OmGW_MHDturb(ss, alphas, betas, xiw=vws[j], cs2=cs2, eps=eps_turb, a_turb=a_turb, b_turb=b_turb,
                                        alpha_turb=alpha_turb, alpPi=alpPi, fPi=fPi, N_turb=N_turb, equip=True, multi_ab=True)

        for m in range(0, len(TTs)):
               
            if ne == 2: TT_st = '%.2e'%TTs[m]
            if ne == 1: TT_st = '%.1e'%TTs[m]

            if pr_T: print('computing temperature T = %s GeV (%i/%i) \n'%(TT_st, m + 1, len(TTs)))

            OmGW_tot_SSM = OmGW_sw_SSM*FGW0[m]
            OmGW_tot_hl = OmGW_sw_hl*FGW0[m]
            if eps_turb > 0:
                OmGW_tot_SSM += OmGW_mhd*FGW0[m]
                OmGW_tot_hl += OmGW_mhd*FGW0[m]

            pos_SSM[m, j, :, :], min_alpha_SSM[m, j, :] = \
                    analysis_LISA_alphabeta(alphas, betas, ss*Hs[m].value, OmGW_tot_SSM, lf=lfs[:, j],
                                               xiw=vws[j], cs2=cs2, pplt=False, SNR=SNR, T=T, plt_notpos=False)
            pos_hl[m, j, :, :], min_alpha_hl[m, j, :] = \
                    analysis_LISA_alphabeta(alphas, betas, ss*Hs[m].value, OmGW_tot_hl, lf=lfs[:, j],
                                               xiw=vws[j], cs2=cs2, pplt=False, SNR=SNR, T=T, plt_notpos=False)
        
            if j == (len(vws) - 1):
                if save:
                    save_files_alphabeta_analysis(pos_SSM[m, :, :, :], pos_hl[m, :, :, :],
                                                  min_alpha_SSM[m, :, :], min_alpha_hl[m, :, :],
                                                  betas, alphas, vws, TT=TTs[m], epsturb=eps_turb,
                                                  pr_T=pr_T)
            if m == 0 and ret:
                print('if ret is set to True only first T is computed and the results are returned by the function')
                return pos_SSM[m, :, :, :], pos_hl[m, :, :, :], min_alpha_SSM[m, :, :], min_alpha_hl[m, :, :]
                
                
def save_files_alphabeta_analysis(pos_SSM, pos_hl, min_alpha_SSM, min_alpha_hl, betas, alphas, vws,
                                  TT='100', dirr='results/', ne=2, epsturb=1., pr_T=True):
    
    '''
    Function that saves the results for an analysis made for a specific temperature TT and a 
    range of alphas, betas, and wall velocities.
    
    It saves the array with the boolean array that determines if the GW signal is above the
    threshold SNR of LISA for MHD turbulence + sound waves (both using the sound shell model SSM
    pos_SSM and the fit from Higgsless simulations pos_hl), the minimum alpha that leads to a
    possible detection for each alpha, min_alpha_SSM and min_alpha_hl, and the betas, alphas
    and vws used in the analysis.
    '''
    
    import pickle
    
    if ne == 2: TT_st = '%.2e'%TT
    if ne == 1: TT_st = '%.1e'%TT
    
    eps_st = ''
    if epsturb != 1:
        eps_st = 'eps_%.1f'%epsturb
    if epsturb < .1:
        eps_st = 'eps_%.2f'%epsturb
    if epsturb == 0:
        eps_st = '_only_sw'
    
    if pr_T: print('saving files for T = %s GeV and eps_turb = %s \n'%(TT_st, eps_st))

    TT_st = TT_st + eps_st
  
    # Open a file and use dump()
    with open(dirr + 'T%s_pos_SSM'%TT_st, 'wb') as file:
        pickle.dump(pos_SSM, file)

    with open(dirr + 'T%s_pos_hl'%TT_st, 'wb') as file:
        pickle.dump(pos_hl, file)

    with open(dirr + 'T%s_min_alpha_SSM'%TT_st, 'wb') as file:
        pickle.dump(min_alpha_SSM, file)

    with open(dirr + 'T%s_min_alpha_hl'%TT_st, 'wb') as file:
        pickle.dump(min_alpha_hl, file)

    with open(dirr + 'T%s_betas'%TT_st, 'wb') as file:
        pickle.dump(betas, file)

    with open(dirr + 'T%s_alphas'%TT_st, 'wb') as file:
        pickle.dump(alphas, file)

    with open(dirr + 'T%s_vws'%TT_st, 'wb') as file:
        pickle.dump(vws, file)
        
def read_files_alphabeta_analysis(dirr='results/', TT='100', ne=2, epsturb=1.):
    
    '''
    Function that reads the results from a LISA detection analysis already performed
    using 'analysis_LISA_alphabeta_Ts_vws' and saved into pickle files using 
    'save_files_alphabeta_analysis'.
    
    It reads the results for a specific temperature TT.
    '''
    
    import pickle
    
    if ne == 2: TT_st = '%.2e'%TT
    if ne == 1: TT_st = '%.1e'%TT
    
    eps_st = ''
    if epsturb != 1:
        eps_st = 'eps_%.1f'%epsturb
    if epsturb < .1:
        eps_st = 'eps_%.2f'%epsturb
    if epsturb == 0:
        eps_st = '_only_sw'
    TT_st = TT_st + eps_st

    with open(dirr + 'T%s_pos_SSM'%TT_st, 'rb') as file:
        pos_all_SSM = pickle.load(file)
    with open(dirr + 'T%s_pos_hl'%TT_st, 'rb') as file:
        pos_all_hl = pickle.load(file)
    with open(dirr + 'T%s_min_alpha_hl'%TT_st, 'rb') as file:
        min_alpha_hl = pickle.load(file)
    with open(dirr + 'T%s_min_alpha_SSM'%TT_st, 'rb') as file:
        min_alpha_SSM = pickle.load(file)
    with open(dirr + 'T%s_alphas'%TT_st, 'rb') as file:
        alphas = pickle.load(file)
    with open(dirr + 'T%s_betas'%TT_st, 'rb') as file:
        betas = pickle.load(file)
    with open(dirr + 'T%s_vws'%TT_st, 'rb') as file:
        vws = pickle.load(file)
        
    return alphas, betas, vws, pos_all_SSM, pos_all_hl, min_alpha_SSM, min_alpha_hl