#!/usr/bin/env python3
#coding: utf-8
# exam/__main__.py
"""EXAM entry point script."""

import typer
import fnmatch
import os
import io 
import re
import random
import configparser
import sys
import getopt
import operator
import time
import shutil
import glob
import subprocess
from random import randint
import yaml
import gettext
from pprint import pprint
from distutils.spawn import find_executable


from .version import __app_name__, __version__

__DEBUG = True 
__NAME = "EXAM" 
__VERSION = __version__
__AUTHOR = "Razer Anthom Nizer Rojas Montaño"
__EMAIL = "razer.anthom@gmail.com"
__PAGE = "http://www.razer.net.br"

def _(m): return m


app = typer.Typer(
    name=__app_name__,
	add_completion=False,
    help=_("{} {} by {} ({}). URL: {}".format(__NAME, __VERSION, __AUTHOR, __EMAIL, __PAGE)))

_EXTENSION = ".yaml"
_QUESTION_EXTENSION = ".tex"
_EXAM_EXTENSION = ".tex"
_TEXT_EXTENSION = ".txt"
_DIR_TEMPLATE = "template/"
# files to copy
_FILES_TEMPLATE_GENERAL = [ "exam.cls", "logo.png", "instructions.tex" ]
# files to copy and substitute [[NAME]] with exam name
_FILES_TEMPLATE = [ "exam_model.tex", "exam_model_result.tex" ]
_HEADER_FILE = "header_model.tex"


_ALTERNATIVES_SESSION = "[alternatives]"

_QUESTION_SPACE 	= "0.3cm"
_ALTERNATIVE_SPACE 	= "0.2cm"


##### Commands
_COMMAND_HELP		= "help"
_COMMAND_INIT		= "init"
_COMMAND_NEW		= "new"
_COMMAND_CLEAR		= "clear"
_COMMAND_REMOVE		= "remove"
_COMMAND_CLONE		= "clone"
_COMMAND_SHOW		= "show"
_COMMAND_SHOWCONFIG	= "showConfig"
_COMMAND_QUESTIONS	= "questions"

_COMMAND_CREATE		= "create"
_COMMAND_GENERATE	= "generate"
_COMMAND_LATEX 		= "latex"

##### Files sufixes
_ANSWER_SHEET_FILE_SUFFIX		= "_answer_sheet.tex"
_QUESTIONS_FILE_SUFFIX	= "_questions.tex"
_ANSWERS_FILE_SUFFIX = "_answers.txt"
_ANSWERS_HORIZ_FILE_SUFFIX = "_horiz_answers.txt"


# constants
_HEADER_SUFFIX 	= "_header.tex"

class Config:
	configuration = dict()
	CONFIG_FILE = "config.yaml"
	CWD = ""
	PATH_TEMPLATE = ""
	PATH_SCRIPT = ""
	PATH_QUESTIONS = ""

class Exam:
	examConfig = dict() 
	allQuestions = []
	quantities = []
	countExamQuestions = 0
	questionValue = 0
	questions = []   		# name of questions, shuffle
	correctAnswers = []  	# correct answers to each question
 
	EXAM_CONFIG_FILENAME = ""
	EXAM_CONFIG_FILE = ""
	EXAM_NAME = ""
	EXAM_PATH = ""

	ANSWER_FILE = ""           # only filename
	ANSWER_FILENAME = ""       # path and filename
	ANSWER_SHEET_FILENAME = ""
	ANSWER_SHEET_FILE = ""
	ANSWERS_FILENAME = ""
	ANSWERS_FILE = ""
	ANSWERS_HORIZ_FILENAME = ""
	ANSWERS_HORIZ_FILE = ""
	EXAM_FILENAME = ""         # only filename
	EXAM_FILE = ""             # path and filename
	EXAM_HEADER_FILENAME = ""  # only filename
	EXAM_HEADER_FILE = ""      # path and filename
	QUESTIONS_FILENAME = ""    # only filename
	QUESTIONS_FILE = ""        # path and filename


