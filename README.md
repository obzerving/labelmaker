Labelmaker

This is an Alexa skill written in Flask-Ask that runs on a Raspberry Pi connected
to a Brother P-Touch label printer. Though it does not use Amazon Web Services (AWS),
you need a developer account to set up the skill.

A typical session:

User: Alexa, start label maker

Alexa: Welcome to label maker. How many lines of text will there be in this label?

User: two
[Though the skill will adjust the font size based on the number of lines,
it probably makes sense to limit it to 4 lines for readability.]

Alexa: What should I put on the first line?

User: tuna salad

Alexa: What should I put on the next line?

User: timestamp
["timestamp" by itself on a line will be replaced by the current date.
"nothing" by itself will be replaced by a blank line.]

Alexa: How many inches do you want the label to be?

User: one and an eigth
[The skill recognizes a non-exhaustive list of decimals and fractions,
such as "one point two," "three quarters," and "one and three fifths."
In addition, if you say "zero," the skill will make the label the minimum
length needed.]

Alexa: How many copies of the label do you want?

User: three

Alexa: The label will be 1.125 inches and will say TUNA SALAD\n01/24/2017.
       Shall I print 3 copies of it?

User: yes

Alexa: Your label has been printed.

Hardware Requirements:

- Brother P-touch 2430PC printer

- Raspberry Pi with Internet connectivity

Software Requirements:

 - Debian Jessie (https://www.raspberrypi.org/downloads/raspbian/)
     
 - libusb (sudo apt-get install libusb-1.0.0-dev)
 
 - libgd (sudo apt-get install libgd2-xpm-dev)
 
 - ImageMagick (sudo apt-get install imagemagick)
 
 - Ptouch-print (https://github.com/dradermacher/ptouch-print)

 - Flask-Ask (https://github.com/johnwheeler/flask-ask)
 
 
 Installation:
 
 1. Install required software on Raspberry (in order listed)
 
 2. Build the skill. See this article, "Flask-Ask: A New Python Framework for Rapid Alexa Skills Kit Development"
 (https://developer.amazon.com/blogs/post/Tx14R0IYYGH3SKT/Flask-Ask-A-New-Python-Framework-for-Rapid-Alexa-Skills-Kit-Development)
 for the step-by-step instructions. Make the following changes:

    a. Instead of memory_game.py, you will be running labelmaker.py

    b. Use the templates.yaml in this repository

    c. Use "label maker" for both the "Name" and "Invocation Name" fields"

    d. The Intent Schema for this skill is in this repository under intents.txt.

    e. The utterances for this skill are in this repository under utterances.txt

    f. As part of the "Configure the Skill" step, you will need to add the
       custom slots "DENOMINATOR" and "CATCHALL" in the configuration section
       [The list for each custom slot is in this repository under CustomSlots.txt]
    