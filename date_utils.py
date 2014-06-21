
# this stores some date utilities
# mainly for the definitions of relative dates


import datetime
import calendar


def N_(msg):
    return msg


reldate_list = []

make_zdate =  datetime.datetime(year=1900,month=1,day=1,hour=0,minute=0,second=0,microsecond=0)

SecDelta = datetime.timedelta(seconds=1)

DayDelta = datetime.timedelta(days=1)

WeekDelta = datetime.timedelta(days=7)

TwoWeekDelta = datetime.timedelta(days=14)

# so these are weird - not sure how to represent these
# and we cannot use this as datetime requires the year
MonthDelta = datetime.datetime(year=1900,month=1,day=1)

QuarterDelta = datetime.datetime(year=1900,month=3,day=1)

HalfYearDelta = datetime.datetime(year=1900,month=6,day=1)

YearDelta  = datetime.datetime(year=1,month=1,day=1)

ThirtyDayDelta = datetime.timedelta(days=30)

NinetyDayDelta = datetime.timedelta(days=90)

# ;; if you add any more FooDeltas, add to this list!!!

deltalist = [ \
              ('SecDelta', SecDelta),
	      ('DayDelta', DayDelta),
	      ('WeekDelta', WeekDelta),
	      ('TwoWeekDelta', TwoWeekDelta),
	      ('MonthDelta', MonthDelta),
	      ('QuarterDelta', QuarterDelta),
	      ('HalfYearDelta', HalfYearDelta),
	      ('YearDelta', YearDelta),
	      ('ThirtyDayDelta', ThirtyDayDelta),
	      ('NinetyDayDelta', NinetyDayDelta),
            ]


def get_start_cal_year ():
    newtim = datetime.datetime.now()
    return newtim.replace(sec=0,min=0,hour=0,mday=0,mon=0,tzinfo=None)

def get_end_cal_year ():
    newtim = datetime.datetime.now()
    return newtim.replace(sec=59,min=59,hour=23,mday=31,mon=12,tzinfo=None)

def get_start_prev_year ():
    newtim = datetime.datetime.now()
    return newtim.replace(year=newtim.year-1,sec=0,min=0,hour=0,mday=1,mon=0,tzinfo=None)

def get_end_prev_year ():
    newtim = datetime.datetime.now()
    return newtim.replace(year=newtim.year-1,sec=59,min=59,hour=23,mday=31,mon=12,tzinfo=None)

def get_start_next_year ():
    newtim = datetime.datetime.now()
    return newtim.replace(year=newtim.year+1,sec=0,min=0,hour=0,mday=1,mon=1,tzinfo=None)

def get_end_next_year ():
    newtim = datetime.datetime.now()
    return newtim.replace(year=newtim.year+1,sec=59,min=59,hour=23,mday=31,mon=12,tzinfo=None)

def get_start_accounting_period ():
    #(gnc:secs->timepair (gnc-accounting-period-fiscal-start)))
    pass

def get_end_accounting_period ():
    #(gnc:secs->timepair (gnc-accounting-period-fiscal-end)))
    pass

def get_start_this_month ():
    newtim = datetime.datetime.now()
    return newtim.replace(sec=0,min=0,hour=0,mday=1,tzinfo=None)

def get_end_this_month ():
    newtim = datetime.datetime.now()
    monrng = calendar.monthrange(newtim.year,newtim.mon)
    return newtim.replace(sec=59,min=59,hour=23,mday=monrng[1],tzinfo=None)
    
def get_start_prev_month ():
    newtim = datetime.datetime.now()
    if newtim.mon == 1:
        return newtim.replace(sec=59,min=59,hour=23,mday=1,mon=12,year=newtim.year-1,tzinfo=None)
    else:
        return newtim.replace(sec=0,min=0,hour=0,mday=1,mon=newtim.mon-1,tzinfo=None)

def get_end_prev_month ():
    newtim = datetime.datetime.now()
    if newtim.mon == 1:
        monrng = calendar.monthrange(newtim.year-1,12)
        return newtim.replace(sec=59,min=59,hour=23,mday=monrng[1],mon=12,year=newtim.year-1,tzinfo=None)
    else:
        monrng = calendar.monthrange(newtim.year,newtim.mon-1)
        return newtim.replace(sec=0,min=0,hour=0,mday=monrng[1],mon=newtim.mon-1,tzinfo=None)
    