############################################################################
# Shows help
############################################################################
def usage(s=""):
	if s!="":
		print(_("ERROR: ").format(s))
		print("")
	print (__NAME + " " + __VERSION + " by " + __AUTHOR + " (" + __EMAIL + ")")
	print ("")
	print (_("Usage: "))
	print ("     exam <command> [parameters]")
	print ("")
	print (_("Commands:"))
	print (_("     help            : show this message"))
	print (_("     init <name>     : create new <name>.yaml file, create template files"))
	print (_("     new <name>      : given a <name>.yaml file, create a new exam"))
	print (_("     latex <name>    : generate latex and PDF of exam from previous generated exam"))
	print (_("     generate <name> : with .yaml file, calls new and latex "))
	print ("")
	print ("")
	print (_("     show  <name>    : show configurations"))
	print (_("     showConfig      : show global configurations"))
	print (_("     clear <name>    : remove generated exam files"))
	print (_("     remove <name>   : remove all exam files"))
	print (_("     clone <e1> <e2> : copy exam e1 to e2"))
	print ("")
	print (_("Common use: init | clone > new > latex  "))
	print (_("Common use: init | clone > generate  "))

############################################################################
# 
############################################################################
def getRandom():
	key_num = random.SystemRandom()
	return key_num.random()

############################################################################
# Helper : log a string with level l (spaces)
############################################################################
def log(s, l=0):
	print((" " * (l*3) + s))

############################################################################
# Helper : debug a string with level l (spaces)
############################################################################
def _DEBUG(s, l):
	if __DEBUG:
		print((" " * (l*3)) + s)
  
def letter(n):
    if n<0 or n>4:
        log(_("Error translating number to letter - answer: {}").format(n))
        sys.exit(1)
    return chr(65 + n)

############################################################################
# Helper : remove a file s
############################################################################
def removeFile(s):
	if os.path.exists(s):
		os.remove(s)
  
def removeFilesFromDirectory(s):
	if os.path.exists(s):
		for f in os.listdir(s):
			os.remove(s+f)

############################################################################
# Helper : put '/' at the end
############################################################################
def slash(s):
	if not s.endswith("/"):
		s = s + "/"
	return s

############################################################################
# Helper : remove suffix
############################################################################
def removeSuffix(s, suf):
	if not s.endswith(suf):
		return s
	else:
		return s[:-len(suf)]


############################################################################
# 
############################################################################
def error(string):
	print (_("ERROR: {}").format(string) )
	sys.exit(1)

############################################################################
# 
############################################################################
def errorCommand(string):
	print (_("Syntax error: {}").format(string) )
	usage()
	sys.exit(1)

############################################################################
# Loads the configuration file
############################################################################
def loadConfig():
    
	Config.CWD = slash(os.getcwd())
	Config.PATH_SCRIPT = slash(os.path.dirname(os.path.realpath(__file__)))
	if os.path.exists(Config.CWD + Config.CONFIG_FILE):
		Config.CONFIG_FILE = Config.CWD + Config.CONFIG_FILE
	else:
		Config.CONFIG_FILE = Config.PATH_SCRIPT + Config.CONFIG_FILE
	with open(Config.CONFIG_FILE, 'r') as file:
		my_config = yaml.safe_load(file)
  
	Config.configuration = my_config
	Config.PATH_TEMPLATE = slash(Config.PATH_SCRIPT + _DIR_TEMPLATE)
	Config.PATH_QUESTIONS = slash(Config.PATH_SCRIPT + Config.configuration["config"]["questions"]["path"])
	Config.LOCALE = Config.configuration["config"]["locale"]
	# internationalization
	el = gettext.translation('base', localedir=Config.PATH_SCRIPT + 'locales', languages=[Config.LOCALE])
	el.install()
	# _ = el.gettext


############################################################################
# Loads exam file
############################################################################
def loadExamConfig():
    
    if not os.path.exists(Exam.EXAM_CONFIG_FILE):
        error(_("File {} does not exists.").format(Exam.EXAM_CONFIG_FILENAME))
        
    with open(Exam.EXAM_CONFIG_FILE, 'r') as file:
        my_config = yaml.safe_load(file)
            
    return my_config

############################################################################
# Prompt a question y/n/c
############################################################################
def prompt(question):
    
	while True:
		sys.stdout.write(question + " [Y/n/c]  ")
		choice = input().lower()
		if choice=="" or choice=="Y" or choice=="y":
			return True
		elif choice=="N" or choice=="n":
			return False
		elif choice=="C" or choice=="c":
			sys.exit(0)
		else:
			sys.stdout.write(_("Please respond with 'y' (yes) or 'n' (no) or 'c' (cancel).\n"))

