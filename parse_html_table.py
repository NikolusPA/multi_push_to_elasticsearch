#!/usr/local/bin/python3.7
from bs4 import BeautifulSoup
import os, argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filetoparse', '-f', default='html_file')
    args = parser.parse_args()
   
    with open(args.filetoparse, "r") as filetoparse:
      filetoparse_content = filetoparse.read()
    soup = BeautifulSoup(filetoparse_content, "html.parser")
    all_divs = soup.findAll('div')
    for div in all_divs:
      try: 
        if div['id'] == 'main-content':
          trs = div.table.tbody.findAll('tr')
      except: pass
    for tr in trs:
      p_s = tr.findAll('td')
      stroka = ""
      try: 
        for p in p_s:
          stroka += str(p.getText()) + " | "
        print (stroka)
      except: pass
