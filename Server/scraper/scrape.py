from urllib.request import urlopen
import bs4
from bs4 import BeautifulSoup
from FreeRoomFinderServer.models import Room, RoomBookedSlot
import re
import datetime
from time import sleep

import sys

class ubc_Scrape:
    base_url = "https://courses.students.ubc.ca/cs/main?pname=subjarea&tname=subjareas&req=0"
    subject_url = "https://courses.students.ubc.ca/cs/main?pname=subjarea&tname=subjareas&req=1&dept={subject}"
    course_url = "https://courses.students.ubc.ca/cs/main?pname=subjarea&tname=subjareas&req=3&dept={subject}&course={cid}"
    section_url = "https://courses.students.ubc.ca/cs/main?pname=subjarea&tname=subjareas&req=5&dept={subject}&course={cid}&section={section}"

    subjects = ["AANB", "ACAM", "ADHE", "AFST", "AGEC", "ANAT", "ANSC", "ANTH", "APBI", "APPP", "APSC", "ARBC", "ARC", "ARCH", "ARCL",
               "ARST", "ARTH", "ARTS", "ASIA", "ASIC", "ASLA", "ASTR", "ASTU", "ATSC", "AUDI", "BA", "BAAC", "BABS", "BAEN", "BAFI",
                "BAHC", "BAHR", "BAIM", "BAIT", "BALA", "BAMA", "BAMS", "BAPA", "BASC", "BASD", "BASM", "BATL", "BAUL", "BIOC", "BIOF",
                "BIOL", "BIOT", "BMEG", "BOTA", "BRDG", "BUSI", "CAPS", "CCFI", "CCST", "CDST", "CEEN", "CELL", "CENS", "CHBE", "CHEM",
                "CHIL", "CHIN", "CICS", "CIVL", "CLCH", "CLST", "CNPS", "CNRS", "CNTO", "COEC", "COGS", "COHR", "COMM", "COMR", "CONS",
                "CPEN", "CPSC", "CRWR", "CSIS", "CSPW", "CTLN", "DANI", "DENT", "DERM", "DES", "DHYG", "DMED", "DSCI", "ECED", "ECON",
                "ECPS", "EDCP", "EDST", "EDUC", "EECE", "ELEC", "ELI", "EMBA", "ENDS", "ENGL", "ENPH", "ENPP", "ENVR", "EOSC", "EPSE",
                "ETEC", "EXCH", "EXGR", "FACT", "FEBC", "FHIS", "FIPR", "FISH", "FIST", "FMPR", "FMST", "FNEL", "FNH", "FNIS", "FOOD",
                "FOPR", "FRE", "FREN", "FRSI", "FRST", "FSCT", "GBPR", "GEM", "GENE", "GEOB", "GEOG", "GERM", "GPP", "GREK", "GRS", "GRSJ",
                "GSAT", "HEBR", "HESO", "HGSE", "HINU", "HIST", "HPB", "HUNU", "IAR", "IEST", "IGEN", "INDE", "INDO", "INDS", "INFO", "ISCI",
                "ITAL", "ITST", "IWME", "JAPN", "JRNL", "KIN", "KORN", "LAIS", "LARC", "LASO", "LAST", "LATN", "LAW", "LFS", "LIBE", "LIBR",
                "LING", "LLED", "LWS", "MATH", "MDVL", "MECH", "MEDD", "MEDG", "MEDI", "MGMT", "MICB", "MIDW", "MINE", "MRNE", "MTRL",
                "MUSC", "NAME", "NEST", "NEUR", "NRSC", "NURS", "OBMS", "OBST", "OHS", "ONCO", "OPTH", "ORNT", "ORPA", "OSOT", "PAED",
                "PATH", "PCTH", "PERS", "PHAR", "PHIL", "PHRM", "PHTH", "PHYL", "PHYS", "PLAN", "PLNT", "POLI", "POLS", "PORT",
                "PSYC", "PSYT", "PUNJ", "RADI", "RELG", "RES", "RGLA", "RHSC", "RMST", "RSOT", "RUSS", "SANS", "SCAN", "SCIE", "SEAL",
                "SGES", "SLAV", "SOAL", "SOCI", "SOIL", "SOWK", "SPAN", "SPHA", "SPPH", "STAT", "STS", "SURG", "SWED", "TEST", "THTR",
                "TIBT", "TRSC", "UDES", "UFOR", "UKRN", "URO", "URST", "URSY", "VANT", "VGRD", "VISA", "VRHC", "VURS", "WOOD",
                "WRDS", "WRIT", "ZOOL"]
    day_conversion = {
        "Mo": "Monday",
        "mo": "Monday",
        "Tu": "Tuesday",
        "tu": "Tuesday",
        "We": "Wednesday",
        "we": "Wednesday",
        "Th": "Thursday",
        "th": "Thursday",
        "Fr": "Friday",
        "fr": "Friday",
        "Sa": "Saturday",
        "sa": "Saturday",
        "Su": "Sunday",
        "su": "Sunday",
    }
    delay = 0.00

    @staticmethod
    def section_to_rooms(page, subject, course, section):
        """
        """
        print("~"+subject+" "+course+" "+section, file=sys.stderr)
        room_found = False
        body = page.body
        table = body.find("table", class_="table-striped", recursive=True)
        tbody = table.find("tbody", recursive=True)
        rows = tbody.find_all("tr", recursive=True)
        # print(rows, file=sys.stderr)

        for row in rows:
            row = str(row).split("<td>")
            for x in range(len(row)):
                row[x] = row[x].strip().strip("</td>").strip()

            row.pop(0)
            if len(row) < 2 or not row[4] or "No Scheduled Meeting" in row[4] or "To Be" in row[4]:
                continue

            days = row[1].split()
            # print(row, file=sys.stderr)
            days = [ubc_Scrape.day_conversion[day[:2]] for day in days]

            start_time = {
                "h": int(row[2].split(":")[0]),
                "m": int(row[2].split(":")[1])
            }
            end_time = {
                "h": int(row[3].split(":")[0]),
                "m": int(row[3].split(":")[1])
            }

            roomnum = row[5].split(">")[1].split("<")[0]

            # register a room
            room_obj, created = Room.objects.update_or_create(
                university="ubc",
                campus="Vancouver",
                building=row[4],
                number=roomnum
            )
            room_found = True

            # TODO: Fix semester stuff
            # register a room booking for each weekday
            for day in days:
                if "1" in row[0]:
                    slot = RoomBookedSlot(
                        university="ubc",
                        start_time=datetime.time(start_time["h"], start_time["m"]),
                        end_time=datetime.time(end_time["h"], end_time["m"]),
                        occasion=subject+" "+course+" "+section,
                        room=room_obj,
                        semester="Fall",
                        year=2017,
                        weekday=day
                    )
                    slot.save()
                if "2" in row[0]:
                    slot = RoomBookedSlot(
                        university="ubc",
                        start_time=datetime.time(start_time["h"], start_time["m"]),
                        end_time=datetime.time(end_time["h"], end_time["m"]),
                        occasion=subject+" "+course+" "+section,
                        room=room_obj,
                        semester="Winter",
                        year=2017,
                        weekday=day
                    )
                    slot.save()

        if room_found:
            return 1
        else:
            return 0

    @staticmethod
    def course_to_rooms(page, subject, course):
        """
        """
        sections = []
        rooms_found = 0
        body = page.body
        table = body.find("table", class_="table table-striped section-summary", recursive=True)
        tbody = table.find("tbody", recursive=True)
        rows = tbody.find_all("tr", recursive=True)

        for row in rows:
            data = row.find("a", recursive=True)
            if not data is None and not "Comments" in str(data):
                sections.append(data.text.split()[-1])
                # break  ##

        for section in sections:
            url = ubc_Scrape.section_url.format(subject=subject, cid=course, section=section)
            page = ubc_Scrape.get_page(url)
            rooms_found += ubc_Scrape.section_to_rooms(page, subject, course, section)

        return rooms_found

    @staticmethod
    def subject_to_rooms(page, subject):
        """
        """
        courses = []
        rooms_found = 0
        body = page.body
        table = body.find("table", class_="table", recursive=True)
        tbody = table.find("tbody", recursive=True)
        rows = tbody.find_all("tr", recursive=True)

        for row in rows:
            data = row.find("a", recursive=True)
            courses.append(data.text.split()[-1])

        for course in courses:
            url = ubc_Scrape.course_url.format(subject=subject, cid=course)
            page = ubc_Scrape.get_page(url)
            rooms_found += ubc_Scrape.course_to_rooms(page, subject, course)

        return rooms_found

    @staticmethod
    def get_page(url):
        """
        Takes a url and returns a BeautifulSoup object of the page
        :param url:
        :return:
        """
        sleep(ubc_Scrape.delay) # prevent spamming the page
        page = urlopen(url)  # download the page
        soup = BeautifulSoup(page, "html5lib")  # convert it to a BeautifulSoup data structure
        return soup

    @staticmethod
    def register_subject(subject, year, semester, campus):
        """
        For a given year, semester, campus, and subject, register all room bookings for that subject.
        :param subject: The four-character subject code
        :param year: The four-digit year
        :param semester: The semester, in words: "Fall", "Winter", or "Spring"
        :param campus: The campus: "Truro" or "Halifax"
        :return: None
        """
        url = ubc_Scrape.subject_url.format(subject=subject)
        page = ubc_Scrape.get_page(url)
        rooms_found = ubc_Scrape.subject_to_rooms(page, subject)
        print("{} rooms found".format(rooms_found))

    @staticmethod
    def register_all_subjects_in_semester_all_campuses(year, semester):
        for campus in ubc_Scrape.campuses:
            for subject in ubc_Scrape.subjects:
                ubc_Scrape.register_subject(subject, year, semester, campus)
                print("{} done for {} in {} {}".format(subject, campus, semester, year))

    @staticmethod
    def register_all_subjects_in_semester(year, semester, campus):
        for subject in ubc_Scrape.subjects:
            ubc_Scrape.register_subject(subject, year, semester, campus)
            print("{} done for {} in {} {}".format(subject, campus, semester, year))

###############################################################################################################################

class Scrape:
    day_conversion = {**ubc_Scrape.day_conversion,}

    @staticmethod
    def register_all_pages_in_subject(university, subject, year, semester, campus):
        if "ubc" in university:
            ubc_Scrape.register_all_pages_in_subject(subject, year, semester, campus)

    @staticmethod
    def register_all_subjects_in_semester_all_campuses(university, year, semester):
        if "ubc" in university:
            ubc_Scrape.register_all_subjects_in_semester_all_campuses(subject, year, semester)

    @staticmethod
    def register_all_subjects_in_semester(university, year, semester, campus):
        if "ubc" in university:
            ubc_Scrape.register_all_subjects_in_semester(year, semester, campus)
