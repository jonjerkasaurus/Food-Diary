#!/usr/bin/env python
import urllib
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
import json
import xlwt
import xlrd
import datetime
from xlutils.copy import copy
import os.path


#This is a Food Diary application that take 3 inputs (food, amount and unit)
#and looks up the food in the USDA API.  Nutrition info is calculated and written to
#an Excel file.

class USDA():
    def __init__(self):
        self.food = raw_input('Enter a food')
        #self.amount = raw_input('How much did you eat?')
        #self.unit = raw_input('grams? oz? cup? Tbl spoon?')
        self.usda_api = 'GP5A0NW2blnuGGXZSWDXTAJ38UpMrMpfp1JrnNPC'
        self.values = {'format': 'json', 'q': self.food, 'sort': 'n', 'max' : '100','offset': '0', 'api_key': self.usda_api}
        
        
    def unit_conversion(self, amount, unit):
        """The USDA API stores nutrition info in units per 100 grams, so if the amount and unit are
        given in terms of oz, it must be converted to grams"""
        #self.amount = int(self.amount)
        if unit == 'oz':
            amount = amount*28.35
        elif unit == 'cup':
            amount = amount*225
        elif unit == 'Tbl spoon':
            amount = amount*14.79
        
    def first_search(self):
        """This looks up a food in the USDA API and returns a selection for the user to choose"""
        try:
            data = urllib.urlencode(self.values)
            url = 'http://api.nal.usda.gov/usda/ndb/search/?' + str(data)
            json_obj = urllib2.urlopen(url)
            data2 = json.load(json_obj)        
            data3 = data2['list']
        #Display a list of search results, prompt the user to pick the item that best matches their search
        #and search database for that ndbno number.
            for items in data3['item']:
                print(items['name'])
                print(items['ndbno'])
        except HTTPError as e:
            print 'Could not find ' + food + '. Try another search.'
    
