"""
Fermi Science Tools GRB Analysis for VHE Detection

This code will analyze the PH weekly files downloaded


"""

import os


from LAT_files import LAT_DATA as LD
from LAT_files import LAT_Files as LF
import gt_apps as my_apps



"This assumes that this script will be in the working directory with the SC file, a Scripts folder, and a Background folder. "

class LAT_Analysis:
    
    def __init__(self, Burst, fssc_path ):
        self.Burst = Burst
        self.fssc_path = fssc_path
        """if os.path.exists(Burst) == False:
            os.mkdir('GRB'+Burst)
        else:
            pass
        os.chdir('GRB'+Burst)"""
        LD
        LF(Burst)
        home = os.getcwd()
        self.home = home
        PH = home+'/'+str(LD.grb[Burst]['ph_file_name'])
        self.PH = PH
        SC = home+'/'+'lat_spacecraft_merged.fits'
        self.SC = SC
        MET = float(LD.grb[Burst]['MET'])
        self.MET = MET
        RA = float(LD.grb[Burst]['RA'])
        self.RA = RA
        DEC = float(LD.grb[Burst]['DEC'])
        self.DEC = DEC
        date = str(LD.grb[Burst]['Date'])
        self.date = date
    
    def Analyze(self):
        from GtApp import GtApp
        
        import pyLikelihood
        from UnbinnedAnalysis import *
        os.chdir('Scripts')
        from make2FGLxml import *
        os.chdir('..')
        tbin = []
        self.tbin = tbin
        timebins = []
        self.timebins = timebins
       
        times = [100, 1900,3700,5500,7300,9100, 10900, 12700, 14500]
        self.times = times
        if os.path.exists('Analysis Files') == False:
            os.mkdir('Analysis Files')
        else:
            pass
        os.chdir('Analysis Files')
        for t in times:
            filelist = [ f for f in os.listdir(".") ]
            for f in filelist:
                os.remove(f)
            
            try:
                try:
                    my_apps.filter['ra'] = self.RA
                    my_apps.filter['dec'] = self.DEC
                    my_apps.filter['rad'] = 15
                    my_apps.filter['emin'] = 100
                    my_apps.filter['emax'] = 300000
                    my_apps.filter['zmax'] = 100
                
                
                    if  t == 100:
                        print "Running gtselect. Extracting data from "+ str(t-100) +" to " +str(t)+ " seconds..."
                        my_apps.filter['evclass'] = 0
                        my_apps.filter['tmin'] = self.MET
                        my_apps.filter['tmax'] = self.MET+t
                    else:
                        print "Running gtselect. Extracting data from "+ str(t-1800) +" to " +str(t)+ " seconds..."
                        my_apps.filter['evclass'] = 2
                        my_apps.filter['tmin'] = self.MET + t - 1800
                        my_apps.filter['tmax'] = self.MET + t
                    my_apps.filter['infile'] = self.PH
                    my_apps.filter['outfile'] = 'filtered.fits'
                    my_apps.filter.run()
                except:
                        print "There was a problem with gtselect."
                        raise
                print "Running gtmaketime..."
                try:
                    my_apps.maketime['scfile'] = self.SC
                    my_apps.maketime['filter'] = '(DATA_QUAL>0)&&(LAT_CONFIG==1)'
                    my_apps.maketime['roicut'] = 'yes'
                    my_apps.maketime['evfile'] = 'filtered.fits'
                    my_apps.maketime['outfile'] = 'filtered_gti.fits'
                    my_apps.maketime['debug'] = True
                    my_apps.maketime.run()
                except:
                    print "There was a problem with gtmaketime. We were unable to complete selecting the good time intervals."
                    raise
                print "Running gtexpCube..."
                try:
                    my_apps.expCube['evfile'] = 'filtered_gti.fits'
                    my_apps.expCube['scfile'] = self.SC
                    my_apps.expCube['outfile'] = 'ltCube.fits'
                    my_apps.expCube['dcostheta'] = 0.025
                    my_apps.expCube['binsz'] = 1
                    my_apps.expCube.run()
                except:
                    print "There was a problem with gtexpCube."
                    raise

                print "Running gtexpmap..."
                try:
                    my_apps.expMap['evfile'] = 'filtered_gti.fits'
                    my_apps.expMap['scfile'] = self.SC
                    my_apps.expMap['expcube'] ='ltCube.fits'
                    my_apps.expMap['outfile'] ='expMap.fits'
                    my_apps.expMap['irfs'] ='CALDB'
                    my_apps.expMap['srcrad'] = 25
                    my_apps.expMap['nlong'] = 120
                    my_apps.expMap['nlat'] = 120
                    my_apps.expMap['nenergies'] = 20
                    my_apps.expMap.run()
                except:
                    print "There was a problem with gtexpmap."
                    raise

                print "Making source file and populating it with sources..."
                gll_psc = self.home+'/background_files/gll_psc_v08.fit'
                gll_iem = self.home+'/background_files/gll_iem_v05_rev1.fit'
                iso_source = self.home+'/background_files/iso_source_v05_rev1.txt'
                mymodel = srcList(gll_psc,'filtered_gti.fits','model.xml')
                mymodel.makeModel(gll_iem, 'gll_iem_v05_rev1', iso_source, 'iso_source_v05_rev1', extDir = self.fssc_path+ '/refdata/fermi/pyBurstAnalysisGUI/templates')
                print "Adding diffuse response..."
                
                diffrsp = GtApp('gtdiffrsp')
                diffrsp['evfile'] = 'filtered_gti.fits'
                diffrsp['scfile'] = self.SC
                diffrsp['srcmdl'] = 'model.xml'
                diffrsp.run()
                
                print "Running likelihood analysis..."
                obs = UnbinnedObs('filtered_gti.fits',self.SC,expMap='expMap.fits',expCube='ltCube.fits',irfs='CALDB')
                like = UnbinnedAnalysis(obs,'model.xml',optimizer='NewMinuit')
                self.like = like
                print 'Adding GRB'+self.Burst+' as a source.'
                new_Source = pyLike.PointSource(0,0,like.observation.observation)
                pl = pyLike.SourceFactory_funcFactory().create("PowerLaw2")
                pl.setParamValues((1, -2, 20, 2e5))
                indexPar = pl.getParam("Index")
                indexPar.setBounds(-3.5, -1)
                #indexPar.setFree(False)
                #indexPar.setValue(-2)
                integralPar = pl.getParam("Integral")
                integralPar.setBounds(1e-5, 1000.0)
                integralPar.setScale(1e-6)
                pl.setParam(integralPar)
                LLPar = pl.getParam("LowerLimit")
                ULPar = pl.getParam("UpperLimit")
                LLPar.setBounds(20,200000)
                ULPar.setBounds(20,200000)
                LLPar.setScale(1.0)
                ULPar.setScale(1.0)
                pl.setParam(LLPar)
                pl.setParam(ULPar)
                new_Source.setSpectrum(pl)
                new_Source.setName("GRB"+self.Burst)
                new_Source.setDir(self.RA,self.DEC, True, False)
                like.addSource(new_Source)
                
                sourceDetails = {}
                for source in like.sourceNames():
                    sourceDetails[source] = like.Ts(source)
                for source,TS in sourceDetails.iteritems():
                    print source, TS
                    if (TS < 9.0):
                        if source == 'GRB'+self.Burst:
                            pass
                        else:
                            print "Deleting..."
                            self.like.deleteSource(source)
                likeobj = pyLike.NewMinuit(like.logLike)
                like.fit(verbosity=0,covar=True, optObject=likeobj)
                print 'Our convergence is...'
                print likeobj.getRetCode()
                tbin.append(like)
                timebins.append(t)
                
            except:
                print "Looks like there was an issue with this timebin."
                pass
        os.chdir('..')
    def plot_counts(self, timebin = 1):
        
        import matplotlib.pyplot as plt
        import numpy as np
        E = (self.tbin[timebin].energies[:-1] + self.tbin[timebin].energies[1:])/2.
        plt.figure(figsize=(9,9))
        plt.ylim((0.4,1e4))
        plt.xlim((200,300000))
        sum_model = np.zeros_like(self.tbin[timebin]._srcCnts(self.tbin[timebin].sourceNames()[0]))
        for sourceName in self.tbin[timebin].sourceNames():
            if sourceName == "GRB"+self.Burst:
                sum_model = sum_model + self.tbin[timebin]._srcCnts(sourceName)
                plt.loglog(E,self.tbin[timebin]._srcCnts(sourceName),label=sourceName[0:])
            else:
                sum_model = sum_model + self.tbin[timebin]._srcCnts(sourceName)
                plt.loglog(E,self.tbin[timebin]._srcCnts(sourceName),label=sourceName[1:])
                    
        plt.loglog(E,sum_model,label='Total Model')
        plt.errorbar(E,self.tbin[timebin]._Nobs(),yerr=np.sqrt(self.tbin[timebin]._Nobs()), fmt='o',label='Counts')
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2)
        plt.show()
    
    

    def csv_write(self):
        import csv
        if os.path.exists('GRBs') == False:
            os.mkdir('GRBs')
        else:
            pass
        os.chdir('GRBs')
        with open('GRB'+self.Burst+'.csv', 'wb') as fp:
            a = csv.writer(fp, delimiter=',')
            data = [['Time after trigger(s)','Photon Flux(counts/cm^2/s)', 'Photon Flux Error(counts/cm^2/s)', 'Energy Flux(MeV/cm^2/s)','Energy Flux Error(MeV/cm^2/s)','Index','Index Error','RA','DEC','MET','Date']]
            for t in range(len(self.tbin)):
                GRB_DATA = str(self.tbin[t].model['GRB'+self.Burst])
                Index_line = GRB_DATA.split('\n')[3]
                index = Index_line.split(' ')[11]
                index_error = Index_line.split(' ')[13]
                data.append([self.timebins[t],self.tbin[t].flux('GRB'+self.Burst),self.tbin[t].fluxError('GRB'+self.Burst),self.tbin[t].energyFluxError('GRB'+self.Burst),self.tbin[t].energyFluxError('GRB'+self.Burst),index, index_error,self.RA,self.DEC,self.MET,self.date])
            a.writerows(data)
        os.chdir('..')

    def VHE_Analysis(self, eblModel = 'Dominguez', instrument = 'VERITAS2', redshift = 0.34):
        from VHE_Analysis import take_data
        eblModel = self.eblModel
        instrument = self.instrument
        redshift = self.redshift
        if os.path.isfile('GRBs/GRB'+self.Burst+'.csv') == True:
            take_data( Burst = self.Burst, redshift =  self.redshift, instrument = self.instrument, eblModel = self.eblModel)
        else:
            print "It seems that either the GRBs folder does not exist or the csv file does not exist."



