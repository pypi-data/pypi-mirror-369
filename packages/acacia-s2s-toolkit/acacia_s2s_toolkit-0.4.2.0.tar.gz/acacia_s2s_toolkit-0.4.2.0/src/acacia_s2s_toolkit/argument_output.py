# output suitable ECDS variables in light of requested forecasts.
from acacia_s2s_toolkit import variable_dict, argument_check
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def get_endtime(origin_id):
    # next find maximum end time
    end_time=None
    for originID, fc_length in variable_dict.forecast_length_hours.items():
        if originID == origin_id:
            end_time=fc_length
            break

    if end_time is None:
        print (f"[ERROR] could not find forecast length for originID '{origin_id}'.")
        return None

    return end_time

def get_num_pert_fcs(origin_id):
    # find number pert. forecasts
    num_pert_fcs=None
    for originID, num_fc_ens in variable_dict.forecast_pert_members.items():
        if originID == origin_id:
            num_pert_fcs=num_fc_ens
            break

    if num_pert_fcs is None:
        print (f"[ERROR] could not find number pert. forecasts for originID '{origin_id}'.")
        return None

    return num_pert_fcs

def get_num_pert_hcs(origin_id):
    # find number pert. forecasts
    num_pert_hcs=None
    for originID, num_hc_ens in variable_dict.reforecast_pert_members.items():
        if originID == origin_id:
            num_pert_hcs=num_hc_ens
            break

    if num_pert_hcs is None:
        print (f"[ERROR] could not find number pert. reforecasts for originID '{origin_id}'.")
        return None

    return num_pert_hcs

def get_timeresolution(variable):
    # first find which sub-category the variable sits in
    time_resolution=None
    for category_name, category_dict in variable_dict.s2s_variables.items():
        for subcategory_name, subcategory_vars in category_dict.items():
            if variable in subcategory_vars:
                time_resolution = subcategory_name
                break # found correct time resolution
        if time_resolution:
            break # break outer loop

    if time_resolution is None:
        print (f"[ERROR] could not find variable '{variable}'.")
        return None
    return time_resolution

def output_leadtime_hour(variable,origin_id,start_time=0):
    '''
    Given variable (variable abbreivation), output suitable leadtime_hour. The leadtime_hour will request all avaliable steps. Users should be able to pre-define leadtime_hour if they do not want all output.
    return: leadtime_hour
    '''
    time_resolution = get_timeresolution(variable)

    # next find maximum end time
    end_time = get_endtime(origin_id)

    # given time resolution, work out array of appropriate time values
    if time_resolution.endswith('6hrly'):
        leadtime_hour = np.arange(start_time,end_time+1,6)
    else:
        leadtime_hour = np.arange(start_time,end_time+1,24) # will output 0 to 1104 in steps of 24 (ECMWF example). 
 
    print (f"For the following variable '{variable}' using the following leadtimes '{leadtime_hour}'.")

    return leadtime_hour

def output_sfc_or_plev(variable):
    '''
    Given variable (variable abbreivation), output whether variable is sfc level or on pressure levels?
    return: level_type
    '''
    # Flatten all variables from nested dictionary
    level_type=None
    for category_name, category_dict in variable_dict.s2s_variables.items():
        for subcategory_vars in category_dict.values():
            if variable in subcategory_vars:
                level_type = category_name
                return level_type
    if level_type == None:
        print (f"[ERROR] No leveltype found for '{variable}'.")
        return level_type

def output_webapi_variable_name(variable):
    ''' 
    Given variable abbreviation, output webAPI paramID.
    return webAPI paramID.

    '''
    for variable_abb, webapi_code in variable_dict.webAPI_params.items():
        if variable == variable_abb:
            return webapi_code
    print (f"[ERROR] No webAPI paramID found for '{variable}'.")
    return None

def output_originID(model):
    '''
    Given model name, output originID.
    return originID.

    '''
    for modelname, originID in variable_dict.model_origin.items():
        if model == modelname:
            return originID
    print (f"[ERROR] No originID found for '{model}'.")
    return None


def output_ECDS_variable_name(variable):
    '''
    Given variable name, output the matching ECDS variable name
    
    return ECDS_varname (ECMWF Data Store)
    '''
    ECDS_varname='10m_uwind'
    return ECDS_varname