def get_start_next_month ():
    newtim = datetime.datetime.now()
    if newtim.mon == 12:
        return newtim.replace(sec=0,min=0,hour=0,mday=1,mon=1,year=newtim.year+1,tzinfo=None)
    else:
        return newtim.replace(sec=0,min=0,hour=0,mday=1,mon=newtim.mon+1,tzinfo=None)

def get_end_next_month ():
    newtim = datetime.datetime.now()
    if newtim.mon == 12:
        monrng = calendar.monthrange(newtim.year+1,1)
        return newtim.replace(sec=59,min=59,hour=23,mday=monrng[1],mon=1,year=newtim.year+1,tzinfo=None)
    else:
        monrng = calendar.monthrange(newtim.year,newtim.mon+1)
        return newtim.replace(sec=0,min=0,hour=0,mday=monrng[1],mon=newtim.mon+1,tzinfo=None)
    
def get_start_current_quarter ():
    newtim = datetime.datetime.now()
    return newtim.replace(sec=0,min=0,hour=0,mday=1,mon=newtim.mon-((newtim.mon-1)%3),tzinfo=None)

def get_end_current_quarter ():
    newtim = datetime.datetime.now()
    endmon = newtim.mon + (2 - ((newtim.mon-1)%3))
    monrng = calendar.monthrange(newtim.year,endmon)
    newtim = datetime.datetime.now()
    return newtim.replace(sec=59,min=59,hour=23,mday=monrng[1],mon=endmon,tzinfo=None)

def get_start_prev_quarter ():
    newtim = datetime.datetime.now()
    prvmon = newtim.mon - ((newtim.mon-1)%3) - 3
    if prvmon < 1:
        prvmon = 9
        prvyr = newtim.year-1
    else:
        prvyr = newtim.year
    return newtim.replace(sec=0,min=0,hour=0,mday=1,mon=prvmon,year=prvyr,tzinfo=None)

def get_end_prev_quarter ():
    newtim = datetime.datetime.now()
    prvmon = newtim.mon + ((newtim.mon-1)%3) - 3
    if prvmon < 1:
        prvmon = 12
        prvyr = newtim.year-1
    else:
        prvyr = newtim.year
    monrng = calendar.monthrange(prvyr,prvmon)
    return newtim.replace(sec=59,min=59,hour=23,mday=monrng[1],mon=prvmon,year=prvyr,tzinfo=None)

def get_start_next_quarter ():
    newtim = datetime.datetime.now()
    nxtmon = newtim.mon + 3 - ((newtim.mon-1)%3)
    if nxtmon > 12:
        nxtmon = 1
        nxtyr = newtim.year+1
    else:
        nxtyr = newtim.year
    return newtim.replace(sec=0,min=0,hour=0,mday=1,mon=nxtmon,year=nxtyr,tzinfo=None)

def get_end_next_quarter ():
    newtim = datetime.datetime.now()
    nxtmon = newtim.mon + 3 + ((newtim.mon-1)%3)
    if nxtmon > 12:
        nxtmon = 3
        nxtyr = newtim.year+1
    else:
        nxtyr = newtim.year
    monrng = calendar.monthrange(nxtyr,nxtmon)
    return newtim.replace(sec=59,min=59,hour=23,mday=monrng[1],mon=nxtmon,year=nxtyr,tzinfo=None)


def get_today ():
    return datetime.datetime.now()


# these are confusing - what exactly is 1 month ago - current month length before now?

def get_one_month_ago ():
    prvtim = datetime.datetime.now()
    if prvtim.mon == 1:
        prvmon = 12
        prvyr = prvtim.year-1
    else:
        prvmon = prvtim.mon-1
        prvyr = prvtim.year
    # it looks as though the scheme gets the length of the previous month
    monrng = calendar.monthrange(prvyr,prvmon)
    prvmdy = prvtim.mday
    if monrng[1] > prvtim.mday:
        prvmdy = monrng[1]
    return prvtim.replace(mday=prvmdy,mon=prvmon,year=prvyr,tzinfo=None)