############################################################################
# Define directories and global values
############################################################################
def defineGlobals(exam):
 

	Exam.EXAM_NAME = removeSuffix(exam, _EXTENSION)
	Exam.EXAM_PATH = slash(Config.CWD + Exam.EXAM_NAME)
	
	# Set names and file names
	Exam.EXAM_CONFIG_FILENAME = Exam.EXAM_NAME + _EXTENSION
	Exam.EXAM_CONFIG_FILE = Config.CWD + Exam.EXAM_CONFIG_FILENAME
 
	Exam.ANSWER_SHEET_FILENAME = Exam.EXAM_NAME + _ANSWER_SHEET_FILE_SUFFIX
	Exam.ANSWER_SHEET_FILE = Exam.EXAM_PATH + Exam.ANSWER_SHEET_FILENAME
 
	Exam.ANSWERS_FILENAME = Exam.EXAM_NAME + _ANSWERS_FILE_SUFFIX
	Exam.ANSWERS_FILE = Exam.EXAM_PATH + Exam.ANSWERS_FILENAME
	Exam.ANSWERS_HORIZ_FILENAME = Exam.EXAM_NAME + _ANSWERS_HORIZ_FILE_SUFFIX
	Exam.ANSWERS_HORIZ_FILE = Exam.EXAM_PATH + Exam.ANSWERS_HORIZ_FILENAME
 
	Exam.EXAM_HEADER_FILENAME = Exam.EXAM_NAME + _HEADER_SUFFIX  
	Exam.EXAM_HEADER_FILE = Exam.EXAM_PATH + Exam.EXAM_HEADER_FILENAME
 
	Exam.EXAM_FILENAME = Exam.EXAM_NAME + _EXAM_EXTENSION
	Exam.EXAM_FILE = Exam.EXAM_PATH + Exam.EXAM_FILENAME
 
	Exam.QUESTIONS_FILENAME = Exam.EXAM_NAME + _QUESTIONS_FILE_SUFFIX
	Exam.QUESTIONS_FILE = Exam.EXAM_PATH + Exam.QUESTIONS_FILENAME
	
 
 
############################################################################
# Remove all temp and exam files
############################################################################
def cleanFiles():
    removeFile(Exam.QUESTIONS_FILENAME)
    removeFile(Exam.ANSWER_FILE)
     

############################################################################
# 
############################################################################
def copyInitFiles():
	try:  
		# create folder to new exam
		if not os.path.isdir(Exam.EXAM_NAME):
			os.mkdir(Exam.EXAM_NAME)
		else:
			res = prompt(_("Directory {} already exists. Can overwrite files?").format(Exam.EXAM_NAME))
			if res:
				log(_("Removing files..."), 1)
				removeFilesFromDirectory(Exam.EXAM_PATH)
			else:
				log(_("To make a new exam, files need to be overwritten. Try again."))
				sys.exit(0)
	except OSError:  
		log (_("!!! Creation of the directory {} failed").format(Exam.EXAM_NAME))
		sys.exit(1)

	# Copy template files into exam folder
	for f in _FILES_TEMPLATE_GENERAL:
		fn = Config.PATH_TEMPLATE + f
		if not os.path.exists(fn):
			log (_("!!! Template file {} does not exist").format(fn))
			sys.exit(1)
		log (_("Copying file {}...").format(f), 1)
		shutil.copy(fn, Exam.EXAM_PATH)

	# SED command to substitute template string [[NAME]] with the name of exam
	sed_command = ["sed", "-e", "s/\[\[NAME\]\]/" + Exam.EXAM_NAME + "/g"]
	
	# Copy files, change name and execute SED to change [[NAME]]
	for f in _FILES_TEMPLATE:
		fn = Config.PATH_TEMPLATE + f
		fout = Exam.EXAM_PATH + f.replace("exam_model", Exam.EXAM_NAME)

		log (_("Copying file {}...").format(f), 1)
		if not os.path.exists(fn):
			log (_("!!! Template file {} does not exist").format(fn))
			sys.exit(1)
   
		with open(fout, "w") as outfile:
			# change [[NAME]] and write to outfile
			subprocess.call(sed_command + [fn], stdout=outfile)

    