def output_plevs(variable):
    '''
    Output suitable plevs, if q, (1000, 925, 850, 700, 500, 300, 200) else add 100, 50 and 10 hPa. 
    '''
    all_plevs=[1000,925,850,700,500,300,200,100,50,10]
    if variable == 'q':
        plevs=all_plevs[:-3] # if q is chosen, don't download stratosphere
    else:
        plevs=all_plevs
    print (f"Selected the following pressure levels: {plevs}")
    
    return plevs

def output_fc_lags(origin_id,fcdate):
    '''
    Given origin_id, output lagged ensemble forecasts.
    return array with day lag positions, i.e. [0,-1,-2].
    '''
    if origin_id not in variable_dict.day_fclag_ensemble:
        raise ValueError(f"[ERROR] No forecast lags found for origin_id '{origin_id}'.")

    # Special handling for CPTEC (sbsj). Initialisation only given for Wednesday and Thursday.
    if origin_id == 'sbsj':
        date_obj = datetime.strptime(fcdate, '%Y%m%d')
        weekday = date_obj.weekday()+1  # Monday = 1, ..., Sunday = 7
        if weekday == 4:  # Thursday
            return [0, -1]
        else:
            return [0]
    # Return the list from the dictionary
    return variable_dict.day_fclag_ensemble[origin_id]

def get_hindcast_model_date(origin_id,fcdate):
    ''' Given origin_id, output appropriate date for reforecast dataset. This is the hindcast model version, not the set of reforecast dates.
    '''
    
    if origin_id not in variable_dict.reforecast_model_freq:
        raise ValueError(f"[ERROR] No reforecast model frequency found for origin_id '{origin_id}'.")
  
    rf_model_freq = variable_dict.reforecast_model_freq[origin_id]

    # four options.
    # (1) single string representing one reforecast model release
    # (2) array with weekday initialisations, i.e. 1 = Monday
    # (3) odd dates (ECMWF)
    # (4) four per month (egrr [UKMO] and rksl [KMA])

    if isinstance(rf_model_freq,str) and rf_model_freq.startswith('2'): # reforecast model version with single date
        mrf_date = rf_model_freq
    elif isinstance(rf_model_freq,(list,tuple)): # days of week
        print ('days of week')
        # forecast and reforecast at same frequency
        mrf_date = fcdate
    elif rf_model_freq == 'odddates': # ECMWF config.
        print ('odd dates')
        day = int(fcdate[6:]) # get day comp.
        if day % 2 == 0 or fcdate[4:] == '0229': # even date or 29th Feb
            day -= 1
            mrf_date = fcdate[:6]+f"{day:02d}" # create new fcdate
        else:
            mrf_date = fcdate
    elif rf_model_freq == 'fourpermonth': # KMA and UKMO:
        day_select = [1,9,17,25]
        day = int(fcdate[6:])
        closest_day = min(day_select,key=lambda x:abs(day-x))
        mrf_date = fcdate[:6]+f"{closest_day:02d}"

    print (f'chosen model reforecast date: {mrf_date}')

    return mrf_date
        
def get_hindcast_year_span(origin_id,fcdate):
    ''' Given origin_id, output appropriate set of years for reforecasts.
    '''
    if origin_id not in variable_dict.reforecast_years:
        raise ValueError(f"[ERROR] No reforecast years found for origin_id '{origin_id}'.")

    rf_yrs = variable_dict.reforecast_years[origin_id] # description of reforecast years

    if "fixed" in rf_yrs:
        start, end = rf_yrs["fixed"]
        rf_years = np.arange(start,end+1) # give full set of years, i.e. 1981, 1982, ..., 2013.
    elif "dynamic" in rf_yrs:
        n_years = rf_yrs["dynamic"]
        fc_year = int(fcdate[:4]) # get year component of date.
        rf_years = np.arange(fc_year - n_years,fc_year)
    else:
        raise ValueError(f"[ERROR] Couldn't compute appropriate reforecast years for origin_id '{origin_id}'.")

    return rf_years

