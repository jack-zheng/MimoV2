import re
import logging
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
sys.path.append('./..')
from project import db, app, models


def parse_task_time(line):
    """
        give a line string, return task context and time.
    """
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


def time_plus12(time):
    """
    if time format is 10:00-11.00 keep as before,
    if time format is 2.00-3.00, transfer to 14.00-15.00
    :param time:
    :return:
    """
    timelist = []
    split01 = time.split('-')
    for sub in split01:
        split02 = sub.split('.')
        timelist.append(split02[0])
        timelist.append(split02[1])
    if int(timelist[0]) < 9:
        timelist[0] = str(int(timelist[0]) + 12)
    if int(timelist[2]) < 9:
        timelist[2] = str(int(timelist[2]) + 12)
    return timelist[0] + '.' + timelist[1] + '-' + timelist[2] + '.' + timelist[3]


def time_zone_minus_8(time):
    """
    transfer to utc time, lcoal time is GTM(+8)
    :param time:
    :return:
    """
    timelist = []
    split01 = time.split('-')
    for sub in split01:
        split02 = sub.split('.')
        timelist.append(split02[0])
        timelist.append(split02[1])
    timelist[0] = str(int(timelist[0]) - 8)
    timelist[2] = str(int(timelist[2]) - 8)
    return timelist[0] + '.' + timelist[1] + '-' + timelist[2] + '.' + timelist[3]


def parse_time(time):
    times = time.split('-')
    period_time = []
    for sub in times:
        t = datetime.strptime(sub, '%H.%M')
        period_time.append(t)
    return period_time


def parse_date(line):
    """
        check if this line is a date line, if yes return parsed datetime, else return ''
    """
    line = line.replace(" ", "")
    ret = re.search(r'\d{1,2}-\d{1,2}', line)
    if ret is not None and len(line) <= 5:
        return ret.group(0)
    else:
        return ""


def insert_to_db(daynode, release):
    timestamp = datetime.strptime(daynode.get('timestamp'), "%Y-%m-%d") + timedelta(hours=-8)
    release = release
    tasks = daynode.findall('task')
    for task in tasks:
        title = task.text
        timeperiod = task.find('time').text
        time = float(task.find('time').find('minutes').text)
        tmp = models.Task(title=title, timestamp=timestamp,\
                          timeperiod=timeperiod, time=time, release=release)
        db.session.add(tmp)
    db.session.commit()


def to_day_element(tasks):
    """
        input:
            task_detail sample: [17-01-01, [task_name, time_period] ...]
        return:
            Element obj show as
            <day timestamp='2017-01-01'>
                <task>
                    do something
                    <time>
                        12.00-13.00
                        <minutes>60</minutes>
                    </time>
                </task>

                <task...>
            </day>
    """
    daynode = ET.Element('day')

    # set day
    date_time = datetime.strptime(tasks[0], '%y-%m-%d')
    datetimestr = date_time.strftime('%Y-%m-%d')
    daynode.set('timestamp', datetimestr)
    del tasks[0]

    for task in tasks:       
         # set task
        tasknode = ET.Element('task')
        tasknode.text = task[0]

        # set time detail
        timenode = ET.SubElement(tasknode, 'time')
        timestr = time_plus12(task[1])
        timestr = time_zone_minus_8(timestr)
        timenode.text = timestr

        # set minutis
        period = parse_time(timestr)
        minutestr = (period[1] - period[0]).seconds/60
        minutesnode = ET.SubElement(timenode, 'minutes')
        minutesnode.text = str(minutestr)

        # tmp work around, most stable way is fix the logic miss of parse time


        daynode.append(tasknode)

    return daynode


def write_to_xml(filename, xmlelement):
    """
        write passed context to xml file
    """
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

        @classmethod
        def setUpClass(cls):

            print("invoke setupclass")
            app.config['TESTING'] = True
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath('.'), 'test.db')
            db.create_all()

        def setUp(self):
            files = os.listdir('.')
            for file in files:
                if file.endswith('test.xml'):
                    os.remove(file)
                    logging.warning('========== remove file: %s ==========' % file)
                    
        def test_to_date_element(self):
            ret = to_day_element(["17-01-01",["task01", "12.00-13.00"], ["task02", "1.00-1.30"]])
            self.assertEqual(len(ret.getchildren()), 2)
            self.assertEqual("2017-01-01", ret.get('timestamp'))
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
            """
                when blank line and unmatch line passed in, none type obj return
            """
            ret = parse_task_time("asdf:adsf")
            self.assertEqual(None, ret)

            ret = parse_task_time('\n')
            self.assertEqual(None, ret)

        def test_insert_to_db(self):
            daynode = ET.Element('day')
            daynode.set('timestamp', '2017-4-5')

            # add multiple task node to day
            tasknode01 = ET.SubElement(daynode, 'task')
            tasknode01.text = 'task01'
            timenode01 = ET.SubElement(tasknode01, 'time')
            timenode01.text = '1.00-2.00'
            minutenode01 = ET.SubElement(timenode01, 'minutes')
            minutenode01.text = '60.0'

            # add multiple task node to day
            tasknode02 = ET.SubElement(daynode, 'task')
            tasknode02.text = 'task02'
            timenode02 = ET.SubElement(tasknode02, 'time')
            timenode02.text = '1.00-1.20'
            minutenode02 = ET.SubElement(timenode02, 'minutes')
            minutenode02.text = '30.0'
            insert_to_db(daynode, '1708')

            # assert count == 2
            ret = models.Task.get_all()
            self.assertEqual(len(ret), 2)

        def test_time_plus12(self):
            time01 = '12.00-13.00'
            time02 = '1.00-2.00'
            time03 = '1.10-1.20'
            ret01 = time_plus12(time01)
            self.assertEqual(time01, ret01)
            ret02 = time_plus12(time02)
            self.assertEqual(ret02, '13.00-14.00')
            ret03 = time_plus12(time03)
            self.assertEqual(ret03, '13.10-13.20')

        def test_time_zone_minus_8(self):
            time01 = '12.00-13.00'
            ret01 = time_zone_minus_8(time01)
            self.assertEqual(ret01, '4.00-5.00')

        @classmethod
        def tearDownClass(cls):
            print("tear down class invoked");
            db.session.remove()
            db.drop_all()


    unittest.main()


