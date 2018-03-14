import sublime, sublime_plugin
import re
from itertools import chain
from collections import Counter

def createFeedbackDictionary(source_lines, view, current_line_number):

    feedback_dictionary = {}
    current_header = ""
    prev_header = ""
    line_num = 0 # The num of the lines as we look through.

    for line in source_lines:

        line_text = view.substr(line)

        # See if this is a header - if so find out which
        header_match = re.match( r'^#+\s*(.*)', line_text)

        if header_match:
           prev_header = header_match.group(1).strip()

        # If this is the current line - see what the previous header was   
        line_num = view.rowcol(line.begin())[0] 
        if line_num == current_line_number:
            current_header = prev_header

        # If this is a bullet point add it to the list for the header
        bullet_match = re.match( r'^\s*-\s+((?!@@)(?!e\.g\.).+)', line_text) # Ignore lines starting with @@
        if bullet_match and len(bullet_match.group(1).strip()) > 0:
            
            bullet_text = bullet_match.group(1).strip()

            if bullet_text.find('@@') > -1:
                bullet_text = bullet_text[:bullet_text.find('@@')]

            print(bullet_text.find('@@'))    

            # Add it if it's not already there
            if prev_header not in feedback_dictionary:
                feedback_dictionary[prev_header] = []

            feedback_dictionary[prev_header].append(bullet_text)

    # If the current line of the cursor is below the last line, then we're within the last header
    if current_line_number >= line_num:
        current_header = prev_header

    return feedback_dictionary, current_header

class InsertfeedbackCommand(sublime_plugin.TextCommand):

    def run(self, edit, insert_text):
        self.view.insert(edit, self.view.sel()[0].begin(), insert_text)

class FeedwhackCommand(sublime_plugin.TextCommand):

    feedback_dictionary = {}
    current_feedback_list = set()
    all_feedback = []    

    def insert_line(self, index):

        if index == -1:
            return
        else:
            self.view.run_command('insertfeedback', {"insert_text": self.current_feedback_list[index] })

    def run(self, edit):

        source_lines = self.view.lines(sublime.Region(0, self.view.size()))
        current_line = self.view.rowcol(self.view.sel()[0].begin())[0]
        current_header = ""

        self.feedback_dictionary, current_header = createFeedbackDictionary(source_lines, self.view, current_line)
    
        if current_header in self.feedback_dictionary:
            # Open the quick panel to select the thing 
            print(Counter(self.feedback_dictionary[current_header]).most_common())
            self.current_feedback_list = [fb for fb,count in Counter(self.feedback_dictionary[current_header]).most_common()]
            self.view.window().show_quick_panel(self.current_feedback_list, self.insert_line)  
        else:
            sublime.error_message("You are not in a section I recognise")

class FeedwhackallCommand(sublime_plugin.TextCommand):

    feedback_dictionary = {}
    current_feedback_list = set()
    all_feedback = []    

    def insert_line(self, index):

        if index == -1:
            return
        else:
            self.view.run_command('insertfeedback', {"insert_text": self.current_feedback_list[index] })

    def run(self, edit):

        source_lines = self.view.lines(sublime.Region(0, self.view.size()))
        current_line = self.view.rowcol(self.view.sel()[0].begin())[0]
        current_header = ""

        self.feedback_dictionary, current_header = createFeedbackDictionary(source_lines, self.view, current_line)

        if current_header in self.feedback_dictionary:
            # Open the quick panel to select the thing 
            self.current_feedback_list = list(chain.from_iterable([ v for v in self.feedback_dictionary.values() ]))
            print(len(self.current_feedback_list))
            self.view.window().show_quick_panel(self.current_feedback_list, self.insert_line)  
        else:
            sublime.error_message("You are not in a section")

