"""
LAT Weekly Files Download

This code will download the LAT weekly files associated with bursts from the online LAT burst table.
http://fermi.gsfc.nasa.gov/ssc/observations/types/grbs/lat_grbs/table.php


"""
import os
import re
from mechanize import Browser
import urllib
import urllib2
from bs4 import BeautifulSoup

"Populates a dictionary of all the GRBs in the online table"
def populate():
    x
class LAT_DATA:
    soup = BeautifulSoup(urllib.urlopen("http://fermi.gsfc.nasa.gov/ssc/observations/types/grbs/lat_grbs/table.php"))
    rows = soup.findAll(name='tr')
    grb = {}
    names = []
    for row in rows:
        GRB = row.findAll(name='td')
        if GRB:
            # get last td "center"
            grb[GRB[1].text] = {'Name':GRB[1].text, 'MET': GRB[2].text, 'RA':GRB[5].text,'DEC': GRB[6].text,'THETA':GRB[9].text,'ZENITH':GRB[10].text,'Date': GRB[3].text+' '+GRB[4].text }
            names.append(GRB[1].text)
    def __inst__(self, Name):
        self.Name = Name
        self.grb=grb
        self.names = names
        print 'Retrieved GRB data.'
        
    
        "Check the online table for all the important options."
    
                
def LAT_Files(Name):
            br = Browser()
            br.set_handle_robots(False)
            br.set_handle_refresh(False)
            br.addheaders = [('User-agent','Firefox')]
            if Name == 'all':
                    for n in names:
                        response = br.open("http://heasarc.gsfc.nasa.gov/cgi-bin/Tools/xTime/xTime.pl")
            #print response.read()
                        response1 = br.response()
            #print response1
                        br.form = list(br.forms())[2] 
                        br.form['time_in_sf'] = LAT_DATA.grb[n]['MET']
                        soup = BeautifulSoup(urllib.urlopen(response.geturl()))
                        html = soup('table')[1].findAll('td')[13]
                        response = br.submit()
                        week = html.get_text()
                        LAT_DATA.grb[n]['Week'] = week
                        if os.path.exists('LAT_Week_Files') == False:
                            os.mkdir('LAT_Week_Files')
                        else:
                            pass
                        os.chdir('LAT_Week_Files')
                        if int(week) > 99:
                            url_ph = 'http://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/weekly/photon/lat_photon_weekly_w'+week+'_p203_v001.fits'
                            #url_sc = 'http://fermi.gsfc.nasa.gov/ssc/observations/timeline/ft2/files/FERMI_POINTING_FINAL_'+week+'_2013101_2013108_00.fits'
                        else: 
                            url_ph = 'http://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/weekly/photon/lat_photon_weekly_w0'+week+'_p203_v001.fits'
                            #url_sc = 'http://fermi.gsfc.nasa.gov/ssc/observations/timeline/ft2/files/FERMI_POINTING_FINAL_0'+week+'_2013101_2013108_00.fits'

                        ph_file_name = 'Fermi_ph_week_'+week+'.fits'
                        LAT_DATA.grb[Name]['ph_file_name'] = 'LAT_Week_Files/'+ph_file_name
                        sc_file_name = 'Fermi_sc_week_'+week+'.fits'
                        LAT_DATA.grb[Name]['sc_file_name'] ='LAT_Week_Files/'+sc_file_name

                        if os.path.isfile(ph_file_name) == True:
                            print 'The file for GRB'+n+' is already in your directory.'
                        else:
                            'Congratulations, you have downloaded the files for GRB'+Name+'.'
                            urllib.urlretrieve(url_ph, ph_file_name)
                        os.chdir('..')
            else:
                        try:
                                response = br.open("http://heasarc.gsfc.nasa.gov/cgi-bin/Tools/xTime/xTime.pl")
                                #print response.read()
                                response1 = br.response()
                                #print response1
                                br.form = list(br.forms())[2] 
                                br.form['time_in_sf'] = LAT_DATA.grb[Name]['MET']
                                response = br.submit()
                                soup = BeautifulSoup(urllib.urlopen(response.geturl()))
                                html = soup('table')[1].findAll('td')[13]
                                week = html.get_text()
                                LAT_DATA.grb[Name]['Week'] = week

                                if os.path.exists('LAT_Week_Files') == False:
                                    os.mkdir('LAT_Week_Files')
                                else:
                                    pass
                                os.chdir('LAT_Week_Files')
                                if int(week) > 99:
                                        url_ph = 'http://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/weekly/photon/lat_photon_weekly_w'+week+'_p203_v001.fits'
                                        #url_sc = 'http://fermi.gsfc.nasa.gov/ssc/observations/timeline/ft2/files/FERMI_POINTING_FINAL_'+week+'_2013101_2013108_00.fits'
                                else: 
                                        url_ph = 'http://heasarc.gsfc.nasa.gov/FTP/fermi/data/lat/weekly/photon/lat_photon_weekly_w0'+week+'_p203_v001.fits'
                                        #url_sc = 'http://fermi.gsfc.nasa.gov/ssc/observations/timeline/ft2/files/FERMI_POINTING_FINAL_0'+week+'_2013101_2013108_00.fits'

                                ph_file_name = 'Fermi_ph_week_'+week+'.fits'
                               
                                LAT_DATA.grb[Name]['ph_file_name'] = 'LAT_Week_Files/'+ph_file_name
                                sc_file_name = 'Fermi_sc_week_'+week+'.fits'
                                
                                LAT_DATA.grb[Name]['sc_file_name'] = 'LAT_Week_Files/'+sc_file_name
                                if os.path.isfile(ph_file_name) == True:
                                        print 'The file for GRB'+Name+' is already in your directory.'
                                else:
                                    urllib.urlretrieve(url_ph, ph_file_name)
                                    print 'Congratulations! You have just downloaded the files for GRB'+Name+'.'
                                os.chdir('..')
         
                        except:
                                print 'Unfortunately, GRB'+Name+' has not been added to our list yet. Have a nice day!' 
