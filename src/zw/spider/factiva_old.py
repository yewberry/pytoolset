import json
import csv
from bs4 import BeautifulSoup

def process(fn):
	with open(fn) as f:
		html_doc = f.read()
		soup = BeautifulSoup(html_doc, 'html.parser')
		root = soup.contents[0]
		cata = []
		result = []
		for p in root.contents:
			if p.name == 'li':
				cata.append(p)
		print('root contents length: %s'%len(cata))
		for c in cata:
			cname = c.a.string
			cnews = []
			arr = c.find_all('li')
			for p in arr:
				cnews.append(p.a.text)
			result.append({'cname': cname, 'items': cnews})
			
		with open(fn + '.csv', 'w', encoding='utf_8_sig') as f:
			writer = csv.writer(f)
			cur_cty = ''
			for p in result:
				nm = p['cname']
				items = p['items']
				for n in items:
					print(n)
					arr = n.split(':')
					if len(arr)>1:
						typ = arr[0].strip()
						inm = arr[1].strip()
					else:
						typ = ''
						inm = n
						cur_cty = n
					o = [nm, typ, inm, cur_cty]
					writer.writerow(o)

def merge(fn, idx, result):
	with open(fn, 'r', encoding='utf_8_sig') as f:
		reader = csv.reader(f)
		for row in reader:
			if row[1] == '':
				continue
			else:
				k = row[idx]
				if k not in result:
					result[k] = row[1]

def main():
	# process('etc/factiva_by_indu.html')
	# process('etc/factiva_by_geo.html')
	# process('etc/factiva_by_lang.html')
	# process('etc/factiva_by_type.html')
	result = {}
	merge('etc/factiva_by_geo.html.csv', 2, result)
	merge('etc/factiva_by_indu.html.csv', 2, result)
	merge('etc/factiva_by_type.html.csv', 2, result)
	merge('etc/factiva_by_lang.en_17912.csv', 2, result)
	c = 0
	with open('etc/merge.csv', 'w', encoding='utf_8_sig') as f:
		writer = csv.writer(f)
		for p in result:
			o = result[p]
			r = [p, o]
			c += 1
			writer.writerow(r)
	print(c)

if __name__ == '__main__':
	main()