############################################################################
# 
############################################################################
def generateHeaderFile():
    
	with io.open(Config.PATH_TEMPLATE + _HEADER_FILE, "r", encoding="utf-8") as f:
		newText = f.read().replace("[[CLASS]]", Exam.examConfig["exam"]["class"])
		newText = newText.replace("[[EXAM]]", Exam.examConfig["exam"]["name"])
		newText = newText.replace("[[DATE]]", Exam.examConfig["exam"]["date"])

	with io.open(Exam.EXAM_HEADER_FILE, "w", encoding="utf-8") as f:
		f.write(newText)

############################################################################
# 
############################################################################
def generateAnswerSheet():

	str_ans = "\\renewcommand{\\arraystretch}{2}\n"
	str_ans += "\\begin{tabular}{|c|c||c|c|}\n"
	str_ans += "\\hline\n"
	str_ans += " Questão & Resposta & Questão & Resposta\\\\\n"
	str_ans += "\\hline\n"
	lines = Exam.countExamQuestions // 2
	for i in range(1, lines+1):
		str_ans += "\\hline\n"
		str_ans += str(i) + " & & " + str(i+lines) + " & \\\\\n"
		if i % 5 == 0:
			str_ans += "\\hline\n"
	str_ans += "\\hline\n"
	str_ans += "\\end{tabular}\n"

	with open(Exam.ANSWER_SHEET_FILE, "a+") as exam_file:
		exam_file.write(str_ans)

############################################################################
# 
############################################################################
def hasRestriction(q_list, q):
    
    list_restrictions = Config.configuration["config"]["restrictions"]
    for restriction in list_restrictions:
        if q in restriction:
            # question q is in a restrictions
            # need to verify if one of the list already in q_list
            for q_restriction in restriction:
                if q_restriction in q_list:
                    return True
    return False

############################################################################
# 
############################################################################
def getRestrictions(q):
    
	list_res = []
	list_restrictions = Config.configuration["config"]["restrictions"]
	for restriction in list_restrictions:
		if q in restriction:
			for q_restriction in restriction:
				if q_restriction!=q:
					list_res.append(q_restriction)
	return list_res

############################################################################
# 
############################################################################
def generateQuestions():
	# Loads all questions
	count_questions = 0
	Exam.quantities = []
	q_files_temp = []
	for d in Exam.examConfig["questions"]:
		# d is a folder, like angular
		temp = slash(Config.PATH_QUESTIONS + d)
	
		if not os.path.exists(temp):
			error(_("Question path does not exists: {} ".format(temp)))
   
		for q in Exam.examConfig["questions"][d]:
			# q is a question type (prefix), like angular_F
			#print ("   " + q)
			# loads many lists as questions types we have, maintain only question name (without extension)
			# removed .lower() after removeSuffix
			q_files_type = [[d, q, removeSuffix(arc, ".tex")] for arc in os.listdir(temp) if (os.path.isfile(os.path.join(temp, arc)) and arc.startswith(q))]
			q_files_temp.append(q_files_type)
			c = Exam.examConfig["questions"][d][q]
			if (c == "*"):
				quant = len(q_files_type)
			else:
				if c > len(q_files_type):
					error(_("Too few questions in database to create exam: {} questions stored but {} questions solicited.").format(str(len(q_files_type)), str(c)))
				else:
					quant = c
			count_questions += quant
			Exam.quantities.append(quant)
   
			log(_("Question type : {}").format(q), 1)
			log(_("Questions in database : {}").format(str(len(q_files_type))), 2)
			log(_("Questions in exam     : {}").format(str(c)), 2)
     
	Exam.allQuestions = q_files_temp
	Exam.countExamQuestions = count_questions
 
	log(_("Generating {} questions...").format(str(Exam.countExamQuestions)), 1)

	generateAnswerSheet()
 
	# calculate score of each question
	int_value = True
	if (Exam.examConfig["exam"]["total_score"] % Exam.countExamQuestions != 0):
		int_value = False
		Exam.questionValue = round( float(Exam.examConfig["exam"]["total_score"]) / Exam.countExamQuestions, 1)
		#log("!!! ATTENTION: Value of questions is not integer: "+ str(Exam.examConfig["exam"]["total_score"]) + " / " + str(Exam.countExamQuestions) + " => " + str(Exam.questionValue), 1)
	else:
		Exam.questionValue = Exam.examConfig["exam"]["total_score"] / Exam.countExamQuestions

	log(_("Score of each question {}").format(Exam.questionValue), 1)
 
	# randomize all questions to choose
	for questions in Exam.allQuestions:
		random.seed(getRandom())
		while True:
			random.shuffle(questions)
			if random.random() > 0.5:
				break


	# pick each question without restriction
	Exam.questions = []
	count = 0
	for questions_type in Exam.allQuestions:
		# quantity of that kind question
  
		quant = Exam.quantities[count]
		count_questions = 0
		for d_type, q_type, question in questions_type:
			if not hasRestriction(Exam.questions, question):
				# can add this question
				Exam.questions.append([d_type, q_type, question])
				count_questions += 1
				if count_questions >= quant:
					break

		count += 1

	#pprint(Exam.questions)
	#pprint(len(Exam.questions))
 
	if (len(Exam.questions) < Exam.countExamQuestions):
		error(_("Insufficient questions to make this exam. Need {} but only can choose {} with all restrictions.").format(+ str(Exam.countExamQuestions), str(len(Exam.questions))))
  
	# Randomize questions choosen
	random.seed(getRandom())
	while True:
		random.shuffle(Exam.questions)
		if random.random() > 0.5:
			break


