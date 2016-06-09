
#!/usr/bin/python
# -*- coding: utf8 -*-

import numpy as np
import math
import datetime

## Chuyen so gio nang thanh buc xa mat toi (Ra)
class sh2ra():
    def __init__(self,SH,lat,datetime):
        self.SH = np.array(SH)
        self.lat = float(lat)
        self.datetime = datetime
        
    # Tao list J (so ngay trong nam):
    def J_list(self):
        datetime = self.datetime
        J = []
        for element in datetime:
            J.append(float(element.strftime("%j")))
        J = np.array(J)
        return J
           
    # Chuyen vi do sang don vi radian
    def To_Radian(self):
        lat = self.lat
        ra_lat = lat*(math.pi)/180           
        return ra_lat
    
    # Tinh dr (inverse relative distance Earth-Sun):
    def dr(self):
        J = self.J_list()
        dr = 1 + 0.033*np.cos(2*math.pi*J/365)
        return dr
    
    # Tinh sigma (the solar declination)
    def sigma(self):
        J = self.J_list()
        sigma = 0.409*np.sin(2*math.pi*J/365 - 1.39)
        return sigma
    
    
    # Tinh omega_s (sunset hour angle)
    def omega_s(self):
        ra_lat = self.To_Radian()
        sigma = self.sigma()
        omega_s = np.arccos(-np.tan(ra_lat)*np.tan(sigma))
        return omega_s
    
    # Tinh Ra (Extraterrestrial radiation for daily periods)
    def Ra(self):
        dr = self.dr()
        omega_s = self.omega_s()
        ra_lat = self.To_Radian()
        sigma = self.sigma()                   
        Ra = 24*60*0.0820*dr*(omega_s*np.sin(ra_lat)*np.sin(sigma)+np.cos(ra_lat)*np.cos(sigma)*np.sin(omega_s))/(math.pi)
        return Ra
    
    # Tinh N (Daylight hours)
    def Daylight_hours(self):
        omega_s = self.omega_s()
        N = 24*omega_s/(math.pi)
        return N
    
    # Tinh Rs (Solar radiation)
    def Ra_solar(self):
        N = self.Daylight_hours()
        n = self.SH
        Ra = self.Ra()
        Rs = (0.25+0.5*n/N)*Ra
        
        return Rs