from gui_lib.container import Container
from gui_lib.label import Label
from gui_lib.listbox import Listbox
from gui_lib.fill import Fill
from verenigingNaamCoupler import getVerenigingNaam
from productNaamCoupler import getProductType
from math import copysign, floor
import curses

def strConvert(value):
    return value.encode('utf-8')

def intConvert(value):
    return str(value)

def moneyConvert(value):
    prefix = ""
    if value < 0:
        prefix = "-"
        value = -value

    cents = value % 100
    value /= 100
    if cents < 10:
        return prefix + str(value)+ ",0" + str(cents)
    return prefix + str(value) + "," + str(cents)

_regelLayout = [
        ('Productnaam', 'naam', 2, strConvert),
        ('Aantal', 'aantal', 1, intConvert),
        ('Stukprijs', 'stukprijs', 2, moneyConvert),
        ('Totaalprijs', 'totaalprijs', 2, moneyConvert),
        ('BTW', 'btw', 1, moneyConvert)
]

class factuurRegel(Container):
    def __init__(self, width, height, factuurregel):
        super(factuurRegel, self).__init__(width, height)
        self.factuurRegel = factuurregel

        self.totalWeight = 0
        self.fieldLabel = []
        self.fieldLabelIdx = []
        for i in range(0, len(_regelLayout)):
            self.totalWeight += _regelLayout[i][2]
            self.fieldLabel.append(Label(0,0,_regelLayout[i][3](factuurregel[_regelLayout[i][1]])))
            self.fieldLabelIdx.append(self.addChild(0,0,self.fieldLabel[-1]))

        self.resize(width, height)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.boxPerWeight = width/self.totalWeight

        offset = 0
        for i in range(0, len(_regelLayout)):
            self.fieldLabel[i].resize(self.boxPerWeight*_regelLayout[i][2], 1)
            self.setChildPos(self.fieldLabelIdx[i], offset, 0)
            offset += _regelLayout[i][2] * self.boxPerWeight

    def onFocus(self):
        for fieldLabel in self.fieldLabel:
            fieldLabel.setAttribute(curses.A_REVERSE)
        return True

    def offFocus(self):
        for fieldLabel in self.fieldLabel:
            fieldLabel.setAttribute(curses.A_NORMAL)

class factuurRegelHeader(Container):
    def __init__(self, width, height):
        super(factuurRegelHeader, self).__init__(width, height)
        self.totalWeight = 0
        self.fieldLabel = []
        self.fieldLabelIdx = []
        for i in range(0, len(_regelLayout)):
            self.totalWeight += _regelLayout[i][2]
            self.fieldLabel.append(Label(0,0,_regelLayout[i][0], curses.A_BOLD))
            self.fieldLabelIdx.append(self.addChild(0,0,self.fieldLabel[-1]))

        self.resize(width, height)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.boxPerWeight = width/self.totalWeight

        offset = 0
        for i in range(0, len(_regelLayout)):
            self.fieldLabel[i].resize(self.boxPerWeight*_regelLayout[i][2], 1)
            self.setChildPos(self.fieldLabelIdx[i], offset, 0)
            offset += _regelLayout[i][2] * self.boxPerWeight

