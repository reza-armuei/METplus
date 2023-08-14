"""
Program Name: time_util.py
Contact(s): George McCabe
Abstract:
History Log:  Initial version
Usage: Create a subclass
Parameters: None
Input Files: N/A
Output Files: N/A
"""

import datetime
from dateutil.relativedelta import relativedelta
import re

from .string_manip import split_level, format_thresh

'''!@namespace TimeInfo
@brief Utility to handle timing in METplus wrappers
@code{.sh}
Cannot be called directly. These are helper functions
to be used in other METplus wrappers
@endcode
'''

# dictionary where key is letter of time unit, i.e. Y and value is
# the string representation of it, i.e. year
TIME_LETTER_TO_STRING = {
    'Y': 'year',
    'm': 'month',
    'd': 'day',
    'H': 'hour',
    'M': 'minute',
    'S': 'second',
}


def shift_time_seconds(time_str, shift):
    """ Adjust time by shift seconds. Format is %Y%m%d%H%M%S
        Args:
            @param time_str: Start time in %Y%m%d%H%M%S
            @param shift: Amount to adjust time in seconds
        Returns:
            New time in format %Y%m%d%H%M%S
    """
    return (datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S") +
            datetime.timedelta(seconds=shift)).strftime("%Y%m%d%H%M%S")


def get_relativedelta(value, default_unit='S'):
    """!Converts time values ending in Y, m, d, H, M, or S to relativedelta object
        Args:
          @param value time value optionally ending in Y,m,d,H,M,S
            Valid options match format 3600, 3600S, 60M, or 1H
          @param default_unit unit to assume if no letter is found at end of value
          @return relativedelta object containing offset time"""
    if isinstance(value, int):
        return get_relativedelta(str(value), default_unit)

    mult = 1
    reg = r'(-*)(\d+)([a-zA-Z]*)'
    match = re.match(reg, value)
    if match:
        if match.group(1) == '-':
            mult = -1
        time_value = int(match.group(2)) * mult
        unit_value = match.group(3)

        # create relativedelta (dateutil) object for unit
        # if no units specified, use seconds unless default_unit is specified
        if unit_value == '':
            if default_unit == 'S':
                return relativedelta(seconds=time_value)
            else:
                unit_value = default_unit

        if unit_value == 'H':
            return relativedelta(hours=time_value)

        if unit_value == 'M':
            return relativedelta(minutes=time_value)

        if unit_value == 'S':
            return relativedelta(seconds=time_value)

        if unit_value == 'd':
            return relativedelta(days=time_value)

        if unit_value == 'm':
            return relativedelta(months=time_value)

        if unit_value == 'Y':
            return relativedelta(years=time_value)

        # unsupported time unit specified, return None
        return None


def get_seconds_from_string(value, default_unit='S', valid_time=None):
    """!Convert string of time (optionally ending with time letter, i.e. HMSyMD to seconds
        Args:
          @param value string to convert, i.e. 3M, 4H, 17
          @param default_unit units to apply if not specified at end of string
          @returns time in seconds if successfully parsed, None if not"""
    rd_obj = get_relativedelta(value, default_unit)
    return ti_get_seconds_from_relativedelta(rd_obj, valid_time)


def time_string_to_met_time(time_string, default_unit='S', force_hms=False):
    """!Convert time string (3H, 4M, 7, etc.) to format expected by the MET
        tools ([H]HH[MM[SS]])"""
    total_seconds = get_seconds_from_string(time_string, default_unit)
    return seconds_to_met_time(total_seconds, force_hms=force_hms)


