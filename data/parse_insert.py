import re
import logging
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom


def parse_task_time(line):
    '''
        give a line string, return task context and time.
    '''
    stripret = "".join(line.split())
    p = re.compile(r'\d+[.:]\d{2}-\d+[.:]\d{2}')
    findret = p.findall(stripret)   
    if findret:
        formatstr = " ".join(line.split())
        timeregx = r'\d+[.:]\d{2}\s*-\s*\d+[.:]\d{2}'
        time = re.compile(timeregx).findall(formatstr)[0].replace(" ", "").replace(":", ".")
        taskcontext = re.sub(timeregx, "", formatstr).strip().replace(":", "")
        return [taskcontext, time]
    else:
        # log it if line can't be parse
        logging.warning("unparsed line: [%s]" % line)


def parse_time(time):
    '''
        time format: 12.00-13.00 or 1.00-2.00
        return cost time in minutes
    '''
    times = time.split('-')
    period_time = []
    for sub in times:
        if len(sub) == 5:
            # time format: 12.00
            t = datetime.strptime(sub, '%H.%M')
        else:
            t = datetime.strptime(sub+"PM", '%I.%M%p')
        period_time.append(t)
    return period_time

def parse_date(line):
    '''
        check if this line is a date line, if yes return parsed datetime, else return ''
    '''
    line = line.replace(" ", "")
    ret = re.search(r'\d{1,2}-\d{1,2}', line)
    if ret is not None and len(line) <= 5:
        return ret.group(0)
    else:
        return ""

def to_day_element(tasks):
    '''
        input:
            task_detail sample: [17-01-01, [task_name, time_period] ...]
        return:
            Element obj show as
            <day datetime='2017-01-01'>
                <task>
                    do something
                    <time>
                        12.00-13.00
                        <minutes>60</minutes>
                    </time>
                </task>

                <task...>
            </day>
    '''
    daynode = ET.Element('day')

    # set day
    date_time = datetime.strptime(tasks[0], '%y-%m-%d')
    datetimestr = date_time.strftime('%Y-%m-%d')
    daynode.set('datetime', datetimestr)
    del tasks[0]

    for task in tasks:       
         # set task
        tasknode = ET.Element('task')
        tasknode.text = task[0]

        # set time detail
        timenode = ET.SubElement(tasknode, 'time')
        timenode.text = task[1]

        # set minutis
        
        period = parse_time(task[1])
        minutestr = (period[1] - period[0]).seconds/60
        minutesnode = ET.SubElement(timenode, 'minutes')
        minutesnode.text = str(minutestr)

        daynode.append(tasknode)

    return daynode


def write_to_xml(filename, xmlelement):
    '''
        write passed context to xml file
    '''
    xmlpretty = prettify(xmlelement)
    with open(filename, 'w') as f:
        f.write(xmlpretty)



def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


if __name__ == '__main__':  
    import os
    import unittest

    class test(unittest.TestCase):
        
        def setUp(self):
            files = os.listdir('.')
            for file in files:
                if file.endswith('test.xml'):
                    os.remove(file)
                    logging.warning('========== remove file: %s ==========' % file)
                    
        def test_to_date_element(self):
            ret = to_day_element(["17-01-01",["task01", "12.00-13.00"], ["task02", "1.00-1.30"]])
            self.assertEqual(len(ret.getchildren()), 2)
            self.assertEqual("2017-01-01", ret.get('datetime'))
            self.assertEqual("task01", ret.find('task').text)

            self.assertEqual("12.00-13.00", ret.find('task').find('time').text)   
            self.assertEqual("60.0", ret.find('task').find('time').find('minutes').text)

            self.assertEqual("1.00-1.30", ret.findall('task')[1].find('time').text)
            self.assertEqual("task02", ret.findall('task')[1].text)
            self.assertEqual("30.0", ret.findall('task')[1].find('time').find('minutes').text)

        def test_write_to_xml(self):
            root = ET.Element('root')
            root.text = 'root'

            filename = "write_test.xml"
            write_to_xml(filename, root)

            # get file list and assert target file exit
            files = os.listdir('.')
            self.assertTrue(filename in files)

        def test_parse_task_time(self):
            '''
                when blank line and unmatch line passed in, none type obj return
            '''
            ret = parse_task_time("asdf:adsf")
            self.assertEqual(None, ret)

            ret = parse_task_time('\n')
            self.assertEqual(None, ret)            

    unittest.main()

'''  
    with open ('./release1708.txt', 'r', encoding="utf8") as f:
        lines = f.readlines()

    print('file name: %s' % f.name)
    yearstr = re.search(r'\d{4}', f.name).group(0)[:2]
    print('year: %s' % datetime.strptime(yearstr, '%y'))

    release_node = ET.Element('')
    for line in lines:
        datestr = isdate(line)
        if datestr:
            print('parsed date: %s' % datetime.strptime(datestr, '%m-%d').replace(year=int("20"+yearstr)))

        ret = parse_task_time(line)
        if ret:
            logging.warning('task: %s, time: %s' %(ret[0].encode('utf8'), ret[1].encode('utf8')))
            period = parse_time(ret[1])
            logging.warning('time period: %s, time cost/minutes: %s' % (period, (period[1] - period[0]).seconds/60))
'''