class factuurDetail(Container):
    def __init__(self, width, height, factuur, manager):
        super(factuurDetail, self).__init__(width, height)

        #Associated data object
        self.factuur = factuur
        self.manager = manager

        self.infobox = factuurInfobox(width,0,factuur)
        self.infoboxIdx = self.addChild(0,0,self.infobox)

        self.factuurRegelHeader = factuurRegelHeader(width,1)
        self.factuurRegelHeaderIdx = self.addChild(0,0,self.factuurRegelHeader)

        self.factuurRegelBox = Listbox(width, 0)
        self.factuurRegelBoxIdx = self.addChild(0,0,self.factuurRegelBox)

        self.factuurBorrelTotaal = 0
        self.factuurKantineTotaal = 0
        self.factuurEmballageTotaal = 0
        self.factuurOverigeTotaal = 0
        self.factuurBorrelTotaalOnafgerond = 0
        self.factuurKantineTotaalOnafgerond = 0
        self.factuurEmballageTotaalOnafgerond = 0
        self.factuurOverigeTotaalOnafgerond = 0

        for regel in factuur['regels']:
            self.factuurRegelBox.append(factuurRegel(width,1,regel))
            if 'prd_id' in regel:
                type = getProductType(regel['prd_id'])
                if type=='kantine':
                    self.factuurKantineTotaal += copysign(regel['totaalprijs'], regel['aantal'])
                    self.factuurKantineTotaalOnafgerond += regel['stukprijs'] * regel['aantal']
                elif type=='borrel':
                    self.factuurBorrelTotaal += copysign(regel['totaalprijs'], regel['aantal'])
                    self.factuurBorrelTotaalOnafgerond += regel['stukprijs'] * regel['aantal']
                elif type=='emballage':
                    self.factuurEmballageTotaal += copysign(regel['totaalprijs'], regel['aantal'])
                    self.factuurEmballageTotaalOnafgerond += regel['stukprijs'] * regel['aantal']
                else:
                    self.factuurOverigeTotaal += copysign(regel['totaalprijs'], regel['aantal'])
                    self.factuurOverigeTotaalOnafgerond += regel['stukprijs'] * regel['aantal']
            else:
                self.factuurOverigeTotaal += copysign(regel['totaalprijs'], regel['aantal'])
                self.factuurOverigeTotaalOnafgerond += regel['stukprijs'] * regel['aantal']

        self.factuurBorrelTotaalLabel = Label(0,0,"Borreltotaal: " + moneyConvert(int(self.factuurBorrelTotaal)))
        self.factuurBorrelTotaalLabelIdx = self.addChild(0,0,self.factuurBorrelTotaalLabel)
        self.factuurBorrelmargeTotaalLabel = Label(0,0,"Borrelmargetotaal: " + moneyConvert(int(floor(self.factuurBorrelTotaal/1.03))))
        self.factuurBorrelmargeTotaalLabelIdx = self.addChild(0,0,self.factuurBorrelmargeTotaalLabel)
        self.factuurKantineTotaalLabel = Label(0,0,"Kantinetotaal: " + moneyConvert(int(self.factuurKantineTotaal)))
        self.factuurKantineTotaalLabelIdx = self.addChild(0,0,self.factuurKantineTotaalLabel)
        self.factuurEmballageTotaalLabel = Label(0,0,"Emballagetotaal: " + moneyConvert(int(self.factuurEmballageTotaal)))
        self.factuurEmballageTotaalLabelIdx = self.addChild(0,0,self.factuurEmballageTotaalLabel)
        self.factuurOverigeTotaalLabel = Label(0,0,"Overigetotaal: " + moneyConvert(int(self.factuurOverigeTotaal)))
        self.factuurOverigeTotaalLabelIdx = self.addChild(0,0,self.factuurOverigeTotaalLabel)
        self.factuurTotaalLabel = Label(0,0,"Totaal: " + moneyConvert(int(self.factuurBorrelTotaal+self.factuurKantineTotaal+self.factuurEmballageTotaal+self.factuurOverigeTotaal)))
        self.factuurTotaalLabelIdx = self.addChild(0,0,self.factuurTotaalLabel)

        # added details:

        self.factuurBorrelTotaalOnafgerondLabel = Label(0,0,"Borreltotaal-onafgerond: " + moneyConvert(int(self.factuurBorrelTotaalOnafgerond)))
        self.factuurBorrelTotaalOnafgerondLabelIdx = self.addChild(0,0,self.factuurBorrelTotaalOnafgerondLabel)
        self.factuurKantineTotaalOnafgerondLabel = Label(0,0,"Kantinetotaal-onafgerond: " + moneyConvert(int(self.factuurKantineTotaalOnafgerond)))
        self.factuurKantineTotaalOnafgerondLabelIdx = self.addChild(0,0,self.factuurKantineTotaalOnafgerondLabel)
        self.factuurEmballageTotaalOnafgerondLabel = Label(0,0,"Emballagetotaal-onafgerond: " + moneyConvert(int(self.factuurEmballageTotaalOnafgerond)))
        self.factuurEmballageTotaalOnafgerondLabelIdx = self.addChild(0,0,self.factuurEmballageTotaalOnafgerondLabel)
        self.factuurOverigeTotaalOnafgerondLabel = Label(0,0,"Overigetotaal-onafgerond: " + moneyConvert(int(self.factuurOverigeTotaalOnafgerond)))
        self.factuurOverigeTotaalOnafgerondLabelIdx = self.addChild(0,0,self.factuurOverigeTotaalOnafgerondLabel)
        self.factuurTotaalOnafgerondLabel = Label(0,0,"Totaal-onafgerond: " + moneyConvert(int(self.factuurBorrelTotaalOnafgerond+self.factuurKantineTotaalOnafgerond+self.factuurEmballageTotaalOnafgerond+self.factuurOverigeTotaalOnafgerond)))
        self.factuurTotaalOnafgerondLabelIdx = self.addChild(0,0,self.factuurTotaalOnafgerondLabel)

        self.factuurAfrondingLabel = Label(0,0,"Afronding: " + moneyConvert(int(self.factuurBorrelTotaalOnafgerond - self.factuurBorrelTotaal + self.factuurKantineTotaalOnafgerond - self.factuurKantineTotaal + self.factuurEmballageTotaalOnafgerond - self.factuurEmballageTotaal + self.factuurOverigeTotaalOnafgerond - self.factuurOverigeTotaal)))
        self.factuurAfrondingLabelIdx = self.addChild(0,0,self.factuurAfrondingLabel)

        self.resize(width, height)

    def keyEvent(self, key):
        if key == curses.KEY_BACKSPACE:
            self.manager.pop()
        elif key == ord('c'):
            print "test"
        else:
            super(factuurDetail,self).keyEvent(key)

    def resize(self, width, height):
        self.width = width
        self.height = height
        swidth = int(width/3.)
        hwidth = 2*int(width/3.)
        voffset = 0
        self.infobox.resize(width, 0)
        self.setChildPos(self.infoboxIdx,0,voffset)
        voffset += self.infobox.size()[1]
        self.factuurRegelHeader.resize(width, 1)
        self.setChildPos(self.factuurRegelHeaderIdx, 0, voffset)
        voffset += 1
        self.factuurRegelBox.resize(width, height - voffset - 4)
        self.setChildPos(self.factuurRegelBoxIdx, 0, voffset)

        # left colomn
        self.factuurBorrelTotaalLabel.resize(swidth, 1)
        self.setChildPos(self.factuurBorrelTotaalLabelIdx, 0, height-4)
        self.factuurKantineTotaalLabel.resize(swidth, 1)
        self.setChildPos(self.factuurKantineTotaalLabelIdx, 0, height-3)
        self.factuurEmballageTotaalLabel.resize(swidth, 1)
        self.setChildPos(self.factuurEmballageTotaalLabelIdx, 0, height-2)
        self.factuurOverigeTotaalLabel.resize(swidth, 1)
        self.setChildPos(self.factuurOverigeTotaalLabelIdx, 0, height-1)

        # middle column
        self.factuurBorrelTotaalOnafgerondLabel.resize(swidth, 1)
        self.setChildPos(self.factuurBorrelTotaalOnafgerondLabelIdx, swidth, height-4)
        self.factuurKantineTotaalOnafgerondLabel.resize(swidth, 1)
        self.setChildPos(self.factuurKantineTotaalOnafgerondLabelIdx, swidth, height-3)
        self.factuurEmballageTotaalOnafgerondLabel.resize(swidth, 1)
        self.setChildPos(self.factuurEmballageTotaalOnafgerondLabelIdx, swidth, height-2)
        self.factuurOverigeTotaalOnafgerondLabel.resize(swidth, 1)
        self.setChildPos(self.factuurOverigeTotaalOnafgerondLabelIdx, swidth, height-1)

        #right column

        self.factuurBorrelmargeTotaalLabel.resize(swidth, 1)
        self.setChildPos(self.factuurBorrelmargeTotaalLabelIdx, hwidth, height-4)
        self.factuurTotaalLabel.resize(swidth, 1)
        self.setChildPos(self.factuurTotaalLabelIdx, hwidth, height-3)
        self.factuurTotaalOnafgerondLabel.resize(swidth, 1)
        self.setChildPos(self.factuurTotaalOnafgerondLabelIdx, hwidth, height-2)
        self.factuurAfrondingLabel.resize(swidth, 1)
        self.setChildPos(self.factuurAfrondingLabelIdx, hwidth, height-1)

