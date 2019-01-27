# -*- coding: utf-8 -*-

import os,codecs
from lit import tools

from lit.text import Text
from lit.text.tcp import TextTCP
#import lit
#lit.ENGLISH=lit.load_english()

class TextECCO(Text):
	@property
	def title(self):
		return self.meta['fullTitle']

	@property
	def author(self):
		author1=self.meta.get('author','')
		if author1: return author1
		return self.meta.get('marcName','')

	@property
	def length(self):
		try:
			return float(self.meta['num_words_adorn'])
		except (ValueError,KeyError) as e:
			return 0

	@property
	def year_first_pub(self):
		opts=['year']
		for k in self.meta:
			if 'cluster_first_pub' in k:
				opts+=[k]
		vals = []
		for x in opts:
			try:
				v=int(self.meta[x])
				vals+=[v]
			except ValueError:
				pass
		if not vals: return None
		return min(vals)

	def text_plain(self,root_dir='/Volumes/sherlock/ecco/'): # root_dir=None):  ### SETTING DEFAULT TO SHERLOCK: NOTICE OF HARDWIRING
		if not root_dir: root_dir=self.corpus.path_txt
		fnfn = os.path.join(root_dir, self.id, 'txt', self.id.split('/')[-1]+'.clean.txt')
		if not os.path.exists(fnfn): return
		return codecs.open(fnfn,encoding='utf-8').read()




class TextECCO_TCP(TextTCP):
	@property
	def meta_by_file(self):
		if not hasattr(self,'_meta'):
			fnfn=os.path.join(self.path_header,self.id+'.hdr')
			mtxt=codecs.open(fnfn,encoding='utf-8').read()
			md=self.extract_metadata(mtxt)
			md['fnfn_xml']=self.fnfn
			md['id']=self.id
			md['genre'],md['medium']=self.return_genre()
			del md['notes']
			self._meta=md
		return self._meta





class TextECCO_LitLang(Text):
	@property
	def meta_by_file(self):
		if not hasattr(self,'_meta'):
			import gzip
			mtxt=''
			f = gzip.open(self.fnfn,'rb')
			for line in f:
				line=line.decode('iso-8859-1').encode('utf8')
				mtxt+=line
				if '</citation>' in line:
					break

			md=self.extract_metadata(mtxt)
			md['id']=self.id
			self._meta=md
		return self._meta

	def extract_metadata(self,mtxt,word_stats=True):
		md={}
		## IDs
		import bs4
		dom=bs4.BeautifulSoup(mtxt,'html.parser')
		md={}

		simples = ['documentID','ESTCID','pubDate','releaseDate','sourceLibrary','language','model','documentType','marcName','birthDate','deathDate','marcDate','fullTitle','currentVolume','totalVolumes','imprintFull','imprintCity','imprintPublisher','imprintYear','collation','publicationPlace','totalPages']

		for x in simples:
			try:
				md[x]=dom.find(x.lower()).text
			except AttributeError:
				md[x]=''


		## Num Holdings
		md['holdings_num_libraries']=mtxt.count('</holdings>')
		#md['libraries'] = [tag.text for tag in dom('libraryname')]
		md['notes'] = ' | '.join([tag.text for tag in dom('notes')])

		for subjhead in dom('locsubjecthead'):
			subtype=subjhead['type']
			for subj in subjhead('locsubject'):
				subfield=subj['subfield']
				val=subj.text
				md[subtype+'_'+subfield]=val

		try:
			md['year']=int(''.join([x for x in md['pubDate'] if x.isdigit()][:4]))
		except (ValueError,TypeError) as e:
			md['year']=0

		## if word_stats

		words=[w for w,p in self.tokens]
		md['num_words']=len(words)
		md['ocr_accuracy']=len([w for w in words if w in lit.ENGLISH]) / float(len(words)) if len(words) else 0.0

		return md

	@property
	def text(self):
		import gzip
		try:
			with gzip.open(self.fnfn, 'rb') as f:
				file_content = f.read()
		except IOError:
			print "!! Error on gzip for file id",self.id
			return ''
		return file_content

	@property
	def fnfn_txt(self):
		return os.path.join(self.corpus.path_txt,self.id+'.txt.gz')

	@property
	def fnfn(self):
		return os.path.join(self.corpus.path_xml,self.id+'.xml.gz')

	@property
	def has_plain_text_file(self):
		return os.path.exists(self.fnfn_txt)

	@property
	def text_plain_from_file(self):
		if not self.has_plain_text_file:
			return False

		import gzip
		try:
			with gzip.open(self.fnfn_txt,'rb') as f:
				txt=f.read().decode('utf-8')
		except:
			print "!! ERROR: could not decompress:",self.id
			return ''
		return txt


	def text_plain(self, OK_word=['wd'], OK_page=['bodyPage'], remove_catchwords=True, return_lists=False, save_when_gen=True):
		cache=self.text_plain_from_file
		if cache:
			print '>>',self.fnfn_txt,'from cache'
			return cache

		from lit.text import clean_text

		"""
		Get the plain text from the ECCO xml files.
		OK_word sets the tags that define a word: in ECCO, <wd>.
		OK_page sets the tags that define a page we want:
		- bodyPage are the body pages
		- frontmatter are frontmatter paggers;
			-- I've decided not to include them, but you can add them by adding it to the OK_page list
		"""

		print '>>', self.fnfn

		txt=[]
		dom = self.dom
		body = dom.find('text')
		if not body: return ''
		for page in body.find_all('page'):
			if page['type'] in OK_page:
				page_txt=[]
				para_txt=[]
				line_txt=[]
				lastParent=None
				lastLineOffset=None
				for tag in page.find_all():
					if tag.name in OK_word:


						## Check for new paragraph
						if tag.parent != lastParent:
							if line_txt:
									para_txt+=[line_txt]
									line_txt=[]
							if para_txt:
								page_txt+=[para_txt]
								para_txt=[]
						lastParent=tag.parent

						## Check for new line
						lineOffset = int(tag['pos'].split(',')[0])
						if lastLineOffset is None:
							lastLineOffset=lineOffset
						elif lineOffset < lastLineOffset:
							if line_txt:
								para_txt+=[line_txt]
								line_txt=[]
						lastLineOffset = lineOffset

						text=clean_text(tag.text)
						line_txt+=[text]

				if line_txt:
					para_txt+=[line_txt]
				if para_txt:
					page_txt+=[para_txt]
				if page_txt:
					txt+=[page_txt]

		for page_i,page in enumerate(txt):
			#print '>> page:',page_i
			if remove_catchwords:
				last_word_this_page = page[-1][-1][-1]
				first_word_next_page = txt[page_i+1][0][0][0] if len(txt)>page_i+1 else None
				if last_word_this_page == first_word_next_page:
					# if last word is a catchword for first word of next page,
					# remove the last line
					page[-1][-1].pop()

			page = [para for para in page if len(para) and sum(len(line) for line in para)>0]
			txt[page_i] = page

		if return_lists:
			return txt

		## otherwise, make plain text
		plain_text = u"\n\n\n".join(u"\n\n".join(u"\n".join(u" ".join(word for word in line) for line in para) for para in page) for page in txt)

		if save_when_gen:
			self.save_plain_text(txt=plain_text,compress=True)

		return plain_text


def clean_text(txt):
	txt=txt.replace(u'\u2223','') # weird kind of | character
	txt=txt.replace(u'\u2014','-- ') # em dash
	return txt
