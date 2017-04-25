from Tkinter import*
from xlrd import *
from tkFileDialog import askopenfilename
import tkMessageBox,re,time, docclass
from bs4 import BeautifulSoup
from urllib2 import urlopen, URLError
from ttk import Scrollbar
from selenium import webdriver

class GradesPredictor(Frame):
    def __init__(self, parent, color):
        self.color = color
        self.courses_xls = {}   #{course: [department,grade]}
        self.descriptions = {}  #{course: description}
        self.graded = []        # [graded courses]
        self.result = {}        # {course: [department, predicted grade]}
        Frame.__init__(self, parent,bg=self.color)
        self.parent = parent
        self.frame1 = Frame(self, bg=self.color)
        self.frame1.pack(fill=X)
        self.frame2 = Frame(self, bg=self.color)
        self.frame2.pack(pady=5, fill = X)
        self.frame3 = Frame(self, bg=self.color)
        self.frame3.pack(fill = X)
        self.frame3a = Frame(self, bg=self.color)
        self.frame3a.pack(fill = X)
        self.frame3b = Frame(self, bg=self.color)
        self.frame3b.pack(fill=X)
        self.frame3c = Frame(self, bg=self.color)
        self.frame3c.pack(fill = X,padx=10)
        self.frame4 = Frame(self, bg=self.color)
        self.frame4.pack(fill=X)
        self.frame4a = Frame(self, bg=self.color)
        self.frame4a.pack(fill=X)
        self.frame4b = Frame(self, bg=self.color)
        self.frame4b.pack(fill=X, padx=10)
        self.initUI()


    def initUI(self):
        self.parent.title("Guess My Grade! v1.0")
        self.pack(fill=BOTH, expand=True)

        heading = Label (self.frame1, text="Guess My Grade! v1.0", fg = "white", bg="royalblue4",font = ("Georgia",20,"bold"))
        heading.pack(fill=X)
        label1 = Label(self.frame2, text="Please upload your curriculum file with the grades:",fg="blue4",font = ("Georgia",14), bg=self.color)
        label1.pack(side = LEFT,fill = X,padx = 10)
        Button(self.frame2, text="Browse", bg="brown",fg="white",cursor='hand2',command=self.Browse,
               font=("Georgia",14),width=15).pack(side=LEFT,fill=X, padx=100,anchor=CENTER)

        divider = Label(self.frame3a, text="." * 500, bg=self.color)
        divider.pack(fill=X)
        label2 = Label(self.frame3b, text = "Enter URLs for course descriptions:",font = ("Arial",14),bg=self.color)
        label2.pack(padx=10,anchor = NW)
        self.descriptions_url = Text(self.frame3b, width=100, height=8, wrap=WORD, font='Calibri 11')
        self.descriptions_url.pack(padx=10,pady=3, anchor=NW)
        label3 = Label(self.frame3b, text = "Key:",font=("Arial",13,"bold"),bg=self.color)
        label3.pack(padx=10,anchor=NW)

        self.grades = ["A", "B", "C", "D", "F", "green4", "green1", "orange", "red", "black",'white','black','white','white','white']
        for i in range(5):
            i = Label(self.frame3c, text=self.grades[i],bg=self.grades[i+5],fg="white",font=("Georgia",14),width=8)
            i.pack(side=LEFT, padx = 5)
        Button(self.frame3c, text="Predict Grades", cursor='hand2', command=self.get_descriptions,
               bg="brown",fg="white",font=("Georgia",14),width=15).pack(side=LEFT, fill=X, padx=30,anchor=CENTER)

        divider = Label(self.frame4a, text="." * 500, bg=self.color)
        divider.pack(fill=X)
        label4 = Label(self.frame4a, text="Predicted grades:",fg="blue4",font = ("Georgia",14,"bold"),bg=self.color)
        label4.pack(side=LEFT, fill=X, padx=10)
        self.result_displayer = Text(self.frame4b, width=100, height=20, bg='white', font=('', 10), exportselection=0)
        self.result_displayer.pack(side=LEFT, pady=5, anchor=W)
        scroll_bar2 = Scrollbar(self.frame4b)
        scroll_bar2.pack(side=LEFT, fill=Y)
        scroll_bar2.config(command=self.result_displayer.yview)
        self.result_displayer['yscrollcommand'] = scroll_bar2.set

    def Browse(self):
        # Reading and extracting data from xls files
        try:
            courses_file_path = askopenfilename()
            wb = open_workbook(courses_file_path)
            sheet = wb.sheet_by_index(0)
            self.xls_data_indxing(sheet)
        except IOError:
            pass
        except XLRDError:
            pass

    def xls_data_indxing(self, sheet):
        '''Looping through every row in the file and looping through every column in each row, if we catch
        'Code' we increase the value of the 'semesters_counter' by one indicating that we are in a new
        academic year and index the 'Code' location. Then by continuing looping through columns in 'Code'
        row, if we catch 'Grade' we save its location with the value of the 'semesters_counter', if we catch
        'Code' again, we couple it with the value of the 'semesters_counter' and save its location in
        the codes_index dictionary.
           '''
        codes_index = {}  # {semester:[[row,column]#for the course code, [row,column]#for the grade]}
        semesters_counter = 0
        for row in range(sheet.nrows):
            for column in range(sheet.ncols):
                cell_value = sheet.cell_value(row, column)
                if type(cell_value) == unicode and cell_value.encode('ascii', 'ignore') == 'Code':
                    semesters_counter += 1
                    if not(semesters_counter in codes_index.keys()):
                        codes_index.setdefault(semesters_counter,[])
                        codes_index[semesters_counter].append([row,column])
                    else:
                        semesters_counter -= 1
                elif type(cell_value) == unicode and cell_value.encode('ascii', 'ignore') == 'Grade':
                    codes_index.setdefault(semesters_counter, [])
                    codes_index[semesters_counter].append([row,column])
        self.fetch_xls_courses(sheet, codes_index)

    def fetch_xls_courses(self,sheet, codes_index):
        courses = {}  # {course:[department,grade]}
        for semester in codes_index:
            codeRow = codes_index[semester][0][0]
            codeColumn = codes_index[semester][0][1]
            # gradeRow = codes_index[semester][1][0] basically not needed as it is the same as codeRow
            gradeColumn = codes_index[semester][1][1]
            while 1:
                codeRow += 1
                course_code = sheet.cell_value(codeRow,codeColumn)
                course_grade = re.compile('\W').sub('',sheet.cell_value(codeRow,gradeColumn))
                if type(course_code) == str:
                    break
                if 'uni' in course_code.encode('ascii', 'ignore').lower():
                    courses[course_code] = ['UNI',course_grade]
                else:
                    courses[course_code] = [semester,course_grade]
        self.courses_xls = courses

    def get_descriptions(self):
        # Fetching the links properly from the Text widget. Had the user separate the urls in
        # anyway or write anything else, this function will match only the urls and ignore any
        # redundant text or spaces.
        self.result_displayer.delete(0.0,END)
        self.descriptions = {}  # {course_code: description}
        urls = re.compile('\s+').sub('\n', self.descriptions_url.get(0.0, END)).split('\n')[0:]
        for url in urls:
            try:    # Trying if the provided text is a url,
                    # if it is, is it a valid one?
                urlopen(url)
            except URLError:
                continue
            except ValueError:
                continue
            self.fetch_descriptions(url)
        self.training()

    def fetch_descriptions(self, url):
        # Differentiating between different departments pages,
        # and clicking on "Course Description" if needed.
        # Each page has a different html code design, so they have to be dealt with separately.
        if url[-2:] == '12':
            url = self.click_description(url)
            self.CS(url)
        elif url[-2:] == '13':
            url = self.click_description(url)
            self.EE(url)
        elif url[-2:] == '14':
            url = self.click_description(url)
            self.IE(url)
        else:
            self.UNI(url)

    def IE(self, url):
        soup = BeautifulSoup(url, "html.parser").find(class_='fakulte_ack').span.div
        for course in soup.find_all('div'):
            try:
                course_name = course.strong.text
                if len(course_name) < 1:
                    raise AttributeError
                elif course_name == 'ELECTIVE COURSES':
                    continue
            except AttributeError:
                course_name = course.a.text
            course_code = self.course_code(course_name)
            course_desc = course.text.split(course_name)[-1]
            course_desc = course_desc.split('Textbook:')[0]  # filtering out the text book
            course_desc = re.compile('\s+').sub(' ', course_desc)
            course_desc = re.compile('Description: ').sub('', course_desc)
            if not(course_code in self.descriptions):
                self.descriptions[course_code] = course_desc

    def CS(self, url):
        soup = BeautifulSoup(url, "html.parser").find(class_='fakulte_ack').span.div.find_all('p')[1].span
        courses = []
        for course in soup.find_all('strong'):
            if len(course.text) < 1: continue
            courses.append(course.text)
        for course in range(len(courses)-1):
            course_name = courses[course]
            next_course_name = courses[course+1]
            course_desc = soup.text.split(course_name)[-1].split(next_course_name)[0]
            if 'Textbook:' in course_desc:
                course_desc = course_desc.split('Textbook')[0]
            course_desc = re.compile('\s+').sub(' ',course_desc)
            course_desc = re.compile('Description: ').sub('', course_desc)
            course_code = self.course_code(course_name)
            if not(course_code in self.descriptions):
                self.descriptions[course_code] = course_desc

    def EE(self, url):
        soup = BeautifulSoup(url, "html.parser").find(class_='fakulte_ack').span.div
        for course in range(len(soup.find_all('div'))):
            course_name = soup.find_all('div')[course].text
            if len(re.findall(re.compile('[A-Z]+ \d+[A-Z]?'),course_name))\
                    and not('Textbook:' in soup.find_all('div')[course+1].text):
                try:
                    course_code = self.course_code(course_name)
                except IndexError: continue
                course_desc = soup.find_all('div')[course+1].text
                if len(re.findall(re.compile('[A-Z]+ \d+[A-Z]?'),course_desc)): continue
                try:
                    if not (len(re.findall(re.compile('[A-Z]+ \d+[A-Z]?'), soup.find_all('div')[course + 2].text))\
                            or 'Textbook:' in soup.find_all('div')[course + 2].text):
                        course_desc += soup.find_all('div')[course + 2].text
                except IndexError:
                    pass
                course_desc = re.compile('\s+').sub(' ',course_desc)
                course_desc = re.compile('Description: ').sub('',course_desc)
                if not(course_code in self.descriptions):
                    self.descriptions[course_code] = course_desc

    def uni_course_code(self, course_name):
        codes = re.findall(re.compile('\s\d{3}'), course_name)
        return ['UNI' + str(x) for x in codes]

    def UNI(self, url):
        soup = BeautifulSoup(urlopen(url), "html.parser").find(class_='fakulte_ack').span
        for course in range(len(soup.find_all('p'))):
            course_name = soup.find_all('p')[course].text
            if len(re.findall(re.compile('[A-Z]+ \d+[A-Z]?'), course_name)):
                if len(re.findall(re.compile('[A-Z]+ \d+[A-Z]?'), soup.find_all('p')[course + 2].text)):
                    checker = 1
                else:
                    checker = 2
                course_code = self.uni_course_code(course_name)
                course_desc = soup.find_all('p')[course + checker].text
                course_desc = re.compile('\s+').sub(' ', course_desc)
                course_desc = re.compile('Description: ').sub('', course_desc)
                for item in course_code:
                    if not (item in self.descriptions):
                        self.descriptions[item] = course_desc

    def course_code(self, course_name):
        return re.findall(re.compile('[A-Z]+ \d+[A-Z]? '), course_name)[0][:-1]

    def click_description(self, url):
        # So that when the link is opened, the program should automatically go and click on:
        # "course description".
        driver = webdriver.Chrome()
        driver.get(url)
        course_des = driver.find_element_by_link_text("Course Descriptions")
        course_des.click()
        time.sleep(5)
        html = driver.page_source
        driver.close()
        # Returning the html needed for parsing the course description.
        return html

    def training(self):
        self.result = {}
        # __ TRAINING __
        self.result = {}    # {course:[department, predicted grade]}
        self.graded = []    # Differentiating between the graded courses and the ungraded ones.
        cl = docclass.naivebayes(docclass.getwords)
        for course in self.courses_xls:  # {course:[department,grade]}
            grade = self.courses_xls[course][-1]
            if len(grade) > 0:  # checking for a provided grade
                try:
                    cl.train(self.descriptions[str(course)], grade)  # (course description, grade)
                    self.graded.append(course)
                except KeyError:
                    continue
        #__ PREDICTION __
        # {course: description}
        '''After we have trained the classifier with descriptions of the graded courses and matched them
        with the provided grade, now we pass the ungraded courses descriptions to docclass.classify
        method to calculate the predicted grades.
        The predicted grades will be stored in a dictionary just like the one of the pre-graded courses one:
        {course:[department, predicted_grade]}'''
        for course in self.descriptions:
            if course not in self.graded:
                try:
                    predicted_grade = cl.classify(self.descriptions[course], default='unknown')
                    if course in self.courses_xls:
                        department = self.courses_xls[course][0]
                    elif 'UNI' in course:
                        department = 'UNI'
                    else:
                        department = re.findall(re.compile('[A-Z]+'),course)[0]
                    self.result[course] = [department, predicted_grade]
                except UnboundLocalError:
                    tkMessageBox.showerror('ERROR','Please provide grades file')
                    break
        self.display_results()

    def display_results(self):
        departments = {} #{department:[course, predicted grade]}
        for course in self.result:   #{course:[department, predicted grade]}
            predicted_grade = self.result[course][1]
            department = self.result[course][0]
            if type(department) == int:
                department = '0Semester%d' % department
                # The numbers at the start of the string is just for displaying them in that order:
                # semesters, Departmental Electives and then UNI courses.
            elif 'UNI' in department:
                department = '2UNI COURSES'
            else:
                department = '1Departmental Electives'
            departments.setdefault(department,[])
            departments[department].append([course, predicted_grade]) #{department:[course, predicted grade]}
        self.result_displayer.tag_config('department', font='Calibri 14', underline=1)
        grades = 'ABCDF'
        for grade in range(len(grades)):
            self.result_displayer.tag_config(grades[grade], font='Times 12', background=self.grades[grade+5], foreground=self.grades[grade+10])
        for department in sorted(departments):
            self.result_displayer.insert(END,department[1:]+'\n'*2)
            self.highlight(department[1:], 'department')
            for predictions in departments[department]:   # [course, predicted grade]
                self.result_displayer.insert(END, predictions[0]+'-->'+predictions[1]+'\n')
                self.highlight(predictions[0]+'-->'+predictions[1]+'\n',predictions[1][0])
            self.result_displayer.insert(END,'\n'*2)

    def highlight(self, keyword, tag):
        pos = '1.0'
        while 1:
            idx = self.result_displayer.search(keyword, pos, END)
            if not idx:
                break
            pos = '{}+{}c'.format(idx, len(keyword))
            self.result_displayer.tag_add(tag, idx, pos)
            # I used some code from:
            # http://stackoverflow.com/questions/17829713/tkinter-text-highlight-specific-lines-using-keyword

def main():
    root = Tk()
    root.geometry("980x600+120+20")
    GradesPredictor(root, 'honeydew')
    root.mainloop()
main()