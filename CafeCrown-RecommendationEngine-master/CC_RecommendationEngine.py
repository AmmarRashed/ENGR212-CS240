from Tkinter import *
from ttk import Combobox
from xlrd import open_workbook
import anydbm,pickle,unicodedata,tkMessageBox
from recommendations import *
class Recommender(Frame):
    def __init__(self,parent):
        self.parent=parent
        self.initUI()
        self.read_ratings_database()
    def initUI(self):
        #First frame is for the upper part of the gui in which we want to write the header of the app.
        TitleFrame=Frame(self.parent)
        TitleFrame.pack(side=TOP,fill=X)

        #Since this gui has many parts to be divided into, so we create frames for each part.
        #Besides, some parts need to be 'pack'ed and others to be 'grid'ed,
        #Thus, we can combine them by dividing the window to multiple frames with different layouts.
        EntryFrame=Frame(self.parent)
        EntryFrame.pack(side=TOP,fill=X)
        chooseFrame=Frame(EntryFrame)
        chooseFrame.pack(side=LEFT)
        Label(TitleFrame,justify=LEFT,text="Cafe Crown Recommendation Engine - SEHIR Special Edition",
              fg='white',bg='RoyalBlue',font=("Helvetica",18,"bold")).pack(side=TOP,fill=X)
        Label(TitleFrame,text="Welcome!",fg='black',font=("Times",14)).pack(side=TOP)
        Label(TitleFrame,
                text="Please rate entries that you have had in CC,"
                     " and we will recommend you what you may like to have!",
                fg='black',font=("Times",14)).pack(side=TOP)
        LabelFrame(TitleFrame,bg='black').pack(side=TOP,fill=X,pady=7)
        Label(chooseFrame,text='Choose a meal:',fg='red4',
              font=("Helvetica",16)).grid(row=0,column=0,sticky=W,padx=10)

        self.meal_name=StringVar()
        self.select_meal=Combobox(chooseFrame,textvariable=self.meal_name)

        #reading the menu excel file
        wb=open_workbook('Menu.xlsx')
        self.sheet=wb.sheet_by_index(0)
        meals=()

        #constructing the menu combobox and adding the meals to it.
        for meal in range(1,self.sheet.nrows):
            meals+=(self.sheet.cell(meal,0).value,)
        self.select_meal['values']=meals
        self.select_meal.current(0)
        self.select_meal.grid(row=1,column=0,sticky=W,ipadx=30,padx=10)

        Label(chooseFrame,text="Enter your rating:",fg='red4',
              font=("Helvetica",16)).grid(row=0,column=1,sticky=E,padx=50)

        #The rating scale
        self.rating=Scale(chooseFrame,orient=HORIZONTAL,from_=1,to=10)
        self.rating.grid(row=1,column=1,sticky=E,padx=50,pady=15,ipadx=30)
        Button(chooseFrame,text="Add",fg='blue',font=("times",12,'bold'),
               command=self.AddRating,cursor="hand2").grid(row=1,column=2,ipadx=25)

        ratesframe=Frame(EntryFrame)
        ratesframe.pack(side=RIGHT,padx=40)
        self.rates_list=Listbox(ratesframe,width=35,height=7)
        self.fill_rates_listbox()

        self.rates_list.pack(side=LEFT)
        scrollbar=Scrollbar(ratesframe,command=self.rates_list.yview)
        self.rates_list.config(yscrollcommand=scrollbar.set)

        Button(ratesframe,text="Remove\n Selected",font=("Times",12,"bold"),
               cursor="hand2",fg='red',command=self.Remove).pack(side=RIGHT,anchor=E,padx=10)
        scrollbar.pack(side=RIGHT,fill=Y)

        LabelFrame(self.parent,bg='black').pack(side=TOP,fill=X,pady=7)
        Label(self.parent,text='Get Recommendations',font=("Times",18,"bold"),fg='black').pack(anchor=N)
        LabelFrame(self.parent,bg='black').pack(side=TOP,fill=X,pady=7)

        SettingFrame=Frame(self.parent)
        SettingFrame.pack(side=LEFT,anchor=NW)
        Label(SettingFrame,text="Settings:",fg='red4',
              font=("Helvetica",18,"bold")).grid(row=0,column=0,sticky=W,padx=10)
        Label(SettingFrame,text="Number of recommendations:",fg='black',
              font=("Helvetica",11)).grid(row=1,column=0,sticky=W,padx=10)
        self.nor=StringVar() #number of recommendatoins
        self.nor.set(5)
        self.n_recommendations=Entry(SettingFrame,width=3,textvariable=self.nor).grid(row=1,column=0,padx=220,sticky=W)

        self.recommendationFrame=Frame(self.parent)
        self.recommendationFrame.pack(pady=25)
        Label(self.recommendationFrame,text="Choose recommendation method:",fg='violetred4',
              font=("Helvetica",10,"italic")).grid(row=1,column=2,sticky=W)
        self.method=StringVar()
        self.method.set("userBased")
        self.method_check=''
        #method_check will be used in getting the top matches method to differentiate between
        #similar users and similar items.

        #Adding two groups of Radiobuttons, one for method (User-based, Item-based),
        #The other group is for the similarity metric(Euclidean, Pearson or Jaccard.
        Radiobutton(self.recommendationFrame,variable=self.method,value="userBased",text="User-Based",
                    cursor="hand2",font=("Times",8,'bold')).grid(row=2,column=2,sticky=W)
        Radiobutton(self.recommendationFrame,variable=self.method,value="itemBased",text="Item-Based",
                    cursor="hand2",font=("Times",8,'bold')).grid(row=3,column=2,sticky=W)
        Label(self.recommendationFrame,text="Choose similarity metric:",fg='violetred4',font=("Helvetica",10,"italic")).grid(row=4,column=2,sticky=W)

        self.metric=StringVar()
        self.metric.set("euclidean")
        Radiobutton(self.recommendationFrame,variable=self.metric,value="euclidean",text="Euclidean Score",
                    cursor="hand2",font=("Times",8,'bold')).grid(row=5,column=2,sticky=W)
        Radiobutton(self.recommendationFrame,variable=self.metric,value="pearson",text="Pearson Score",
                    cursor="hand2",font=("Times",8,'bold')).grid(row=6,column=2,sticky=W)
        Radiobutton(self.recommendationFrame,variable=self.metric,value="jaccard",text="Jaccard Score",
                    cursor="hand2",font=("Times",8,'bold')).grid(row=7,column=2,sticky=W)
        Button(self.recommendationFrame,text="Get Recommendation",fg='blue',
               cursor="hand2",font=("Helvetica",12,"bold"),command=self.result).grid(row=6,column=2,padx=150)
        self.resultFrame=Frame(SettingFrame)
        self.resultFrame.grid(row=10,pady=150,padx=5,column=0)


    def result(self):
        self.parent.geometry('1150x630')
        Label(self.resultFrame,text="Result Box (Recommendations):",font=("Times",14)).grid(row=0,column=0,sticky=W)
        listFrame=Frame(self.resultFrame)
        listFrame.grid(row=1)
        self.resultList=Listbox(listFrame,width=60,height=6)
        scrollbar2=Scrollbar(listFrame,command=self.resultList.yview)
        scrollbar2.pack(side=RIGHT,fill=Y)
        self.resultList.config(yscrollcommand=scrollbar2.set)
        self.resultList.pack(side=LEFT)

        similarsFrame=Frame(self.resultFrame)
        similarsFrame.grid(row=1,column=2,sticky=NW,padx=10)
        self.base=StringVar()
        #Users similar to you
        self.sim_users=Label(similarsFrame,bg='violetred4',fg='white',font=("Helvetica",12,"bold"))
        self.sim_users.pack(padx=10,ipadx=73,anchor=NW)
        self.similarUsersList=Listbox(similarsFrame,width=50,height=5)
        self.similarUsersList.bind('<<ListboxSelect>>',self.userRatings)
        self.similarUsersList.pack(pady=2)
        ratingsFrame=Frame(self.recommendationFrame)
        ratingsFrame.grid(row=10,column=2,pady=45,sticky=W)
        self.base_details=StringVar()
        #Users ratings (select a user on the left)
        self.sim_ratings=Label(ratingsFrame,fg="white",bg="red4",font=("Helvetica",12,"bold"))
        self.sim_ratings.pack(anchor=NW,ipadx=30)
        self.userRatesList=Listbox(ratingsFrame,width=59,height=5)
        self.userRatesList.pack(side=LEFT,anchor=NE,fill=Y)
        scrollbar3=Scrollbar(ratingsFrame,command=self.userRatesList.yview)
        scrollbar3.pack(side=LEFT,fill=Y)
        self.userRatesList.config(yscrollcommand=scrollbar3.set)
        self.similarities=[]
        self.recommendation_method()
        self.get_matches()

    #Reading the other users ratings from the provided data base,
    def read_ratings_database(self):
        self.rating_db=anydbm.open('cc_ratings.db','r')
        self.other_ratings={}
        for person in self.rating_db:
            self.other_ratings[person]=pickle.loads(self.rating_db[person])
        try:
            self.meals_rating_dict = pickle.loads(self.db["meals ratings"])
        except KeyError:
            self.meals_rating_dict = {}
        self.simDistances={}

    #Creating a database to store user's ratings and fill the listbox of the ratings from last changes.
    def fill_rates_listbox(self):
        self.db=anydbm.open("ownratings.db","c")
        try:
            self.meals_rating_dict=pickle.loads(self.db["meals ratings"])
            for meal,rating in pickle.loads(self.db["meals ratings"]).items():
                self.rates_list.insert(END,meal+" --> "+str(rating))
        except KeyError:
            self.meals_rating_dict={}

    def AddRating(self):
        meal = self.select_meal.get()
        rating = self.rating.get()

        #If we wish to prevent any meal from being added more than once in user's ratings listbox,
        # we have to take into consideration the type of the meal name provided,
        # since some have Turkish letters.
        if type(meal) == unicode:
            if self.normalize(meal) not in self.meals_rating_dict:
                self.meals_rating_dict[self.normalize(meal)]=rating
                self.rates_list.insert(END,meal+" --> "+str(rating))
            else:
                self.meals_rating_dict[self.normalize(meal)]=rating
                meal_index=self.find_index_inListbox(self.normalize(meal),self.rates_list)
                self.rates_list.insert(END,meal+" --> "+str(rating))
                self.rates_list.delete(meal_index)
        else:
            if meal not in self.meals_rating_dict:
                self.meals_rating_dict[meal]=rating
                self.rates_list.insert(END,meal+" --> "+str(rating))
            else:
                self.meals_rating_dict[meal]=rating
                meal_index=self.find_index_inListbox(meal,self.rates_list)
                self.rates_list.insert(END,meal+" --> "+str(rating))
                self.rates_list.delete(meal_index)
        self.db["meals ratings"]=pickle.dumps(self.meals_rating_dict)

    #normalizing meals names that have Turkish letter into strings.
    def normalize(self,unicode):
        return unicodedata.normalize('NFKD',unicode).encode('utf8')

    #To find the index of an item in the listbox.
    #This is used to change the rating of a meal in the listbox without having
    #  to remove it and add it again to the listbox with the new rating.
    def find_index_inListbox(self,my_item,listbox):
        index=0
        for item in listbox.get(0,END):
            if type(item)==unicode:
                item = self.normalize(item)
            if my_item in item:
                break
            index+=1
        return index

    #Removing an item from the list box
    def Remove(self):
        if type(self.rates_list.get(ACTIVE)) == unicode:
            meal=self.normalize(self.rates_list.get(ACTIVE)).split(' --> ')[0]
        else:
            meal=self.rates_list.get(ACTIVE).split(' --> ')[0]
        self.meals_rating_dict.pop(meal)
        self.rates_list.delete(ACTIVE)
        self.db["meals ratings"]=pickle.dumps(self.meals_rating_dict)

    '''
    #Any change in the user's ratings' list box gets stored in the meals-ratings dictionary,
    so that it is always updated with user's last change in his meals-ratings list.
    #The user-ratings database gets updated every time the meals-ratings dictionary gets any change from
    the user.
    '''
    # This is an alternative algorithm if we wish to merely deal with indeces, yet it might be easier as
    # we won't need to check for type(meal) in AddRating method
    def RemoveSelected(self):
        # try:
        #     selected_meal=self.rates_list.selection_get()
        #     for meal_index in range(len(self.meals_rating_dict)):
        #         if self.rates_list.get(meal_index)== selected_meal:
        #     self.rates_list.delete(meal_index)
        #     for meal_name in self.meals_rating_dict:
        #         if type(selected_meal) == unicode and type(meal_name) == unicode:
        #             if self.normalize(selected_meal).split(' --> ')[0] == self.normalize(meal_name):
        #                 self.meals_rating_dict.pop(meal_name)
        #                 break
        #         else:
        #             if selected_meal.split(' --> ')[0]== meal_name:
        #                 self.meals_rating_dict.pop(meal_name)
        #                 break
        #     self.db["meals ratings"]=pickle.dumps(self.meals_rating_dict)
        # except TclError:
        #     tkMessageBox.showerror("Error","No selected items to remove")
        pass

    #Getting the similar users
    def get_matches(self):
        try:
            x=int(self.nor.get())
            if x>500:
                raise ZeroDivisionError
        except ValueError:
            tkMessageBox.showerror("Error","Please enter a valid number of recommendations")
        except ZeroDivisionError:
            tkMessageBox.showinfo("Too much recommendations",
                                  "The number of recommendations should not exceed 500, which is quite enough")
        self.other_ratings["you"]=self.meals_rating_dict
        self.resultList.delete(0,END)
        self.get_metric()
        if self.method_check=='user':
            similarUsers=topMatches(self.other_ratings,"you",n=int(self.nor.get()),similarity=self.get_metric())
            self.get_recommendations()
        elif self.method_check=='item':
            self.other_ratings["you"]=self.meals_rating_dict
            similarUsers=[(self.meals_rating_dict[i],i) for i in self.meals_rating_dict.keys()]
            self.get_recommended_items()

        self.similarUsersList.delete(0,END)
        for user in similarUsers:
            self.similarUsersList.insert(END,'%s --> %s'%(user[1],user[0]))

    def get_metric(self):
        if self.metric.get()=="euclidean":
            sim_metric=sim_distance
        elif  self.metric.get()=="jaccard":
            sim_metric=sim_jaccard
        else:
            sim_metric=sim_pearson
        return sim_metric

    #Getting selected (focused or clicked-on from similarUsers list) similar user ratings,
    #and adding or showing them in the user ratings list
    def userRatings(self,event):
        try:
            self.userRatesList.delete(0,END)
            selecteditem=self.similarUsersList.selection_get().split(' -->')[0]
            method=self.recommendation_method()
            if method=='user':
                self.userRatesList.insert(END,selecteditem+' also rated the following')
                self.userRatesList.insert(1,'')
                for meal,rating in self.other_ratings[selecteditem].items():
                    self.userRatesList.insert(END,meal+' --> '+str(rating))
            elif method=='item':
                if type(selecteditem)==unicode:
                    selecteditem=self.normalize(selecteditem)
                similar_meals=topMatches(transformPrefs(self.other_ratings),selecteditem,
                                         n=int(self.nor.get()),similarity=self.get_metric())
                for rating,meal in similar_meals:
                    self.userRatesList.insert(END,meal+' --> '+str(rating))
        except KeyError:
            tkMessageBox.showinfo("Misunderstandig","Please click on Get Recommendation button to update result lists")

    #Checking for the recommendation method, and processing the recommendatino engine based on the output.
    def recommendation_method(self):
        method=self.method.get()
        try:
            if method == 'userBased':
                self.base='Users similar to you'
                self.base_details='Users ratings (select a user on the left)'
                self.method_check='user'
            elif method == 'itemBased':
                self.base='Select a meal'
                self.base_details='Similar meals'
                self.method_check='item'
            self.sim_ratings.config(text=self.base_details,width=30)
            self.sim_users.config(text=self.base,width=15)
            return self.method_check
        except ZeroDivisionError:
            tkMessageBox.showinfo("Unsufficient input",
                                  "You can try the following:\n1- add more ratings.\n"
                                  "2- decrease the number of recommendations.\n"
                                  "3- try different recommendation method.\n"
                                  "4- try different similarity metric.")

    def get_recommendations(self):
        self.resultList.delete(0,END)
        sim_metric=self.get_metric()
        self.other_ratings["you"]=self.meals_rating_dict
        for recommendation in getRecommendations(self.other_ratings,"you",sim_metric):
            self.resultList.insert(END,str(recommendation[0])+' --> '+str(recommendation[1]))
        self.resultList.delete(int(self.nor.get()),END)

    def get_recommended_items(self):
        self.resultList.delete(0,END)
        similar_items=calculateSimilarItems(self.other_ratings,int(self.nor.get()))
        for recommendation in getRecommendedItems(self.other_ratings,similar_items,'you'):
            self.resultList.insert(END,str(recommendation[0])+' --> '+str(recommendation[1]))
        self.resultList.delete(int(self.nor.get()),END)


if __name__=='__main__':
    root=Tk()
    root.geometry('1150x500')
    root.title("Cafe Crown Recommendation Engine")
    recommender=Recommender(root)
    root.mainloop()