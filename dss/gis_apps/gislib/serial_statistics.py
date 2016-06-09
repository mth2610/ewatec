import numpy as np
import pandas
import csv
#from matplotlib import dates
import matplotlib as mpl
from matplotlib import pylab
from pylab import *
import PIL, PIL.Image, StringIO
import matplotlib.pyplot as plt
import scipy.stats as st
from datetime import datetime
import time
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import DateFormatter
from scipy import stats
import statsmodels.formula.api as sm
from scipy.stats import probplot
from statsmodels.graphics.regressionplots import *

def str2datetime(strlist,formatdatetime="%Y-%m-%d %H:%M:%S"):
    result = [datetime.strptime(e,formatdatetime) for e in strlist]
    return result

def graph_in_endcode64(DF,variable="",unit="", title = "", linear_regression = False):
    DateTime = pandas.to_datetime(DF.index.values)
    data = np.array(DF.values)


    figure = plt.figure(facecolor='white')
    subplot = figure.add_subplot(111)
    # Construct the graph
    subplot.plot(DateTime, data, linewidth=1.0)

    if variable != "" and unit != "":
        subplot.set_xlabel('DateTime')
        subplot.set_ylabel(variable + " (" + unit + ")")
    else:
        pass

    if title != "":
        print title
        subplot.set_title(title)


    if linear_regression == True:

        index_non_nan = np.isfinite(data)
        x = np.array(mpl.dates.date2num(list(DateTime)))
        z = np.polyfit(x[index_non_nan],data[index_non_nan],1)
        p = np.poly1d(z)

        subplot.plot(DateTime,p(x),'r')
    else:
        pass


    formatter = DateFormatter('%m/%Y')

    subplot.grid(True)
    subplot.xaxis.set_major_formatter(formatter)
    subplot.xaxis.set_major_locator(MaxNLocator(8))
#    figure.autofmt_xdate()

    # Store image in a string buffer
    buffer = StringIO.StringIO()
    canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()
    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    pylab.close()
    img = str((buffer.getvalue()).encode('Base64'))

    return img

def reject_outliers(data, m=1.5):
    data = np.array(data)
    q1 = np.percentile(data,25)
    q3 = np.percentile(data,75)
    iqr = q3 - q1
    L = q1 - m*iqr
    U = q3 + m*iqr

    for i in range(len(data)):
        if not(L<data[i]<U):
            data[i] = np.nan


    return data

def getMedianFiltered(signal, threshold = 3):
    """
    return an array in which the location have value True  indicate that this is outlier and False for non-outlier
    """

    if type(signal) == list:
        signal = np.array(signal)
    else:
        pass

    difference = np.abs(signal - np.median(signal))
    median_difference = np.median(difference)

    if median_difference == 0:
        mask = [False for i in range(len(signal))]
        return mask
    else:
        s = difference / float(median_difference)
        mask = s > threshold
        return mask


class DetectOuliers():
    def __init__(self,DF):
        self.DF = DF
        self.index = DF.index.values
        self.value = DF.values

    def medianFilter(self, movingWindowSize = 50, threshold = 8):
        index = self.index
        value = self.value
        outlierList = []

        for i in range(0,len(index),movingWindowSize):
            if i+movingWindowSize <= len(index):
                outlierList.extend(getMedianFiltered(value[i:(i+movingWindowSize)],threshold))
            else:
                outlierList.extend(getMedianFiltered(value[i:],threshold))

        return self.DF.join(pandas.DataFrame({"outlier":outlierList}, index = index ))

    def nonParametricMethod(self, m=1.5):
        index = self.index
        value = self.value
        outlierList = []
        q1 = np.percentile(value,25)
        q3 = np.percentile(value,75)
        iqr = q3 - q1
        L = q1 - m*iqr
        U = q3 + m*iqr


        for data in value:
            if not(L<=data<=U):
                outlierList.append(True)
            else:
                outlierList.append(False)

        return self.DF.join(pandas.DataFrame({"outlier":outlierList}, index = index ))


    def outlierDetectionPlot(self,filteredData,variable="",unit=""):
        outlierDataPD = filteredData[filteredData['outlier'] == True]
#        filteredData[filteredData['outlier'] == True] = np.nan
        figure = plt.figure(facecolor='white')
        subplot = figure.add_subplot(111)

        orginalData, = subplot.plot(filteredData.index.values,filteredData[variable].values,color = 'b')
        outlierData = subplot.scatter(outlierDataPD.index.values,outlierDataPD[variable].values,color = 'r')


        subplot.set_ylabel(variable +"("+unit+")")
        subplot.legend([outlierData],["Outliers"])
        subplot.grid()
        grid(True)
        subplot.xaxis.set_major_locator(MaxNLocator(8))

        # Store image in a string buffer
        buffer = StringIO.StringIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()
        img = str((buffer.getvalue()).encode('Base64'))

        return img