############################################################################
# Generate correct answer to each question
############################################################################
def generateCorrectAnswers():
	
	Exam.correctAnswers = []
    
	while True:
		random.seed(getRandom())
		answers = random.choices([0, 1, 2, 3, 4], k=Exam.countExamQuestions)
		count = [answers.count(0), answers.count(1), answers.count(2), answers.count(3), answers.count(4)]
		min_a = min(count)
		max_a = max(count)
		if max_a-min_a <= Exam.examConfig["exam"]["balanced_questions"]:
			# now we can accept answers
			Exam.correctAnswers = answers
			break
		else:
			# unbalanced number of correct ansers
			answers = []
	log(f"A={Exam.correctAnswers.count(0)}, B={Exam.correctAnswers.count(1)}, C={Exam.correctAnswers.count(2)}, D={Exam.correctAnswers.count(3)}, E={Exam.correctAnswers.count(4)}", 1)
   
    
############################################################################
# 
############################################################################
def generateExamFile():
    
	count = 0
	#log(f"Questions in exam: {len(Exam.questions)}", 1)
	# d_type - folder, q_type - type (prefix of question name), q_name - full name of question
	for d_type, q_type, q_name in Exam.questions:
		# load question file
		filename = slash(Config.PATH_QUESTIONS + d_type) + q_name + _QUESTION_EXTENSION
		#pprint(filename)
		with open(filename, "r") as question_file:
			question_text = question_file.read() 
		alts = question_text.find(_ALTERNATIVES_SESSION)
  
		q_statement = question_text[:alts].strip()
		alts_str = question_text[alts+len(_ALTERNATIVES_SESSION):]
		alts_arr = alts_str.split("//")
		alts_final = []
		for a in alts_arr:
			if (a.strip().startswith("*")):
				str_alt_right = "\\CorrectChoice " + a[2:].strip()
			else:
				alts_final.append("\\choice " + a.strip())
    
		# randomize wrong answers
		random.seed(getRandom())
		while True:
			random.shuffle(alts_final)
			if random.random() > 0.5:
				break

	    # insert right answer in correct position
		if Exam.correctAnswers[count] > len(alts_final):
			alts_final.append(str_alt_right)
		else:
			alts_final.insert(Exam.correctAnswers[count], str_alt_right)
		str_right_answer_letter = letter(Exam.correctAnswers[count])
  
		# save questions in exam file
		#log(f"Writing questions {count} {Exam.QUESTIONS_FILENAME}.", 1)
		with open(Exam.QUESTIONS_FILE, "a+") as exam_file:
			exam_file.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n% " + q_name + " - Q" + str(count+1) + " - " + str_right_answer_letter + " \n")
			exam_file.write("% Question: " + q_name + "\n")
			exam_file.write("% Number:   " + str(count+1) + "\n")
			exam_file.write("% Correct:  " + str_right_answer_letter + "\n")
			exam_file.write("% Type:     " + q_type + "\n")
			exam_file.write("% Path:     " + d_type + "/" + q_name + _EXAM_EXTENSION + "\n")
			exam_file.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")
			exam_file.write("\\begin{minipage}{\linewidth}\n") 


			if isinstance(Exam.questionValue, int):
				str_question_score = str(Exam.questionValue)
			else:
				str_question_score = "%.1f" % Exam.questionValue
				str_question_score = str_question_score.replace(".", ",")
    
			#### TODO - parei aqui, estou gerando o arquivo .tex da prova, para cada questao
  
			exam_file.write("\\question\n\n")	
			exam_file.write("[" + str_question_score + "]\ ")	
			exam_file.write(q_statement)
			exam_file.write("\n\n")
			if (_ALTERNATIVE_SPACE != ""):
				exam_file.write("\\vspace{" + _ALTERNATIVE_SPACE + "}\n")
			exam_file.write("\\begin{choices}\n")	
			for c in alts_final:
				exam_file.write(c)
				exam_file.write("\n")
			exam_file.write("\\end{choices}\n\n")	
			exam_file.write("\\end{minipage}\n") 
			if (_QUESTION_SPACE != ""):
				exam_file.write("\\vspace{" + _QUESTION_SPACE + "}\n")
			exam_file.write("\n\n")

		count += 1