def seconds_to_met_time(total_seconds, force_hms=False):
    seconds_time_string = str(total_seconds % 60).zfill(2)
    minutes_time_string = str(total_seconds // 60 % 60).zfill(2)
    hour_time_string = str(total_seconds // 3600).zfill(2)

    # if hour is 6 or more digits, we need to add minutes and seconds
    # also if minutes and/or seconds they are defined
    # add minutes if seconds are defined as well
    if (force_hms or len(hour_time_string) > 5 or
            minutes_time_string != '00' or seconds_time_string != '00'):
        return hour_time_string + minutes_time_string + seconds_time_string
    else:
        return hour_time_string


def ti_get_hours_from_relativedelta(lead, valid_time=None):
    """! Get hours from relativedelta. Simply calls get seconds function and
         divides the result by 3600.

         @param lead relativedelta object to convert
         @param valid_time (optional) valid time required to convert values
          that contain months or years
         @returns integer value of hours or None if cannot compute
    """
    lead_seconds = ti_get_seconds_from_relativedelta(lead, valid_time)
    if lead_seconds is None:
        return None

    # integer division doesn't handle negative numbers properly
    # (result is always -1) so handle appropriately
    if lead_seconds < 0:
        return - (-lead_seconds // 3600)

    return lead_seconds // 3600


def ti_get_seconds_from_relativedelta(lead, valid_time=None):
    """!Check relativedelta object contents and compute the total number of seconds
        in the time. Return None if years or months are set, because the exact number
        of seconds cannot be calculated without a relative time"""

    # return None if input is not relativedelta object
    if not isinstance(lead, relativedelta):
        return None

    # if valid time is specified, use it to determine seconds
    if valid_time and isinstance(valid_time, datetime.datetime):
        return int((valid_time - (valid_time - lead)).total_seconds())

    if lead.months != 0 or lead.years != 0:
        return None

    total_seconds = 0

    if lead.days != 0:
        total_seconds += lead.days * 86400

    if lead.hours != 0:
        total_seconds += lead.hours * 3600

    if lead.minutes != 0:
        total_seconds += lead.minutes * 60

    if lead.seconds != 0:
        total_seconds += lead.seconds

    return total_seconds


def ti_get_seconds_from_lead(lead, valid='*'):
    if isinstance(lead, int):
        return lead

    if valid == '*':
        valid_time = None
    else:
        valid_time = valid

    return ti_get_seconds_from_relativedelta(lead, valid_time)


def ti_get_hours_from_lead(lead, valid='*'):
    lead_seconds = ti_get_seconds_from_lead(lead, valid)
    if lead_seconds is None:
        return None

    return lead_seconds // 3600


def get_time_suffix(letter, letter_only):
    if letter_only:
        return letter

    return f" {TIME_LETTER_TO_STRING[letter]} "


def format_time_string(lead, letter, plural, letter_only):
    if letter == 'Y':
        value = lead.years
    elif letter == 'm':
        value = lead.months
    elif letter == 'd':
        value = lead.days
    elif letter == 'H':
        value = lead.hours
    elif letter == 'M':
        value = lead.minutes
    elif letter == 'S':
        value = lead.seconds
    else:
        return None

    if value == 0:
        return None

    abs_value = abs(value)
    suffix = get_time_suffix(letter, letter_only)
    output = f"{abs_value}{suffix}"
    if abs_value != 1 and plural and not letter_only:
        output = f"{output.strip()}s "

    return output


def ti_get_lead_string(lead, plural=True, letter_only=False):
    """!Check relativedelta object contents and create string representation
        of the highest unit available (year, then, month, day, hour, minute, second).
        This assumes that only one unit has been set in the object"""
    # if integer, assume seconds
    if isinstance(lead, int):
        return ti_get_lead_string(relativedelta(seconds=lead), plural=plural)

    # return None if input is not relativedelta object
    if not isinstance(lead, relativedelta):
        return None

    # if any of the values are negative, add - before the final result
    if (lead.years < 0 or lead.months < 0 or lead.days < 0 or lead.hours < 0 or
            lead.minutes < 0 or lead.seconds < 0):
        negative = '-'
    else:
        negative = ''

    output_list = []
    for time_letter in TIME_LETTER_TO_STRING.keys():
        output = format_time_string(lead, time_letter, plural, letter_only)
        if output is not None:
            output_list.append(output)

    # if nothing was found, return 0 hour(s) or 0H
    if not output_list:
        if letter_only:
            return '0H'

        return f"0 hour{'s' if plural else ''}"

    output = ''.join(output_list)
    # remove whitespace from beginning and end of string
    output = output.strip()

    return f"{negative}{output}"


def get_met_time_list(string_value, sort_list=True):
    """! Convert a string into a list of strings in MET time format HHMMSS.

    @param string_value input string to parse
    @param sort_list If True, sort the list values. If False, skip sorting.
     Default is True.
    @returns list of strings with MET times
    """
    return _format_time_list(string_value, get_met_format=True,
                             sort_list=sort_list)


def get_delta_list(string_value, sort_list=True):
    """! Convert a string into a list of relativedelta objects.

    @param string_value input string to parse
    @param sort_list If True, sort the list values. If False, skip sorting.
     Default is True.
    @returns list of relativedelta objects
    """
    return _format_time_list(string_value, get_met_format=False,
                             sort_list=sort_list)


def _format_time_list(string_value, get_met_format, sort_list=True):
    """! Helper function to convert a string into a list of times.

    @param string_value input string to parse
    @param get_met_format If True, format the items in MET time format HHMMSS.
     If False, format each item as a relativedelta object
    @param sort_list If True, sort the list values. If False, skip sorting.
     Default is True.
    @returns list of either strings with MET times or relativedelta objects
    """
    out_list = []
    if not string_value:
        return []

    for time_string in string_value.split(','):
        time_string = time_string.strip()
        if get_met_format:
            value = time_string_to_met_time(time_string, default_unit='H',
                                            force_hms=True)
            out_list.append(value)
        else:
            delta_obj = get_relativedelta(time_string, default_unit='H')
            out_list.append(delta_obj)

    if sort_list:
        if get_met_format:
            out_list.sort(key=int)
        else:
            out_list.sort(key=ti_get_seconds_from_relativedelta)

    return out_list


def ti_calculate(input_dict):
    """!Read in input dictionary items and compute missing items. Output from
    this function can be passed back into it to re-compute items that have
    changed.
    Required inputs: init, valid

    @param input_dict dictionary containing time info to use in computations
    @returns dictionary with updated items/values
    """
    # copy input dictionary to prevent modifying input dictionary
    out_dict = input_dict.copy()

    _set_loop_by(out_dict)

    # look for forecast lead information in input
    # set forecast lead to 0 if not specified
    _set_lead(out_dict)

    # set offset to 0 if not specified
    _set_offset(out_dict)

    _set_init_valid_lead(out_dict)

    # set valid_fmt and init_fmt if they are not wildcard
    if out_dict['valid'] != '*':
        out_dict['valid_fmt'] = out_dict['valid'].strftime('%Y%m%d%H%M%S')

    if out_dict['init'] != '*':
        out_dict['init_fmt'] = out_dict['init'].strftime('%Y%m%d%H%M%S')

    # calculate da_init from valid and offset
    if out_dict['valid'] != '*':
        out_dict['da_init'] = out_dict['valid'] + out_dict['offset']
        out_dict['da_init_fmt'] = out_dict['da_init'].strftime('%Y%m%d%H%M%S')

    # convert offset to seconds and compute offset hours
    out_dict['offset'] = int(out_dict['offset'].total_seconds())
    out_dict['offset_hours'] = int(out_dict['offset'] // 3600)

    # set synonyms for items
    if 'da_init' in out_dict:
        out_dict['date'] = out_dict['da_init']
        out_dict['cycle'] = out_dict['da_init']
    else:
        out_dict['date'] = out_dict['init']

    # if any init/valid/lead are wildcard, skip updating other lead values
    if out_dict['lead'] == '*' or out_dict['valid'] == '*' or out_dict['init'] == '*':
        return out_dict

    # get difference between valid and init to get total seconds since relativedelta
    # does not have a fixed number of seconds
    total_seconds = int((out_dict['valid'] - out_dict['init']).total_seconds())

    # change relativedelta to integer seconds unless months or years are used
    # if they are, keep lead as a relativedelta object to be handled differently
    if out_dict['lead'].months == 0 and out_dict['lead'].years == 0:
        out_dict['lead'] = total_seconds
        out_dict['lead_hours'] = int(total_seconds // 3600)
        out_dict['lead_minutes'] = int(total_seconds // 60)
        out_dict['lead_seconds'] = total_seconds

    return out_dict


def _set_lead(the_dict):
    if 'lead' in the_dict.keys():
        # if lead is relativedelta or wildcard, pass it through
        # if not, treat it as seconds
        if (not isinstance(the_dict['lead'], relativedelta) and
                the_dict['lead'] != '*'):
            the_dict['lead'] = relativedelta(seconds=the_dict['lead'])

    elif 'lead_seconds' in the_dict.keys():
        the_dict['lead'] = relativedelta(seconds=the_dict['lead_seconds'])

    elif 'lead_minutes' in the_dict.keys():
        the_dict['lead'] = relativedelta(minutes=the_dict['lead_minutes'])

    elif 'lead_hours' in the_dict.keys():
        lead_hours = int(the_dict['lead_hours'])
        lead_days = 0
        # if hours is more than a day, pull out days and relative hours
        if lead_hours > 23:
            lead_days = lead_hours // 24
            lead_hours = lead_hours % 24

        the_dict['lead'] = relativedelta(hours=lead_hours, days=lead_days)
    else:
        # set lead to 0 if it was no specified
        the_dict['lead'] = relativedelta(seconds=0)

    # get string representation of forecast lead
    if the_dict['lead'] == '*':
        the_dict['lead_string'] = 'ALL'
    else:
        the_dict['lead_string'] = ti_get_lead_string(the_dict['lead'])


def _set_offset(the_dict):
    if 'offset_hours' in the_dict.keys():
        the_dict['offset'] = datetime.timedelta(hours=the_dict['offset_hours'])
        return

    if 'offset' in the_dict.keys():
        if not isinstance(the_dict['offset'], datetime.timedelta):
            the_dict['offset'] = datetime.timedelta(seconds=the_dict['offset'])
        return

    the_dict['offset'] = datetime.timedelta(seconds=0)


def _set_loop_by(the_dict):
    # loop_by is already set
    if the_dict.get('loop_by'):
        return

    init = the_dict.get('init')
    valid = the_dict.get('valid')
    # if init and valid are both set, don't set loop_by
    if init and valid:
        return

    # set loop_by to which init or valid is set
    if init:
        the_dict['loop_by'] = 'init'
    elif valid:
        the_dict['loop_by'] = 'valid'


def _set_init_valid_lead(the_dict):
    wildcard_items = [item for item in ('init', 'lead', 'valid')
                      if the_dict.get(item) == '*']
    # if 2 or more are wildcards, cannot compute init/valid/lead, so return
    if len(wildcard_items) >= 2:
        return

    # assumed that 1 or fewer items are wildcard or unset
    init = the_dict.get('init')
    valid = the_dict.get('valid')
    lead = the_dict.get('lead')
    loop_by = the_dict.get('loop_by')

    # if init and valid are both set and not wildcard, compute based on loop_by
    if init and valid and init != '*' and valid != '*':
        if loop_by == 'init':
            the_dict['valid'] = init + lead
        elif loop_by == 'valid':
            the_dict['init'] = valid - lead
    elif init and init != '*':
        the_dict['valid'] = init + lead
        if not loop_by:
            the_dict['loop_by'] = 'init'
    elif valid and valid != '*':
        the_dict['init'] = valid - lead
        if not loop_by:
            the_dict['loop_by'] = 'valid'


def add_to_time_input(time_input, clock_time=None, instance=None, custom=None):
    if clock_time:
        clock_dt = datetime.datetime.strptime(clock_time, '%Y%m%d%H%M%S')
        time_input['now'] = clock_dt

    # if instance is set, use that value, otherwise use empty string
    time_input['instance'] = instance if instance else ''

    # if custom is specified, set it
    # otherwise leave it unset so it can be set within the wrapper
    if custom:
        time_input['custom'] = custom


def add_field_info_to_time_info(time_info, var_info):
    """!Add field information from var_info to the time_info dictionary to use
    in string template substitution. Sets new items in time_info.

    @param time_info dictionary containing time information to substitute
    filename template tags
    @param var_info dictionary containing information for the fields to process
    """
    if var_info is None:
        return

    for key, value in var_info.items():
        # skip index and extra field info
        if key == 'index' or key.endswith('extra'):
            continue

        if key.endswith('thresh'):
            value = format_thresh(value)

        time_info[key] = value