def get_three_months_ago ():
    prvtim = datetime.datetime.now()
    if prvtim.mon < 3:
        prvmon = prvtim.mon + 12
        prvyr = prvtim.year-1
    else:
        prvyr = prvtim.year
    prvmon = prvtim.mon - 3
    # it looks as though the scheme gets the length of the previous month
    monrng = calendar.monthrange(prvyr,prvmon)
    prvmdy = prvtim.mday
    if monrng[1] > prvtim.mday:
        prvmdy = monrng[1]
    return prvtim.replace(mday=prvmdy,mon=prvmon,year=prvyr,tzinfo=None)

def get_six_months_ago ():
    prvtim = datetime.datetime.now()
    if prvtim.mon < 6:
        prvmon = prvtim.mon + 12
        prvyr = prvtim.year-1
    else:
        prvyr = prvtim.year
    prvmon = prvtim.mon - 6
    # it looks as though the scheme gets the length of the previous month
    monrng = calendar.monthrange(prvyr,prvmon)
    prvmdy = prvtim.mday
    if monrng[1] > prvtim.mday:
        prvmdy = monrng[1]
    return prvtim.replace(mday=prvmdy,mon=prvmon,year=prvyr,tzinfo=None)

def get_one_year_ago ():
    prvtim = datetime.datetime.now()
    prvyr = prvtim.year-1
    # it looks as though the scheme gets the length of the previous month
    monrng = calendar.monthrange(prvyr,prvtim.mon)
    prvmdy = prvtim.mday
    if monrng[1] > prvtim.mday:
        prvmdy = monrng[1]
    return prvtim.replace(mday=prvmdy,year=prvyr,tzinfo=None)

def get_one_month_ahead ():
    newtim = datetime.datetime.now()
    if newtim.mon == 12:
        newmon = 1
	newyr = newtim.year+1
    else:
        newmon = newtim.mon+1
        newyr = newtim.year
    # it looks as though the scheme gets the length of the previous month
    monrng = calendar.monthrange(newyr,newmon)
    newmdy = newtim.mday
    if monrng[1] > newtim.mday:
        newmdy = monrng[1]
    return newtim.replace(mday=newmdy,mon=newmon,year=newyr,tzinfo=None)

def get_three_months_ahead ():
    newtim = datetime.datetime.now()
    if newtim.mon > 9:
        newmon = newtim.mon - 9
	newyr = newtim.year+1
    else:
        newmon = newtim.mon+3
        newyr = newtim.year
    # it looks as though the scheme gets the length of the previous month
    monrng = calendar.monthrange(newyr,newmon)
    newmdy = newtim.mday
    if monrng[1] > newtim.mday:
        newmdy = monrng[1]
    return newtim.replace(mday=newmdy,mon=newmon,year=newyr,tzinfo=None)

def get_six_months_ahead ():
    newtim = datetime.datetime.now()
    if newtim.mon > 6:
        newmon = newtim.mon - 6
	newyr = newtim.year+1
    else:
        newmon = newtim.mon+6
        newyr = newtim.year
    # it looks as though the scheme gets the length of the previous month
    monrng = calendar.monthrange(newyr,newmon)
    newmdy = newtim.mday
    if monrng[1] > newtim.mday:
        newmdy = monrng[1]
    return newtim.replace(mday=newmdy,mon=newmon,year=newyr,tzinfo=None)

def get_one_year_ahead ():
    newtim = datetime.datetime.now()
    newyr = newtim.year+1
    # it looks as though the scheme gets the length of the previous month
    monrng = calendar.monthrange(newyr,newtim.mon)
    newmdy = newtim.mday
    if monrng[1] > newtim.mday:
        newmdy = monrng[1]
    return newtim.replace(mday=newmdy,year=newyr,tzinfo=None)

# and now for the relative dates

date_string_db = {}
relative_date_values = {}

