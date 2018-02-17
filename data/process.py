import xml.etree.ElementTree as ET
import parse_insert as pi
import os
import re

# read process file
processfiles = [file for file in os.listdir('.') if file.endswith('.txt') and file.startswith('release')]

for file in processfiles:
    with open(file, 'r', encoding='utf8') as f:
        lines  = f.readlines()
        build = re.search(r'\d{4}', f.name).group(0)
        year = build[:2]
        print("parsed build %s, year %s" % (build, year))

    # define root node 
    releasenode = ET.Element('release')
    releasenode.set('build', build)


    dayinfo = []
    for line in lines:
        datestr = pi.parse_date(line)
        if datestr:
            datestr = year + "-" + datestr
            if dayinfo:
                # when line is date and there is a day info stored, flush it and init dayinfo list
                daynode = pi.to_day_element(dayinfo)
                releasenode.append(daynode)
                del dayinfo[:]
                dayinfo.append(datestr)
            else:
                dayinfo.append(datestr)
                print("date: %s, push to dayifo list" % datestr)
        else:
            # if not a date line, then should be task line, parse it
            parsed_line = pi.parse_task_time(line)
            if parsed_line:
                dayinfo.append(parsed_line)

    with open(build + ".xml", 'w') as f:
        f.write(pi.prettify(releasenode))
                


        
