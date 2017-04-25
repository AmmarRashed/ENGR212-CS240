import pandas, numpy as np
import matplotlib.pyplot as plt
import math, re
from Tkinter import *
from tkFileDialog import askopenfilename
from tkMessageBox import showinfo
from ttk import Combobox
# Time Spent on FaceBook and GPA
# Null Hypothesis: The effect of Facebook on GPA is due to chance.
# Alternative Hypothesis: The effect of Facebook on GPA is significant.

class LinearRegression:
    def __init__(self,data1, data2, type=None):
        data1 = list(data1)
        data2 = list(data2)
        if type == 'log':
            for i in range(len(data2)):
                data2[i] = math.log10(data2[i])
        self.data1 = data1  # 1)Time Spent on Facebook.
        self.data2 = data2  # 1)Gender, Age or GPA
        self.pool = None
        try:
            self.data2[0] + 0
            self.data1[0] + 0
        except TypeError:
            if 'M' in self.data2:
                self.data2 = self.numirate(self.data2)
            else:
                self.data1 = self.numirate(self.data1)
        self.dataDict = {}
        for i in range(len(self.data1)):
            self.dataDict.setdefault(self.data1[i],[])
            self.dataDict[self.data1[i]].append(self.data2[i])
        self.group1 = self.jointer([self.dataDict[sorted(self.dataDict.keys())[i]] for i in range(len(self.dataDict)/2)])
        if len(self.dataDict)%2 == 0:
            self.group2 = self.jointer([self.dataDict[sorted(self.dataDict.keys())[i]] for i in range(len(self.dataDict)/2,len(self.dataDict))])
        else:
            self.group2 = self.jointer([self.dataDict[sorted(self.dataDict.keys())[i]] for i in
                                        range(len(self.dataDict) / 2+1, len(self.dataDict))])
        self.slope, self.intercept = [float(x) for x in self.leastSquare(self.data1, self.data2)]
        self.xs = np.linspace(min(data1),max(data1),2)
        self.fit_line = []
        for x in self.xs:
            self.fit_line.append(self.linear_fit(x))
        self.fit = []
        for x in self.data1:
            self.fit.append(self.linear_fit(x))

    def jointer(self,ListOfLists):
        temp = []
        for i in ListOfLists:
            temp += i
        return temp

    def numirate(self, list):
        for gender in range(len(list)):
            if 'M' in list[gender]:
                list[gender] = 1
            else:
                list[gender] = 0
        return list

    def linear_fit(self, x):
        return self.intercept + self.slope * x

    def test_statistic(self, data):
        group1, group2 = data
        return abs(self.mean(group1)-self.mean(group2))

    def make_model(self):
        self.pool = np.hstack((self.group1,self.group2))

    def run_model(self):
        np.random.shuffle(self.pool)
        return self.pool[:len(self.group1)], self.pool[len(self.group1):]

    def pvalue(self, iter=1000):
        self.make_model()
        self.pool = np.ndarray.tolist(self.pool)
        diff_means = self.diffmeans(iter)
        actual_diffMean = abs(self.mean(self.group1) - self.mean(self.group2))
        p_counter = sum([1 for i in diff_means if i>actual_diffMean])
        return p_counter/float(iter)

    def diffmeans(self, iter=1000):
        return [self.test_statistic(self.run_model()) for i in range(iter)]

    def makePMF(self, valuesList):
        data = {}
        for number in valuesList:
            if number not in data:
                data[number] = 1
            else:
                data[number] += 1
        my_pmf = {}
        for number, freq in data.items():
            my_pmf[number] = float(freq) / sum(data.values())
        return my_pmf

    def makeCDF(self, pmfDict):
        my_cdf = {}
        for i in range(len(pmfDict.items())):
            if i == 0:
                my_cdf[i] = pmfDict.values()[i]
            else:
                my_cdf[i] = my_cdf[i - 1] + pmfDict.values()[i]
        return my_cdf

    def plotCDF(self):
        self.make_model()
        list = self.diffmeans()
        ys = self.makeCDF(self.makePMF(list)).values()
        xs = np.linspace(min(list),max(list),len(ys))
        plt.plot(xs, ys, 'r')

    def hypothesis_test(self, alpha=0.05):
        pvalue = self.pvalue()
        if pvalue<alpha:
            result = ('P-value = %g < %g\nNull Hypothesis rejected by difference in means statistic'%(pvalue, alpha))
        else:
            result = 'P-value = %g > %g\nNull Hypothesis is true by difference in means statistic' % (pvalue, alpha)
        return result

    def scatter_plot(self, type=None):
        fig = plt.figure()
        subplot = fig.add_subplot(111)
        if type == 'log':
            ys = [np.log10(i) for i in self.data2]
            fit = [np.log10(i) for i in self.fit_line]
            plt.scatter(self.data1, ys)
            plt.plot(self.xs, fit, 'g')
            plt.yscale('log')
        else:
            plt.scatter(self.data1, self.data2)
            plt.plot(self.xs, self.fit_line, 'g')


    def mean(self, data_list):
        return float(sum(data_list)) / len(data_list)

    def leastSquare(self, data1, data2):    # If we wish to use F statistic
        #   y = alpha + beta * x
        A = []
        b = []
        for i in range(len(data1)):
            A.append([1, data1[i]])
            b.append([data2[i]])
        A = np.matrix(A)
        b = np.matrix(b)
        # A.X = b
        # AT. A. X = AT. b
        # X = (AT.A).-1  . AT.b, where -1 means 'Inverse of the matrix' and X=(alpha, beta),
        # alpha is the intercept, and beta is the slope
        alphaBeta_array = (A.T * A).I * A.T * b
        slope = float(alphaBeta_array[1])
        intercept = float(alphaBeta_array[0])
        return slope, intercept

    def ESS(self):
        mean = self.mean(self.data2)
        return sum([(self.fit[i] - mean) ** 2 for i in range(len(self.data2))])

    def residuals(self):
        xs = np.asarray(self.data1)     # Time Spent on FB
        ys = np.asarray(self.data2)     # GPA
        res = [ys[student] - (self.intercept + self.slope * xs[student]) for student in range(len(xs))]
        xx = np.linspace(min(xs),max(xs),len(res))
        return xx, res

    def variance(self, xs):
        temp = 0
        for x in xs:
            temp += (x-self.mean(xs))**2
        return float(temp/float(len(xs)))

    def covariance(self, xs, ys):
        meanx = self.mean(xs)
        meany = self.mean(ys)     # mean is float(sum(xs))/len(xs)
        cov = 0
        for i in range(len(xs)):
            cov += (xs[i]-meanx)*(ys[i]-meany)
        cov /= (len(xs)-1)
        return cov

    def SSres(self):  # or RSS
        return sum([(self.data2[i] - self.fit[i]) ** 2 for i in range(len(self.fit))])

    def SStot(self):
        mean = self.mean(self.data2)
        return sum([(yi - mean)**2 for yi in self.data2])

    def Rsquared(self):
        return 1 - self.SSres()/self.SStot()
        # or alternatively:
        # return self.ESS()/self.SStot(ys)

    def test_significance_F(self):    # With F statistic
        # H0: beta1 = 0, No linear relationship and the slope is 0
        # H1: There is a linear relation ship and the |slope| > 0
        # _______ Using: F statistic ______
        k = 1  # as we have only one beta
        # k is the number of the degrees of freedom for the 'regressiors'
        MSE = self.ESS() / k  # Mean square of ESS or SSreg
        df_res = (len(self.data2) - (k + 1))  # degrees of freedom of the residuals
        MSR = self.SSres() / df_res  # Mean square of RSS or SSres
        F_static = MSE / MSR
        critical_level = 3.92217243   # from F-distribution table f(0.05, 1, 117)
        if F_static > critical_level:
            result = 'F-statistic = %g  >  critical_level= %g\nNull hypothesis rejected by F-statistic' % (F_static, critical_level)
        else:
            result = 'F-statistic = %g  <  critical_level= %g\nNull hypothesis is true by F-statistic' % (F_static, critical_level)
        return result

    def pearson_cof(self):
        xs = self.data1
        ys = self.data2
        return self.covariance(xs, ys)/float((self.variance(xs)**0.5)*(self.variance(ys)**0.5))

    def std(self, xs):
        return self.variance(xs)**0.5

