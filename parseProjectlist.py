#!/usr/bin/env python
#coding: utf8
from datetime import datetime

#This python script is supposed to be run by the findOverdueProjectReviews.sh script.
#It parses the information of the IDS projectlist on https://ispe-qm.fzi.de/wiki/IDS-TKS-QM-Projektliste.
#The website is downloaded by the findOverdueProjectReviews.sh script beforehand.
#This python script does not access the website directly but only reads from the downloaded website.
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


#a class that provides methods to parse the projectlist website
class IDSPLParser:

  # constructor
  def __init__(self):
    self.projList = [['' for i in range(12)] for j in range(0)] #create a 2D list w/ 12 columns & 0 lines (lines are later added w/ "append")
    self.projList_raw = "empty"                                 #the website as raw as can be (see also IDSPLParser::readWebsite())
    self.start_idx=[]                                           #line in which the ith project starts
    self.end_idx=[]                                             #line in which the ith project ends


  #returns all the lines of the k-th project from projList_raw
  def getkthProject_raw(self, k):
    return_list=self.projList_raw[self.start_idx[k]:self.end_idx[k]]
    return return_list


  #gets a line in raw form and extracts the next data field
  def getNextEntry(self,str_line):
    str_line=str_line.replace(' ','')
    if str_line.find('</td></tr><tr><td>')==0: #which always marks the beginning of a line
      str_line = str_line[17:] # the length of '</td></tr><tr><td>' is 17. thats why there is a "17".
    elif str_line.find('</td><td>')==0:
      str_line = str_line[8:]
    entryEndIdx = str_line.find('</td><td>')
    entry = str_line[0:entryEndIdx]
    return entry


  # deletes the next entry and returns the string without this entry (would be better to do this directly in getNextEntry())
  def deleteNextEntry(self, str_line):
    str_line=str_line.replace(' ','')
  if str_line.find('</td><td>')>=0: #which marks the beginning of a new data field
    str_line = str_line[9+str_line.find('</td><td>'):] # add 9, because 9 is the length of '</td><td>'
    return str_line


  # read the plain website that has been downloaded by the script line by line and and save each line in a list
  def readWebsite(self):
    with open("IDS-TKS-QM-Projektliste") as website:
      self.projList_raw=website.readlines()
        for i in range(len(self.projList_raw)):
          self.projList_raw[i]=self.projList_raw[i].replace('\n','')


  # remove rubbish before and after projectList
  def removeGarbish(self):
    #find first occurence of "</td></tr><tr><td> IDS </td><td>". thats where the list starts...
    for i in range(len(self.projList_raw)):
      if self.projList_raw[i].find("</td></tr><tr><td> IDS </td><td>") >= 0:
        start_line = i
        self.projList_raw = self.projList_raw[start_line:]
        break
    #find first occurence of "</td></tr></table>". thats where the list ends...
    for i in range(len(self.projList_raw)):
      if self.projList_raw[i].find("</td></tr></table>") >= 0:
        end_line = i
        self.projList_raw = self.projList_raw[:end_line]
        break


  # find the first and last line of each project in projList_raw and safe the findings in self.start_idx and self.end_idx. (Before using this function, execute self.removeGarbish() in order to delete
  # the uninteresting parts of the website before and after the project list.)
  def findProjects(self):
    i=0
    while i < len(self.projList_raw):
      if self.projList_raw[i].find("IDS")>=0:
        self.start_idx.append(i) #first occurence of "IDS"
      if self.projList_raw[i].find('</td></tr><tr><td colspan="12">')>=0:
        self.end_idx.append(i)
      i+=1


  # parses the kth project by extracting the data from the projList_raw, which is a list(!!) of strings. The data gets written into the projList, which is a 2D matrix(!!) of strings, where each entry
  # corresponds exactly to the table entry on the website
  def parsekthProject(self, k):
    kthProj_raw = self.getkthProject_raw(k)
    kthProj_line = ['empty' for i in range(12)] # instanciate a new empty list with 12 columns 
    #Debugu: print self.getNextEntry(kthProj_raw[0])
    for i in range(12): #we know that there are 12 columns
      kthProj_line[i] = self.getNextEntry(kthProj_raw[0]) #caching of all entries of one project in one line
      kthProj_raw[0] = self.deleteNextEntry(kthProj_raw[0]) #deletes the data from the projList_raw list (remember, kthPoj_raw is a string
    #now, the next planned review date has to be extracted. it is in the last line of the project in the 10th column. if the project only has one line, we are good by now and can stop.
    if len(kthProj_raw)==1:
      self.projList.append(kthProj_line) #save the project data in the 2D list self.projList
      return      
    last_line_raw = kthProj_raw[len(kthProj_raw)-1]
    for i in range(9): #we are interested in the 10th entry -> so we need to delete the 9 before
       last_line_raw = self.deleteNextEntry(last_line_raw)
    kthProj_line[9] = self.getNextEntry(last_line_raw) 
    #delete the 10th entry from the raw version to get the 11th column
    last_line_raw = self.deleteNextEntry(last_line_raw)
    kthProj_line[10] = self.getNextEntry(last_line_raw)
    self.projList.append(kthProj_line) #save the project data in the 2D list self.projList


  # write mails to files
  def writeMailsToFile(self):
    kuerzelToMail = {'DA':'darius.azarfar@kit.edu', 'PB':'pascal.becker@fzi.de', 'GB':'bolano@fzi.de','JM':'mangler@fzi.de'}
    for k in range(len(self.projList)): #each line is a project so k is the number of the project
      #safe scheduled review as datetime
      date_str = self.projList[k][9]
      day_str = date_str[0:2]
      month_str = date_str[3:5]
      year_str = date_str[6:10]
      date = datetime(int(year_str), int(month_str), int(day_str))
      executionDate = self.projList[k][10]
      if datetime.now()>date and executionDate.find("J")==-1 and executionDate.find("X")==-1: #"J", if the review has been done. "X" if it was postponed.
        delta = str(datetime.now()-date)
        delta = delta[:delta.find(",")]
        TO = 'TO:   '+ self.projList[k][6]
        Subject = '\nSubject:   [QMB] Projectreview Reminder '+ self.projList[k][1]
        text = 'TO:   '+ self.projList[k][6]+ '\nSubject:   [QMB] !!! New reminder policies for 2018 !!! Projectreview Reminder '+ self.projList[k][1] + '\n\n\n!!!!!--------------NEW FOR 2018:---------!!!!!!!!! \n \nEscalation policy (starting february): \noverdue > 1 days: biweekly reminder mail (monday)\noverdue > 42 days: Arne in CC once \noverdue > 180 days: congrats, you are the new QMB\n\n\n---- Start of mail --- \n\n\nHello there,\n\nyou get this biweekly reminder because you are responsible for the project '+ self.projList[k][1] + ' and a project review or final review for this project is ' + delta + ' overdue.\nIf you are not responsible or the project review is not overdue, please let me know.\n \nFor instructions on how to do a project review please refer to https://ispe-qm.fzi.de/wiki/IDS-TKS-Processes (english).\nOr to https://ispe-qm.fzi.de/wiki/IDS-TKS_Prozesse (deutsch). \n\nTo get an overview of all projects and their scheduled review dates go to\nhttps://ispe-qm.fzi.de/wiki/IDS-TKS-QM-Projektliste.\n \nIn case of questions, please ask.  \n\nBest,\nSören, your friendly QMB '
        mailtext = TO + Subject + Text
        f = open('mails/To:' + self.projList[k][6] + ' - ' + self.projList[k][1] + '', 'w')
        f.write(mailtext)
    print "Mails have been prepared. Please send manually and move them to the correct Folder."


 # print overview of all overdue projects to console
  def printAllOverdue(self):
    print "Overdue Projectreviews"
    for k in range(len(self.projList)):
        #safe scheduled review as datetime
        date_str = self.projList[k][9]
        day_str = date_str[0:2]
        month_str = date_str[3:5]
        year_str = date_str[6:10]
        date = datetime(int(year_str), int(month_str), int(day_str))
        executionDate = self.projList[k][10]
        if datetime.now()>date and executionDate.find("J")==-1:
            delta = str(datetime.now()-date)
            delta = delta[:delta.find(",")]
            print ("ExecutionDate: "+ executionDate + " - " + delta + " overdue: " + self.projList[k][1]+ " guilty "+ self.projList[k][6] + " [ scheduled review: "+ self.projList[k][9]+" ]")



### ------------ MAIN ----------------- ###

#initialize class intsance that is used for the data extraction and parsing
parser = IDSPLParser()

#read website from file and save it as list of strings (each line in the list represents one line of the Website)
parser.readWebsite()

#remove everything before and after the ProjectList data
parser.removeGarbish()

#identify the start and the end line of a project and save it in self.start_idx[] and self.end_idx[]
parser.findProjects()

#parse each of the k projects that have been found
for k in range(len(parser.start_idx)):
  parser.parsekthProject(k)

#write emails as txt files in the folder /mails
parser.writeMailsToFile()

#print result to console
parser.printAllOverdue()
