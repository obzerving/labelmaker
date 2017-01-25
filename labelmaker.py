from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import sys
import string
from datetime import date
import os
import urllib
import math
import re
import logging

SESSION_STATE = "state"
SESSION_LINES = "lines"
SESSION_LENGTH = "length"
SESSION_CURRENT = "current"
SESSION_LABEL = "label"
SESSION_COPIES = "copies"

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

## State Description
##   0   Asking for the number of lines to put on the label
##   1   Asking for the text of the line to put on the label
##   2   Asking for the length of the label
##   3   Asking for number of copies of label
##   4   Asking for approval to print label

@ask.launch
def launch():
    state = 0 ## Initial state engine
    session.attributes[SESSION_STATE] = state
    welcome = render_template('welcome')
    reprompt = render_template('reprompt')
    return question(welcome).reprompt(reprompt)

@ask.intent('RouteNumber')
def RouteNumber(wholenumber, decimal, numerator, denominator):
    divtable = ['half','third','thirds','fourth','fourths','quarter', \
                'quarters','fifth','fifths','sixth','sixths','seventh', \
                'sevenths','eighth','eigths','nineth','nineths','tenth','tenths']
    divvalue = [2,3,3,4,4,4,4,5,5,6,6,7,7,8,8,9,9,10,10]
    value = 0
    ntype = 0 ## integer = 0; float = 1
    # Let's see what got filled in
    if wholenumber is not None:
        if wholenumber.isdigit():
            wn = wholenumber
            ntype = 0 ## So far, it's an integer
        else:
            askline = render_template('asknumber')
            return question(askline)
    else:
        wn = '0'
        ntype = -1 ## So far, we don't have a valid number
    if decimal is not None: ## See if this is a decimal number
        if decimal.isdigit():
            value = float(wn + '.' + decimal) ## Add it to whole number
            ntype = 1 ## we have a decimal number
        else:
            askline = render_template('asknumber')
            return question(askline)
    else: ## It's not. See if it is a fraction
        if (denominator is not None):
            if (numerator is not None):
                fdividend = int(numerator)
            else:
                fdividend = 1
            fdivisor = 0
            for frac in range(len(divtable)):
                if divtable[frac] == denominator:
                    fdivisor = divvalue[frac]
            if fdivisor != 0:
                fracstr = str(float(fdividend)/float(fdivisor)) # convert to decimal string
                value = float(wn)+float(fracstr)
                ntype = 1 ## we have a fraction
            else:
                askline = render_template('asknumber')
                return question(askline)
    if ntype == -1: ## We didn't get a valid number
        askline = render_template('asknumber')
        return question(askline)
    if ntype == 0:
        value = int(wn)
    state = session.attributes[SESSION_STATE]
    if state == 0:
        if ntype == 0:
            if value == 0: ## Has to be at least one line
                askline = render_template('zeroline')
                return question(askline)
            session.attributes[SESSION_LINES] = value
            state = 1  ## Set up to receive label text
            current = 0
            label = ''
            session.attributes[SESSION_STATE] = state
            session.attributes[SESSION_CURRENT] = current
            session.attributes[SESSION_LABEL] = label
            if value == 1:
                askline = render_template('oneline')
            else:
                 askline = render_template('multiline')
            linehelp = render_template('linehelp')
            return question(askline).reprompt(linehelp)
        else: ## Expected an integer line count
            askline = render_template('asknumber')
            return question(askline)
    if state == 1:
        label = session.attributes[SESSION_LABEL]
        current = session.attributes[SESSION_CURRENT]
        lines = session.attributes[SESSION_LINES]
        if current > 0:
            label = label + '\n'
        label = label + str(value) ###### WORK ON THIS
        current = current + 1
        session.attributes[SESSION_CURRENT] = current
        session.attributes[SESSION_LABEL] = label
        if current < lines: 
            askline = render_template('nextline') ## ask for next line
        else:
            askline = render_template('asksize') ## got all the lines
            state = 2 ## ask for label length
        session.attributes[SESSION_STATE] = state
        return question(askline)
    if state == 2:
        if ntype == 0:
            length = float(value)
        else:
            length = value
        session.attributes[SESSION_LENGTH] = length
        askline = render_template('askcopies') ## got all the lines
        state = 3 ## ask for number of copies
        session.attributes[SESSION_STATE] = state
        return question(askline)
    if state == 3:
        if ntype == 0:
            copies = value
            if copies == 0: ## Has to be at least one copy
                askline = render_template('zerocopy')
                return question(askline)
            session.attributes[SESSION_COPIES] = copies
            length = session.attributes[SESSION_LENGTH]
            label = session.attributes[SESSION_LABEL]
            if length == 0.0:
                if copies > 1:
                    askline = render_template('messages', msg=label, copies=copies)
                else:
                    askline = render_template('message', msg=label)
            else:
                if copies > 1:
                    askline = render_template('sizemsgs', labelsize=length, msg=label, copies=copies)
                else:
                    askline = render_template('sizemsg', labelsize=length, msg=label)
            state = 4 ## ready for printing
            session.attributes[SESSION_STATE] = state
            return question(askline)
        else: ## Expected an integer copy count
            askline = render_template('asknumber')
            return question(askline)