class MultipleRegression:
    def __init__(self, indpnt_vars, depnt_var):
        # indpnt_vars = [[genders], [ages], [times]] according to what is provided
        # depnt_var = [GPA's]
        self.indpnt_vars = indpnt_vars
        self.depnt_var = depnt_var
        self.fit = None
        # If we have gender variable, M or F, we substitute M by 1, and F by 0
        for i in range(len(self.indpnt_vars)):
            if 'M' in self.indpnt_vars[i]:
                self.indpnt_vars[i] = self.numirate(self.indpnt_vars[i])
            break
        if 'M' in self.depnt_var:
            self.depnt_var = self.numirate(self.depnt_var)
        self.intercept, self.betas = self.multiple_regression_fit()
        self.my_errors = self.errors()

    def numirate(self, list):
        for gender in range(len(list)):
            if 'M' in list[gender]:
                list[gender] = 1.0
            else:
                list[gender] = 0.0
        return list


    def multiple_regression_fit(self):
        # Y = alpha + beta1 * x1 + beta2 * x2 + ... + beta_n * x_n
        # data should be in that form: [[x11,x21,x31,y11],[x21,x22,x32,y22]]
        # e.g. age:20, FB hours: 300, GPA: 3.55>>> data = [[20,300,3.55]]
        A = []
        b = []
        for i in range(len(self.depnt_var)):
            temp = [1]
            for var in range(len(self.indpnt_vars)):
                temp.append(self.indpnt_vars[var][i])
            A.append(temp)
            b.append([self.depnt_var[i]])
        A = np.matrix(A)
        b = np.matrix(b)
        X = (A.T * A).I * A.T * b
        intercept = float(X[0])
        betas = []
        for beta in X[1:]:
            betas.append(float(beta))
        return intercept, betas

    def mean(self, list):
        return sum(list)/float(len(list))

    def errors(self):
        # _____________________RESIDUALS__________________________
        self.fit = self.intercept
        vars = {}
        for b in range(len(self.betas)):
            self.fit += self.betas[b]*np.array(self.indpnt_vars[b])
        residuals = [self.depnt_var[i] - self.fit[i] for i in range(len(self.depnt_var))]
        self.SSres = sum([i**2 for i in residuals])
        return {'R-squared': self.R_squared(self.depnt_var), 'residuals': residuals}

    def SStot(self, varlist):    # or TSS
        mean = self.mean(varlist)
        return sum([(yi - mean)**2 for yi in varlist])

    def ESS(self):
        mean = self.mean(self.depnt_var)
        return sum([(fi - mean)**2 for fi in self.fit])

    def R_squared(self, ys):
        return 1 - (self.SSres/self.SStot(ys))
        # OR alternatively
        # return self.ESS()/self.SStot(ys)

    def adjusted_R2(self, R2, n, k):
        return 1-(1-R2)*((n-1)/float(n-k-1))

    def test_significance(self):
        self.errors()
        # H0: beta1 = beta2 = beta3 = 0, No linear relationship
        # H1: At least one coefficient is not zero, at least one X variable (gender, age or time spent on FB)
        # affects Y (student's GPA)
        # _______ Using: F statistic ______
        k = len(self.indpnt_vars)    # as we have beta1, beta2,..., beta_k, we have three independent variables
        # k is the number of the degrees of freedom for the 'regressiors'
        MSE = self.ESS()/k  # Mean square of ESS or SSreg
        df_res = (len(self.depnt_var) - (k + 1))     # degrees of freedom of the residuals
        MSR = self.SSres/df_res      # Mean square of RSS or SSres
        # print self.ESS()+self.SSres(self.depnt_var)
        # print self.SStot(self.depnt_var, self.mean(self.depnt_var))
        F_static = MSE/MSR
        if k == 3:
            critical_level = 2.68349915  # from F-distribution table f(0.05, 3, 115)
        elif k == 2:
            critical_level = 3.07444726  # from F-distribution table f(0.05, 2, 116)

        if F_static > critical_level:
            result = 'F-statistic = %g  >  critical_level= %g\nNull hypothesis rejected\n' \
                  'At least one of these variables is statistically ' \
                  'significant in affecting the student\'s GPA'%(F_static,critical_level)
        else:
            result = 'F-statistic = %g  <  critical_level= %g\n' \
                  'Null hypothesis is true\n' \
                  'None of these variables is statistically significant in affecting student\'s GPA' \
                  '' % (F_static, critical_level)

        return result

