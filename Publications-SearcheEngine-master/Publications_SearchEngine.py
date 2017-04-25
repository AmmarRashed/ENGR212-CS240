from Tkinter import *
from ttk import Button, Scrollbar
from bs4 import BeautifulSoup
from urllib2 import *
import shelve, tkMessageBox, re, math, timeit

ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

class SearchEngine(Frame):
    def __init__(self, parent, color):
        self.parent = parent
        self.color = color
        self.parent['bg'] = self.color
        self.url = None
        self.soup = None
        self.text = None
        self.wordlocation = {}
        # {publication: {word: count}}
        self.links = {}
        # {publication1:[link1, link2 , ...etc], publication2:[link1, link3, ...etc]}
        self.citations = {}
        # {publication : number of citations}
        self.categories = {}
        # {category : [publications]}
        self.filtered_publications = []
        self.page = StringVar()
        self.page.set(1) # Page number, used in self.paging method
        # HEADER ----------------------------------------------------------------
        Label(self.parent, text='SEHIR Scholar', font='Calibri 26 bold', fg='white', bg='deepskyblue4').pack(fill=X)
        # URL Entering Frame ----------------------------------------------------
        self.urlFrame = Frame(self.parent, bg=self.color)
        self.urlFrame.pack(side=TOP)
        Label(self.urlFrame, text='Url for faculty list:', bg=self.color).grid(row=1, column=1, pady=8)
        self.url = StringVar()
        self.urlEntry = Entry(self.urlFrame, textvariable=self.url, width=70).grid(row=1, column=2, padx=8)
        Button(self.urlFrame, text='Build Index', cursor='hand2', command=self.read_db).grid(row=1, column=3, padx=10)
        # Keywords for searching
        self.keyWord = StringVar()
        Entry(self.parent, textvariable=self.keyWord, font='Calibri 18', width=50).pack(side=TOP,pady=5)
        # Settings Frame --------------------------------------------------------
        self.settingFrame = Frame(self.parent, bg=self.color)
        self.settingFrame.pack(side=TOP)
        # Ranking Criteria
        Label(self.settingFrame, text='Ranking Criteria', bg=self.color).grid(row=1, column=1,sticky=W)
        self.var_freq = IntVar()
        self.var_freq.set(1)
        self.wordFreqCB = Checkbutton(self.settingFrame, text='Word Frequency', variable=self.var_freq,
                                      command=self.search, cursor='hand2', bg=self.color)
        self.wordFreqCB.grid(row=2, column=1)
        self.var_cit = IntVar()
        self.var_cit.set(1)
        self.citationCountCB = Checkbutton(self.settingFrame, variable=self.var_cit, text='Citation Count',
                                           command=self.search, cursor='hand2', bg=self.color)
        self.citationCountCB.grid(row=3,column=1, sticky=W)
        # Weight
        Label(self.settingFrame, text='Weight', bg=self.color).grid(row=1, column=2, padx=30, sticky=W)
        self.wordFreq = StringVar()
        self.citationCount = StringVar()
        Entry(self.settingFrame, textvariable=self.wordFreq, width=3).grid(row=2, column=2)
        Entry(self.settingFrame, textvariable=self.citationCount, width=3).grid(row=3, column=2)
        # Filter Papers
        Label(self.settingFrame, text='Filter Papers', bg=self.color).grid(row=1, column=3)
        self.filterLB = Listbox(self.settingFrame, selectmode=MULTIPLE, width=25, height=6)
        self.filterLB.grid(row=2, rowspan=2, column=3)
        self.scrollbarLB = Scrollbar(self.settingFrame, orient=HORIZONTAL, command=self.filterLB.xview)
        self.filterLB['xscrollcommand'] = self.scrollbarLB.set
        self.scrollbarLB.grid(row=4, column=3, sticky=E+W)
        Button(self.settingFrame, text='Search', cursor='hand2', command=self.search).grid(row=2, column=4, padx=8)
        self.textFrame = Frame(self.parent, bg=self.color)
        self.textFrame.pack(side=TOP, pady=(30,0))
        self.runtime = StringVar()
        Label(self.textFrame, bg=self.color, fg='red', textvariable=self.runtime).pack(side=TOP, anchor=W)
        self.text = Text(self.textFrame, wrap=WORD, font='Calibri 10', width=100, height= 15)
        self.sb = Scrollbar(self.textFrame, command=self.text.yview)
        self.text['yscrollcommand']=self.sb.set
        self.sb.pack(side=RIGHT,ipady=100)
        self.text.pack(side=RIGHT)
        self.pagesFrame = Frame(self.parent, bg=self.color)
        self.pagesFrame.pack(side=TOP)
        self.previousB = Button(self.pagesFrame)
        self.nextB = Button(self.pagesFrame)
        self.pageLabel = Label(self.pagesFrame)
        self.currentPage = Label(self.pagesFrame)
        self.page_list = {}
        self.end_time = 0 # to calculate the run time, called in search method
        self.start_time = 0
        self.double_ranking = {}
        self.citation_scores = {}
        self.freq_scores = []
    def read_db(self):
        self.db = shelve.open('searchingDatabase.db', 'c')
        self.filterLB.delete(0,END)
        try:
            self.wordlocation = self.db['words']
            # {publication: {word: count}}
            self.citations = self.db['citations']
            # {publication : number of citations}
            self.categories = self.db['categories']
            # {category : [publications]}
        except KeyError:
            self.read_url()
            self.db['words'] = self.wordlocation
            self.db['citations'] = self.citations
            self.db['categories'] = self.categories
        except ValueError:
            tkMessageBox.showerror('URL error', 'Please enter a valid URL or check your internet connection')
        for category in sorted(self.categories):
            self.filterLB.insert(END, category)
        self.filterLB.select_set(0, END)

    # FETCHING DATA AND CRAWLING BLOCK ---------------------------------------------
    def read_url(self):
        try:
            self.soup = BeautifulSoup(urlopen(self.url.get()), 'html.parser')
            professors = self.soup.find(class_="box first")
            link_repetetion_check = []
            for tag in professors.find_all('a'):
                link = "http://cs.sehir.edu.tr" + str(tag.get('href', None))
                try:
                    if not (link in link_repetetion_check):
                        self.fetch_publications(link)
                        link_repetetion_check.append(link) # making sure that we don't visit the same link twice
                        # It is not needed in this project, yet it is a good habit to have in crawling!
                except httplib.InvalidURL:
                    pass
            self.word_location_count()
        except ValueError:
            tkMessageBox.showerror('URL error', 'Please enter a valid URL')
        except URLError:
            tkMessageBox.showerror('URL error', 'Please enter a valid URL or check your internet connection')

    def fetch_publications(self, link):
        soup = BeautifulSoup(urlopen(link), 'html.parser')
        # This is for the citation count
        # {publication1:[link1, link2 , ...etc], publication2:[link1, link3, ...etc]}
        all_publications = soup.find(id='publication')
        cit_pat = '\d+\s+Citations'  # e.g [40 Citations]
        cit_patn = '\d+'  # e.g 40
        category_counter = 0
        for cat in all_publications.find_all('ul'):  # looping through every category in the page
            categories = all_publications.find_all('p')
            for category in categories:
                self.categories.setdefault(category.text, [])
            for pub in cat.find_all('li'):
                # Looping through every publication in that link
                # Getting the text of the publication and getting rid of excessive spaces
                # and appending them to the publication list
                publication = re.compile('\s+').sub(' ', pub.text)
                publication = publication[len(re.findall('\d+.', publication)[0])+1:] # Getting rid of the publication
                # number in that link, as we cannot compare them with others from other pages as they will more likely
                # be different according to the number even if they are the same publications.
                category = categories[category_counter]
                self.categories[category.text].append(publication)  # {category : [publications]}
                self.links.setdefault(publication, [link]) # {publication:[links]}
                if link not in self.links[publication]:
                    self.links[publication].append(link)
                try:
                    self.citations[publication] = int(re.findall(cit_patn, re.findall(cit_pat, pub.a.text)[0])[0])
                except:
                    self.citations[publication] = 0
            category_counter += 1
            # {publication : number of citations}
            # Here we add the number of citations mentioned in the page (e.g [40 citation]) plus
            # the number of cs professors publications pages that publication was mentioned in.

    def word_location_count(self):
        # Here we get each word in each publication and index it with the frequency of its appearance
        # and in which publication it appeared with that frequency.
        # {word:{frequency:publication}}
        for pub in self.links:
            self.getFreqs(pub)
        # {publication :{word :count} }

    # Computing the frequency of each word in each frequency
    def getFreqs(self, text):  # {publication:{word:count}}
        cleaned_text = re.compile('[^A-Za-z0-9]').sub(' ', text)
        words = re.split('\s+',cleaned_text)
        for word in words:
            word = word.lower()
            if not (word in ignorewords) and len(word) > 3:  # the, of, to, and ...
                self.wordlocation.setdefault(text, {word: 0})
                self.wordlocation[text].setdefault(word, 0)
                temp = self.wordlocation[text][word]
                self.wordlocation[text][word] = temp + 1.0  #/len(words)

    # SEARCHING BLOCK ------------------------------------------------------------------------------
    def search(self):
        self.start_time = timeit.default_timer()
        try:
            self.freq_scores = []
            self.double_ranking = {}
            self.text.delete(0.0, END)
            publications = []
            pub_scores = {} # {publication : score}
            filtered = self.filter_categories(self.selected_categories())
            # {publication:[{word:count},number of citations]}
            for publication in filtered:
                for key_word in re.split('\s+',self.keyWord.get()):
                    if key_word.lower() in filtered[publication][0]:
                        pub_scores.setdefault(publication, 1)
                        temp = pub_scores[publication]
                        pub_scores[publication] = temp * self.rank_method(filtered, publication, key_word)
            pub_scores_normalized = self.normalizescores(pub_scores)
            for pub in pub_scores_normalized:
                publications.append([pub_scores_normalized[pub],pub])
            # RANKING ---------------------------------------------------
            results = sorted(publications)[::-1]  # [[publication, score]] sorted from maximum to minimum score
            for count in range(len(results)):
                results[count][1] = str(count+1)+'.\t' + results[count][1]
            pages = int(math.ceil(len(results) / 10.0))
            self.page_list = {}
            # Separating pages, each will have maximum 10 publications
            for page in range(pages):
                start = page*10
                limit = (page+1)*10
                self.page_list[page+1] = results[start:limit] # {page number : [[publication, score]]}
            self.end_time = timeit.default_timer()
            self.paging()
        except TypeError:
            self.text.delete(0.0,END)
            self.page.set(1)
            self.nextB['state'] = DISABLED
            self.previousB['state'] = DISABLED
            tkMessageBox.showerror('ERROR','choose at least one ranking measure')
        except ValueError:
            self.text.delete(0.0,END)
            self.page.set(1)
            self.nextB['state'] = DISABLED
            self.previousB['state'] = DISABLED
            if len(self.filterLB.curselection())==0:
                tkMessageBox.showerror('ERROR', 'choose at least one ranking measure')
            elif len(self.wordFreq.get()) < 1 or len(self.citationCount.get()) < 1:
                tkMessageBox.showerror('ERROR', 'Please enter a valid weight')
            else:
                try:
                    int(self.wordFreq.get())
                    int(self.citationCount.get())
                except TypeError:
                    tkMessageBox.showerror('ERROR', 'Please enter a valid weight')
                if len(self.keyWord.get()) < 3:
                    tkMessageBox.showerror('ERROR', 'Please enter a proper key word for searching')
                else:
                    tkMessageBox.showerror("ERROR", "Could not find the keyword in the database")

    def rank_method(self, scores_dict, publication, word):
        # scores_dict = {publication:[{word:count},number of citations]}
        freq_score = scores_dict[publication][0][word]
        citation_score = scores_dict[publication][1]
        if self.var_freq.get() and self.var_cit.get():
            self.double_ranking[publication]=[freq_score,max(citation_score,1)] # {publication:[freq_score,citation_score]}
            self.citation_scores[publication] = max(citation_score,1)
            self.freq_scores.append(freq_score)
            # return freq_score*self.wordFreq.get() + citation_score*self.citationCount.get()
            return 1
        elif self.var_freq.get():
            return int(freq_score)
        elif self.var_cit.get():
            return int(citation_score)
        else:
            raise TypeError

    def normalizescores(self, scores, smallIsBetter=0): # from mysearchengine.py
        if self.var_freq.get() and self.var_cit.get():  # mingling freq score and citation score together
            for pub in scores:  #{pub : score} in that case all the scores were 1
                freq_score = self.double_ranking[pub][0]
                citation_score = self.double_ranking[pub][1]
                mingling_ratio = max(self.citation_scores.values())/float(max(self.freq_scores))
                # getting freq_score closer to the citation_score
                mingled_score = freq_score*int(self.wordFreq.get())*mingling_ratio \
                                + citation_score*int(self.citationCount.get())
                scores[pub] = mingled_score
        vsmall = 0.00001  # Avoid division by zero errors
        if smallIsBetter:
            minscore = min(scores.values())
            minscore = max(minscore, vsmall)
            return dict([(u, float(minscore) / max(vsmall, l)) for (u, l) \
                         in scores.items()])
        else:
            maxscore = max(scores.values())
            if maxscore == 0:
                maxscore = vsmall
            return dict([(u, float(c) / maxscore) for (u, c) in scores.items()])
        # I personally have a problem with this algorithm, since I think we should simply divide each word count
        # by the number of words in the publication it was mentioned in. And that could simply be applied in
        # get_freq method as referred there

    def selected_categories(self): # Capturing selected categories
        items = []
        chosen_categories = []
        items = map(int, self.filterLB.curselection())
        for cat_indx in range(len(items)):
            chosen_categories.append(self.filterLB.get(items[cat_indx]))
        return chosen_categories
        # I used some code from this link:
        # http://stackoverflow.com/questions/13828531/problems-in-python-getting-multiple-selections-from-tkinter-listbox

    def filter_categories(self, cat_list):
        publicattions = {}  # {publication:[{word:count},number of citations]}
        for cat in cat_list:
            for pub in self.categories[cat]:
                publicattions[pub] = [self.wordlocation[pub], self.citations[pub]]
        return publicattions

    def paging(self):
        self.page.set(1)
        self.pageLabel.config(bg=self.color, text='Page: ')
        self.pageLabel.pack(side=LEFT)
        self.previousB.config(text='Previous', command=self.previous)
        self.previousB.pack(side=LEFT, padx=10)
        self.currentPage.config(bg='white', textvariable=self.page, relief=GROOVE)
        self.currentPage.pack(side=LEFT, ipadx=5)
        self.nextB.config(text='Next', command=self.Next)
        self.nextB.pack(side=LEFT, padx=10)
        self.buttons_states()
        self.show_page()

    def previous(self):
        if self.var_freq.get() or self.var_cit.get():
            self.page.set(int(self.page.get())-1)
            self.buttons_states()
            self.show_page()

    def Next(self):
        if self.var_freq.get() or self.var_cit.get():
            self.page.set(int(self.page.get()) + 1)
            self.buttons_states()
            self.show_page()



    def buttons_states(self):
        n = len(self.page_list)
        if int(self.page.get()) == 1:
            self.previousB['state'] = DISABLED
        else:
            self.previousB['state'] = NORMAL

        if n > 1 and int(self.page.get())<n:
            self.nextB['state'] = NORMAL
        else:
            self.nextB['state'] = DISABLED

    def show_page(self):
        self.text.delete(0.0, END)
        countPublications = (len(self.page_list)-1)*10 + len(self.page_list[max(self.page_list.keys())])
        self.text.tag_config('word', foreground='blue', font=('Calibri 11 bold'))
        self.text.tag_config('score', foreground='red', font=('Calibri 10 bold'))
        for publication in self.page_list[int(self.page.get())]:
            self.text.insert(END,publication[1] +' '+ str(publication[0])+'\n'*2)
            self.highlight(str(publication[0]), 'score')
        for word in re.split('\s+', self.keyWord.get()):
            self.highlight(word, 'word')  # Highlighting lower case (e.g  'data')
            self.highlight(word.upper()[0]+word[1:], 'word') # e.g 'Data'
            self.highlight(word.upper(), 'word') # e.g  'AICCSA'
        self.runtime.set('%d publications (%g Seconds)' %(countPublications,self.end_time - self.start_time))

    def highlight(self, keyword, tag):
        pos = '1.0'
        while True:
            idx = self.text.search(keyword, pos, END)
            if not idx:
                break
            pos = '{}+{}c'.format(idx, len(keyword))
            self.text.tag_add(tag, idx, pos)
        # I used some code from:
            # http://stackoverflow.com/questions/17829713/tkinter-text-highlight-specific-lines-using-keyword
if __name__ == '__main__':
    root = Tk()
    o = SearchEngine(root, 'honeydew')
    root.geometry('1000x600')
    root.mainloop()