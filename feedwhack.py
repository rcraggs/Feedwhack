import sublime, sublime_plugin
import re
from pprint import pprint

class InsertfeedbackCommand(sublime_plugin.TextCommand):

    def run(self, edit, insert_text):
        self.view.insert(edit, self.view.sel()[0].begin(), insert_text)
 
class FeedwhackfindCommand(sublime_plugin.TextCommand):

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

        # Get the current cursor position
        current_line = self.view.rowcol(self.view.sel()[0].begin())[0]

        for line in source_lines:

            line_text = self.view.substr(line)

            # See if this is a header - if so find out which
            header_match = re.match( r'^#+\s(.*)', line_text)

            if header_match:
               prev_header = header_match.group(1)

            # If this is the current line - see what the previous header was   
            if self.view.rowcol(line.begin())[0] == current_line:
                current_header = prev_header

            # If this is a bullet point add it to the list for the header
            bullet_match = re.match( r'^\s*-\s*(.*)', line_text)

            if bullet_match:
                bullet_text = bullet_match.group(1)

                # Add it if it's not already there
                if prev_header not in self.feedback_dictionary:
                    self.feedback_dictionary[prev_header] = set()

                self.feedback_dictionary[prev_header].add(bullet_text)

               # self.feedback_dictionary[prev_header] = self.feedback_dictionary.get(prev_header, []) + [bullet_text]
               # self.all_feedback = self.all_feedback + [bullet_text]

        if current_header in self.feedback_dictionary:
            # Open the quick panel to select the thing 
            self.current_feedback_list = list(self.feedback_dictionary[current_header])
            self.view.window().show_quick_panel(self.current_feedback_list, self.insert_line)  
        else:
            sublime.error_message("You are not in a section")