class USDA2():
    def __init__(self, food, amount):
        self.ndbno = raw_input('Enter the ndbno number of the food you want data for.')
        self.amount = amount
        self.usda_api = 'GP5A0NW2blnuGGXZSWDXTAJ38UpMrMpfp1JrnNPC'
        self.values = {'format': 'json', 'ndbno': self.ndbno, 'type': 'b', 'api_key': self.usda_api}
        self.data8 = {}
        self.date = ''
        self.exists = False
        self.nutrient_ids = ['255', '208', '203', '204', '205', '291', '269', '301',
                            '303', '304', '305', '306', '307', '309', '401', '404',
                            '405', '406', '415', '435', '418', '320', '323',
                            '324', '430', '606', '645', '646', '601']
        self.RDI = {'320':900, '401': 60 , '301':1000, '303':18,'324':400, '323':10, '430':80,
                    '404':1.5, '405':1.7, '406':20, '415':2, '435':400, '418':6, '305':1000,
                    '304':400, '309':15, '306': 3500}
        self.nutrient_names = ['Water', 'Energy (kcal)', 'Protein (g)', 'Total Fat (g)',
                                'Carbohydrate (g)', 'Fiber (g)',
                                'Sugars(g)', 'Calcium % RDI', 'Iron % RDI', 'Magnesium % RDI',
                                'Phosphorus % RDI', 'Potassium % RDI', 'Sodium (mg)', 'Zinc % RDI',
                                'Vitamin C % RDI', 'Thiamin % RDI', 'Riboflavin % RDI',
                                'Niacin % RDI', 'Vitamin B-6 % RDI', 'Folate % RDI', 'Vitamin B-12 % RDI',
                                'Vitamin A, RAE',  'Vitamin E % RDI',
                                'Vitamin D % RDI', 'Vitamin K % RDI',
                                'Fatty acids, total saturated (g)', 'Fatty acids, total monounsaturated (g)',
                                'Fatty acids, total polyunsaturated (g)', 'Cholesterol (g)']
        
    
    def second_search(self):
        """The user is prompted to enter the ndbno number of the food they ate.  THe program then searches the
        USDA API for that number and return nutrient info."""
        data4 = urllib.urlencode(self.values)
        url2 = 'http://api.nal.usda.gov/usda/ndb/reports/?' + str(data4)
        json_obj2 = urllib2.urlopen(url2)
        data5 = json.load(json_obj2)
        data6 = data5['report']
        data7 = data6['food']
        self.data8 = data7['nutrients']
        
    def todays_date(self):
        """Generates a string with today's date to be written to excel."""
        today = datetime.date.today()
        self.date = str(today.month) + '-' + str(today.day) + '-' + str(today.year)
    
    def convert_RDI(self):
        """Converts nutrient info for some nutrients into % RDI"""
        for items in self.data8:
            items['value'] = self.amount/100.0 * float(items['value'])
            if items['nutrient_id'] in self.RDI:
                items['value'] = (float(items['value'])/self.RDI[items['nutrient_id']])*100
            items['value'] = round(items['value'], 2)
    
    def excel_exists(self):
        self.exists = os.path.isfile('Food_Diary.xls')
        
    def write_to_excel1(self, food, amount):
        """This writes the nutrient info to MS Excel if Food Diary file already exists"""
        if self.exists == True:
            try:
                book = xlrd.open_workbook('Food_Diary.xls')
                sheet1 = book.sheet_by_name('Sheet 1')
                numRows = sheet1.nrows
                a1 = sheet1.cell_value(rowx=numRows-1, colx=1)
                if a1 != self.date: #If this is the first entry of the day,  skip down 2 rows.
                    numRows += 2
                
                wb = copy(book)
                w_sheet = wb.get_sheet(0)
                i = 3
                for items in self.data8:
                    temp_id = str(items['nutrient_id'])
                    if temp_id in self.nutrient_ids:
                        w_sheet.write(numRows, self.nutrient_ids.index(temp_id) + i, items['value'])     
                w_sheet.write(numRows, 0, food)
                w_sheet.write(numRows, 1, self.date)
                w_sheet.write(numRows, 2, amount)
                wb.save('Food_Diary.xls')
            except IOError:
                print 'Please close the Excel file and try again'
                
    def write_to_excel2(self, food, amount):
        """This creates Excel file and writes the nutrient info to it"""
        if self.exists == False:           
               book = xlwt.Workbook(encoding='utf-8')
               sheet1 = book.add_sheet('Sheet 1')
               i = 3
               
               for items in self.nutrient_names:
                   sheet1.write(0, i, items)
                   i += 1
               i = 3
               for items in self.data8:
                   temp_id = str(items['nutrient_id'])
                   if temp_id in self.nutrient_ids:
                       sheet1.write(1, self.nutrient_ids.index(temp_id) + i, items['value'])
               sheet1.write(1, 0, food)
               sheet1.write(1, 1, self.date)
               sheet1.write(1, 2, amount)
               sheet1.write(0, 0, 'Food')
               sheet1.write(0, 1, 'Date')
               sheet1.write(0, 2, 'Amount')
               book.save('Food_Diary.xls')
    
            
 
search1 = USDA()
valid = False
while valid == False:
    amount = raw_input('How much did you eat? Please enter a numeric value.')
    try:
        amount = float(amount)
    except ValueError:
        print 'Please enter a numeric value'
    if isinstance(amount, int) == True or isinstance(amount, float) == True:
        valid = True
valid = False
while valid == False:
    unit = raw_input('grams? oz? cup? ')
    UNITS = ['grams','gram', 'g', 'oz', 'ounce', 'ounces', 'cup', 'cups']
    if unit in UNITS:
        valid = True
        
search1.unit_conversion(amount, unit)
search1.first_search()
search2 = USDA2(search1.food, amount)
search2.second_search()
search2.todays_date()
search2.convert_RDI()
search2.excel_exists()
search2.write_to_excel1(search1.food, amount)
search2.write_to_excel2(search1.food, amount)
 

