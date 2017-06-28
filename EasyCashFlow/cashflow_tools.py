
import calendar
# import numpy


def _timeid2float(xdate, pyr):

    if isinstance(xdate, tuple) and len(xdate) == 1 and pyr == 1:
        xmajor, = xdate
        return xmajor
    if isinstance(xdate, tuple) and len(xdate) == 2 and pyr == 1:
        xmajor, xminor = xdate
        if xminor == 0:
            return float(xmajor * pyr + xminor / pyr)
    if isinstance(xdate, tuple) and len(xdate) == 2 and pyr > 1:
        xmajor, xminor = xdate
        return float(xmajor + xminor / pyr)
    raise TypeError("date in invalid format" + xdate.__repr__())


def _float2timeid(xfloat, pyr):
    """Converts a float number in a equivalent pair (maj, min)

    >>> _float2timeid(2000, pyr=1) # doctest: +NORMALIZE_WHITESPACE
    (2000,)

    >>> _float2timeid(2000, pyr=3)  # doctest: +NORMALIZE_WHITESPACE
    (2000, 0)

    >>> _float2timeid(2000.25, pyr=4)  # doctest: +NORMALIZE_WHITESPACE
    (2000, 1)

    >>> _float2timeid(2000.50, pyr=4)  # doctest: +NORMALIZE_WHITESPACE
    (2000, 2)

    """
    if pyr == 1:
        return (int(xfloat), )
    xmajor = int(xfloat)
    xminor = int((xfloat - xmajor) * pyr)
    return (xmajor, xminor)


def _timeid2index(timeid, basis, pyr):
    """Converts a timeid in an integer index


    >>> _timeid2index(timeid=(2000, 3), basis=(2000, 0), pyr=4)
    3

    >>> _timeid2index(timeid=(2000, 0), basis=(2000, 0), pyr=4)
    0

    """
    if not isinstance(timeid, tuple):
        TypeError('Invalid type for timeid: ' + timeid.__repr__())
    if not isinstance(basis, tuple):
        TypeError('Invalid type for basis: ' + basis.__repr__())
    if len(timeid) != len(basis):
        TypeError('Incompatible tuples: ' + basis.__repr__() +', ' + timeid.__repr__())

    if len(timeid) == 1:
        timeid_major, = timeid
        basis_major, = basis
        return timeid_major - basis_major

    timeid_major, timeid_minor = timeid
    basis_major, basis_minor = basis
    return (timeid_major - basis_major) * pyr + (timeid_minor - basis_minor)



def verify_eq_time_range(series1, series2):

    if series1.pyr != series2.pyr:
        msg = 'Time series have different periods per year: '
        raise ValueError(msg + series1.pyr.__repr__() + ', ' + series2.pyr.__repr__())

    if series1.start != series2.start:
        msg = 'Time series have different start date: '
        raise ValueError(msg + series1.start.__repr__() + ', ' + series2.start.__repr__())

    if series1.end != series2.end:
        msg = 'Time series have different end date: '
        raise ValueError(msg + series1.end.__repr__() + ', ' + series2.end.__repr__())



