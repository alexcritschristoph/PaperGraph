from xml.dom import minidom
xmldoc = minidom.parse('abstracts.txt')
itemlist = xmldoc.getElementsByTagName('PubmedArticle')
years = []
titles = []
abstracts = []
pmids = []
journals = []

for s in itemlist:
	title = s.getElementsByTagName('ArticleTitle')
	title = title[0].toprettyxml().split(">")[1].split("<")[0]

	titles.append(title)

	Abstract = s.getElementsByTagName('AbstractText')
	Abstract = Abstract[0].toprettyxml().split(">")[1].split("<")[0]
	abstracts.append(Abstract)

	pmid = s.getElementsByTagName('PMID')
	pmid = pmid[0].toprettyxml().split(">")[1].split("<")[0]
	pmids.append(pmid)

	journal = s.getElementsByTagName('Journal')
	j_title = journal[0].getElementsByTagName('Title')
	j_title = j_title[0].toprettyxml().split(">")[1].split("<")[0]
	journals.append(j_title)

	date = s.getElementsByTagName("DateCreated")
	year = date[0].getElementsByTagName("Year")
	year = year[0].toprettyxml().split(">")[1].split("<")[0]
	years.append(year)

# Create Objects
papers = {}
i = 0
for paper in pmids:
	papers[paper] = {}

	papers[paper]['title'] = titles[i]
	papers[paper]['year'] = years[i]
	papers[paper]['journal'] = journals[i]
	papers[paper]['abstract'] = abstracts[i]
	papers[paper]['pmid'] = pmids[i]
	i+= 1

# Calculate similarity between abstracts

from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer(min_df=1)
abstract_vect = vect.fit_transform(abstracts)

similarities = (abstract_vect * abstract_vect.T).A

#Create edges for network
import numpy as np
cutoff = np.mean(similarities)

similarity_array = similarities.tolist()

from sets import Set


links = Set([])

i = 0
j = 0
for row in similarity_array:
	for comparison in row:
		if comparison < 0.99 and comparison > cutoff:
			if i < j:
				links.add(str(i) + "," + str(j))
			else: 
				links.add(str(j) + "," + str(i))
		j += 1
	i += 1
	j = 0

print len(sorted(list(links)))

# Print link file
for link in links:
	i = int(link.split(",")[0])
	j = int(link.split(",")[1])
	print pmids[i] + "," + pmids[j]