class serial_statistics():
    def __init__(self,DateTime,Values,VariableType = "mean"):
        self.DateTime = DateTime
        self.Values = np.array(Values)
        self.DF = pandas.Series(Values,DateTime)
        self.VariableType = VariableType

    def fill_missingdata(self):
        DF = self.DF
        return DF

    def resample_data(self,timestep = "D", fillingData = "False"):
        VariableType = self.VariableType
        DF = self.DF
        DF = DF.resample(timestep, how = VariableType)


        if fillingData == "True" or fillingData == True:
            DF = DF.fillna(method='pad')
        else:
            pass

        return DF

    def histogram(self,variable="",unit=""):
        value = self.Values
        figure = plt.figure()
        figure.patch.set_facecolor('white')
        n, bins, patches = plt.hist(value[~np.isnan(value)], 30, normed=1, facecolor='yellow', alpha = 0.5)

        if variable != "" and unit != "":
            ylabel('Probability')
            xlabel(variable + " (" + unit + ")")
        else:
            pass

        # Store image in a string buffer
        buffer = StringIO.StringIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()
        img = str((buffer.getvalue()).encode('Base64'))
        return img

    def averagemonthly_statistic(self,variable="",unit=""):
        VariableType = self.VariableType
        DF= self.DF

        if VariableType == "Cumulative":
            DF = DF.resample(M, how='sum')
        else:
            pass

        month = (DF.index.month)

        m1 = DF[month == 1]
        m2 = DF[month == 2]
        m3 = DF[month == 3]
        m4 = DF[month == 4]
        m5 = DF[month == 5]
        m6 = DF[month == 6]
        m7 = DF[month == 7]
        m8 = DF[month == 8]
        m9 = DF[month == 9]
        m10 = DF[month == 10]
        m11 = DF[month == 11]
        m12 = DF[month == 12]


        figure = plt.figure()
        figure.patch.set_facecolor('white')
        boxplot([m1.values,m2.values,m3.values,m4.values,m5.values,m6.values,m7.values,m8.values,m9.values,m10.values,m11.values,m12.values])

        if variable != "" and unit != "":
            ylabel(variable + " (" + unit + ")")
            xlabel("Months")
        else:
            pass
        # Store image in a string buffer
        buffer = StringIO.StringIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()
        img = str((buffer.getvalue()).encode('Base64'))
        return img