class TimeSeries():
    """ Class for representing time series.
    """

    def __init__(self, start=None, end=None, nper=None, pyr=1):

        def check_timeid(timeid):
            #
            if timeid is None:
                return None

            if isinstance(timeid, (float, int)):
                if pyr == 1:
                    return (int(timeid),)
                return (int(timeid), 1)

            if isinstance(timeid, tuple):
                if pyr == 1 and len(timeid) > 1:
                    major, minor = timeid
                    if minor > 1:
                        raise ValueError('Invalid data for minor unit: ' + minor.__repr__())
                    return (int(major),)
                elif pyr > 1 and len(timeid) == 1:
                    major, = timeid
                    return (major, 1)
                elif pyr > 1 and len(timeid) == 2:
                    major, minor = timeid
                    if minor > pyr:
                        raise ValueError('Invalid data: ' + minor.__repr__())
                return timeid

            raise TypeError('Invalid type for TimeId: ' + timeid.__repr__())

        start = check_timeid(start)
        end = check_timeid(end)

        if nper is not None:
            nper = int(nper)

        if start is not None and end is not None and nper is not None:
            float_start = _timeid2float(start, pyr)
            float_end = _timeid2float(end, pyr)
            nperc = int((float_end - float_start) * pyr) + 1
            if nper != nperc:
                msg = 'Invalid data for start, end and nper: ' + start.__repr__()
                msg += ', ' + end.__repr__() + ', ' + nper.__repr__()
                raise ValueError(msg)
        elif start is not None and end is not None:   # computes nper
            float_start = _timeid2float(start, pyr)
            float_end = _timeid2float(end, pyr)
            nper = int((float_end - float_start) * pyr) + 1
        elif start is not None and nper is not None:  # computes end
            float_start = _timeid2float(start, pyr)
            float_end = float_start + (nper - 1) / pyr
            end = _float2timeid(float_end, pyr)
        elif end is not None and nper is not None:  # computes start
            float_end = _timeid2float(end, pyr)
            float_start = float_end - (nper - 1) / pyr
            start = _float2timeid(float_start, pyr)
        elif start is None and end is None and nper is not None:
            if pyr == 1:
                start = (0,)
                end = (nper-1,)
            else:
                start = (0, 0)
                end = _float2timeid((nper - 1) / pyr, pyr)
        else:
            raise ValueError('Invalid data for start, end or nper')

        if nper <= 1:
            raise ValueError('Time Series must have a nper > 1')

        self.start = start
        self.end = end
        self.pyr = pyr
        self.data = [0] * nper


    def __repr__(self):
        """Print the time series."""

        if self.pyr in [4, 7, 12]:
            return self.__repr4712__()

        txt = ['Time Series:']
        txt += ['Start = {:s}'.format(self.start.__repr__())]
        txt += ['End = {:s}'.format(self.end.__repr__())]
        txt += ['pyr = {:s}'.format(self.pyr.__repr__())]

        if self.pyr == 1:
            imajor, = self.start
            iminor = 0
        else:
            imajor, iminor = self.start

        txt_date = []
        txt_freq = []
        txt_val = []

        period = 0
        while period < len(self.data):

            freq = 1
            if self.pyr == 1:
                beg_date = end_date = (imajor,)
            else:
                beg_date = end_date = (imajor, iminor)

            while period + freq < len(self.data) and \
                  self.data[period] == self.data[period + freq]:
                freq += 1
                iminor += 1
                if iminor >= self.pyr:
                    iminor = 0
                    imajor += 1

                if self.pyr == 1:
                    end_date = (imajor,)
                else:
                    end_date = (imajor, iminor)

            iminor += 1
            if iminor >= self.pyr:
                iminor = 0
                imajor += 1

            if freq == 1:

