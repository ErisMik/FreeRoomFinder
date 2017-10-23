from urllib.request import urlopen
import bs4
from bs4 import BeautifulSoup
from FreeRoomFinderServer.models import Room, RoomBookedSlot
import re
import datetime
from time import sleep


class Scrape:
    url = "https://dalonline.dal.ca/PROD/fysktime.P_DisplaySchedule?s_term={year}{semester}&s_crn=&s_subj={subject}&s_numb=&n={index}&s_district={campus}"
    subjects = ["ACSC", "ANAT", "ARTC", "ARBC", "ARCH", "ASSC", "BIOC", "BIOE", "BIOL", "BMNG", "BUSI", "CANA", "CNLT",
                "CHEE", "CHEM", "CHIN", "CIVL", "CLAS", "COMM", "CH_E", "CPST", "CSCI", "CTMP", "CRWR", "DEHY", "DENT",
                "DMUT", "EMSP", "ERTH", "ECON", "ECED", "ECMM", "ENGI", "INWK", "ENGM", "ENGL", "ENSL", "ENVA", "ENVE",
                "ENVS", "ENVI", "EURO", "FILM", "FOSC", "FREN", "GWST", "GEOG", "GERM", "HESA", "HINF", "HLTH", "HPRO",
                "HSCE", "HAHP", "HSTC", "HIST", "HUCD", "INDG", "IENG", "INFX", "INFO", "INTE", "INTD", "IPHE", "ITAL",
                "JOUR", "KINE", "KING", "LAWS", "LEIS", "MRIT", "MGMT", "MGTA", "MARA", "MARI", "MATL", "MATH", "MECH",
                "MDLT", "MEDP", "MEDR", "MICI", "MINE", "MUSC", "NESC", "NUMT", "NURS", "OCCU", "OCEA", "ORAL", "PHDP",
                "PATH", "PERF", "PERI", "PHAC", "PHAR", "PHIL", "PHYC", "PHYL", "PHYT", "PLAN", "POLI", "PGPH", "PEAS",
                "PROS", "PSYR", "PSYO", "PUAD", "RADT", "REGN", "RELS", "RSPT", "RUSN", "SCIE", "SLWK", "SOSA", "SPAN",
                "STAT", "SUST", "THEA", "TYPR", "VISC"]
    campuses = ["Truro", "Halifax"]
    delay = 0.1

    @staticmethod
    def create_url(year, semester, subject, page, campus):
        """
        Creates a timetable url out of given parameters
        :param year: numerical, 4-digit year
        :param semester: "Fall", "Winter", or "Summer", case insensitive
        :param subject: four-letter subject code
        :param page: 0-indexed results page
        :param campus: "Halifax" or "Truro"
        :return: The formatted URL
        """

        if semester.lower() == "fall":
            year += 1
            semester = 10
        elif semester.lower == "winter":
            semester = 20
        elif semester.lower == "summer":
            semester = 30
        else:
            raise KeyError("Invalid semester")

        index = page * 20 + 1

        if campus.lower() == "halifax":
            campus = 100
        elif campus.lower() == "truro":
            campus = 200
        else:
            raise KeyError("Invalid campus")

        url = Scrape.url.format(year=year, semester=semester, subject=subject, index=index, campus=campus)
        print(url)
        return url

    @staticmethod
    def get_page(url):
        """
        Takes a url and returns a BeautifulSoup object of the page
        :param url:
        :return:
        """
        sleep(Scrape.delay) # prevent spamming the page
        page = urlopen(url)  # download the page
        soup = BeautifulSoup(page, "html5lib")  # convert it to a BeautifulSoup data structure
        return soup

    @staticmethod
    def page_to_rooms(page, year, semester):
        """
        Takes a page, scrapes all room information from it, and registers it in the database.
        :param page: The page to scrape, as a BeautifulSoup object
        :param year: The real year, to be written in the database
        :param semester: The semester, to be written in the database
        :return: The number of rooms processed
        """

        num_rooms_found = 0

        body = page.body
        pagebodydiv = body.find("div", class_="pagebodydiv", recursive=True)
        tables = pagebodydiv.find_all("table", class_="dataentrytable", recursive=True)
        if not tables:  # the results table is blank
            return 0
        try:
            table = tables[1]  # get the second dataentrytable, which contains the courses
        except IndexError:
            return 0
        rows = table.find_all("tr")

        # the first two rows are headers, which we ignore
        rows.pop(0)
        rows.pop(0)

        while rows:
            header = rows.pop(0)  # get the row with the course name
            course = header.find("td", class_="detthdr").find("b").string  # course name
            while rows and not rows[0].get("valign"):  # iterate over the rows with room info and notices
                row = rows.pop(0)
                if not row:
                    continue

                # for multirow entries defined by <br>s, separate them into individual rows
                raw_columns = row.find_all("td")
                columns = []
                for col in raw_columns:
                    column = []
                    root = col
                    if "<p " in str(col.contents) or "<b " in str(col.contents):
                        root = col.contents[0]
                    for i, tag in enumerate(root.contents):
                        if "<br" in str(tag):  # if the tag is a line break
                            if i == 0 or str(root.contents[i-1]).strip() == "":  # and it is the first, tag or the previous tag was blank
                                column.append(tag)  # then append a single line break
                            if i+1 != len(root.contents) and "<br" in str(root.contents[i+1]): # and the next tag is a line break
                                column.append(tag)  # then append a single line break
                        elif str(tag).strip() == "":  # if the tag is empty
                            pass  # then do nothing
                        else:  # if the tag is not a line break
                            column.append(tag)  # then append it
                    columns.append(column)
                subrows = []
                while True:
                    at_least_one_not_empty = False
                    subrow = []
                    for col in columns:
                        if col:
                            tag = col.pop(0)
                            subrow.append(tag)
                            at_least_one_not_empty = True
                        else:
                            subrow.append("")
                    subrows.append(subrow)
                    if not at_least_one_not_empty:
                        break

                ignore_next_subrow = False  # some courses are in a certain room only on Dec 5, if we find a message saying the next booking is only that day, we want to ignore it

                for subrow in subrows:

                    if ignore_next_subrow:
                        ignore_next_subrow = False
                        continue

                    # detect days and times
                    days = []
                    time = ""
                    room = ""

                    for value in subrow:
                        if type(value) == bs4.element.NavigableString or type(value) == str:
                            s = str(value)
                        elif type(value) == bs4.element.Tag:
                            s = value.text
                        else:
                            raise ValueError("actual type: {}".format(type(value)))

                        if "*** 05-DEC-2017 - 05-DEC-2017 ***" in s:
                            ignore_next_subrow = True
                            continue  # we want to ignore /this/ subrow too, since rows with this message don't have a course listed

                        if re.match(r"^([A-Z])$", s):  # day: single character
                            days.append(s)
                        elif re.match(r"^\d{4}-\d{4}", s):  # time: is in the format ####-#### with anything after it
                            time = s[:10] # if multiple time slots, the first is most important
                        elif len(s) > 20:
                            room = s
                            break  # room is last object we want; don't want to overwrite it with prof's name

                    if not days or not time or not room:  # probably a header, not a room
                        continue

                    day_conversion = {
                        "M": "Monday",
                        "T": "Tuesday",
                        "W": "Wednesday",
                        "R": "Thursday",
                        "F": "Friday",
                    }

                    days = [day_conversion[day] for day in days]

                    start_time = {
                        "h": int(time[:2]),
                        "m": int(time[2:4])
                    }
                    end_time = {
                        "h": int(time[5:7]),
                        "m": int(time[7:])
                    }

                    # prettify room
                    room = room.replace("&nbsp", "")
                    room = re.sub(r"\*\*\*.+\*\*\*", "", room)  # remove *** messages like this ***

                    # register a room
                    split = room.split()
                    campus = split.pop(0)  # campus is the first word
                    number = split.pop()  # room number is usually the last word
                    room_obj, created = Room.objects.update_or_create(
                        campus=campus,
                        building=" ".join(split),
                        number=number
                    )
                    num_rooms_found += 1

                    # register a room booking for each weekday
                    for day in days:
                        slot = RoomBookedSlot(
                            start_time=datetime.time(start_time["h"], start_time["m"]),
                            end_time=datetime.time(end_time["h"], end_time["m"]),
                            occasion=course,
                            room=room_obj,
                            semester=semester,
                            year=year,
                            weekday=day
                        )
                        slot.save()

        return num_rooms_found

    @staticmethod
    def register_all_pages_in_subject(subject, year, semester, campus):
        """
        For a given year, semester, campus, and subject, register all room bookings for that subject.
        :param subject: The four-character subject code
        :param year: The four-digit year
        :param semester: The semester, in words: "Fall", "Winter", or "Spring"
        :param campus: The campus: "Truro" or "Halifax"
        :return: None
        """
        page_num = 0
        while True:
            page = Scrape.get_page(Scrape.create_url(year, semester, subject, page_num, campus))
            rooms_found = Scrape.page_to_rooms(page, year, semester)
            print("{} rooms found".format(rooms_found))
            if rooms_found == 0:
                break
            page_num += 1

    @staticmethod
    def register_all_subjects_in_semester_all_campuses(year, semester):
        for campus in Scrape.campuses:
            for subject in Scrape.subjects:
                Scrape.register_all_pages_in_subject(subject, year, semester, campus)
                print("{} done for {} in {} {}".format(subject, campus, semester, year))

    @staticmethod
    def register_all_subjects_in_semester(year, semester, campus):
        for subject in Scrape.subjects:
            Scrape.register_all_pages_in_subject(subject, year, semester, campus)
            print("{} done for {} in {} {}".format(subject, campus, semester, year))