############################################################################
# 
############################################################################
def generateAnswersFiles():

	with open(Exam.ANSWERS_FILE, "a+") as arq_prova:
		for count in range(len(Exam.correctAnswers)):
			arq_prova.write(f"Q{count+1} - {letter(Exam.correctAnswers[count])}\n");

	with open(Exam.ANSWERS_HORIZ_FILE, "a+") as arq_prova:
		for count in range(len(Exam.correctAnswers)):
			arq_prova.write(f"{letter(Exam.correctAnswers[count])}\t\t");


############################################################################
# Loads exam structure : questions, excludes, etc
############################################################################
def generateExam():	
	generateHeaderFile()
	generateQuestions()
	generateCorrectAnswers()
	generateExamFile()
	generateAnswersFiles()

############################################################################
# Execute init command
############################################################################
def commandInit():

	if os.path.exists(Exam.EXAM_CONFIG_FILENAME):
		res = prompt(_("File {} already exists. Want to overwrite?").format(Exam.EXAM_CONFIG_FILENAME))
		if not res:
			log (_("File {} maintained.").format(Exam.EXAM_CONFIG_FILENAME))
			return

	with open(Exam.EXAM_CONFIG_FILE, "w") as myfile:
		myfile.write("# YAML exam example file\n\n")
		myfile.write("exam:\n")
		myfile.write("  total_score: 100\n")
		myfile.write("  total_score_objective: 100\n")
		myfile.write('  class: "DS152 - DESENVOLVIMENTO DE APLICAÇÕES CORPORATIVAS - N"\n')
		myfile.write('  name: "PROVA I (C)"\n')
		myfile.write('  date: "13/12/2022"\n')
		myfile.write('  balanced_questions: 3\n')
		myfile.write('\n')

		myfile.write('# "*" to use all questions\n')
		myfile.write('questions:\n')
		myfile.write('  test1:\n')
		myfile.write('    test1_F: 2\n')
		myfile.write('  test2:\n')
		myfile.write('    test2_F: 2\n')
  
	# copyInitFiles(Exam.EXAM_NAME)
	log (_("Exam {} initialized.").format(Exam.EXAM_NAME))
	log (_("File {} created.").format(Exam.EXAM_CONFIG_FILE))


############################################################################
# Execute new command
############################################################################
def commandNew():
	log (_("Generating exam {}.").format(Exam.EXAM_NAME)) 
	cleanFiles()
	copyInitFiles()
	generateExam()
	log(_("Exam {} created.".format(Exam.EXAM_NAME)))
 
