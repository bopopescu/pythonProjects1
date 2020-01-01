import logging
import logging.config
from csvWriter import CsvWriter
from csvReader import CsvReader
from seleniumextractor import SeleniumExtractor

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium_error import *
import config as cfg
import datetime
from collections import OrderedDict
import re
import time
import sys
print sys.getdefaultencoding()

""" logging configureation done here """
logging.config.fileConfig('logging.conf')

# create logger
logger = logging.getLogger('logger_bonus')

""" get the file location and other configuration"""

#static_link_file = cfg.settings['STATIC_LINK_FILE']
abspath = cfg.settings['ABS_PATH']
bonus_file = cfg.settings['BONUS']

csvwriter = CsvWriter(abspath,bonus_file,"SYMBOL,ADJUSTMENT_TYPE,DATE,FACTOR,URL,NSE")
csvwriter.writefile_header()



def get_adjustment_factor(factor_type,factor):
    factor_ret = 1
    split_str = factor.split(":")
    arg1 = float(split_str[1])
    arg2 = float(split_str[0])
    if (factor_type == 'bonus'):     
        sum = arg1 + arg2
        factor_ret = (arg1/sum)
    if(factor_type == 'split'):
        factor_ret = arg1/arg2
        print("inside split")
    return(factor_ret)

def get_bonus_list():
    years_of_bonus = ['2017','2018','2019']
    bonus_url = 'https://www.moneycontrol.com/stocks/marketinfo/bonus/index.php'
    bonus_list = []
    for year in years_of_bonus:
        try:
            selextractor = SeleniumExtractor(bonus_url)
            elem = selextractor.get_elem_by_id("sel_year")
            select = Select(elem)
            select.select_by_visible_text(year)
            elem.send_keys(u'\ue007')
            time.sleep(8)
            # now when the year is loaded, start processing the table
            results = selextractor.get_elems_by_class("tbldata14")
            rows = results[0]
            rows_t = rows.find_elements(By.TAG_NAME,"tr")
            #row_s = results.find_element_by_xpath("'./tr'")
            print(type(rows_t))
            for row in rows_t[2:]:
                try:
                    dict_row = {}
                    elems = row.find_elements(By.TAG_NAME, "td")
                    col0 = elems[0]
                    dict_row['SYMBOL'] = col0.text.splitlines(0)[0]
                    url = col0.find_elements(By.TAG_NAME, "a")[0].get_attribute("href")
                    print((col0.text).splitlines(0)[0])
                    col1 = elems[1]
                    dict_row['ADJUSTMENT_TYPE'] = 'bonus'
                    bonus_factor = get_adjustment_factor('bonus',col1.text)
                    print(col1.text)
                    dict_row['FACTOR'] = bonus_factor
                    col4 = elems[4]
                    dict_row['DATE'] = col4.text
                    dict_row['URL'] = url
                    print("url is",url)
                    dict_row['NSE'] = ''
                    print(col4.text)
                    bonus_list.append(dict_row)
                except NameError as ne:
                    print("another")
                    print("do nothing1")
                    logger.error(ne,exc_info=True)
                except Exception as e:
                    print("do nothing 2")
                    logger.error(e,exc_info=True)
            selextractor.driver.quit() 
        except NameError as ne:
            print("do nothing 3")
            logger.error(ne,exc_info=True)
        except Exception as e:
            print("do nothing 4")
            logger.error(e,exc_info=True) 
    return(bonus_list) 


def get_bonus_details(bonus_list):
    #read the csv file that got created and now we will update ISIN
    for bonus_item in bonus_list:
        try:
            selextractor = SeleniumExtractor(bonus_item['URL'])
            res = selextractor.get_elems_by_class("PB10")
            nse_elem=res[0].find_element_by_xpath("//*[@id='nChrtPrc']/div[4]/div[1]")

            print(nse_elem.text)
            regex = r'\b\w+\b'
            re_pattern = r"\b"+"NSE"+r"\b"
            my_list = (re.findall(regex, nse_elem.text))
            nse_index = my_list.index('NSE')
            nse = my_list[nse_index+1]
            bonus_item['NSE'] = nse
            print(bonus_item)
            csvwriter.writefile_row(bonus_item)
            time.sleep(2)
            selextractor.driver.quit() 
        except NameError as ne:
            print("do nothing 5")
            logger.error(ne,exc_info=True)
        except Exception as e:
            print("do nothing 6")
            logger.error(e,exc_info=True)


if __name__ == '__main__':
    bonus_list = get_bonus_list()
    print("number of entries",len(bonus_list))
    get_bonus_details(bonus_list)




    