#                iminor += 1
#                if iminor >= self.pyr:
#                    iminor = 0
#                    imajor += 1

                txt_date += ['{:s}'.format(beg_date.__str__())]
                txt_freq += [' ']
                txt_val += ['{:1.2f}'.format(self.data[period])]
            else:
                fmt = '{:s}-{:s}'
                txt_date += [fmt.format(beg_date.__str__(), end_date.__str__())]
                txt_freq += ['[{:d}]'.format(freq)]
                txt_val += ['{:1.2f}'.format(self.data[period])]



            period += freq

        max_date = max_freq = max_val = 0
        for index, _ in enumerate(txt_date):
            max_date = max(max_date, len(txt_date[index]))
            max_freq = max(max_freq, len(txt_freq[index]))
            max_val = max(max_val, len(txt_val[index]))

        fmt = ' {:' + '{:d}'.format(max_date) + 's} '
        fmt += '{:' + '{:d}'.format(max_freq) + 's} '
        fmt += '{:>' + '{:d}'.format(max_val) + 's} '


        for index, _ in enumerate(txt_date):
            if index == 0:
                txt += ['Data =' + fmt.format(txt_date[index], txt_freq[index], txt_val[index])]
            else:
                txt += ['      ' +fmt.format(txt_date[index], txt_freq[index], txt_val[index])]

        return '\n'.join(txt)+'\n'


    def __repr4712__(self):
        """ Prints as table with quarters, days or months.

        # >>> TimeSeries(start=(1, 0), pyr=4) # doctest: +NORMALIZE_WHITESPACE
        #   Qtr0 Qtr1 Qtr2 Qtr3
        # 1 0.00

        # >>> TimeSeries(start=(1, 1), pyr=7) # doctest: +NORMALIZE_WHITESPACE
        #   Mon  Tue  Wed  Thu  Fri  Sat  Sun
        # 1 0.00

        # >>> TimeSeries(start=(1, 1), pyr=12)  # doctest: +NORMALIZE_WHITESPACE
        #    Jan  Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec
        # 1 0.00


        """
        smajor, sminor = self.start
        emajor, eminor = self.end

        imajor = smajor
        iminor = 0
        iper = 0

        maxlen = 0
        for data in self.data:
            maxlen = max(maxlen, len('{:.2f}'.format(data)))

        maxlen = maxlen - 3

        fmt_major = '{:<' + '{:<d}'.format(len(emajor.__str__())) + 'd}'
        fmt_minor = ' {:>' + '{:d}'.format(maxlen+3) + '.2f}'
        fmt_void = ' ' * (4+len(max(self.data).__str__()))
        fmt_head = ' {:>' + '{:d}'.format(maxlen+3) + 's}'

        sline = ' ' * len(emajor.__str__())
        if self.pyr == 4:
            names = ['Qtr0', 'Qtr1', 'Qtr2', 'Qtr3']
        elif self.pyr == 7:
            names = calendar.day_abbr
        else:
            names = calendar.month_abbr[1:13]

        for index in range(self.pyr):
            sline += fmt_head.format(names[index])
        txt = [sline]
        sline = ''

        sline = fmt_major.format(imajor)

        is_ok = True

        while is_ok is True:

            if imajor == smajor and iminor < sminor:
                sline += fmt_void
            else:
                sline += fmt_minor.format(self.data[iper])
                iper += 1

            if  imajor == emajor and iminor == eminor:
                is_ok = False

            iminor += 1
            if iminor >= self.pyr:
                iminor = 0
                imajor += 1
                txt.append(sline)
                if is_ok is True:
                    sline = fmt_major.format(imajor)
                else:
                    sline = ''

        txt.append(sline)
        return '\n'.join(txt)



    def __getitem__(self, key):
        """gets the item



        """
        if isinstance(key, tuple):
            key = _timeid2index(timeid=key, basis=self.start, pyr=self.pyr)
        return self.data[key]

    def __setitem__(self, key, value):

        if isinstance(key, tuple):
            key = _timeid2index(timeid=key, basis=self.start, pyr=self.pyr)
        self.data[key] = value

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self.data.__iter__()

    def __next__(self):
        return self.data.__next__()


    def tolist(self):
        """Returns the values as a list"""
        return [x for x in self.data]

    def copy(self):
        """returns a copy of the time series"""
        result = TimeSeries(start=self.start, end=self.end, nper=len(self.data), pyr=self.pyr)
        result.data = [value for value in self.data]
        return result

    #
    # mathematical operations
    #

    def __abs__(self):
        """Returns a new time series computed by applying the `abs` funtion
        to the elements of the original time series.

        >>> abs(cashflow(const_value=[-10]*4, pyr=4)) # doctest: +NORMALIZE_WHITESPACE
           Qtr0  Qtr1  Qtr2  Qtr3
        0 10.00 10.00 10.00 10.00

        """
        result = self.copy()
        for time, _ in enumerate(result.data):
            result[time] = abs(self[time])
        return result

    def __add__(self, other):
        """Addition

        >>> cashflow(const_value=[1]*4, pyr=4) + cashflow(const_value=[2]*4, pyr=4) # doctest: +NORMALIZE_WHITESPACE
          Qtr0 Qtr1 Qtr2 Qtr3
        0 3.00 3.00 3.00 3.00

        """
        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        result = self.copy()
        for index, _ in enumerate(result.data):
            result[index] += other[index]
        return result


    def __floordiv__(self, other):
        """floordiv

        >>> cashflow(const_value=[6]*4, pyr=4) // cashflow(const_value=[4]*4, pyr=4) # doctest: +NORMALIZE_WHITESPACE
          Qtr0 Qtr1 Qtr2 Qtr3
        0 1.00 1.00 1.00 1.00

        """
        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        result = self.copy()
        for index, _ in enumerate(result.data):
            result[index] //= other[index]
        return result


    def __mod__(self, other):
        """

        >>> cashflow( const_value=[6]*4, pyr=4) % cashflow( const_value=[4]*4, pyr=4) # doctest: +NORMALIZE_WHITESPACE
          Qtr0 Qtr1 Qtr2 Qtr3
        0 2.00 2.00 2.00 2.00


        """
        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        result = self.copy()
        for index, _ in enumerate(result.data):
            result[index] %= other[index]
        return result


    def __mul__(self, other):
        """multiplication

        >>> cashflow( const_value=[2]*4, pyr=4) * cashflow( const_value=[3]*4, pyr=4) # doctest: +NORMALIZE_WHITESPACE
          Qtr0 Qtr1 Qtr2 Qtr3
        0 6.00 6.00 6.00 6.00

        """
        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        result = self.copy()
        for index, _ in enumerate(result.data):
            result[index] *= other[index]
        return result


    def __sub__(self, other):

        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        result = self.copy()
        for index, _ in enumerate(result.data):
            result[index] -= other[index]
        return result


    def __truediv__(self, other):

        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        result = self.copy()
        for index, _ in enumerate(result.data):
            result[index] /= other[index]
        return result

    def __radd__(self, other):

        if other == 0:
            return self
        else:
            return self.__add__(other)


    def __iadd__(self, other):

        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        for index, _ in enumerate(self.data):
            self[index] += other[index]
        return self


    def __ifloordiv__(self, other):

        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        for index, _ in enumerate(self.data):
            self[index] //= other[index]
        return self



    def __imod__(self, other):

        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        for index, _ in enumerate(self.data):
            self[index] %= other[index]
        return self



    def __imul__(self, other):

        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        for index, _ in enumerate(self.data):
            self[index] *= other[index]
        return self


    def __isub__(self, other):

        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        for index, _ in enumerate(self.data):
            self[index] -= other[index]
        return self


    def __itruediv__(self, other):

        if isinstance(other, (int, float)):
            other = [other] * len(self)
        else:
            verify_eq_time_range(self, other)
        for index, _ in enumerate(self.data):
            self[index] /= other[index]
        return self