class calibration_validation():
    ## Note that the comman in "observation, " using to pretent the erro "legend does not support ..." (just add to line type)
    def __init__(self,DF,sm_type="line",ob_type="point",sm_color="b",ob_color="r",variablename = "",unit=""):
        self.DF = DF
        self.dropnan_DF = DF.dropna()
        self.DateTime = np.array(DF.index.values)
        self.sm_value = np.array(DF.sm_value)
        self.ob_value = np.array(DF.ob_value)
        self.sm_type = sm_type
        self.ob_type = ob_type
        self.sm_color = sm_color
        self.ob_color = ob_color
        self.variablename = variablename
        self.unit = unit

    def timeseries_plot(self):
        DateTime = self.DateTime
        sm_value = self.sm_value
        ob_value = self.ob_value
        sm_type = self.sm_type
        ob_type = self.ob_type
        sm_color = self.sm_color
        ob_color = self.ob_color
        variablename = self.variablename
        unit = self.unit

        figure = plt.figure(facecolor='white')
        subplot = figure.add_subplot(111)

        if ob_type == "point":
            observation = subplot.scatter(DateTime,ob_value,color = ob_color)
        elif ob_type == "line":
            observation, = subplot.plot(DateTime,ob_value,color = ob_color)

        if sm_type == "point":
            simulation = subplot.scatter(DateTime,sm_value, color = sm_color)
        elif sm_type == "line":
            simulation, = subplot.plot(DateTime,sm_value, color = sm_color )

        subplot.set_ylabel(variablename +"("+unit+")")
        subplot.set_ylim(min(min(sm_value),min(ob_value)),max(max(sm_value),max(sm_value)))
        subplot.legend([observation,simulation],["Observation","Simulation"])
        subplot.grid()
        grid(True)
        subplot.xaxis.set_major_locator(MaxNLocator(8))

        # Store image in a string buffer
        buffer = StringIO.StringIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()
        img = str((buffer.getvalue()).encode('Base64'))

        return img

    def scatter_plot(self):
        sm_value = self.sm_value
        ob_value = self.ob_value

        figure = plt.figure(facecolor='white')
        subplot = figure.add_subplot(111)

        index_non_nan = np.isfinite(sm_value) & np.isfinite(ob_value)

        fit = np.polyfit(sm_value[index_non_nan],ob_value[index_non_nan],deg = 1)
        fx = np.poly1d(fit)
        subplot.scatter(sm_value,ob_value)
        subplot.plot(sm_value, fx(sm_value), color = 'r')
        grid(True)

        formatter = DateFormatter('%Y/%m')
        subplot.set_xlabel("Simulation")
        subplot.set_ylabel("Observation")
        subplot.grid()


        # Store image in a string buffer
        buffer = StringIO.StringIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()
        img = str((buffer.getvalue()).encode('Base64'))

        return img

    def statistical_parameters(self):
        dropnan_DF = self.dropnan_DF
        sm_value = np.array(dropnan_DF.sm_value)
        ob_value = np.array(dropnan_DF.ob_value)

        min_sm = min(sm_value)
        max_sm = max(sm_value)



        mean_sm = np.nanmean(sm_value)
        median_sm = np.median(sm_value)
        std_sm = np.nanstd(sm_value)
        cv_sm = 100*std_sm/mean_sm

        min_ob = min(ob_value)
        max_ob = max(ob_value)
        mean_ob = np.nanmean(ob_value)
        median_ob = np.median(ob_value)
        std_ob = np.nanstd(ob_value)
        cv_ob = 100*std_ob/mean_ob


        pearson_correlation = stats.pearsonr(sm_value,ob_value)
        pearson_r = pearson_correlation[0]
        pearson_p = pearson_correlation[1]

        spearman_correlation = stats.spearmanr(sm_value,ob_value)
        spearman_r = spearman_correlation[0]
        spearman_p = spearman_correlation[1]

        print mean_ob
        print sum((ob_value-sm_value)**2)
        print sum((ob_value-mean_ob)**2)
        nash = 1 - sum((ob_value-sm_value)**2)/sum((ob_value-mean_ob)**2)

        para_dict = {'min_sm':min_sm,'max_sm':max_sm,'mean_sm':mean_sm,'median_sm':median_sm,'std_sm':std_sm,'cv_sm':cv_sm,'min_ob':min_ob,'max_ob':max_ob,'mean_ob':mean_ob,'median_ob':median_ob,'std_ob':std_ob,'cv_ob':cv_ob,'pearson_r':pearson_r,'pearson_p':pearson_p,'spearman_r':spearman_r,'spearman_p':spearman_p,'nash':nash}

        return para_dict

    def residual_analysis(self):
        dropnan_DF = self.dropnan_DF
        model = sm.ols(formula='ob_value ~ sm_value', data=dropnan_DF)
        fitted = model.fit()
        fittedvalues =  np.array(fitted.fittedvalues)
        residual = fittedvalues - np.array(dropnan_DF.ob_value)
        norm_residual = fitted.resid_pearson

        ###


        figure = plt.figure(facecolor='white')

        subplot1 = figure.add_subplot(2,2,1)
        subplot1.scatter(fittedvalues,residual)
        subplot1.set_xlabel("Fitted values")
        subplot1.set_ylabel("Residuals")
        subplot1.set_title("Residuals vs Fitted")

        subplot2 = figure.add_subplot(2,2,2)
        probplot(norm_residual,plot=subplot2)
        subplot2.set_title("Normal Q-Q")
        subplot2.set_ylabel("Standardized residuals")
        subplot2.set_xlabel("Theoretical Quantiles")


        subplot3 = figure.add_subplot(2,2,3)
        subplot3.scatter(fittedvalues,np.sqrt(np.abs(residual)))
        subplot3.set_title("Scale-Location")
        subplot3.set_ylabel(r'$\sqrt{\mathrm{|Standardized\/residuals|}}$')
        subplot3.set_xlabel("Fitted values")

        subplot4 = figure.add_subplot(2,2,4)
        norm_residual = (np.matrix(norm_residual)).T
        H = norm_residual*(norm_residual.T*norm_residual).I*norm_residual.T
        h = H.diagonal()
        subplot4.scatter(np.array(h),np.array(norm_residual.T))
        subplot4.set_title("Residuals vs Leverage")
        subplot4.set_ylabel("Standardized residuals")
        subplot4.set_xlabel("Leverage")
        subplot4.xaxis.set_major_locator(MaxNLocator(6))

        figure.tight_layout()
        # Store image in a string buffer
        buffer = StringIO.StringIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()
        img = str((buffer.getvalue()).encode('Base64'))

        return img
