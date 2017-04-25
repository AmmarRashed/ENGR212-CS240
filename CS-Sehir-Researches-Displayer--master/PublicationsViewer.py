from Tkinter import *
from ttk import Combobox,Scrollbar,Button
from bs4 import BeautifulSoup
from PIL import ImageTk,Image
import urllib2,tkMessageBox,re,cStringIO

class Analyzer(Frame):
    def __init__(self,parent):
        #FILTERING LISTS:
        self.allYears=[]
        self.allInvestigators=[]
        self.allInstitutions=[]
        self.projects={}
        self.photo=None
        #Header label
        self.parent=parent
        Label(self.parent,text="SEHIR Research Projects Analyzer - CS Edition",
              font=('Times 22 bold')
              ,fg='white',bg='RoyalBlue').pack(side=TOP,fill=X)
        #Enter url Frame
        self.entryFrame=Frame(self.parent)
        self.entryFrame.pack(side=TOP,anchor=NW)
        Label(self.entryFrame,text='Please provide a url:',font=('Heldelavia 10')).grid(row=0,sticky=NW,column=0,padx=10)
        Button(self.entryFrame,text='Fetch Research Projects',command=self.fetchProjects,cursor='hand2').grid(row=1,column=1)
        self.urlLink=StringVar()
        self.urlEntry=Entry(self.entryFrame,textvariable=self.urlLink,width=70,fg='DarkBlue',
                            font=('Heldelavia 8 bold'),bg='yellow').grid(row=2,column=0,padx=10)
        Label(self.parent,text='\''*10000).pack(side=TOP)

        #(Filter the research project by:) Frame
        self.midFrame=Frame(self.parent)
        self.midFrame.pack(side=TOP,fill=X)
        self.filterFrame=Frame(self.midFrame)
        self.filterFrame.grid(row=0,column=0)
        Label(self.filterFrame,text='Filter Research Projects by:',
              font=('Heldelavia 11 bold')).grid(row=0,column=0,padx=10,pady=10)
        Label(self.filterFrame,text='year:',fg='blue').grid(row=1,column=0,sticky=W,padx=10)
        Label(self.filterFrame,text='Principal Investigator::',fg='blue').grid(row=2,column=0,sticky=W,padx=10)
        Label(self.filterFrame,text='Funding Institution',fg='blue').grid(row=3,column=0,sticky=W,padx=10)
        #ComboBoxes:
        self.years=StringVar()
        self.years.set('All Years')
        self.yearsCB=Combobox(self.filterFrame,textvariable=self.years,width=26)
        self.yearsCB.grid(row=1,column=1,pady=5)
        self.investigators=StringVar()
        self.investigators.set('All Investigators')
        self.investigatorsCB=Combobox(self.filterFrame,textvariabl=self.investigators,width=26)
        self.investigatorsCB.grid(row=2,column=1,pady=5)
        self.institutions=StringVar()
        self.institutions.set('All Institutions')
        self.institutionsCB=Combobox(self.filterFrame,textvariable=self.institutions,width=26)
        self.institutionsCB.grid(row=3,column=1,pady=5)
        Button(self.midFrame,text='Display Projects Titles',cursor='hand2',width=30,command=self.filtering).grid(row=1,column=0,pady=10)

        #Picking a Project Frame:
        self.pickFrame=Frame(self.midFrame)
        self.pickFrame.grid(row=0,column=1,padx=120)

        #Projects Listbox:
        self.projectsLB=Listbox(self.pickFrame,width=100,height=8)
        self.projectsLB.pack(side=LEFT)
        self.yscrollbar=Scrollbar(self.pickFrame,command=self.projectsLB.yview)
        self.projectsLB['yscrollcommand']=self.yscrollbar.set
        self.yscrollbar.pack(side=RIGHT,fill=Y)
        Button(self.midFrame,text='Show Description',command=self.showDescription,cursor='hand2').grid(row=1,column=1)
        Label(self.parent,text='\''*1000).pack()
        ###############################################################
        #Description Frame:
        self.descriptionFrame=Frame(self.parent,padx=10)
        self.descriptionFrame.pack(side=RIGHT,anchor=NE)
        Label(self.descriptionFrame,text='Project Description:').pack(side=TOP,padx=200)
        self.descriptionText=Canvas(self.descriptionFrame,bg='white'
                                  ,width=450,height=200)
        self.descriptionScrollbar=Scrollbar(self.descriptionFrame,command=self.descriptionText.yview)
        self.descriptionScrollbar.pack(side=RIGHT,fill=Y)
        self.descriptionText['yscrollcommand']=self.descriptionScrollbar.set
        self.descriptionText.pack(side=RIGHT, anchor=NE)

        self.imageFrame=Frame(self.parent)
        self.imageFrame.pack(side=LEFT,anchor=NW)
        self.imageCanvas = Canvas(self.imageFrame)

    def fetchProjects(self):
        try:
            self.url = urllib2.urlopen(self.urlLink.get())
            self.soup = BeautifulSoup(self.url, 'html.parser')
            projects=self.soup.find_all(class_='list-group-item')
            #Parsing data into the following pattern:
            #{project name:[date, Funding Institution, Investigator, Image, Description]}
            names = {}
            for tag in projects:
                filters=tag.find_all('p')
                self.projects[tag.h4.text]=[filters[data].text for data in range(5)]
                temp = self.projects[tag.h4.text]
                temp[3]=tag.find('img')['src'] #image URL
                self.projects[tag.h4.text]=temp
            for project in self.projects:
                # Years:
                date = self.projects[project][0]
                years=[]
                yearPat = re.compile('\d+, \d{4}')  # Date pattern (e.g) '31, 2016'
                startEnd_years=re.findall(yearPat, date)
                startingYear=int(startEnd_years[0][-4:])
                endingYear=int(startEnd_years[1][-4:])
                for year in range(startingYear,endingYear+1):
                    years.append(str(year))
                    if not(str(year) in self.allYears):
                        self.allYears.append(str(year))
                self.projects[project][0]=years

                #Institutions:
                institution = self.projects[project][1]
                institutionPat = 'Funding Institution:'
                institutions = re.split(institutionPat, institution)
                institution = ''
                for name in re.findall('\S+', institutions[-1]):
                    institution += name + ' '
                if not(institution in self.allInstitutions):
                    self.allInstitutions.append(institution)
                self.projects[project][1]=institution

                #Investigators:
                investigator = self.projects[project][2]
                investigatorPat='Principal Investigator:'
                investigators=re.split(investigatorPat,investigator)
                investigator=''
                foreNames=[]
                surName_checker=1 #Surname check works when its value
                # reaches the index of the last name of the investigator,
                # where it will indicate that this is the surname of the investigator so
                # it will put it in the names dictionary where surnames can be sorted
                # while being easily rejoined with the rest of the investigator name
                for name in re.findall('\S+',investigators[-1]):
                    investigator+= name + ' '
                    if surName_checker<len(re.findall('\S+',investigators[-1])):
                        foreNames.append(name)
                    else:
                        names[name]=foreNames
                    surName_checker+=1

            #Sorting Investigator surnames
            for name in sorted(names):
                investigator=''
                for foreName in names[name]:
                    investigator+=foreName+' '
                investigator+=name
                if not(investigator in self.allInvestigators):
                    self.allInvestigators.append(investigator)
                self.projects[project][2]=investigator

            #Preparing the filter lists for the comboboxes
            self.allYears = sorted(self.allYears)
            self.allInstitutions = sorted(self.allInstitutions)
            self.allYears.insert(0, 'All Years')
            self.allInstitutions.insert(0, 'All Institutions')
            self.allInvestigators.insert(0, 'All Investigators')

            #Filling the filtering comboboxes
            self.yearsCB['values']=self.allYears
            self.institutionsCB['values']=self.allInstitutions
            self.investigatorsCB['values']=self.allInvestigators
        except ValueError:
            tkMessageBox.showerror('URL error', 'Please enter a valid URL')
        except urllib2.URLError:
            tkMessageBox.showerror('URL error', 'Please enter a valid URL or check your internet connection')

    def filtering(self): #Filtering the projects according to what the user chooses at the combobox
        self.projectsLB.delete(0,END)
        year=self.years.get()
        institution=self.institutions.get()
        investigator=self.investigators.get()
        # {project name:[date, Funding Institution, Investigator, Image, Description]}
        for project in self.projects:
            if year == 'All Years':
                yearCheck = 1
            else:
                yearCheck = year in self.projects[project][0]
            if institution == 'All Institutions':
                institutionCheck = 1
            else:
                institutionCheck = institution in self.projects[project][1]
            if investigator == 'All Investigators':
                investigatorCheck = 1
            else:
                investigatorCheck = investigator in self.projects[project][2]
            if yearCheck and institutionCheck and investigatorCheck:
                self.projectsLB.insert(END,project)

    def showDescription(self):
        try:
            # {project name:[date, Funding Institution, Investigator, Image, Description]}
            #Showing the project description in Description Text window
            project=self.projectsLB.selection_get()
            description=self.projects[project][4]
            #wraping description text:
            descriptionWords=re.split('\s+',description)
            description=''
            wrapScaler=0 #After each 54 letters it will add a new line
            lineCounter=0 #Count how many lines do we have to adjust the scrollbar accordingly
            while len(descriptionWords)>0:
                if wrapScaler>=60:
                    description += descriptionWords[0] + '\n'
                    wrapScaler=0
                    lineCounter+=1
                else:
                    description+=descriptionWords[0]+' '
                wrapScaler+=len(descriptionWords[0])+1
                descriptionWords=descriptionWords[1:]
            self.descriptionText.delete(ALL) #Cleaning from any previous shown 7
            self.descriptionText.config(scrollregion=(0, 0, lineCounter * 18, lineCounter * 18))
            self.descriptionText.create_text(5,5,text=description,anchor=NW,fill='blue4')

            #Showing Project Image:
            self.imageCanvas.delete(ALL)
            image_url = 'http://cs.sehir.edu.tr'+self.projects[project][3]
            image_byt = urllib2.urlopen(image_url).read()
            file= cStringIO.StringIO(image_byt)
            image=Image.open(file)
            # print image.size
            resizedPhoto=image.resize([580,250]) #Modifing photo size to fit in the available room, OR:
            # resizedPhoto= image.resize([int(0.7 * size) for size in image.size]) if we want to change width and height with the same ratio
            self.photo = ImageTk.PhotoImage(resizedPhoto)
            self.imageCanvas.config(width=800) #Making sure no part of the photo is cropped
            self.imageCanvas.pack(side=LEFT, anchor=NW, padx=20)
            self.imageCanvas.create_image(10, 10, image=self.photo, anchor=NW)
        except TclError:
            tkMessageBox.showerror('URL error', 'Please enter a valid URL')
        except urllib2.URLError:
            tkMessageBox.showerror('URL error', 'Please check your internet connection')

if __name__=='__main__':
    root=Tk()
    o=Analyzer(root)
    root.geometry('1200x600')
    root.mainloop()