def cashflow(const_value=0, start=None, end=None, nper=None, pyr=1, spec=None):

    if isinstance(const_value, list) and nper is None:
        nper = len(const_value)
    time_series = TimeSeries(start=start, end=end, nper=nper, pyr=pyr)
    start = time_series.start
    for index, _ in enumerate(time_series):
        if isinstance(const_value, list):
            time_series[index] = const_value[index]
        else:
            time_series[index] = const_value
    if spec is None:
        return time_series
    if isinstance(spec, tuple):
        spec = [spec]
    for xspec in spec:
        timeid, value = xspec
        if isinstance(timeid, int):
            time = timeid
        else:
            time = _timeid2index(timeid=timeid, basis=start, pyr=pyr)
        time_series[time] = value
    return time_series

def nominal_rate(const_value=0, start=None, end=None, nper=None, pyr=1, spec=None):

    if isinstance(const_value, list) and nper is None:
        nper = len(const_value)
    time_series = TimeSeries(start=start, end=end, nper=nper, pyr=pyr)
    start = time_series.start
    for index, _ in enumerate(time_series):
        if isinstance(const_value, list):
            time_series[index] = const_value[index]
        else:
            time_series[index] = const_value
    if spec is None:
        return time_series
    if isinstance(spec, tuple):
        spec = [spec]
    nummod = len(spec)
    starting = [None] * nummod
    ending = [None] * nummod
    values = [None] * nummod
    for index, xspec in enumerate(spec):
        timeid, value = xspec
        if isinstance(timeid, int):
            time = timeid
        else:
            time = _timeid2index(timeid=timeid, basis=start, pyr=pyr)
        starting[index] = time
        values[index] = value
        ending[index] = len(time_series)
        if index > 0:
            ending[index - 1] = time
    for index in range(nummod):
        for time in range(starting[index], ending[index]):
            time_series[time] = values[index]
    return time_series




