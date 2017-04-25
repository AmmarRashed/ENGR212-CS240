from Tkinter import *
import re, clusters,ttk,tkMessageBox
import tkFileDialog as fd
class courseAnalyzer(Frame):
    def __init__(self,parent):
        self.parent=parent
        self.course_codes={} #This is going to be used to parse courses and their departments
        self.course_descriptions = {} #Going to store words in each course description
        self.pre_course = [] #Its use is commented in fill_course_list method
        #The three variables above are going to be used in fill_course_list method
        self.words = [] #Words in course descriptions that are neither common nor rare
        self.selected_departments=[]
        self.courses=[] #courses that are desired to be clustered, get_selectedDepartments method
        self.courses_wordCount={} #store (neither common nor rare) words in each selected course
        self.data=[] # frequencies list that is to be used in clustering
        self.labels=[] # courses list that is to be used in drawing the dendrogram
        self.initGui()
    def initGui(self):
        Label(self.parent,text='COURSE ANALYZER - SEHIR LIMITED EDITION',
              bg='RoyalBlue',font=("Helvetica",16),fg='white')\
            .pack(side=TOP,fill=X,ipady=5)
        self.uploadFrame=Frame(self.parent)
        self.uploadFrame.pack(side=TOP)
        self.browseFrame=Frame(self.uploadFrame)
        self.browseFrame.grid(row=0,sticky=NW)

        Label(self.browseFrame,text='Upload a file that contains course description:',anchor=NW,font=("Helvetica",11)).grid(row=0,column=0)
        Button(self.browseFrame,text='Browse',cursor='hand2',height=1,command=self.Browse)\
            .grid(row=0,column=1,ipadx=15,padx=150,pady=10)
        self.selectFile=Frame(self.uploadFrame)
        self.selectFile.grid(row=1,sticky=NW)
        # self.selectFile.grid(row=1,sticky=W)
        Label(self.selectFile,text='Selected File:',font=("Helvetica",11),anchor=NW)\
            .grid(row=0,sticky=W,column=0)

        self.filePath=StringVar()
        self.filePath.set("Please select a file")
        Label(self.selectFile,textvariable=self.filePath,
              relief=SOLID,width=70,bd=2,)\
        .grid(row=0,column=1,ipadx=10,ipady=2,padx=30)

        self.mainFrame=Frame(self.parent,relief=SOLID,bd=2,width=300,height=300)
        self.mainFrame.pack(side=TOP,pady=10)
        self.settingsFrame=Frame(self.mainFrame)
        self.settingsFrame.pack(side=TOP)
        self.canvasFrame=Frame(self.mainFrame)
        self.canvasFrame.pack(side=TOP)
        self.sim_frame = Frame(self.settingsFrame)
        self.sim_frame.grid(row=0,column=0,sticky=NW)
        Label(self.sim_frame,text='Similarity Measure:',font=("Helvetica",11))\
            .grid(row=1,column=0,sticky=E)

        self.sim_measure=StringVar()
        self.sim_measure.set('pearson')
        Radiobutton(self.sim_frame,variable=self.sim_measure,value='pearson',
                    text='Pearson',cursor='hand2').grid(row=0,column=1)
        Radiobutton(self.sim_frame,variable=self.sim_measure,value='tanimoto',
                    text='Tanimoto',cursor='hand2').grid(row=2,column=1)
        Label(self.sim_frame,text='Select Course Codes:',font=("Helvetica",10))\
            .grid(row=0,column=2,sticky=E)

        self.coursesFrame=Frame(self.settingsFrame)
        self.coursesFrame.grid(row=0,column=1,sticky=NE)
        self.course_list=Listbox(self.coursesFrame,width=20,height=5,selectmode=MULTIPLE)
        self.course_list.bind('<<ListboxSelect>>',self.get_selectedDepartments)
        self.course_list.pack(side=LEFT)
        course_scroll=ttk.Scrollbar(self.coursesFrame,command=self.course_list.yview)
        course_scroll.pack(side=RIGHT,fill=Y)
        self.course_list.config(yscrollcommand=course_scroll.set)

        Button(self.sim_frame,text="Draw Hierarchical Cluster Diagram",cursor='hand2'
               ,command=self.dendrogram,font=('Helvetica',10),width=30)\
            .grid(row=3,column=0,sticky=E,pady=20)
        Button(self.sim_frame,text="Print Hierarchical Cluster as Text",cursor='hand2'
               ,font=('Helvetica',10),width=25,command=self.clust_txt)\
            .grid(row=3,column=1,sticky=E,padx=40)
        Button(self.sim_frame,text="Show Data Matrix",cursor='hand2'
               ,font=('Helvetica',10),width=20,command=self.print_matrix)\
            .grid(row=3,column=2,sticky=E)
        self.canvas = Canvas(self.canvasFrame, bg='white', width=600, height=600, scrollregion=(0, 0, 0, 0))
        self.hbar = ttk.Scrollbar(self.canvasFrame, orient=HORIZONTAL)
        self.hbar.pack(side=BOTTOM, fill=X)
        self.hbar.config(command=self.canvas.xview)
        self.vbar = ttk.Scrollbar(self.canvasFrame, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(width=self.canvas.winfo_screenwidth()-400, height=self.canvas.winfo_screenheight())
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)

    def Browse(self):
        try:
            path=fd.askopenfilename()
            self.filePath.set(path)
            self.fill_course_list(path)
        except IOError:
            pass
        except IndexError:
            pass

    #A method to parse data(assign each course to a list of its description words), and fill the course listbox
    #Then transfer to getwordscount method
    def fill_course_list(self,path):
        self.course_list.delete(0,END)
        #Reseting courses_codes dictionary, or departments in course listbox:
        self.course_codes={}
        '''if we wish to cluster unique courses from two departments like CS and EE,
        we can simply delete the previous line, which means we don't reset the courses codes and accordingly
        we can add courses from other departments by simply opening its file'''
        with open(path) as file:
            line_counter=0
            for line in file:
                course_pat= '^\w+ \d{3}\w?'
                description_pat='\W+'
                course=re.findall(course_pat,line)
                '''In the dataset we have, it has a pattern. That pattern is: when the number of row
                is even, there is course code and name, otherwise there is the description of the course
                mentioned in the line above.
                So, we check for each line and parse our data accordingly'''
                if line_counter % 2 == 0:
                    course=course[0]
                    department=re.split(description_pat,course)[0]
                    if department in self.course_codes:  # Check if I have that department in the dictionary of courses
                        self.course_codes[department].append(course)
                    else:
                        self.course_codes[department] = [course]
                    self.pre_course = course  # So that next loop we can use it as the course from the row above
                else:
                    self.course_descriptions[self.pre_course]=re.split(description_pat,line)
                line_counter += 1

        # Make all the words in the course description lower cased
        for course in self.course_descriptions:
            for wordIndex in range(len(self.course_descriptions[course])):
                word=self.course_descriptions[course][wordIndex]
                self.course_descriptions[course][wordIndex]=word.lower()
        for course in sorted(self.course_codes.keys()):
            self.course_list.insert(END,course)

        #Create a list of all the words in courses descriptions
        self.countAllWords()

    def countAllWords(self): #count all the words in courses descriptions
        self.words=[]
        '''we need to get the frequency of each word in every and each course description, and then
        neglect the common and rare words. This is to be used in creqting our data matrix'''
        allWords=[] # all the words mentioned in all course descriptions.
        for wordList in self.course_descriptions.values():
            [allWords.append(word) for word in wordList]
        allFreqs=self.counter(allWords)
        self.words=self.eliminateCommonRare(allFreqs,smallerThan=0.005,biggerThan=0.001)

    def counter(self,wordsList):
        Freqs = {}  # assigning each word with its frequency in allWords list
        # Word frequency means how many of it is there in the list
        for word in wordsList:
            if word in Freqs:
                Freqs[word] += 1
            else:
                Freqs[word] = 1
        return Freqs

    def eliminateCommonRare(self,freqsDict,smallerThan,biggerThan):
        words=[]
        sumFreqs = sum(freqsDict.values())  # The summation of all the frequencies
        # Eliminating common & rare words,(0.1%< word count < 0.5% of all the words)
        for word, freq in freqsDict.items():
            if float(freq) / sumFreqs < smallerThan and float(freq) / sumFreqs > biggerThan and len(word) > 3:
                words.append(word)
        #lower casing all words
        for word in range(len(words)):
            words[word]=words[word].lower()
        return words

    def get_selectedDepartments(self,event):
        self.courses_wordCount={}
        self.selected_departments=[self.course_list.get(i) for i in self.course_list.curselection()]
        # get courses of selected departments
        self.courses = [self.course_codes[i] for i in self.selected_departments]

        #Concatinate coureses of each department in one list
        courses=[]
        for department in self.courses:
            for course in department:
                courses.append(course)
        self.courses=courses
        try:
            for course in self.courses:
                self.courses_wordCount[course]=self.counter(self.course_descriptions[course])
                # temp={}
                # for word in self.counter(self.course_descriptions[course])
            temp={} #store selected courses description mutual words with the words computed in countAllWords method
            for course in self.courses_wordCount:
                wordFreqs=self.courses_wordCount[course]
                for word in wordFreqs:
                    if word in self.words:
                        temp[word]=wordFreqs[word]
                    else:
                        temp[word]=0
                self.courses_wordCount[course]=temp
            self.create_dataMatrix()
        except IndexError:
            pass

    def print_matrix(self):
        try:
            # Clearing canvas
            self.canvas.delete('all')
            # Printing the dataMatrix in canvas
            canvasTxt = ''
            scrollScale=[]
            lineCounter=0
            for line in open('dataMatrix.txt', 'r'):
                canvasTxt += line + '\n'
                scrollScale.append(len(line))
                lineCounter+=1
            xscrollScale=int(max(scrollScale)*8.5)
            yscrollScale=lineCounter*35
            self.canvas.create_text(10, 10, text=canvasTxt,anchor=NW)
            self.canvas['scrollregion']=(0,0,xscrollScale,yscrollScale)

        except IOError:
            tkMessageBox.showinfo('No Inout','Please open courses file first')

    def create_dataMatrix(self):
        selected_course_descriptions = {}
        for course in self.course_descriptions:
            temp=''
            for des in self.course_descriptions[course]:
                temp+=des+' '
            if course in self.courses_wordCount:
                selected_course_descriptions[course]=temp

        clusters.create_matrix(selected_course_descriptions,outfile='dataMatrix.txt')
        rows,columns,data = clusters.readfile('dataMatrix.txt')
        self.data=data
        self.labels=rows

    def alternatively(self):
        # This is a slightly different way of creating the data matrix using variables already there.
        # However it will require few changes in self.course_descriptions dictionary to be accurate.
        # out=file('dataMatrix.txt','w+')
        # out.write('Course')
        # for word in self.words:
        #     out.write('\t%s'%word)
        # out.write('\n')
        # for course,wordCount in self.courses_wordCount.items():
        #     out.write(course)
        #     for word in wordCount:
        #         out.write('\t%d'%wordCount[word])
        #     out.write('\n')
        pass

    def clust_txt(self):
        try:
            # Clearing canvas
            self.canvas.delete('all')
            clustTxt = clusters.clust2str(clust=clusters.hcluster(self.data, self.simMeasure()),
                                         labels=self.courses_wordCount.keys())
            self.canvas.create_text(10, 10, anchor=NW,
                            text=clustTxt)
            yscrollScale=len(clustTxt)*1.8
            self.canvas['scrollregion']=(0,0,yscrollScale,yscrollScale)
        except IndexError:
            pass
        except ZeroDivisionError:
            for dataList in self.data:
                dataList.append(0)
            self.clust_txt()

    def simMeasure(self):
        if self.sim_measure.get() == 'pearson':
            return clusters.pearson
        else:
            return clusters.tanimoto

    def dendrogram(self):
        try:
            #clearing canvas
            self.canvas.delete("all")
            clust = clusters.hcluster(self.data, self.simMeasure())
            width=clusters.getheight(clust) * 90
            canvaswidth=self.canvas.winfo_width()
            depth=clusters.getdepth(clust)
            # width is fixed, so scale distances accordingly
            scaling = float(canvaswidth - 150) / depth

            self.canvas.create_line((width/2,0,width/2,10),fill='red')
            yscrollScale=[10]
            #draw first node
            self.drawnode(self.canvas, clust, width/2 ,10, scaling, self.labels,yscrollScale)
            self.canvas['scrollregion']=(0,0,width,sum(yscrollScale))
        except IndexError:
            pass
        except ZeroDivisionError:
            tkMessageBox.showerror('Runtime Error','Insufficient number of courses')

    def drawnode(self,canvas, clust, x, y, scaling, labels,yscrollScale):
        if clust.id < 0:
            h1 = clusters.getheight(clust.left) * 90
            h2 = clusters.getheight(clust.right) * 90
            left = x - (h1 + h2) / 2
            right = x + (h1 + h2) / 2

            # Line length
            ll = max(clust.distance * scaling/4,15)
            '''The max() is to make sure that deeper
            vertical edges in the tree are long enough to see, to visualize the tree better.'''
            yscrollScale.append(ll)
            # Horizontal line from this cluster to children
            canvas.create_line((left + h1 / 2,y,  right - h2 / 2,y), fill='red')
            # Vertical line to left item
            canvas.create_line((left + h1 / 2,y,left + h1 / 2, y + ll), fill='red')

            # Vertical line to right item
            canvas.create_line((right - h2 / 2,y, right - h2 / 2, y + ll), fill='red')

            # Call the function to draw the left and right nodes
            self.drawnode(canvas, clust.left, left + h1 / 2, y + ll,scaling, labels,yscrollScale)
            self.drawnode(canvas, clust.right,right - h2 / 2 , y + ll, scaling, labels,yscrollScale)
        else:
            # If this is an endpoint, draw the item label
            canvas.create_text((x , y+7), text=labels[clust.id], fill='blue')


if __name__=='__main__':
    root=Tk()
    o=courseAnalyzer(root)
    root.geometry('950x600')
    root.mainloop()