############################################################################
# Execute clone command
############################################################################
def commandClone(s):
	log (_("Cloning exam {}.".format(Exam.EXAM_NAME)))
	if os.path.exists(Exam.EXAM_NAME + _EXTENSION):
		shutil.copy(Exam.EXAM_NAME + _EXTENSION, s + _EXTENSION)
	log (_("Exam {} created.").format(s))
 
############################################################################
# Execute showConfig command
############################################################################
def commandShowConfig():
	pprint(Config.__dict__)

############################################################################
# Execute show command
############################################################################
def commandShow():
	log("PATH_SCRIPT = " + Config.PATH_SCRIPT)
	log("EXAM_NAME = " + Exam.EXAM_NAME)
	log("EXAM_PATH = " + Exam.EXAM_PATH)
	log("PATH_TEMPLATE = " + Config.PATH_TEMPLATE)
	log("EXAM_CONFIG_FILE = " + Exam.EXAM_CONFIG_FILE)
	log("PATH_QUESTIONS = " + Config.PATH_QUESTIONS)
 
############################################################################
# Execute generate command
############################################################################
def commandGenerate():
	commandNew()
	commandLatex()
 
############################################################################
# Execute clear command
############################################################################
def commandClear():
	if os.path.exists(Exam.EXAM_PATH):
		res = prompt(_("Want to remove files in directory {} ?").format(Exam.EXAM_NAME))
		if res:
			log(_("Removing files in {}").format(Exam.EXAM_PATH), 1)
			removeFilesFromDirectory(Exam.EXAM_PATH)
	else:
		log(_("Nothing to clear, {} directory does not exists.").format(Exam.EXAM_NAME))
 
############################################################################
# Execute remove command
############################################################################
def commandRemove():
	if os.path.exists(Exam.EXAM_PATH):
		res = prompt(_("Want to remove all exam files ({}) ?").format(Exam.EXAM_NAME))
		if res:
			log(_("Removing files in {}").format(Exam.EXAM_PATH), 1)
			shutil.rmtree(Exam.EXAM_PATH)
			removeFile(Exam.EXAM_NAME + _EXTENSION)
	else:
		log(_("Nothing to clear, {} directory does not exists.").format(Exam.EXAM_NAME))
 
############################################################################
# Execute questions command - list all questions
############################################################################
def commandQuestions():
	log(_("Questions Path : {}").format(Config.PATH_QUESTIONS))
	print("")
 
	dict_questions = dict()
	q_type = ""
	q_type_old = ""
	subs1 = os.listdir(Config.PATH_QUESTIONS)
	subs1.sort()
	for s1 in subs1:
		if os.path.isdir(Config.PATH_QUESTIONS + s1):
			dict_questions[s1] = dict()
			q_type_old = ""
			subs2 = os.listdir(Config.PATH_QUESTIONS + s1)
			subs2.sort()
			for s2 in subs2:
				if os.path.isfile(slash(Config.PATH_QUESTIONS + s1) + s2):
					if s2==".DS_Store":
						continue
					res = re.search(r"(^[A-Za-z0-9_]+)_q[0-9]+\.tex", s2)
					if res:
						q_type = res.group(1)
						if q_type!=q_type_old:
							dict_questions[s1][q_type] = []
							q_type_old = q_type
						dict_questions[s1][q_type].append(s2)
		else:
			if os.path.isfile(Config.PATH_QUESTIONS + s1):
				if s1==".DS_Store":
					continue
				log(_("Question not in folder (not counted): {}").format(s1))

	for type in dict_questions:
		log(f"{type} - (n-types: {len(dict_questions[type])}, n-questions: {sum(len(v) for v in dict_questions[type].values())})", 0)
		for prefix in dict_questions[type]:
			log(f"{prefix} - ({len(dict_questions[type][prefix])}) ", 1)
			for question in dict_questions[type][prefix]:
				rest_list = getRestrictions(removeSuffix(question, _EXAM_EXTENSION))
				log(question + " : " + ", ".join(rest_list), 2)
       
 
