
# coding: utf-8

# In[1]:


# Changelog
# V4: Separates the userpw into 2 files: userpw.txt and details.txt
# userpw.txt contains username and password
# details.txt contains date, start_time, end_time and cobooker
# V5: Accounts for situation where there is no room
# Stores the data from an element as you iterate through the schools
# Process only after no rooms booked
# Attempts to book a new room for you based on the highest availability


# In[2]:

# Imports selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from datetime import datetime
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# In[3]:

def main():
    school_list = ["Lee Kong Chian School of Business","School of Accountancy","School of Economics/School of Social Sciences",
                   "School of Information Systems","School of Law/Kwa Geok Choo Law Library"]

    school_abbrev_list = ["LKCSB","SOA","SOE","SIS","SOL"]
    
    
    #new_order = input("Please input your preference for the schools in the format 01234.")
    
    # new_order = "32104"

    # print(school_list)
    
    # In[4]:


    try:
    
        print("Obtaining user details and booking details from config files...")
    
        # Obtains user/pw from a text file

        userpw_path = os.path.join(os.path.dirname(__file__), 'userpw.txt')
        details_path = os.path.join(os.path.dirname(__file__), 'details.txt')

        info = {}
        with open(userpw_path,'r',errors = 'ignore') as f:
            for line in f:
                line = line.rstrip("\n")
                line = line.split("=")
                info[line[0]] = line[1]

        # Obtains booking details from a text file
        details = {}
        with open(details_path,'r',errors = 'ignore') as f:
            for line in f:
                line = line.rstrip("\n")
                line = line.split("=")
                details[line[0]] = line[1]
                
    except:
        
        # Creates a new text file with username and password
        
        print("No existing config found. Creating new config file...")
        
        info = {}
        with open("./userpw.txt","w",errors = 'ignore') as f:
            info["username"] = input("Please enter your username:")
            info["password"] = input("Please enter your password:")
            userpw = "username=" + info["username"] + "\n" + "password=" + info["password"]
            f.write(userpw)
        
        details = {}
        
        with open("./details.txt","w",errors = 'ignore') as f2:
        
            detail_string = ""
            
            print("The schools you can book from are as follows:")
            for i in range(len(school_list)):
                print(f"[{i}] - {school_list[i]}")

            
        # Creates a new text file with the details
            details["preference"] = input("Please state your preference for schools in the format 01234: ")
            details["date"] = input("Which date do you want to book? Please enter in the format DD-MMM-YYYY: ")
            details["start_time"] = input("What is your desired start time for your booking? Please enter in the format 24hr HH:MM: ")
            details["end_time"] = input("What is the desired end time for your booking? Please enter in the format 24hr HH:MM: ")
            details["co_booker"] = input("You will need a co-booker for booking your GSR. Please enter the full name of your co-booker. ")
            
            # Adds into a list
            for detail in details.keys():
                detail_string += detail + "=" + details[detail] + "\n"
                
            f2.write(detail_string)
                
    # Reorders lists based on preference
    
    new_list = []

    for num in details["preference"]:
        new_list.append(school_list[int(num)])
            
    school_list = new_list

    new_list = []

    for num in details["preference"]:
        new_list.append(school_abbrev_list[int(num)])
        
    school_abbrev_list = new_list
    # print(school_list)

    print("The order you have selected is:")
    
    for school in school_list:
        print(school)

    # In[5]:


    time.sleep(2)

    # Opens the chrome webdriver path
    # options = webdriver.ChromeOptions()
    # options.binary_location = resource_path('.')
    path = resource_path("./driver/chromedriver.exe")
    driver = webdriver.Chrome(path)
    # driver = webdriver.Chrome(chrome_options=options)

    # Starts the driver for the stated url
    driver.get("https://fbs.intranet.smu.edu.sg/home")

    # Makes driver wait 5s for elements unavailable
    driver.implicitly_wait(10)
    
    wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input#userNameInput.text.fullWidth")))
    # Enters Username and Password
    driver.find_element_by_css_selector("input#userNameInput.text.fullWidth").click()
    driver.find_element_by_css_selector("input#userNameInput.text.fullWidth").send_keys(info["username"])

    driver.find_element_by_css_selector("input#passwordInput.text.fullWidth").click()
    driver.find_element_by_css_selector("input#passwordInput.text.fullWidth").send_keys(info["password"])

    driver.find_element_by_css_selector("span#submitButton.submit").click()


    # In[6]:


    has_booked = False
    booking_dict = {}

    for school in school_list:
        
        # Attempts to book for different schools
        print("Currently trying: " + school)

        
        buildings = ["Administration Building","Campus Open Spaces - Events/Activities",
                                     "Concourse - Room/Lab", "Lee Kong Chian School of Business",
                                     "Li Ka Shing Library", "Prinsep Street Residences", "School of Accountancy",
                                     "School of Economics/School of Social Sciences","School of Information Systems",
                                     "School of Law/Kwa Geok Choo Law Library", "SMU Connexion"]

         # To tailor to scraping different schools
        buildings_index = buildings.index(school)
        
        driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))
        driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))
        
        # Selects date
        print("Selecting date...")
        driver.find_element_by_id("DateBookingFrom_c1_textDate").click()
        driver.find_element_by_css_selector(f"div.day[title='{details['date']}']").click()
        
        # Extracts start time from list
        
        start_time_list = driver.find_element_by_id("TimeFrom_c1_ctl04").text
        start_time_list = start_time_list.split("\n")
            
        start_time_index = start_time_list.index(details["start_time"])+1
        
        # Extracts end time from list
        
        end_time_list = driver.find_element_by_id("TimeTo_c1_ctl04").text
        end_time_list = end_time_list.split("\n")

        end_time_index = end_time_list.index(details["end_time"])+1
        
        # Selects start and end time
        
        time.sleep(2)
        driver.find_element_by_xpath(f"""//*[@id="TimeFrom_c1_ctl04"]/option[{start_time_index}]""").click()
        time.sleep(2)
        driver.find_element_by_xpath(f"""//*[@id="TimeTo_c1_ctl04"]/option[{end_time_index}]""").click()
        
        print("Selecting building...")
        
        time.sleep(2)
        
        # Clicks building name
        driver.find_element_by_id('DropMultiBuildingList_c1_panelInputs').click() 

        time.sleep(2)

        # Building name will be a list of elements, in this case 8 is information systems
        driver.find_element_by_id(buildings_index).click()

        time.sleep(2)
        #Clicks ok button after selecting building
        driver.find_element_by_xpath("//*[@id='DropMultiBuildingList_c1_panelTreeView']/input[1]").click()

        #Selects facility types
        print("Selecting facility types...")
        
        time.sleep(2)
        driver.find_element_by_id('DropMultiFacilityTypeList_c1').click()

        # Clicks on GSR, has to account for School of Law differently due to different types of facilities
        if school == "School of Law/Kwa Geok Choo Law Library":
            driver.find_element_by_xpath("""/html/body/div[2]/form/span[1]/span/span/div/div/div/div/div/span/span/span/div/div/div[1]/div[8]/div/div/span/div/table/tbody/tr/td/table/tbody/tr/td/div/div/div/label[3]/span""").click()
        else:
            driver.find_element_by_xpath("""/html/body/div[2]/form/span[1]/span/span/div/div/div/div/div/span/span/span/div/div/div[1]/div[8]/div/div/span/div/table/tbody/tr/td/table/tbody/tr/td/div/div/div/label[2]/span""").click()


        time.sleep(2)
        
        # Clicks out of the box
        driver.find_element_by_xpath("//*[@id='CheckAvailability']/span").click()

        time.sleep(2)
        
        # Clicks on check availability
        availability = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='CheckAvailability']/span")))

        driver.find_element_by_xpath("//*[@id='CheckAvailability']/span").click()

        # Checks if there are available rooms for current building
        print(" ")
        
        print(f"Checking for available rooms in {school}...")
        
        # Temporarily stores the bookings for processing later
        wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.scheduler_bluewhite_event.scheduler_bluewhite_event_line0")))
        booking_list = driver.find_elements_by_css_selector("div.scheduler_bluewhite_event.scheduler_bluewhite_event_line0")
        
        booking_dict[school] = []
        
        for booking in booking_list:
            booking_dict[school].append(booking.get_attribute("title"))
        
        #Clicks on list button
        wait = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "BtnList")))
        driver.find_element_by_id("BtnList").click()
        
        # time.sleep(2)
        
        try:
            
            # Tries to see if there are any rooms available to book. 
            # If not, the script will continue to find from other schools
            
            driver.find_element_by_css_selector("#GridQuick_gv_ctl02_checkMultiple").click()
            
            print("Room found! Making booking...")
            # Clicks make booking
            time.sleep(10)
            driver.find_element_by_id("btnMakeBooking").click()
            
            # Enters purpose
            time.sleep(2)
            driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))
            
            time.sleep(5)
    #         purpose = WebDriverWait(driver, 10).until(EC.element_to_be_selected((By.CSS_SELECTOR, "input#bookingFormControl1_TextboxPurpose_c1.textbox")))
            driver.find_element_by_css_selector("input#bookingFormControl1_TextboxPurpose_c1.textbox").send_keys("meeting")
            
            # Enters use type
            time.sleep(2)
            driver.find_element_by_xpath("""//*[@id="bookingFormControl1_DropDownUsageType_c1"]/option[3]""").click()
            
            # Enters co-bookers
            time.sleep(5)
            driver.find_element_by_id("bookingFormControl1_GridCoBookers_ctl14").click()
            
            # Enters name
            time.sleep(5)
            driver.find_element_by_css_selector("input.textbox.watermark").click()
            time.sleep(2)
            driver.find_element_by_id("bookingFormControl1_DialogSearchCoBooker_searchPanel_textBox_c1").send_keys(f"{details['co_booker']}")
            time.sleep(2)
            driver.find_element_by_id("bookingFormControl1_DialogSearchCoBooker_searchPanel_textBox_c1").send_keys(Keys.ENTER)
            
            # Selects name
            time.sleep(2)
            driver.find_element_by_id("bookingFormControl1_DialogSearchCoBooker_searchPanel_gridView_gv_ctl02_checkMultiple").click()
            
            # Selects select to get out of window
            time.sleep(2)
            driver.find_element_by_id("bookingFormControl1_DialogSearchCoBooker_dialogBox_b1").click()
            
            # Ticks "I agree"
            time.sleep(2)
            driver.find_element_by_id("bookingFormControl1_TermsAndConditionsCheckbox_c1").click()
            
            # Confirms booking
            # driver.find_element_by_id("panel_UIButton2").click()
            
            has_booked = True
            
            pause = input("Please accept the booking:")
            
            
        except Exception as e:
            #print(e)
            print(f"No bookings in {school}. Continuing to other schools...")
        
        print(f"{has_booked} for has_booked")
        
        if has_booked == False:
        
            # Checks for schools checked for rooms so far
            
            print("Schools checked so far: ")
            current_index = school_list.index(school)
            for i in range(current_index+1):
                print(school_list[i])

            print(" ")
            
            # Lists schools left on the list that have yet to be tried
            if current_index < len(school_list) - 1:
                print("Schools left to try: ")
                for i in range(current_index+1,len(school_list)):
                    print(school_list[i])
                    
            if current_index != len(school_list) -1:
                # Refreshes the page if there are still schools to consider
                
                driver.refresh()

                print("Refreshing the page...")
                print(" ")
        
        else:
            # Happens when room is successfully booked.
            
            print("Your booking is complete!")
            print(f"Please remind {details['co_booker']} to accept the booking.")
            
            break    
        


    # In[7]:


    # If there are no available bookings,
    # Process data

    if has_booked == False:
        # Prints when there are no more schools left to find and there is no room booked.
        print("I'm sorry, but there are no available rooms for your specified requirements. :(")
        print("Please select another timeslot from the subsequent list of available timeslots.")
        print("Generating list of available timeslots...")

    overall_dict = {}
    temp_list = []
    for school in school_list:
        
        # Gets a list of facilities from the respective schools
        abbrev = school_abbrev_list[school_list.index(school)]

        facility_file = abbrev + "_GSR.csv"
        facility_path = resource_path("./facilities/"+ facility_file)
        facility_list = pd.read_csv(facility_path, delimiter = ',', header = 0, usecols = [1]).values.tolist()

        
        # Removes nested list from file
        for i in range(len(facility_list)):
            facility_list[i] = facility_list[i][0]
    #     print(facility_list)
        # Processes booking per school
        bookings_list = booking_dict[school]
        
        # Counter for facility list
        count = 0
        
    #     print(f"The length is : {len(facility_list)}")
        for booking in bookings_list:
            if "23:59" in booking:
                count += 1
            elif "not available" not in booking:
                booking = booking.split("\n")
    #             pause = input("")
    #             print(f"Booking is {booking} facility is {facility_list[count]}")
                facility = facility_list[count]
                booking_time = booking[0][booking[0].find(":")+2:]
    #             print(temp_list)
                if facility not in overall_dict:
                    overall_dict[facility] = [booking_time]
                else:
                    overall_dict[facility].append(booking_time)

    #print(overall_dict)
       


    # In[8]:


    def _get_empty_timeslots(list_of_booked_timings, date):
        
        """
        list_of_booked_timings -> list of booked timings 
        day -> string, 'Monday', .,..

        given list of booked timings in the format ['11:30-14:30', '15:00-19:00']
        return all the timings where the GSR is available, in the same format
       

        """
        day = datetime.strptime((details["date"]), '%d-%b-%Y').strftime('%A')
        
        #weekday 8.30 to 10.30
        #weekend 8.30 to 5
        
        list_of_available_timings = []
        
        list_of_booked_timings.sort()
        
        for i in range(len(list_of_booked_timings)-1):
            time_range1 = list_of_booked_timings[i].split('-')
            start_time1 = int(time_range1[0].replace(':', ""))
            end_time1 = int(time_range1[1].replace(':',""))
            
            
            time_range2 = list_of_booked_timings[i+1].split('-')
            start_time2 = int(time_range2[0].replace(':', ""))
            end_time2 = int(time_range2[1].replace(':',""))
            
            if i == 0:
                check = start_time1 - 800
                if check > 0:
                    first = '08:30' + '-' + time_range1[0]
                    list_of_available_timings.append(first)
                   
                    
            if i == len(list_of_booked_timings)-2: 
                check = 2230 - end_time2
                if check > 0: 
                    if day == 'Saturday' or day == 'Sunday':
                        last = time_range2[1] + '-' + '17:00'
                        list_of_available_timings.append(last)
                    else:
                        last = time_range2[1] + '-' + '22:30'
                        list_of_available_timings.append(last)
            
            if start_time2 - end_time1  > 0:
                add =  time_range1[1] + '-' + time_range2[0]
                list_of_available_timings.append(add)
            
        list_of_available_timings.sort()
            
        return list_of_available_timings

    def suitable_time(booking_time, available_time):
        """
        Checks if the booking time will fit into the available time
        
        Time should be input in the format hh:mm-hh:mm (24 hour)
        
        For example,
        
        For a booking time of 09:30-11:30:
        
        for the following available times:
        9:00-11:00 should return 09:30-11:00, 1.5 
        10:00-11:00 should return 10:00-11:00, 1
        10:00-12:00 should return 10:00-11:30, 1.5
        08:00-09:30 should return False
        12:00-13:00 should return False
        
        """
        
        # Splits booking time into start and end time
        
        booking_time_list = booking_time.split("-")
        booking_time_start = booking_time_list[0]
        booking_time_end = booking_time_list[1]    
        
        # Splits available time into start and end time
        
        available_time_list = available_time.split("-")
        available_time_start = available_time_list[0]
        available_time_end = available_time_list[1]
        
        if ((available_time_end <= booking_time_start and available_time_start <= booking_time_start) 
            or 
            (available_time_start >= booking_time_end and available_time_end >= booking_time_end)):
            
            # Returns false for available timings that are out of range
            return False
        
        elif available_time_start >= booking_time_start and available_time_end <= booking_time_end:
            
            # Returns the available timing as a whole if it is a subset of booking timing
            return available_time, get_half_hr_iterations(available_time) * 0.5
        
        else:
            
            result_time_start = max(available_time_start,booking_time_start)
            result_time_end = min(available_time_end,booking_time_end)
            result_time = result_time_start+"-"+result_time_end
            return result_time, get_half_hr_iterations(result_time) * 0.5
            
            
    def get_half_hr_iterations(time_range):
        """
        Given string of booking time-range eg '1030-1200', return the number of 30minutes interval 
        between them eg ['0800-1030', '1200-1400','1630-2230']
        
        hold_start_and_end_timings -> list of start and end timings
        
        time_object_1 & time_object_2 -> converts the start and end timings to datetime.time objects
        whether the day is a weekday or not. 8am to 1030pm
        
        start_booking_time_mins & end_booking_time_mins -> Convert the booking timings into minutes for calculation
        of the number of 30 minutes interval. e.g. 240 minutes -> 4 hours -> 8 thirty minute intervals

        """
        hold_start_and_end_timings = time_range.split('-')
        time_object_1 = datetime.strptime(hold_start_and_end_timings[0],'%H:%M').time()
        time_object_2 = datetime.strptime(hold_start_and_end_timings[1],'%H:%M').time()
        h1, m1, s1 = time_object_1.hour, time_object_1.minute, time_object_1.second
        h2, m2, s2 = time_object_2.hour, time_object_2.minute, time_object_2.second
        
        start_booking_time_mins = (m1 + 60*h1) 
        end_booking_time_mins = (m2 + 60*h2)
        
        return int((end_booking_time_mins - start_booking_time_mins)/60/0.5)


    # print(get_half_hr_iterations('08:30-12:30'))        

    # print(suitable_time("09:30-11:30","09:00-11:00"))
    # print(suitable_time("09:30-11:30","09:30-11:00"))
    # print(suitable_time("09:30-11:30","10:00-11:00"))
    # print(suitable_time("09:30-11:30","08:30-09:30"))
    # print(suitable_time("09:30-11:30","11:30-12:00"))
    # print(suitable_time("09:30-11:30","10:30-12:00"))

            


    # In[9]:


    available_dict = {}
    booking_time = details["start_time"] +"-"+ details["end_time"]

    for facility in overall_dict.keys():
        
        # Gets a list of available timings for each GSR
        available_timings = _get_empty_timeslots(overall_dict[facility],details["date"])
    #     print(f"{facility}:{available}")
        
        # Converts into a dict in the format:
        # Duration : [[GSR,Timing]]
        # eg. 2 : [[GSR 2-20,9-11:00],[GSR 3-37,10:00-12:00]]
        for timing in available_timings:
    #         print(booking_time,timing)
            if suitable_time(booking_time,timing) != False:
            # Checks if timing is suitable
                timing, duration = suitable_time(booking_time,timing)
                if duration not in available_dict:
                    available_dict[duration] = [[timing,facility]]
                else:
                    available_dict[duration].append([timing,facility])
                    
    #for available_time in sorted(available_dict.keys()):
    #    print(f"{available_time}, \n {available_dict[available_time]}")
    #    print(" ")


    # In[10]:

    #print(available_dict[sorted(available_dict.keys())[-1]][0])

    new_booking = available_dict[sorted(available_dict.keys())[-1]][-1]


    # In[11]:


    # Books based on new parameters

    room = new_booking[1]
    new_time = new_booking[0]
    start_time = new_time.split("-")[0]
    end_time = new_time.split("-")[1]
    
    print(f"New booking found at {room} at {new_time}")

    driver.refresh()

    driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))
    driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))

    # Selects date
    print("Selecting date...")
    driver.find_element_by_id("DateBookingFrom_c1_textDate").click()
    driver.find_element_by_css_selector(f"div.day[title='{details['date']}']").click()

    # Extracts start time from list

    start_time_list = driver.find_element_by_id("TimeFrom_c1_ctl04").text
    start_time_list = start_time_list.split("\n")

    start_time_index = start_time_list.index(start_time)+1

    # Extracts end time from list

    end_time_list = driver.find_element_by_id("TimeTo_c1_ctl04").text
    end_time_list = end_time_list.split("\n")

    end_time_index = end_time_list.index(end_time)+1

    # Selects start and end time

    time.sleep(2)
    driver.find_element_by_xpath(f"""//*[@id="TimeFrom_c1_ctl04"]/option[{start_time_index}]""").click()
    time.sleep(2)
    driver.find_element_by_xpath(f"""//*[@id="TimeTo_c1_ctl04"]/option[{end_time_index}]""").click()

    # Enters GSR 
    time.sleep(2)
    driver.find_element_by_xpath("""//*[@id="panel_SimpleSearch"]/div/div/span/input[2]""").click()
    # driver.find_element_by_xpath("""//*[@id="panel_SimpleSearch"]/div/div/span/input[2]""").click()
    driver.find_element_by_id("panel_SimpleSearch_c1").send_keys(room)
    time.sleep(2)
    GSR_search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "panel_buttonSimpleSearch")))
    driver.find_element_by_id("panel_buttonSimpleSearch").click()

    # Enters search availability
    # Clicks on check availability
    time.sleep(2)
    availability = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='CheckAvailability']/span")))
    driver.find_element_by_xpath("//*[@id='CheckAvailability']/span").click()


    # In[12]:


    #Clicks on list button
    driver.find_element_by_id("BtnList").click()
        

            
    # Tries to see if there are any rooms available to book. 
    # If not, the script will continue to find from other schools

    driver.find_element_by_css_selector("#GridQuick_gv_ctl02_checkMultiple").click()

    print("Room found! Making booking...")
    # Clicks make booking
    time.sleep(5)
    driver.find_element_by_id("btnMakeBooking").click()

    # Enters purpose
    time.sleep(2)
    driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))

    time.sleep(5)
    #         purpose = WebDriverWait(driver, 10).until(EC.element_to_be_selected((By.CSS_SELECTOR, "input#bookingFormControl1_TextboxPurpose_c1.textbox")))
    driver.find_element_by_css_selector("input#bookingFormControl1_TextboxPurpose_c1.textbox").send_keys("meeting")

    # Enters use type
    time.sleep(2)
    driver.find_element_by_xpath("""//*[@id="bookingFormControl1_DropDownUsageType_c1"]/option[3]""").click()

    # Enters co-bookers
    time.sleep(2)
    driver.find_element_by_id("bookingFormControl1_GridCoBookers_ctl14").click()

    # Enters name
    time.sleep(2)
    driver.find_element_by_css_selector("input.textbox.watermark").click()
    driver.find_element_by_id("bookingFormControl1_DialogSearchCoBooker_searchPanel_textBox_c1").send_keys(f"{details['co_booker']}")
    driver.find_element_by_id("bookingFormControl1_DialogSearchCoBooker_searchPanel_textBox_c1").send_keys(Keys.ENTER)

    # Selects name
    time.sleep(2)
    driver.find_element_by_id("bookingFormControl1_DialogSearchCoBooker_searchPanel_gridView_gv_ctl02_checkMultiple").click()

    # Selects select to get out of window
    time.sleep(2)
    driver.find_element_by_id("bookingFormControl1_DialogSearchCoBooker_dialogBox_b1").click()

    # Ticks "I agree"
    driver.find_element_by_id("bookingFormControl1_TermsAndConditionsCheckbox_c1").click()

    # Confirms booking
    # driver.find_element_by_id("panel_UIButton2").click()
    
if __name__ == '__main__':
    main()
    pause = input("Press Enter to exit once you have made the booking")