def get_reforecast_date(origin_id,fcdate):
    ''' Given origin_id, output appropriate reforecast date. The DOY component of the rf_date is used to produce complete set of reforecast dates (i.e. 20010405, 20020505, 20030405).

    Note: for CNRM and CPTEC, a complete list of rfdates is given due to inconsistent day-of-years across reforecast years. 
    '''
    if origin_id not in variable_dict.reforecast_freq:
        raise ValueError(f"[ERROR] No reforecast freq information found for origin_id '{origin_id}'.")

    rf_freq_info = variable_dict.reforecast_freq[origin_id]

    if rf_freq_info == 'rf_model_date':
        rf_date = get_hindcast_model_date(origin_id,fcdate)
    elif rf_freq_info == 'fcdate':
        rf_date = fcdate # rf frequency is at same as forecast frequency
    elif isinstance(rf_freq_info,(list,tuple)): #days of month
        # find nearest day of month
        fc_day = int(fcdate[6:])
        closest_day = min(rf_freq_info,key=lambda x:abs(fc_day-x))
        rf_date = fcdate[:6]+f"{closest_day:02d}"
    elif rf_freq_info == 'CNRevery5days':
        # make an array of dates from 2020-01-01 to 2020-12-27
        DOM = {1:[1,6,11,16,21,26,31],2:[5,10,15,20,25],3:[2,7,12,17,22,27],4:[1,6,11,16,21,26],5:[1,6,11,16,21,26,31],
                6:[5,10,15,20,25,30],7:[5,10,15,20,25,30],8:[4,9,14,19,24,29],9:[3,8,13,18,23,28],10:[3,8,13,18,23,28],
                11:[2,7,12,17,22,27],12:[2,7,12,17,22,27]}
        CNR_rf_dates = []
        for month, days in DOM.items():
            for day in days: 
                CNR_rf_dates.append(datetime(2020,month,day))
        # change year of fcdate to 2020-fcdate(MM)-fcdate(DD)
        fc_date_2020 = datetime.strptime(f"2020{fcdate[4:]}",'%Y%m%d')
        # nearest date to altered fcdate is rf_date
        closest_day=min(CNR_rf_dates,key=lambda x:abs(fc_date_2020-x))
        rf_date = closest_day.strftime('%Y%m%d')
    elif rf_freq_info == 'JMA2permonth':
        jma_rf_dates=[datetime(2020,1,16),datetime(2020,1,31), # writing out list of all 2020 hindcast dates
                datetime(2020,2,10),datetime(2020,2,25),
                datetime(2020,3,12),datetime(2020,3,27),
                datetime(2020,4,11),datetime(2020,4,26),
                datetime(2020,5,16),datetime(2020,5,31),
                datetime(2020,6,15),datetime(2020,6,30),
                datetime(2020,7,15),datetime(2020,7,30),
                datetime(2020,8,14),datetime(2020,8,29),
                datetime(2020,9,13),datetime(2020,9,28),
                datetime(2020,10,13),datetime(2020,10,28),
                datetime(2020,11,12),datetime(2020,11,27),
                datetime(2020,12,12),datetime(2020,12,27)]
        # change year of fcdate to 2020-fcdate(MM)-fcdate(DD)
        fc_date_2020 = datetime.strptime(f"2020{fcdate[4:]}",'%Y%m%d')
        # nearest date to altered fcdate is rf_date
        closest_day=min(jma_rf_dates,key=lambda x:abs(fc_date_2020-x))
        rf_date = closest_day.strftime('%Y%m%d')
    elif rf_freq_info == 'CNRMevery7days':
        rf_dates = pd.date_range('19921231','20171228',freq='7D')
        rf_date = []
        for year in np.arange(1993,2017+1):
            fc_date_one_year = datetime.strptime(f"{year}{fcdate[4:]}",'%Y%m%d')
            # nearest date to altered fcdate is rf_date
            closest_day=min(rf_dates,key=lambda x:abs(fc_date_one_year-x))
            rf_date.append(closest_day.strftime('%Y%m%d'))
    elif rf_freq_info == 'CPTECevery7days':
        rf_dates = pd.date_range('19990106','20181226',freq='7D')
        rf_date = []
        for year in np.arange(1999,2018+1):
            fc_date_one_year = datetime.strptime(f"{year}{fcdate[4:]}",'%Y%m%d')
            # nearest date to altered fcdate is rf_date
            closest_day=min(rf_dates,key=lambda x:abs(fc_date_one_year-x))
            rf_date.append(closest_day.strftime('%Y%m%d'))
    else:
        raise ValueError(f"[ERROR] No reforecast freq information found for origin_id '{origin_id}'.")

    return rf_date