############################################################################
# 
############################################################################
def commandLatex():

	if not find_executable('pdflatex'): 
		error(_("Software 'pdflatex' not installed. Install it first to generate PDFs."))
  
	log (_("Compiling TEX files from exam {}.").format(Exam.EXAM_NAME)) 

	os.chdir(Exam.EXAM_NAME)
	latex_command1 = ["pdflatex", "-interaction", "batchmode", "-no-shell-escape", "-output-directory", ".", Exam.EXAM_NAME + ".tex"]
	# latex_command2 = ["pdflatex", "-interaction", "batchmode", "-no-shell-escape", "-output-directory", ".", Exam.EXAM_NAME + "_gabarito.tex"]

	subprocess.call(latex_command1)
	subprocess.call(latex_command1)

	#subprocess.call(latex_command2)
	#subprocess.call(latex_command2)
	
	if not os.path.exists(Exam.EXAM_NAME + ".pdf"):
		log (_("!!! Error generating exam: {}.pdf not generated.").format(Exam.EXAM_NAME), 1)
		sys.exit(1)

	if os.path.exists("../" + Exam.EXAM_NAME + ".pdf"):
		log(_("Backing up file {}.pdf to {}_bak.pdf").format(Exam.EXAM_NAME, Exam.EXAM_NAME), 1)
		shutil.copy("../" + Exam.EXAM_NAME + ".pdf", "../" + Exam.EXAM_NAME + "_bak.pdf")
		os.remove("../" + Exam.EXAM_NAME + ".pdf") 
  
	shutil.copy(Exam.EXAM_NAME + ".pdf", "../")
	os.chdir("..")
	log (_("PDF generated {}.pdf.").format(Exam.EXAM_NAME)) 

   
################################################################################
# Typer Commands

@app.command()
def init(exam: str = typer.Argument(..., help=_("Name of exam that will be created"))):
    defineGlobals(exam)
    commandInit()
    
@app.command()
def new(exam: str = typer.Argument(..., help=_("Exam to generate"))):
	defineGlobals(exam)
	Exam.examConfig = loadExamConfig()
	commandNew()
    
@app.command()
def latex(exam: str = typer.Argument(..., help=_("Exam to compile to PDF"))):
    defineGlobals(exam)
    Exam.examConfig = loadExamConfig()
    commandLatex()

@app.command()
def generate(exam: str = typer.Argument(..., help=_("Exam to generate files"))):
    defineGlobals(exam)
    Exam.examConfig = loadExamConfig()
    commandGenerate()

@app.command()
def questions():
    commandQuestions()

@app.command()
def remove(exam: str = typer.Argument(..., help=_("Exam to remove"))):
    defineGlobals(exam)
    Exam.examConfig = loadExamConfig()
    commandRemove()

@app.command()
def clear(exam: str = typer.Argument(..., help=_("Exam to clear"))):
    defineGlobals(exam)
    Exam.examConfig = loadExamConfig()
    commandClear()

@app.command()
def show(exam: str = typer.Argument(..., help=_("Exam to show details"))):
    defineGlobals(exam)
    Exam.examConfig = loadExamConfig()
    commandShow()

@app.command()
def showconfig():
    commandShow()

@app.command()
def clone(exam_from: str = typer.Argument(..., help=_("Exam source")), exam_to: str = typer.Argument(..., help=_("Exam target"))):
    defineGlobals(exam_from)
    Exam.examConfig = loadExamConfig()
    commandClone(exam_to)

def setHelp():
	# used to translate docstring of funcions
    init.__doc__=_("create new <exam>.yaml file, create template files")
    new.__doc__=_("given a <exam>.yaml file, create a new exam")
    latex.__doc__=_("generate latex and PDF of <exam>.yaml from previous generated exam")
    generate.__doc__=_("with <exam>.yaml file, calls new and latex ")
    show.__doc__=_("show configurations")
    showconfig.__doc__=_("show global configurations")
    clear.__doc__=_("remove generated exam files")
    remove.__doc__=_("remove all exam files")
    clone.__doc__=_("copy exam <exam_from>.yaml to <exam_to>.yaml")
    questions.__doc__=_("show all questions and restrictions")
    
    
def version_callback(value: bool):
    if value:
        print(f"EXAM Version: {__version__}")
        raise typer.Exit()

@app.callback()
def common(
    	ctx: typer.Context,
    	version: bool = typer.Option(None, "--version", "-v", callback=version_callback)):
    pass

def main():
	setHelp()
	loadConfig()
	app()
	return 0
            
if __name__ == '__main__':
    sys.exit(main())