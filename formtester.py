import sys
import mechanize
import random
from convertList import toArray
from progressbar import Bar, ETA, FileTransferSpeed, Percentage, ProgressBar, ReverseBar
import time

class FormNotFound(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def main():
    print "########################################"
    print "######## Welcome to Form Tester ########"
    print "################ v1.0 ##################\n"

    ### Form Variables ###
    print "Enter the url of the main web page."
    URL = raw_input("Enter (ex. http://test.com/): ")

    print "\nEnter the url of the form."
    FormURL = raw_input("Enter (ex. profileCreate.php): ")

    ### Return the Form ###
    try:
        forms = connect_to_form(URL, FormURL)
    except (mechanize.URLError, mechanize.HTTPError, IndexError, ValueError, FormNotFound) as e:
        if isinstance(e, mechanize.HTTPError):
            print "\nError:", e.code
        elif isinstance(e, IndexError):
            print "\nError:", e
        elif isinstance(e, ValueError):
            print "\nError:", e
        elif isinstance(e, FormNotFound):
            print "\nError:", e
        else:
            print "\nError:", e.reason.args
        exitmsg()
        exit(1)

    form = select_form(forms)
    inputs = select_inputs(form)
    print "Selected Inputs: %s\n" % str(inputs)

    print "Enter the number of times you would like to test the form."
    iterations = raw_input("Enter: ")
    while not iterations.isdigit():
        print "Error: Enter a valid, positive integer.\n"
        iterations = raw_input("Enter: ")

    ### Start Timer ###
    start_time = time.time()

    ### Submit Form ###
    blitzkrieg(form, inputs, int(iterations))

    ### Display Completion Time and Exit ###
    print("Completed in %s seconds..." % (time.time() - start_time))
    exitmsg()

'''
Function: connect_to_form
Description: Request access to form from entered web url.
Input: Website URL, Location of Form
Output: Forms found on specified webpage
'''
def connect_to_form(url, formurl):
    print "\nConnecting to Web Page...",
    # Connect to URL (add error handling!!)
    request = mechanize.Request(mechanize.urljoin(url, formurl))
    response = mechanize.urlopen(request)
    monkeypatch_mechanize()
    print "Success."

    # Retrieve forms
    forms = mechanize.ParseResponse(response, backwards_compat=False)
    response.close()

    if len(forms) <= 0:
        raise FormNotFound('No Forms were found on the web page.')

    return forms

'''
Function: select_forms
Description: Display forms and their attributes, in addition
to their index.  User then selects form.
Input: Forms from webpage
Output: Form from webpage
'''
def select_form(forms):
    print "\nThe following forms were retrieved from the url:"
    i = 0
    for form in forms:
        print "Form %d: %s" % (i, str(form.attrs))
        i += 1

    print "\nEnter the index of the form to select it."
    while True:
        index = raw_input("Enter: ")
        if not index.isdigit():
            print "Error: Enter a valid, positive integer.\n"
        elif int(index) < 0 or int(index) >= len(forms):
            print "Error: Enter a index between", 0 ,"and", str(len(forms) - 1) + ".\n"
        else:
            break        
    return forms[int(index)]

'''
Function: select_inputs
Description: Select form inputs to fill.
Input: Form from webpage
Output: List of selected inputs
'''
def select_inputs(f):
    print "\nThe following inputs were retrieved from the form:"
    i = 0
    for control in f.controls:
        required = "no"
        if hasattr(control, 'attrs'):
            if "required" in control.attrs:
                required = "yes"
        print "#%3i:  Name: %-15s   Type: %-12s   Required: %-3s" % (i, control.name, control.type, required)
        i += 1

    indexes = []
    print "\nEnter the index of the form to select it."
    print "Enter one index per line, pressing enter after each index. Type 'DONE' when complete."
    while True:
        index = raw_input("Enter: ")
        if index == "DONE":
            break;
        elif not index.isdigit():
            print "Error: Enter a valid, positive integer.\n"
        elif int(index) < 0 or int(index) >= len(f.controls):
            print "Error: Enter a index between", 0 ,"and", str(len(f.controls) - 1) + ".\n"
        elif int(index) in indexes:
            print "Error: You already selected that input.\n"
        else:
            indexes.append(int(index))
    return indexes

# Work-around for a mechanize 0.2.5 bug. See: https://github.com/jjlee/mechanize/pull/58
def monkeypatch_mechanize():
    if mechanize.__version__ < (0, 2, 6):
        from mechanize._form import SubmitControl, ScalarControl

        def __init__(self, type, name, attrs, index=None):
            ScalarControl.__init__(self, type, name, attrs, index)
            # IE5 defaults SUBMIT value to "Submit Query"; Firebird 0.6 leaves it
            # blank, Konqueror 3.1 defaults to "Submit".  HTML spec. doesn't seem
            # to define this.
            if self.value is None:
                if self.disabled:
                    self.disabled = False
                    self.value = ""
                    self.disabled = True
                else:
                    self.value = ""
            self.readonly = True

        SubmitControl.__init__ = __init__

### Submit the Form a given number of times ###
def blitzkrieg(f, inputs, it):
    setInputValues(f, inputs)

    print "Submitting..."
    widgets = [Bar('>'), Percentage(), ' - ', ETA(), ' ', ReverseBar('<')]
    pbar = ProgressBar(widgets=widgets, maxval=it)
    pbar.start()
    for i in range(it):
        post(form)
        pbar.update(i+1)
    pbar.finish()

def setInputValues(f, inputs):
    for i in inputs:
        print f.controls[i]
        print dir(f.controls[i])

    # TO-DO: Allow user to choose values for input, OR
    # Automatically fill in the inputs

### Submit Form ###
def post(f):
    # TO-DO: Insert values for input in the form

    request = form.click()
    try:
        response = mechanize.urlopen(request)
    except mechanize.HTTPError, response:
        pass
    # debug_post(response)
    response.close()

def debug_post(response):
    print response.geturl()
    for name, value in response.info().items():
        if name != "date":
            print "%s: %s" % (name.title(), value)
            print response.read()

def exitmsg():
    print "\nExiting..."
    print "######################################"

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exitmsg()