class GUI(Frame):
    def __init__(self,parent, color):
        self.data_file = None
        self.dependant_var = None
        self.color = color
        self.parent = parent
        self.parent['bg'] = self.color
        self.parent.title("Guess My Grade! v1.0")
        Label(self.parent, text="Hypothesis Testing and Regression", fg="white", bg="royalblue4",
                        font='Georgia 20 bold').pack(side=TOP, fill=X)
        self.headFrame = Frame(self.parent, bg=self.color)
        self.headFrame.pack(side=TOP, fill=X, pady=10)
        Label(self.headFrame, text="Please upload your data-set xls file:", fg="blue4",
                       font=("Georgia", 14), bg=self.color).grid(row=1, column=1)
        self.b1 = Button(self.headFrame, command=self.browse)
        self.button(self.b1,"Browse")
        self.b1.grid(row=1, column=2, padx=100)
        self.catLB = Listbox(self.headFrame, selectmode=MULTIPLE, width=30, height=7)
        self.catLB.bind('<<ListboxSelect>>', self.getVars)
        self.catLB.grid(row=2, column=1, pady=10)
        self.b2 = Button(self.headFrame, command=self.analyze_data)
        self.b2.grid(row=2, column=2)
        self.button(self.b2, 'Analyze Data')
        self.b3 = Button(self.headFrame)
        self.logCB = IntVar()
        Checkbutton(self.headFrame, text='Log scale', font='Calibri 14 bold', bg=self.color, variable=self.logCB ).grid(row=2, column=3)
        self.dp_var = StringVar()
        self.dep_var = Combobox(self.headFrame, width=10, textvariable=self.dp_var)
        self.dplabel = Label(self.headFrame, text='Select the dependant variable:', bg=self.color)
        self.predictor = StringVar()
        Entry(self.headFrame, textvariable=self.predictor).grid(row=3,column=3)
        self.b = Button(self.headFrame,command=self.predict)
        self.button(self.b,'Predict')
        self.b.grid(row=3, column=4, padx=10)
        self.betasButton = Button(self.headFrame, command=self.betas)
        self.button(self.betasButton, text='Intercept and Slopes')
        self.betasButton.grid(row=3, column=2)
        self.canvas = Canvas(self.parent, bg='honeydew', bd=1, relief=GROOVE)
        self.canvas.pack(side=TOP, fill=BOTH, expand=1)

    def button(self, button, text):
        button.config(text=text, bg='brown', fg='white', cursor='hand2', font='Calibri 14 bold')

    def browse(self):
        self.data_file = pandas.read_csv(askopenfilename())  # {'Gender':[M,F,M,M,...etc],'Age':[18,19,20,...etc],...etc}
        for cat in self.data_file.keys():
            self.catLB.insert(END,cat)

    def getVars(self, event):
        self.vars = []
        self.indx = []
        for i in self.catLB.curselection():
            self.vars.append(self.catLB.get(i))
            self.indx.append(i)
        self.dep_var['values'] = self.vars
        if len(self.vars)>1:
            self.dep_var.grid(row=4, column=1)
            self.dplabel.grid(row=3, column=1)
            self.dep_var.current(0)
            self.b.config(text='Predict %s' % self.dp_var.get())
            self.dep_var.bind("<<ComboboxSelected>>", self.selectLB)
        else:
            self.dep_var.grid_forget()
            self.dplabel.grid_forget()

    def selectLB(self, event):
        self.b.config(text='Predict %s' % self.dp_var.get())
        for i in self.indx:
            self.catLB.selection_set(i,i)

    def analyze_data(self):
        temp = self.vars
        if len(self.vars) < 2:
            showinfo('Error','Please select at least two  variables')
        elif len(self.vars) == 2:
            data1 = list(self.data_file[self.vars[0]])
            data2 = list(self.data_file[self.vars[1]])
            reg = LinearRegression(data1, data2)
            s = self.vars[1]
            if self.logCB.get():
                reg.scatter_plot(type='log')
                s = 'log(%s)' % self.vars[1]
            else:
                reg.scatter_plot()
            title = '%s vs %s' % (s, self.vars[0])
            plt.title(title)
            plt.xlabel(self.vars[0])
            plt.ylabel(s)

            plt.figure(2)
            xx, res = reg.residuals()
            plt.scatter(xx,res)
            plt.title('Residuals')
            plt.xlabel(self.vars[0])
            plt.ylabel('Residual')
            if self.logCB.get():
                plt.yscale('log')

            plt.figure(3)
            reg.plotCDF()
            plt.title('Permutation test')
            plt.xlabel('Difference in means')
            plt.ylabel('CDF')
            if self.logCB.get():
                plt.yscale('log')
            self.display_result1(reg)
            plt.show()
        else:
            my_vars = [var for var in self.vars if var != self.dp_var.get()]
            self.dp_var.get()
            self.indpnt_vars = []
            for indpnt in my_vars:
                self.indpnt_vars.append(list(self.data_file[indpnt]))
            self.dependant_var = list(self.data_file[self.dp_var.get()])
            multiple_reg = MultipleRegression(self.indpnt_vars, self.dependant_var)
            self.display_result2(multiple_reg, my_vars)

    def betas(self):
        try:
            if len(self.vars) < 2:
                showinfo('Error', 'Please select at least two  variables')
            elif len(self.vars) == 2:
                data1 = list(self.data_file[self.vars[0]])
                data2 = list(self.data_file[self.vars[1]])
                reg = LinearRegression(data1, data2)
                showinfo('Betas', 'Intercept = %g\nSlope = %g' % (reg.intercept, reg.slope))
            else:
                multiple_reg = MultipleRegression(self.indpnt_vars, self.dependant_var)
                betas = 'Intercept = %g\n' % multiple_reg.intercept
                modelBetas = multiple_reg.betas
                for beta in range(len(modelBetas)):
                    betas += 'Beta%d = %g\n' %(beta, modelBetas[beta])
                showinfo('Betas', betas)
        except AttributeError:
            showinfo('ERROR', 'Analyze the data first')

    def display_result1(self, model):
        self.canvas.delete(ALL)
        result = model.hypothesis_test()
        result += '\n%s\t\t Mean of %s = %g\n' % \
                  (model.test_significance_F(),self.vars[0], model.mean(model.data1))
        result += '\nPearson Correlation Coefficient = \t%g\tMean of %s = %g\nR-squared = \t\t\t%g' % \
                  (model.pearson_cof(), self.vars[1], model.mean(model.data2), model.Rsquared())
        SS = ['SSres = %g' % model.SSres(), 'SSreg = %g' % model.ESS(), 'SStot = %g' % model.SStot()]
        result += '\n\n%s\n%s\n%s' % (SS[0], SS[1], SS[2])
        self.canvas.create_text(5,5, text=result, font='Calibri 16 bold', anchor=NW,fill='blue4')

    def display_result2(self, model, my_vars):
        self.canvas.delete(ALL)
        significance = model.test_significance()
        SS = ['SSres = %g' % model.SSres, 'SSreg = %g' % model.ESS(), 'SStot = %g' % model.SStot(self.dependant_var), '']
        result_text = 'Variable\t\tParameter Estimate\n\nIntercept\t\t%g\t\t\t%s\n' %(model.intercept, SS[0])
        for i in range(len(my_vars)):
            check = 0
            if 'Spend' in my_vars[i]:
                result_text += my_vars[i] + '\t%g\t\t%s\n' % (model.betas[i], SS[i+1])
                check = 1
            elif 'Age' not in my_vars and 'Gender' in my_vars[i]:
                result_text += my_vars[i] + '\t\t%g\t\t\t%s\n' % (model.betas[i], SS[i + 1])
                check = 1
            elif 'Age' in my_vars[i] or 'Gender' in my_vars[i]:
                if 'Spend' in self.dp_var.get():
                    result_text += my_vars[i] + '\t\t%g\t\t\t%s\n' % (model.betas[i], SS[i + 1])
                else:
                    result_text += my_vars[i] + '\t\t%g\t\t%s\n' % (model.betas[i], SS[i + 1])
                check = 1
            if check == 1: continue
            result_text += my_vars[i] + '\t\t%g\t\t%s\n' % (model.betas[i], SS[i+1])
        result_text += '\n R-Squared =\t%g\n' % model.errors()['R-squared']
        result_text += '%s' % significance
        self.canvas.create_text(5, 5, text=result_text, font='Calibri 16 bold', anchor=NW, fill='blue4')

    def predict(self):
        try:
            if len(self.vars) < 3:
                data2 = list(self.data_file[self.dp_var.get()])
                temp = [i for i in self.vars if self.dp_var.get() not in i]
                data1 = list(self.data_file[temp[0]])
                reg = LinearRegression(data1, data2)
                prediction = reg.linear_fit(int(self.predictor.get()))
                if 'Gender' in self.dp_var.get():
                    prediction = round(prediction)
                    if prediction != 1 and prediction != 0:
                        raise ValueError

                showinfo('Prediction','Predicted %s = %g' % (self.dp_var.get(), prediction))
            else:
                try:
                    multiple_reg = MultipleRegression(self.indpnt_vars, self.dependant_var)
                    xs = re.findall(re.compile('\d+'),self.predictor.get())
                    for i in range(len(xs)):
                        xs[i] = float(xs[i])
                    prediction = sum([multiple_reg.betas[i]*xs[i] for i in range(len(self.indpnt_vars))]) + multiple_reg.intercept
                    if 'Gender' in self.dp_var.get():
                        prediction = round(prediction)
                    showinfo('Prediction', 'Predicted %s = %g' % (self.dp_var.get(), prediction))
                except IndexError:
                    showinfo('Error', 'Insufficient predictors')
                except AttributeError:
                    showinfo('Error', 'Please analyze the data first')
        except ValueError:
            showinfo('Gender is 1 for Male and 0 for Female')

if __name__ == '__main__':
    root = Tk()
    GUI(root, 'honeydew')
    root.geometry('900x600')
    root.mainloop()