class factuurInfobox(Container):
    def __init__(self, width, height, factuur):
        super(factuurInfobox, self).__init__(width, height)

        #Associated data object
        self.factuur = factuur

        #Layout settings
        self.labelWidth = 19
        self.minValueWidth = 20

        if 'vereniging_id' in factuur:
            self.otherPartyLabel = Label(0,1,"Vereniging:")
            self.otherPartyValue = Label(0,1,getVerenigingNaam(factuur['vereniging_id']).encode('utf-8'))
        else:
            self.otherPartyLabel = Label(0,1,"Leverancier:")
            self.otherPartyValue = Label(0,1,factuur['leverancier'].encode('utf-8'))
        self.volgnummerLabel = Label(0,1,"Volgnummer:")
        self.volgnummerValue = Label(0,1,str(factuur['volgnummer']))

        self.factuurDatumLabel = Label(0,1,"Factuurdatum:")
        self.factuurDatumValue = Label(0,1,factuur['factuurdatum'].encode('utf-8'))
        self.leverDatumLabel = Label(0,1, "Leverdatum:")
        self.leverDatumValue = Label(0,1,factuur['leverdatum'].encode('utf-8'))

        self.separatorFill = Fill(0,0,'|')
        self.separatorFillIdx = self.addChild(0,0,self.separatorFill)

        self.hasVerantwoordelijke = False
        if 'verantwoordelijke' in factuur:
            self.hasVerantwoordelijke = True
            self.verantwoordelijkeLabel = Label(0,1,"Verantwoordelijke:")
            self.verantwoordelijkeValue = Label(0,1,factuur['verantwoordelijke'].encode('utf-8'))

        self.otherPartyLabelIdx = self.addChild(0,0,self.otherPartyLabel)
        self.otherPartyValueIdx = self.addChild(0,0,self.otherPartyValue)
        self.volgnummerLabelIdx = self.addChild(0,0,self.volgnummerLabel)
        self.volgnummerValueIdx = self.addChild(0,0,self.volgnummerValue)
        self.factuurDatumLabelIdx = self.addChild(0,0,self.factuurDatumLabel)
        self.factuurDatumValueIdx = self.addChild(0,0,self.factuurDatumValue)
        self.leverDatumLabelIdx = self.addChild(0,0,self.leverDatumLabel)
        self.leverDatumValueIdx = self.addChild(0,0,self.leverDatumValue)
        if self.hasVerantwoordelijke:
            self.verantwoordelijkeLabelIdx = self.addChild(0,0,self.verantwoordelijkeLabel)
            self.verantwoordelijkeValueIdx = self.addChild(0,0,self.verantwoordelijkeValue)

        self.resize(width, 0)

    def resize(self, width, height):
        #ignore height, we determine that ourselves
        self.width = width

        if (self.width - 1)/2 - self.labelWidth >= self.minValueWidth:
            #two column layout
            colWidth = (self.width-1)/2
            colOffset = colWidth+1
            valueWidth = max(0, colWidth-self.labelWidth)

            self.separatorFill.resize(1,2)
            self.setChildPos(self.separatorFillIdx, colWidth,0)

            self.otherPartyLabel.resize(self.labelWidth,1)
            self.setChildPos(self.otherPartyLabelIdx,0,0)
            self.otherPartyValue.resize(valueWidth, 1)
            self.setChildPos(self.otherPartyValueIdx,self.labelWidth,0)

            self.volgnummerLabel.resize(self.labelWidth,1)
            self.setChildPos(self.volgnummerLabelIdx,0,1)
            self.volgnummerValue.resize(valueWidth, 1)
            self.setChildPos(self.volgnummerValueIdx,self.labelWidth,1)

            self.factuurDatumLabel.resize(self.labelWidth,1)
            self.setChildPos(self.factuurDatumLabelIdx, colOffset,0)
            self.factuurDatumValue.resize(valueWidth,1)
            self.setChildPos(self.factuurDatumValueIdx, colOffset + self.labelWidth,0)

            self.leverDatumLabel.resize(self.labelWidth,1)
            self.setChildPos(self.leverDatumLabelIdx, colOffset,1)
            self.leverDatumValue.resize(self.labelWidth,1)
            self.setChildPos(self.leverDatumValueIdx, colOffset + self.labelWidth, 1)

            if self.hasVerantwoordelijke:
                self.height = 3
                self.verantwoordelijkeLabel.resize(self.labelWidth,1)
                self.setChildPos(self.verantwoordelijkeLabelIdx, 0, 2)
                self.verantwoordelijkeValue.resize(width-self.labelWidth,1)
                self.setChildPos(self.verantwoordelijkeValueIdx, self.labelWidth, 2)
            else:
                self.height = 2
        else:
            #one column layout
            valueWidth = max(0, width-self.labelWidth)

            self.separatorFill.resize(0,0)
            self.setChildPos(self.separatorFillIdx, 0,0)

            self.otherPartyLabel.resize(self.labelWidth, 1)
            self.setChildPos(self.otherPartyLabelIdx,0,0)
            self.otherPartyValue.resize(valueWidth, 1)
            self.setChildPos(self.otherPartyValueIdx,self.labelWidth,0)

            self.volgnummerLabel.resize(self.labelWidth, 1)
            self.setChildPos(self.volgnummerLabelIdx,0,1)
            self.volgnummerValue.resize(valueWidth, 1)
            self.setChildPos(self.volgnummerValueIdx,self.labelWidth,1)

            self.factuurDatumLabel.resize(self.labelWidth, 1)
            self.setChildPos(self.factuurDatumLabelIdx,0,2)
            self.factuurDatumValue.resize(valueWidth, 1)
            self.setChildPos(self.factuurDatumValueIdx,self.labelWidth,2)

            self.leverDatumLabel.resize(self.labelWidth,1)
            self.setChildPos(self.leverDatumLabelIdx,0,3)
            self.leverDatumValue.resize(valueWidth,1)
            self.setChildPos(self.leverDatumValueIdx,self.labelWidth,3)

            if self.hasVerantwoordelijke:
                self.height = 5
                self.verantwoordelijkeLabel.resize(self.labelWidth, 1)
                self.setChildPos(self.verantwoordelijkeLabelIdx,0,4)
                self.verantwoordelijkeValue.resize(valueWidth,1)
                self.setChildPos(self.verantwoordelijkeValueIdx,self.labelWidth,4)
            else:
                self.height = 4
