import parse_insert as pi
import os
from datetime import datetime

# read process file
processfiles = [file for file in os.listdir('.') if file.endswith('.txt') and file.startswith('2017')]

for file in processfiles:
    with open(file, 'r', encoding='utf8') as f:
        lines  = f.readlines()
        release = f.name.split('.')[0].split('_')[1]

    year_str = '2017'
    date_str = ''

    for line in lines:
        print("line: %r" % line)
        parsed_date = pi.parse_date(line)
        if parsed_date:
            date_str = year_str + '-' + parsed_date
        else:
            # if not a date line, then should be task line, parse it
            parsed_line = pi.parse_task_time(line)
            if parsed_line:
                title = parsed_line[0]
                period = parsed_line[1].split('-')

                # transfer from str to datetime
                format_str = "%Y-%m-%d %H.%M"
                t1 = datetime.strptime(date_str + ' ' + period[0], format_str)
                t2 = datetime.strptime(date_str + ' ' + period[1], format_str)

                if t1.hour < 9:
                    t1 = pi.time_plus12(t1)

                if t2.hour < 9:
                    t2 = pi.time_plus12(t2)

                minutes = (t2 - t1).seconds/60

                # convert local time to utc time
                t1 = pi.time_zone_minus_8(t1)
                t2 = pi.time_zone_minus_8(t2)
                print('title: %s, t1: %s, t2: %s, mins: %s' % (title, t1.strftime(format_str), t2.strftime(format_str), minutes))
                pi.insert_to_db(title, release, minutes, t1, t2)