def output_formatted_leadtimes(leadtime_hour,fcdate,variable,lag,fc_enslags):
    # create new fcdate based on lag
    new_fcdate = datetime.strptime(fcdate, '%Y%m%d')+timedelta(days=lag)
    convert_fcdate = new_fcdate.strftime('%Y-%m-%d')

    # convert leadtimes
    # is it an average field?
    time_resolution = get_timeresolution(variable)
    # if an average field, use '0-24/24-48/48-72...'
    leadtime_hour_copy = leadtime_hour[:]

    # need to ensure correct selection of lead time given lag. Essentially all members should sample same forecast period.
    max_lag = np.abs(np.min(fc_enslags))
    lag_minus_1 = lag*-1
    lag_end = (max_lag-lag_minus_1)*-1

    if time_resolution.startswith('aver'):
        if lag_end == 0:
            leadtime_hour_copy=leadtime_hour_copy[lag_minus_1:]
        else:
            leadtime_hour_copy=leadtime_hour_copy[lag_minus_1:lag_end]
        leadtimes='/'.join(f"{leadtime_hour_copy[i]}-{leadtime_hour_copy[i]+24}" for i in range(len(leadtime_hour_copy)-1))
    else: # instantaneous field
        nsteps_per_day = 4
        if lag_end == 0:
            leadtime_hour_copy=leadtime_hour_copy[lag_minus_1*nsteps_per_day:]
        else:
            leadtime_hour_copy=leadtime_hour_copy[lag_minus_1*nsteps_per_day:lag_end*nsteps_per_day]
        leadtimes = '/'.join(str(x) for x in leadtime_hour_copy)
    print (leadtimes)
    return leadtimes, convert_fcdate

def create_reforecast_dates(rfyears,rfdate):
    ''' function that produces a list of reforecast dates given set of years and chosen reforecast date
    '''
    if np.size(rfdate) == 1: # for a single reforecast date that is then repeated for all reforecast years
        DOY = rfdate[4:]
        rf_dates = '/'.join(f"{int(year)}{DOY}" for year in rfyears)
    else:
        rf_dates = '/'.join(f"{date}" for date in rfdate) 
    return rf_dates
 

def check_and_output_all_fc_arguments(variable,model,fcdate,area,data_format,grid,plevs,leadtime_hour):
    # check variable name. Is the variable name one of the abbreviations?
    argument_check.check_requested_variable(variable)
    # is it a sfc or pressure level field. # output sfc or level type
    level_type = output_sfc_or_plev(variable)

    # if level_type == plevs and plevs=None, output_plevs. Will only give troposphere for q. 
    # work out appropriate pressure levels
    if level_type == 'pressure':
        if plevs is None:
            plevs = output_plevs(variable)
        else:
            print (f"Downloading the requested pressure levels: {plevs}") # if not, use request plevs.
        # check plevs
        argument_check.check_plevs(plevs,variable)
    else:
        print (f"Downloading the following level type: {level_type}")
        plevs=None

    # get ECDS version of variable name. - WILL WRITE UP IN OCTOBER 2025!
    #ecds_varname = variable_output.output_ECDS_variable_name(variable)
    ecds_varname=None

    # get webapi param
    webapi_param = output_webapi_variable_name(variable) # temporary until move to ECDS (Aug - Oct).

    # check model is in acceptance list and get origin code!
    argument_check.check_model_name(model)
    # get origin id
    origin_id = output_originID(model)

    # if leadtime_hour = None, get leadtime_hour (output all hours).
    if leadtime_hour is None:
        leadtime_hour = output_leadtime_hour(variable,origin_id) # the function outputs an array of hours. This is the leadtime used during download.
    print (f"For the following variable '{variable}' using the following leadtimes '{leadtime_hour}'.")

    # check fcdate.
    argument_check.check_fcdate(fcdate,origin_id)

    # check dataformat
    argument_check.check_dataformat(data_format)

    # check leadtime_hours (as individuals can choose own leadtime_hours).
    argument_check.check_leadtime_hours(leadtime_hour,variable,origin_id)

    # check area selection
    argument_check.check_area_selection(area)

    return level_type, plevs, webapi_param, ecds_varname, origin_id, leadtime_hour

def check_and_output_all_hc_arguments(variable,origin_id,fcdate,rfyears=None):
    ''' Function that will output all the necessary arguments to download reforecast data
    '''
    # get the date of the reforecast model
    rf_model_date = get_hindcast_model_date(origin_id,fcdate)

    # get the reforecast years
    if rfyears is None:
        rfyears = get_hindcast_year_span(origin_id,fcdate)
    # after computing reforecast years, check the chosen set
    argument_check.check_requested_reforecast_years(rfyears,origin_id,fcdate)

    # get the appropriate reforecast date
    rf_date = get_reforecast_date(origin_id,fcdate)

    return rf_model_date, rfyears, rf_date


