import json
import csv

def main():
	fn = 'by_type.har'
	with open('etc/'+fn) as f:
		data = json.load(f)
		entries = data['log']['entries']
		regions = []
		tokens = []
		count = 0
		tc = 0
		for p in entries:
			try:
				ts = json.loads(p['response']['content']['text'])
			except Exception as e:
				print('ERROR when parse text')
				continue
			if 'tokens' in ts:
				ts = ts['tokens']
				for t in ts:
					count += 1
					tid = t['id']
					if len(tid)>50:
						regions.append(t)
					else:
						tokens.append(t)
			else:
				print('ERROR no tokens')
				continue
		
		print(count)
		print(len(regions))
		print(len(tokens))
		regs = [{'id':o['id'], 'label':o['label'], 'news':[]} for o in regions]
		news = [{'id':o['id'], 'label':o['label'], 'parents':o['parentsIds'], 'labels':o['labels']} for o in tokens]
		def get_hm(recs):
			hm = {}
			for p in recs:
				if p['id'] in hm:
					print('found dup'+p['id'])
				hm[p['id']] = p
			return hm
		regs_hm = get_hm(regs)
		for idx,p in enumerate(news):
			if idx==9040:
				a = 0
			prts = p['parents']
			for prt in prts:
				if prt in regs_hm:
					o = regs_hm[prt]
					o['news'].append(p)
					continue
		with open('etc/'+fn+'.csv', 'w', encoding='utf_8_sig') as f:
			writer = csv.writer(f)
			for p in regs_hm:
				r = regs_hm[p]
				news = r['news']
				for n in news:
					reg = r['label']
					lbl = n['label']
					o = [r['label'], n['id'], lbl]
					writer.writerow(o)

if __name__ == '__main__':
	main()