@ask.intent('LinesIntent', convert={'lines': int})
def GetLineCount(lines):
    if lines == 0: ## Has to be at least one line
        askline = render_template('zeroline')
        return question(askline)
    session.attributes[SESSION_LINES] = lines
    state = 1
    current = 0
    label = ''
    session.attributes[SESSION_STATE] = state
    session.attributes[SESSION_CURRENT] = current
    session.attributes[SESSION_LABEL] = label
    if lines == 1:
        askline = render_template('oneline')
    else:
        askline = render_template('multiline')
    linehelp = render_template('linehelp')
    return question(askline).reprompt(linehelp)

@ask.intent('CopiesIntent', convert={'copies': int})
def GetCopyCount(copies):
    if copies == 0: ## Has to be at least one copy
        askline = render_template('zerocopy')
        return question(askline)
    session.attributes[SESSION_COPIES] = copies
    length = session.attributes[SESSION_LENGTH]
    label = session.attributes[SESSION_LABEL]
    if length == 0.0:
        if copies > 1:
            askline = render_template('messages', msg=label, copies=copies)
        else:
            askline = render_template('message', msg=label)
    else:
        if copies > 1:
            askline = render_template('sizemsgs', labelsize=length, msg=label, copies=copies)
        else:
            askline = render_template('sizemsg', labelsize=length, msg=label)
    state = 4 ## ready for printing
    session.attributes[SESSION_STATE] = state
    return question(askline)

@ask.intent('YesIntent')
def PrintLabel():
    state = session.attributes[SESSION_STATE]
    if state == 4:
        length = session.attributes[SESSION_LENGTH]
        copies = session.attributes[SESSION_COPIES]
        label = session.attributes[SESSION_LABEL]
        label = '"' + label + '"'
        if length == 0.0:
            pixstr = ''
            label = 'label:' + label
        else:
            lenpix = (length / 0.00555556) # assumes 180 pixels per inch
            pixstr = str(int(lenpix))
            label = 'caption:' + label
        cmd = '/usr/bin/convert -gravity center -monochrome -negate -size ' + \
              pixstr + 'x76 ' + label + ' /tmp/lm.png'
        if os.system(cmd) != 0:
            return statement(render_template('imfail'))
        cmd = '/usr/local/bin/ptouch-print'
        for i in range(0, copies):
            if i > 0:
                cmd = cmd + ' --cutmark'
            cmd = cmd + ' --image /tmp/lm.png'
        os.system(cmd)
        askline = render_template('result')
        return statement(askline)

@ask.intent('NoIntent')
def nogo():
    ## close_user_session()
    return statement(render_template('cancel'))

