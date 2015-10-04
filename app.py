from flask import Flask
from flask import render_template
from flask import request
import json
from flask import jsonify
import uuid
import subprocess
from xml.dom import minidom
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sets import Set
import os
import signal
import sys
from math import log

app = Flask(__name__)


@app.route("/")
def main_page():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_graph():
	print "GOT HERE"
	query = request.form['query']

	#Run the esearch command
	file_name = str(uuid.uuid4()) + ".dat"

	command = "esearch -query '"+ query +"' -db pubmed | efetch -format Abstract -mode xml "
	process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

	bytes = lines = 0
	result = ''
	for line in process.stdout:
		lines += 1
		result += line
		if lines > 2200 and '</PubmedArticle>' in line:
			os.killpg(process.pid, signal.SIGTERM)
			break

	print result.count("PubmedArticleSet")
	if result.count("PubmedArticleSet") % 2 == 0:
		result += "</PubmedArticleSet>"
	result = result.replace("&", '')
	#Parse results of esearch command
	print "****1***"
	try:
		xmldoc = minidom.parseString(result)
	except Exception as e:
		print result.split("\n")[-1]
		print result.split("\n")[-2]
		print e.message
	print "****2***"
	itemlist = xmldoc.getElementsByTagName('PubmedArticle')
	print "****3***"
	years = []
	titles = []
	abstracts = []
	pmids = []
	journals = []
	print "****4***"
	for s in itemlist:
		print "****5***"
		print s.toprettyxml()
		title = s.getElementsByTagName('ArticleTitle')
		title = title[0].toprettyxml().split(">")[1].split("<")[0]
		print "found title"
		titles.append(title)

		try:
			Abstract = s.getElementsByTagName('AbstractText')
			Abstract = Abstract[0].toprettyxml().split(">")[1].split("<")[0]
			abstracts.append(Abstract)
			print "found abstract"
		except:
			Abstract = ''
			abstracts.append(Abstract)

		pmid = s.getElementsByTagName('PMID')
		pmid = pmid[0].toprettyxml().split(">")[1].split("<")[0]
		pmids.append(pmid)
		print "found pmid"

		journal = s.getElementsByTagName('Journal')
		j_title = journal[0].getElementsByTagName('Title')
		j_title = j_title[0].toprettyxml().split(">")[1].split("<")[0]
		journals.append(j_title)
		print "found journal"

		date = s.getElementsByTagName("DateCreated")
		year = date[0].getElementsByTagName("Year")
		year = year[0].toprettyxml().split(">")[1].split("<")[0]
		years.append(year)
		print "found year"

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

	vect = TfidfVectorizer(min_df=1)
	abstract_vect = vect.fit_transform(abstracts)

	similarities = (abstract_vect * abstract_vect.T).A
	cutoff = np.percentile(similarities, 25)
	similarity_array = similarities.tolist()

	print similarity_array
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
	link_data = []
	for link in links:
		i = pmids[int(link.split(",")[0])]
		j = pmids[int(link.split(",")[1])]

		link_data.append([i,j])

	#Pass [links, nodes] to javascript
	return jsonify({"links":link_data, "nodes":papers})

if __name__ == "__main__":
    app.run(debug=True)