def reldate_initialize ():
    global date_string_db
    global relative_date_values

    # whats a good way to map this - this seems to be storing each string
    # separately

    date_string_db = { \

        'start-cal-year' : { \
            'string' : N_("Start of this year"),
            'desc' : N_("First day of the current calendar year."), },

        'end-cal-year' : { \
            'string' : N_("End of this year"),
            'desc' : N_("Last day of the current calendar year."), },

        'start-prev-year' : { \
            'string' : N_("Start of previous year"),
            'desc' : N_("First day of the previous calendar year."), },

        'end-prev-year' : { \
            'string' : N_("End of previous year"),
            'desc' : N_("Last day of the previous calendar year."), },

        'start-next-year' : { \
            'string' : N_("Start of next year"),
            'desc' : N_("First day of the next calendar year."), },

        'end-next-year' : { \
            'string' : N_("End of next year"),
            'desc' : N_("Last day of the next calendar year."), },

        'start-accounting-period' : { \
            'string' : N_("Start of accounting period"),
            'desc' : N_("First day of the accounting period, as set in the global preferences."), },

        'end-accounting-period' : { \
            'string' : N_("End of accounting period"),
            'desc' : N_("Last day of the accounting period, as set in the global preferences."), },

        'start-this-month' : { \
            'string' : N_("Start of this month"),
            'desc' : N_("First day of the current month."), },

        'end-this-month' : { \
            'string' : N_("End of this month"),
            'desc' : N_("Last day of the current month."), },

        'start-prev-month' : { \
            'string' : N_("Start of previous month"),
            'desc' : N_("First day of the previous month."), },

        'end-prev-month' : { \
            'string' : N_("End of previous month"),
            'desc' : N_("Last day of previous month."), },

        'start-next-month' : { \
            'string' : N_("Start of next month"),
            'desc' : N_("First day of the next month."), },
 
        'end-next-month' : { \
            'string' : N_("End of next month"),
            'desc' : N_("Last day of next month."), },

        'start-current-quarter' : { \
            'string' : N_("Start of current quarter"),
            'desc' : N_("First day of the current quarterly accounting period."), },

        'end-current-quarter' : { \
            'string' : N_("End of current quarter"),
            'desc' : N_("Last day of the current quarterly accounting period."), },

        'start-prev-quarter' : { \
            'string' : N_("Start of previous quarter"),
            'desc' : N_("First day of the previous quarterly accounting period."), },

        'end-prev-quarter' : { \
            'string' : N_("End of previous quarter"),
            'desc' : N_("Last day of previous quarterly accounting period."), },

        'start-next-quarter' : { \
            'string' : N_("Start of next quarter"),
            'desc' : N_("First day of the next quarterly accounting period."), },

        'end-next-quarter' :  { \
            'string' : N_("End of next quarter"),
            'desc' : N_("Last day of next quarterly accounting period."), },

        'today' : { \
            'string' : N_("Today"),
            'desc' : N_("The current date."), },

        'one-month-ago' : { \
            'string' : N_("One Month Ago"),
            'desc' : N_("One Month Ago."), },

        'one-week-ago' : { \
            'string' : N_("One Week Ago"),
            'desc' : N_("One Week Ago."), },

        'three-months-ago' : { \
            'string' : N_("Three Months Ago"),
            'desc' : N_("Three Months Ago."), },

        'six-months-ago' : { \
            'string' : N_("Six Months Ago"),
            'desc' : N_("Six Months Ago."), },

        'one-year-ago' : { \
            'string' : N_("One Year Ago"),
            'desc' : N_("One Year Ago."), },

        'one-month-ahead' : { \
            'string' : N_("One Month Ahead"),
            'desc' : N_("One Month Ahead."), },

        'one-week-ahead' : { \
            'string' : N_("One Week Ahead"),
            'desc' : N_("One Week Ahead."), },

        'three-months-ahead' : { \
            'string' : N_("Three Months Ahead"),
            'desc' : N_("Three Months Ahead."), },

        'six-months-ahead' : { \
            'string' : N_("Six Months Ahead"),
            'desc' : N_("Six Months Ahead."), },

        'one-year-ahead' : { \
            'string' : N_("One Year Ahead"),
            'desc' : N_("One Year Ahead."), },
    }

    # this also includes the function to compute the date
    # its a list in scheme but in python make a dict
    relative_date_values = { \
        'start-cal-year' : [ date_string_db['start-cal-year']['string'], 
                             date_string_db['start-cal-year']['desc'], 
                             get_start_cal_year ],
        'end-cal-year' : [ date_string_db['end-cal-year']['string'], 
                           date_string_db['end-cal-year']['desc'], 
                           get_end_cal_year ],
        'start-prev-year' : [ date_string_db['start-prev-year']['string'], 
                              date_string_db['start-prev-year']['desc'], 
                              get_start_prev_year],
        'start-next-year' : [ date_string_db['start-next-year']['string'], 
                              date_string_db['start-next-year']['desc'], 
                              get_start_next_year],
        'end-prev-year' : [ date_string_db['end-prev-year']['string'], 
                            date_string_db['end-prev-year']['desc'], 
                            get_end_prev_year ],
        'end-next-year' : [ date_string_db['end-next-year']['string'], 
                            date_string_db['end-next-year']['desc'], 
                            get_end_next_year ],
        'start-accounting-period' : [ date_string_db['start-accounting-period']['string'], 
                                      date_string_db['start-accounting-period']['desc'], 
                                      get_start_accounting_period ],
        'end-accounting-period' : [ date_string_db['end-accounting-period']['string'], 
                                    date_string_db['end-accounting-period']['desc'], 
                                    get_end_accounting_period ],
        'start-this-month' : [ date_string_db['start-this-month']['string'], 
                               date_string_db['start-this-month']['desc'], 
                               get_start_this_month ],
        'end-this-month' : [ date_string_db['end-this-month']['string'], 
                             date_string_db['end-this-month']['desc'], 
                             get_end_this_month ],
        'start-prev-month' : [ date_string_db['start-prev-month']['string'], 
                               date_string_db['start-prev-month']['desc'], 
                               get_start_prev_month ],
        'end-prev-month' : [ date_string_db['end-prev-month']['string'], 
                             date_string_db['end-prev-month']['desc'], 
                             get_end_prev_month ],
        'start-next-month' : [ date_string_db['start-next-month']['string'], 
                               date_string_db['start-next-month']['desc'], 
                               get_start_next_month ],
        'end-next-month' : [ date_string_db['end-next-month']['string'], 
                             date_string_db['end-next-month']['desc'], 
                             get_end_next_month ],
        'start-current-quarter' : [ date_string_db['start-current-quarter']['string'], 
                                    date_string_db['start-current-quarter']['desc'], 
                                    get_start_current_quarter ],
        'end-current-quarter' : [ date_string_db['end-current-quarter']['string'], 
                                  date_string_db['end-current-quarter']['desc'], 
                                  get_end_current_quarter ],
        'start-prev-quarter' : [ date_string_db['start-prev-quarter']['string'], 
                                 date_string_db['start-prev-quarter']['desc'], 
                                 get_start_prev_quarter ],
        'end-prev-quarter' : [ date_string_db['end-prev-quarter']['string'], 
                               date_string_db['end-prev-quarter']['desc'], 
                               get_end_prev_quarter ],
        'start-next-quarter' : [ date_string_db['start-next-quarter']['string'], 
                                 date_string_db['start-next-quarter']['desc'], 
                                 get_start_next_quarter ],
        'end-next-quarter' : [ date_string_db['end-next-quarter']['string'], 
                               date_string_db['end-next-quarter']['desc'], 
                               get_end_next_quarter ],
        'today' : [ date_string_db['today']['string'], 
                    date_string_db['today']['desc'], 
                    get_today ],
        'one-month-ago' : [ date_string_db['one-month-ago']['string'], 
                            date_string_db['one-month-ago']['desc'], 
                            get_one_month_ago ],
        'three-months-ago' : [ date_string_db['three-months-ago']['string'], 
                               date_string_db['three-months-ago']['desc'], 
                               get_three_months_ago ],
        'six-months-ago' : [ date_string_db['six-months-ago']['string'], 
                             date_string_db['six-months-ago']['desc'], 
                             get_six_months_ago ],
        'one-year-ago' : [ date_string_db['one-year-ago']['string'], 
                           date_string_db['one-year-ago']['desc'], 
                           get_one_year_ago ],
        'one-month-ahead' : [ date_string_db['one-month-ahead']['string'], 
                              date_string_db['one-month-ahead']['desc'], 
                              get_one_month_ahead ],
        'three-months-ahead' : [ date_string_db['three-months-ahead']['string'], 
                                 date_string_db['three-months-ahead']['desc'], 
                                 get_three_months_ahead ],
        'six-months-ahead' : [ date_string_db['six-months-ahead']['string'], 
                               date_string_db['six-months-ahead']['desc'], 
                               get_six_months_ahead ],
        'one-year-ahead' : [ date_string_db['one-year-ahead']['string'], 
                               date_string_db['one-year-ahead']['desc'], 
                               get_one_year_ahead ],
        }

reldate_initialize()