@ask.intent('CatchAllIntent')
def workflow(anythinga,anythingb,anythingc,anythingd,anythinge,anythingf,anythingg,anythingh):
    anything = ''
    if anythinga is not None:
        anything = anythinga.upper()
    if anythingb is not None:
        anything = anything + ' ' + anythingb.upper()
    if anythingc is not None:
        anything = anything + ' ' + anythingc.upper()
    if anythingd is not None:
        anything = anything + ' ' + anythingd.upper()
    if anythinge is not None:
        anything = anything + ' ' + anythinge.upper()
    if anythingf is not None:
        anything = anything + ' ' + anythingf.upper()
    if anythingg is not None:
        anything = anything + ' ' + anythingg.upper()
    if anythingh is not None:
        anything = anything + ' ' + anythingh.upper()
    state = session.attributes[SESSION_STATE]
    if state == 0: ## extract number of lines in label
        match = re.search(r'(\w+)', anything)
        if match:
            lines = int(match.group(1))
            if lines == 0: ## Has to be at least one line
                askline = render_template('zeroline')
                return question(askline)
            session.attributes[SESSION_LINES] = lines
            state = 1
            current = 0
            label = ''
            session.attributes[SESSION_STATE] = state
            session.attributes[SESSION_CURRENT] = current
            session.attributes[SESSION_LABEL] = label
            if lines == 1:
                askline = render_template('oneline')
            else:
                askline = render_template('multiline')
            linehelp = render_template('linehelp')
            return question(askline).reprompt(linehelp)
        else:
            return question(reprompt)
    if state == 1: ## add text to label
        label = session.attributes[SESSION_LABEL]
        current = session.attributes[SESSION_CURRENT]
        lines = session.attributes[SESSION_LINES]
        if current > 0:
            label = label + '\n'
        if anything == 'TIMESTAMP': ## timestamp must be only word in line
            today = date.today()
            label = label + today.strftime('%m/%d/%Y')
        elif anything == 'NOTHING': ## must be only word in line
            label = label + ' ' ## just add a blank space
        else:
            label = label + anything
        current = current + 1
        session.attributes[SESSION_CURRENT] = current
        session.attributes[SESSION_LABEL] = label
        if current < lines: 
            askline = render_template('nextline') ## ask for next line
        else:
            askline = render_template('asksize') ## got all the lines
            state = 2 ## ask for label length
        session.attributes[SESSION_STATE] = state
        return question(askline)
    if state == 2:
        label = session.attributes[SESSION_LABEL]
        match = re.search(r'(\w+)', anything)
        if match:
            length = float(match.group(1))
            session.attributes[SESSION_LENGTH] = length
            state = 3 ## ask for number of copies
            session.attributes[SESSION_STATE] = state
            return question(askline)
        else:
            askline = render_template('asknumber')
            return question(askline)
    if state == 3:
        match = re.search(r'(\w+)', anything)
        if match:
            copies = int(match.group(1))
            if copies == 0: ## Has to be at least one copy
                askline = render_template('zerocopy')
                return question(askline)
            session.attributes[SESSION_COPIES] = copies
            length = session.attributes[SESSION_LENGTH]
            label = session.attributes[SESSION_LABEL]
            lines = session.attributes[SESSION_LINES]
            if length == 0.0:
                if copies > 1:
                    askline = render_template('messages', msg=label, copies=copies)
                else:
                    askline = render_template('message', msg=label)
            else:
                if copies > 1:
                    askline = render_template('sizemsgs', labelsize=length, msg=label, copies=copies)
                else:
                    askline = render_template('sizemsg', labelsize=length, msg=label)
            state = 4 ## ready for printing
            session.attributes[SESSION_STATE] = state
            return question(askline)
        else:
            askline = render_template('asknumber')
            return question(askline)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    ## close_user_session()
    return statement(render_template('cancel'))


@ask.intent('AMAZON.StopIntent')
def stop():
    ## close_user_session()
    return statement(render_template('stop'))

@ask.session_ended
def session_ended():
    ## close_user_session()
    return "", 200

if __name__ == '__main__':
    app.run(debug=True)