def repr_table(cols, header=None):


    if header is None and isinstance(cols, TimeSeries):
        print(cols.__repr__())
        return

    if header is not None and isinstance(cols, TimeSeries):
        print(header.__repr__())
        print(cols.__repr__())
        return

    if len(cols) > 1:
        for xcol in cols[1:]:
            verify_eq_time_range(cols[0], xcol)

    len_timeid = len(cols[0].end.__repr__())
    fmt_timeid = '{:<' + '{:d}'.format(len_timeid) + 's}'

    if header is None:
        len_number = 0
    else:
        len_number = 0
        for row in header:
            for element in row:
                len_number = max(len_number, len(element))

    for xcol in cols:
        for element in xcol:
            len_number = max(len('{:1.2f}'.format(element)), len_number)

    fmt_number = ' {:' + '{:d}'.format(len_number) + '.2f}'
    fmt_header = ' {:>' + '{:d}'.format(len_number) + 's}'

    if cols[0].pyr == 1:
        xmajor, = cols[0].start
        xminor = 0
    else:
        xmajor, xminor = cols[0].start

    txt = []
    isfirst = True
    for row in header:
        if isfirst is True:
            header = fmt_timeid.format('t')
            isfirst = False
        else:
            header = fmt_timeid.format(' ')
        for element in row:
            header += fmt_header.format(element)
        txt.append(header)

    txt.append('-' * len_timeid + '------' + '-' * len_number * len(cols))

    for time, _ in enumerate(cols[0]):
        if cols[0].pyr == 1:
            timeid = (xmajor,)
        else:
            timeid = (xmajor, xminor)
        txtrow = fmt_timeid.format(timeid.__repr__())
        for xcol in cols:
            txtrow += fmt_number.format(xcol[time])
        txt.append(txtrow)
        if cols[0].pyr == 1:
            xmajor += 1
        else:
            xminor += 1
            if xminor == cols[0].pyr:
                xminor = 0
                xmajor += 1

    return '\n'.join(txt)



def cfloplot(cflo):

    len_timeid = len(cflo.end.__repr__())
    fmt_timeid = '{:<' + '{:d}'.format(len_timeid) + 's}'

    len_number = 0
    for value in cflo:
        len_number = max(len_number, len('{:1.2f}'.format(value)))

    fmt_number = ' {:' + '{:d}'.format(len_number) + '.2f}'
    fmt_header = ' {:>' + '{:d}'.format(len_number) + 's}'

    if cflo.pyr == 1:
        xmajor, = cflo.start
        xminor = 0
    else:
        xmajor, xminor = cflo.start

    maxval = max(abs(cflo))
    if maxval == 0:
        maxval = 1


    width = 20

    txt = []
    txtrow = fmt_timeid.format("time") + fmt_header.format('value')
    txtrow += " +" + "-" * (width - 2) + "+" + "-" * (width - 2) + "+"
    txt.append(txtrow)

    for value in cflo:

        if cflo.pyr == 1:
            timeid = (xmajor)
        else:
            timeid = (xmajor, xminor)

        txtrow = fmt_timeid.format(timeid.__repr__())
        txtrow += fmt_number.format(value)

        # fmt_row = "                    *                    "
        xlim = int(width * abs(value / maxval))
        if value < 0:
            txtrow += " " + " " * (width - xlim) + '*' * (xlim)
        elif value > 0:
            txtrow += " " + " " * (width - 1) + "*" * (xlim)
        else:
            txtrow += " " + " " * (width - 1) + '*'

        txt.append(txtrow)

        if cflo.pyr == 1:
            xmajor += 1
        else:
            xminor += 1
            if xminor == cflo.pyr:
                xminor = 0
                xmajor += 1
    print('\n'.join(txt))

def combine(array1, array2):
    print(array1)
    array3 = []
    minimum = min(len(array1),len(array2))
    for x in range(0,minimum):
        array3.append(array1[x] + array2[x])
    if(len(array1)<len(array2)):
        for x in range(minimum,len(array2)):
            array3.append(array2[x])
    else:
        for x in range(minimum,len(array1)):
            array3.append(array1[x])

    return array3

def substract(array1, array2):
    print(array1)
    array3 = []
    minimum = min(len(array1),len(array2))
    for x in range(0,minimum):
        array3.append(array1[x] - array2[x])
    if(len(array1)<len(array2)):
        for x in range(minimum,len(array2)):
            array3.append(array2[x])
    else:
        for x in range(minimum,len(array1)):
            array3.append(array1[x])

    return array3

def pv(interest,time,cfd):
    pv = cfd[time]/((1+(interest/100))**time)
    temp = cfd[0]
    cfd[time] = 0
    cfd[0] = pv + temp

    return pv

def fw(interest,time,cfd):
    fw = cfd[time]*((1+(interest/100))**time)
    temp = cfd[len(cfd)-1]
    cfd[time] = 0
    cfd[len(cfd)-1] = fw + temp

    return fw

def startPlot(period):
    plot = []
    for i in range(0, period):
        plot.append(0)

    return plot


