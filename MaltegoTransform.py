#!/usr/bin/python 
#######################################################
# Maltego Python Local Transform Helper               #
#   Version 0.3                                       #
#                                                     #
# Local transform specification can be found at:      #
#    http://ctas.paterva.com/view/Specification	      #
#                                                     #
# For more help and other local transforms            #
# try the forum or mail me:                           #
#                                                     #
#   http://www.paterva.com/forum                      #
#                                                     #
#  Andrew MacPherson [ andrew <<at>> Paterva.com ]    #
#                                                     #
#  UPDATED: 2016/08/29 - PR ["&amp;","&gt;","&lt;"]   #
#  UPDATED: 2015/10/29 - PR                           #
#  UPDATED: 2016/08/19 - AM (fixed # and = split)     #
#######################################################

import sys

BOOKMARK_COLOR_NONE = "-1"
BOOKMARK_COLOR_BLUE = "0"
BOOKMARK_COLOR_GREEN = "1"
BOOKMARK_COLOR_YELLOW = "2"
BOOKMARK_COLOR_ORANGE = "3"
BOOKMARK_COLOR_RED = "4"

LINK_STYLE_NORMAL = "0"
LINK_STYLE_DASHED = "1"
LINK_STYLE_DOTTED = "2"
LINK_STYLE_DASHDOT = "3"

UIM_FATAL = 'FatalError'
UIM_PARTIAL = 'PartialError'
UIM_INFORM = 'Inform'
UIM_DEBUG = 'Debug'


class MaltegoEntity(object):
    value = ""
    weight = 100
    displayInformation = None
    additionalFields = []
    iconURL = ""
    entityType = "Phrase"

    def __init__(self, entity_type=None, v=None):
        if entity_type is not None:
            self.entityType = entity_type
        if v is not None:
            self.value = sanitise(v)
        self.additionalFields = []
        self.displayInformation = None

    def set_type(self, entity_type=None):
        if entity_type is not None:
            self.entityType = entity_type

    def setValue(self, entity_value=None):
        if entity_value is not None:
            self.value = sanitise(entity_value)

    def setWeight(self, w=None):
        if w is not None:
            self.weight = w

    def setDisplayInformation(self, di=None):
        if di is not None:
            self.displayInformation = di

    def addAdditionalFields(self, field_name=None, display_name=None, matching_rule=False, value=None):
        self.additionalFields.append([sanitise(field_name), sanitise(display_name), matching_rule, sanitise(value)])

    def setIconURL(self, iU=None):
        if iU is not None:
            self.iconURL = iU

    def setLinkColor(self, color):
        self.addAdditionalFields('link#maltego.link.color', 'LinkColor', '', color)

    def setLinkStyle(self, style):
        self.addAdditionalFields('link#maltego.link.style', 'LinkStyle', '', style)

    def setLinkThickness(self, thick):
        self.addAdditionalFields('link#maltego.link.thickness', 'Thickness', '', str(thick))

    def setLinkLabel(self, label):
        self.addAdditionalFields('link#maltego.link.label', 'Label', '', label)

    def setBookmark(self, bookmark):
        self.addAdditionalFields('bookmark#', 'Bookmark', '', bookmark)

    def setNote(self, note):
        self.addAdditionalFields('notes#', 'Notes', '', note)

    def returnEntity(self):
        print("<Entity Type=\"" + str(self.entityType) + "\">")
        print("<Value>" + str(self.value) + "</Value>")
        print("<Weight>" + str(self.weight) + "</Weight>")
        if self.displayInformation is not None:
            print("<DisplayInformation><Label Name=\"\" Type=\"text/html\"><![CDATA[" + str(
                self.displayInformation) + "]]></Label></DisplayInformation>")
        if len(self.additionalFields) > 0:
            print("<AdditionalFields>")
            for i in range(len(self.additionalFields)):
                if str(self.additionalFields[i][2]) != "strict":
                    print("<Field Name=\"" + str(self.additionalFields[i][0]) + "\" DisplayName=\"" + str(
                        self.additionalFields[i][1]) + "\">" + str(self.additionalFields[i][3]) + "</Field>")
                else:
                    print("<Field MatchingRule=\"" + str(self.additionalFields[i][2]) + "\" Name=\"" + str(
                        self.additionalFields[i][0]) + "\" DisplayName=\"" + str(
                        self.additionalFields[i][1]) + "\">" + str(self.additionalFields[i][3]) + "</Field>")
            print("</AdditionalFields>")
        if len(self.iconURL) > 0:
            print("<IconURL>" + self.iconURL + "</IconURL>")
        print("</Entity>")


class MaltegoTransform(object):
    entities = []
    exceptions = []
    UIMessages = []
    values = {}

    def __init__(self):
        self.values = {}
        self.value = None

    def parseArguments(self, argv):
        if argv[1] is not None:
            self.value = argv[1]

        if len(argv) > 2:
            if argv[2] is not None:
                input_vars = argv[2].split('#')
                for x in range(0, len(input_vars)):
                    vars_values = input_vars[x].split('=', 1)
                    if len(vars_values) == 2:
                        self.values[vars_values[0]] = vars_values[1]

    def getValue(self):
        if self.value is not None:
            return self.value

    def getVar(self, var_name):
        if var_name in self.values.keys():
            if self.values[var_name] is not None:
                return self.values[var_name]

    def addEntity(self, entity_type, entity_value):
        me = MaltegoEntity(entity_type, entity_value)
        self.addEntityToMessage(me)
        return self.entities[len(self.entities) - 1]

    def addEntityToMessage(self, maltego_entity):
        self.entities.append(maltego_entity)

    def addUIMessage(self, message, message_type="Inform"):
        self.UIMessages.append([message_type, message])

    def addException(self, exception_string):
        self.exceptions.append(exception_string)

    def throwExceptions(self):
        print("<MaltegoMessage>")
        print("<MaltegoTransformExceptionMessage>")
        print("<Exceptions>")

        for i in range(len(self.exceptions)):
            print("<Exception>" + self.exceptions[i] + "</Exception>")
            print("</Exceptions>")
            print("</MaltegoTransformExceptionMessage>")
            print("</MaltegoMessage>")
            exit()

    def returnOutput(self):
        print("<MaltegoMessage>")
        print("<MaltegoTransformResponseMessage>")

        print("<Entities>")
        for i in range(len(self.entities)):
            self.entities[i].returnEntity()
        print("</Entities>")

        print("<UIMessages>")
        for i in range(len(self.UIMessages)):
            print("<UIMessage MessageType=\"" + self.UIMessages[i][0] + "\">" + self.UIMessages[i][1] + "</UIMessage>")
        print("</UIMessages>")

        print("</MaltegoTransformResponseMessage>")
        print("</MaltegoMessage>")

    def writeSTDERR(self, msg):
        sys.stderr.write(str(msg))

    def heartbeat(self):
        self.writeSTDERR("+")

    def progress(self, percent):
        self.writeSTDERR("%" + str(percent))

    def debug(self, msg):
        self.writeSTDERR("D:" + str(msg))


def sanitise(value):
    replace_these = ["&", ">", "<"]
    replace_with = ["&amp;", "&gt;", "&lt;"]
    temp_value = value
    for i in range(0, len(replace_these)):
        temp_value = temp_value.replace(replace_these[i], replace_with[i])
    return temp_value
