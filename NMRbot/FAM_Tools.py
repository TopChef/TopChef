## devFAM_Tools.py           v.20140226
##  Development version!!!  used for testing ONLY!!!
##  collection of functions for use in python scripts generated at NMRFAM
##  written by L.Clos (lclos@nmrfam.wisc.edu)
##  To access, place this file in <Topspin home>/exp/stan/nmr/py/user/

global verNMR
from TopCmds import *
import traceback
import time
import sys

################################################################################
## modified INPUT_DIALOG from TopCmds.py
## returns output AND button pressed index
## if button index != 0, .getValues() returns None
def INPUT_DIALOGmod(title=None, header=None, items=None, values=None,\
                    comments=None, types=None, buttons=None, mnemonics=None, columns = 30):
    dia = dialogs.MultiLineInputDia(title, header, items, values, types, comments,\
                                    buttons, mnemonics, 0, columns, 1, None)
    return dia.getValues(),dia.getDialogCloseReason()

################################################################################
#### NMRbot - Automated NMR Object Class ####
## This is the main object class to use in automated NMR acquisition scripts.
## Instantiate with the following line in your script:
## "exprun = NMRbot(title)" -title variable is optional text appended to outputs
## Once instantiated, start run with following line in your script:
## "exprun.intiate_newrun(extratxt,funclt,parlt)" 
##    -All variables are optional. extratxt is text appearing in Start dialog
##     window, funclt is list of NMRbot method names (default below), parlt is 
##     list of Bruker parameter names.
##funclt = ['series_watstd','sample_num','sample_names','sample_solvs',\
##          'sample_positions','sample_parlts','sample_folderformat',\
##          'sample_conds','sample_NSmult','sample_expadapt','series_getprosol',\
##          'series_findH2Ooffset','series_wobb','series_shimcmd','series_autogain']
class NMRbot(Object):
    vernum = 20140226
    def __init__(self,title=''):
        self.title = title
        try:
            self.curinfo = CURDATA()
            self.curdir = self.curinfo[3]
        except:
            ERRMSG('START THIS SCRIPT\nFROM AN ACTIVE DATA SET')
            EXIT()

    def __errorexit__(self,text='Sample input wizard cancelled.',sampobj=None,exitnow=False):
        self.update_auditlt(text)
        if sampobj != None: sampobj.__errorexit__(text,self.curdir)
        ERRMSG(text)
        if exitnow != False:
            self.out_auditlt()
            EXIT()
    ## method to initiate new automated run        
    def initiate_newrun(self,funclt=[],parlt=['standard1D'],extratxt=''):
        self.funclt = funclt
        self.parlt = parlt
        result = SELECT(self.title+'-Start','%s\n'%self.title+' ver# %s\n written by L.Clos (lclos@nmrfam.wisc.edu)\n\n'%NMRbot.vernum+\
                      'This script is written to run sets of\n'+\
                      'experiments on a series of samples.\n\n'+\
                      'Required: >= Topspin 3.0, SampleJet, ATM accessory.\n\n'+extratxt,['Proceed','Cancel'])
        if result != 0:
            ERRMSG('Sample input wizard cancelled.')
            EXIT()
        else:
            self.get_sampleinfo()
            try:
                self.run_exps()
            except:
                self.update_auditlt('\n## !!Instrument Error Encountered!! ##')
                self.update_auditlt(traceback.format_exc())
                self.out_auditlt()
                
        EXIT()
    ## method to collect info about samples and experiment parameters to run    
    def get_sampleinfo(self):
        self.sampinfoobj = SampleInfo(self)
        allsamptxt = self.sampinfoobj.report
        if CONFIRM(self.title+' -Proceed?','Proceed with data collection for %d samples?\n%s'%(self.sampinfoobj.samplenum,allsamptxt)) == 1:
            self.initiate_auditlt()
            self.update_auditlt('information for %d samples succesfully input by user:'%self.sampinfoobj.samplenum)
            self.update_auditlt(allsamptxt)
            self.update_auditlt('\n## Proceeding With Sample Series Data Collection ##\n')
        else:
            ERRMSG('User declined to proceed with data collection!')
            EXIT()
    ## method to run series of samples, each with unique experiment parameter sets
    def run_exps(self):
        sampleobjlt = self.sampinfoobj.sampleobjlt
        #funcltrun = self.sampinfoobj.funcltrun
        if self.sampinfoobj.watstd != 0:
            watstdobj = Sample('WATSTD','WATSTD',int(self.sampinfoobj.watstd),solvent='H2O+D2O',\
                               wobb=self.sampinfoobj.wobb,shimcmd='topshim 3d tunea tuneb')
            result = self.init_newsample(watstdobj)
            if result == False:
                self.__errorexit__('Water STD sample failed... proceeding')
        for currsamp in sampleobjlt:
            self.update_auditlt('## SAMPLE %s ##'%currsamp.name)
            try:
                self.init_newsample(currsamp)
            except:
                self.__errorexit__('Aborting series for %s'%currsamp.name)
            expmodindlt = []
            # set up experiment folders
            for y in range(len(currsamp.parlt)):
                expno = str(y+1)
                dataset = [currsamp.folder,expno,'1',self.curdir]
                NEWDATASET(dataset,None,'PROTON')
                RE(dataset,'y')
                #XCMD('rpar %s all'%currsamp.parlt[y],WAIT_TILL_DONE) #caused error in topspin 3.2.5, wouldn't allow getprosol
                #20140226-commented out for test
                #getparcmd = 'rpar %s all remove=yes'%currsamp.parlt[y]
                #getparcmd = 'rpar %s all'%currsamp.parlt[y]
                #result = XCMD(getparcmd,WAIT_TILL_DONE).getResult()
                #self.update_auditlt('creating exp %s with %s parameters'%(expno,currsamp.parlt[y]),int(result.getResult()),currsamp)
                #if result.getResult() < 0: old result was int, new is None
                try:
                    XCMD('rpar %s all'%currsamp.parlt[y],WAIT_TILL_DONE) #caused error in topspin 3.2.5, wouldn't allow getprosol
                except:
                    expmodindlt.append(y)
                    self.update_auditlt('!! failed to load %s parameter set !!'%currsamp.parlt[y],100,currsamp)
                    set_title(dataset,'Failed to load %s parameter set\nThis experiment skipped'%currsamp.parlt[y])
                    continue
                else:
                    self.update_auditlt('creating exp %s with %s parameters'%(expno,currsamp.parlt[y]),100,currsamp)

                ndim = GETACQUDIM()
                SLEEP(2)
                if currsamp.getprosol == 1:
                    XCMD('getprosol',WAIT_TILL_DONE) #20140114 - error in exec, looking for server if rpar was flawed (topspin >3.2.5)
                    self.update_auditlt('  prosol parameters loaded',100,currsamp)
                if currsamp.NSmult != 1:
                    ns = GETPAR('NS')
                    newns = int(ns)*currsamp.NSmult
                    PUTPAR('NS','%s'%str(newns))
                    self.update_auditlt('  NS changed to %d'%newns,100,currsamp)
                if self.offset1Hfound == True:
                    ## adapt offset of channel
                    for dim in range(1,ndim+1):
                        nuc = GETPAR('NUC%d'%dim)
                        if nuc == 'off':
                            nuc = nuc1
                        if nuc == '1H':
                            nucoff = currsamp.get_expnucpars(nuc,'offset')
                            if  nucoff == 0.0:
                                continue
                            else:
                                PUTPAR('O%dP'%dim,'%3.4f'%nucoff)
                                self.update_auditlt('  %s offset changed to %3.4f'%(nuc,nucoff),100,currsamp)
                        nuc1 = nuc
               ### HERE is where pulsecal goes
                SLEEP(2)
                if self.sampinfoobj.autogain:
                    result = XCPR('rga',WAIT_TILL_DONE)
                    self.update_auditlt('  optimizing receiver gain',result.getResult(),currsamp)
                    rg = GETPAR('RG')
                    self.update_auditlt('  receiver gain set to %s'%rg,100,currsamp)
                SLEEP(3)
                    
            self.update_auditlt('experiment folders set up',0,currsamp)
            # que up experiments
            self.update_auditlt('## Data Acquisition ##',100,currsamp)
            for y in range (len(currsamp.parlt)):
                expno = str(y+1)
                if y in expmodindlt:
                    self.update_auditlt('# Exp %s - skipped due to failed set-up!!'%expno,100,currsamp)
                    continue
                else:
                    dataset = [currsamp.folder,expno,'1',self.curdir]
                    RE(dataset,'y')
                    pp = GETPAR('PULPROG')
                    line4audit = '# Exp %s - %s (%s)'%(expno,currsamp.parlt[y],pp)
                    if currsamp.adaptlt[y] == '2': line4audit += ' - SWadapted'
                    self.update_auditlt(line4audit,100,currsamp)
                set_title(dataset,'%s in %s, position %d\n%s (%s)'\
                          %(currsamp.name,currsamp.solvent,currsamp.position,currsamp.parlt[y],pp))
                #below for adaptive sw and offset
                ndim = GETACQUDIM()
                if currsamp.adaptlt[y] == '2':
                    ##adapt sw of exp dimension
                    for dim in range(1,ndim+1):
                        dimnuc = GETPAR('%d NUC1'%dim)
                        dimnucsw = currsamp.get_expnucpars(dimnuc,'sw')
                        if dimnucsw == 0.0:
                            continue
                        else:
                            PUTPAR('%d SW'%dim,'%3.4f'%dimnucsw)
                            self.update_auditlt('  F%d SW changed to %3.2f'%(dim,dimnucsw),100,currsamp)
                    ## adapt offset of channel
                    for dim in range(1,ndim+1):
                        nuc = GETPAR('NUC%d'%dim)
                        if nuc == 'off':
                            nuc = nuc1
                        nucoff = currsamp.get_expnucpars(nuc,'offset')
                        if  nucoff == 0.0:
                            continue
                        else:
                            PUTPAR('O%dP'%dim,'%3.4f'%nucoff)
                            self.update_auditlt('  F%d %s offset changed to %3.2f'%(dim,nuc,nucoff),100,currsamp)
                        nuc1 = nuc
                dimtxt = 'dims %s-'%ndim
                for dim in range(1,ndim+1):
                    if dim > 1: dimtxt += ';'
                    dimtxt += ' F%d %s, SW %3.2f'%(dim,GETPAR('%d NUC1'%dim),float(GETPAR('%d SW'%dim)))
                self.update_auditlt('%s'%dimtxt,100,currsamp)
                SLEEP(3)
                self.update_auditlt('start %s'%get_timetag(),100,currsamp)
                result = XCPR('zg',WAIT_TILL_DONE)
                self.update_auditlt('end   %s'%get_timetag(),result.getResult(),currsamp)
                if result.getResult() < 0: continue
                elif ndim == 1 and currsamp.adaptlt[y] == '1':
                    nuc = GETPAR('NUC1')
                    offset = float(GETPAR('O1P'))
                    newsw,newoff = get_sw_o1(nuc,offset,self.title)
                    currsamp.update_expnucpars(nuc,newsw,newoff)
                    self.update_auditlt('  %s adaptive offset determined = %3.4f'%(nuc,newoff),100,currsamp)
                    self.update_auditlt('  %s adaptive SW determined = %3.4f'%(nuc,newsw),100,currsamp)
            currsamp.out_auditlt(self.curdir)
        result = XCPR('sx ej',WAIT_TILL_DONE)
        self.update_auditlt('\nejecting last sample',result.getResult())
        return
    ## initiate new sample - insert,tune,shim,find HDO offset
    def init_newsample(self,sampleobj):
        sampleobj.initiate_auditlt()
        self.update_auditlt('info:\n%s'%sampleobj.sampleinfo_report(),100,sampleobj)
        # initialize instrument
        result = XCPR('ii',WAIT_TILL_DONE)
        SLEEP(3)
        self.update_auditlt('instrument initialization',int(result.getResult()),sampleobj)
        # load sample via SampleJet cmd
        result = XCPR('sx %s'%str(sampleobj.position),WAIT_TILL_DONE)
        SLEEP(3)
        self.update_auditlt('loading sample position %d'%sampleobj.position,int(result.getResult()),sampleobj)
        if result.getResult() < 0: return False
        SLEEP(3)
       ##### Here is the place to insert WAIT for temp equilibration
        # solvent lock
        result = XCPR('lock %s'%sampleobj.solvent,WAIT_TILL_DONE)
        SLEEP(3)
        self.update_auditlt('%s solvent lock'%sampleobj.solvent,int(result.getResult()),sampleobj)
        SLEEP(3)
        if result.getResult() < 0: return False
        if sampleobj.wobb == 1:
            # tune probe for 1H,13C,15N
            result = run_probetune()
            self.update_auditlt('  tuning probe channels',int(result.getResult()),sampleobj)
            if result.getResult() < 0: return False
        # sample shimming - recursive shimming and peakshape analysis should go here
        if sampleobj.shimcmd != '':
            if ';' in sampleobj.shimcmd:
                shimlt = sampleobj.shimcmd.split(';')
                for comd in shimlt:
                    result = XCPR(comd,WAIT_TILL_DONE)
                    SLEEP(5)
                    self.update_auditlt('  %s'%comd,int(result.getResult()),sampleobj)
                    if result.getResult() < 0: return False
            else:
                result = XCPR(sampleobj.shimcmd,WAIT_TILL_DONE)
                SLEEP(5)
                self.update_auditlt('  %s'%sampleobj.shimcmd,int(result.getResult()),sampleobj)
                if result.getResult() < 0: return False
        # search for intense HDO peak
        self.offset1Hfound = False
        if sampleobj.findH2Ooffset == 1:
            if 'H2O' in sampleobj.solvent or 'D2O' in sampleobj.solvent:
                self.offset1Hfound = True
                new1Hoff = get_solvent_offset(self.curdir)
                sampleobj.update_expnucpars('1H',offset=new1Hoff)
                self.update_auditlt('  determined 1H offset = %s'%new1Hoff,100,sampleobj)
        return

    def get_parlt(self):
        result,button = INPUT_DIALOGmod(self.title+'-Set Experiment Parameters','The initialization script did not specify the set of\n'+\
                                        'experiment parameters to be run for each sample.\nPlease indicate the maximum number of experiments\n'+\
                                        'you want run for each sample.',['Number of experiments?'],['10'],None,['1'],\
                                        ['Accept','Cancel'],['a','c'],4)
        if button == 1: EXIT()
        else: npars = int(result[0])
        newitemlt = ['Experiment %d -->'%x for x in range(1,(npars+1))]
        newparlt = ['']*npars
        canigonow = False
        while canigonow == False:
            newpars,button = INPUT_DIALOGmod(self.title+'-Set Experiment Parameters','Please type parameter set names:',newitemlt,newparlt,None,\
                                             ['1']*npars,['Accept','Cancel'],['a','c'],20)
            if button >=1: EXIT()
            elif '' in newpars:
                ERRMSG('SOME FIELDS LEFT BLANK!!\nTRY AGAIN.',modal=1)
                continue
            else:
                canigonow = True
        return newpars
                                                        
    def initiate_auditlt(self):
        print '\n\n### NMRbot %s python script started ###\n- %s'%(self.title,get_timetag())
        self.auditlt = []
        self.reportname = 'NMRbot_%s_SeriesReport.%s.txt'%(self.title,get_timetag())
        self.auditlt.append('## %s ##'%self.reportname)
        self.auditlt.append('## Status Report for Automated Sample Data Collection Over Sample Series ##')
        self.auditlt.append('## Host = %s ##\n'%GETHOSTNAME())
        self.auditlt.append('## NMRbot version %d ##\n'%NMRbot.vernum)
        self.auditlt.append('## Sample Series Initiated - %s ##\n'%get_timetag())
    
    def update_auditlt(self,lineotxt,result=100,sampobj=None):
        if '#' not in lineotxt:
            newlineotxt = '- '+lineotxt
        else: newlineotxt = lineotxt
        if result >= 0 and result != 100: newlineotxt += ' - passed'
        elif result < 0: newlineotxt += ' - failed'
        print newlineotxt
        self.auditlt.append(newlineotxt)
        if sampobj != None: sampobj.update_auditlt(lineotxt,result)

    def out_auditlt(self):
        self.auditlt.append('\n## Sample Series Ended - %s ##\n'%get_timetag())
        out_statusreport(self.auditlt,self.curdir,self.reportname)

################################################################################
#### Sample Object Class ####
class Sample(Object):
    def __init__(self,name='none',folder='unknown',position=101,condition='',\
    	           solvent='D2O',parlt=[],NSmult=1,adaptlt=[],getprosol=0,\
    	           	findH2Ooffset=0,wobb=0,shimcmd='topshim tunea tuneb'):
        self.name = name
        self.folder = folder
        self.position = position
        self.condition = condition
        self.solvent = solvent
        self.parlt = parlt
        self.NSmult = NSmult
        if adaptlt == []:
            self.adaptlt = [[0]*len(parlt)]
        else: self.adaptlt = adaptlt
        self.getprosol = getprosol
        self.findH2Ooffset = findH2Ooffset
        self.wobb = wobb
        self.shimcmd = shimcmd
        self.expnucdict = {'1H':0,'13C':1,'15N':2}
        self.expnucofflt = [0.0,0.0,0.0]
        self.expnucswlt = [0.0,0.0,0.0]
    def __errorexit__(self,text='Error detected',curdir='/'):
        self.update_auditlt(text)
        self.out_auditlt(curdir)
    def __getitem__(self):
        return [self.name,self.folder,self.position,self.solvent,self.parlt]
    def __repr__(self):
        return '%s in %s - %s'%(self.name,self.solvent,self.position)
    def update_expnucpars(self,dimatm,sw=0.0,offset=0.0):
        nucind = self.expnucdict[dimatm]
        if self.expnucswlt[nucind] == 0.0: self.expnucswlt[nucind] = sw
        if self.expnucofflt[nucind] == 0.0: self.expnucofflt[nucind] = offset
        return
    def get_expnucpars(self,dimatm,par='offset'):
        nucind = self.expnucdict[dimatm]
        if par == 'offset': return self.expnucofflt[nucind]
        if par == 'sw': return self.expnucswlt[nucind]
    def initiate_auditlt(self):
        self.auditlt = []
        self.reportname = 'NMRbot_%s_SampleReport.%s.txt'%(self.name,get_timetag())
        self.auditlt.append('%s'%self.reportname)
        self.auditlt.append('Status Report for Automated Sample Data Collection')
        self.auditlt.append('## Host = %s ##\n'%GETHOSTNAME())
        self.auditlt.append('## NMRbot version %d ##\n'%NMRbot.vernum)
        self.auditlt.append('## Initiated - %s ##\n'%get_timetag())
    def update_auditlt(self,lineotxt,result=100):
        if '#' not in lineotxt:
            lineotxt = '- '+lineotxt
        if result >= 0 and result != 100: lineotxt += ' - passed'
        elif result < 0: lineotxt += ' - failed'
        #print lineotxt
        self.auditlt.append(lineotxt)
    def out_auditlt(self,topdir):
        curdir = '%s/%s'%(topdir,self.folder)
        self.auditlt.append('\n## %s Experiment Set Ended - %s ##\n'%(self.name,get_timetag()))
        out_statusreport(self.auditlt,curdir,self.reportname)
    def sampleinfo_report(self):
        outtxt = '  %s in %s at position %d\n  foldername => %s\n  Exps => %s'\
                   %(self.name,self.solvent,self.position,self.folder,','.join(self.parlt))
        return outtxt
################################################################################
#### Sample Information Object Class ####
class SampleInfo(Object):
    def __init__(self,RunObj):
        curinfo = CURDATA()
        self.curdir = curinfo[3]   #current user /nmr directory
        self.parlt = RunObj.parlt  #list of experiment parameters to load
        self.funclt = RunObj.funclt#list of SampleInfo functions to call
        self.title = RunObj.title  #title from NMRbot file
        self.samplenamelt = []     #list of sample names
        self.solventlt = []        #list of sample solvents
        self.samplepositlt = []    #list of sample positions
        self.expparsameforall = True #flag to denote is parameter set is same for all samples
        self.master_solvlt = ['Acetic','Acetone','C6D6','CD3CN','CD3CN_SPE','CDCl3','CH3CN+D2O','CH3OH+D2O','D2O',\
                              'DMF','DMSO','EtOD','H2O+D2O','HDMSO','Juice','MeOD','oC6D4Cl2','pC6D4Br2','Plasma',\
                              'Pyr','TFE','THF','Tol','Urine']
        #below variables set for optional parameters
        self.samplenum = 10        #number of samples, not including any water std
        self.watstd,self.folderformat,self.samplecondlt,self.NSmultlt = 0,['1','2','3','0','4'],[],[]
        self.getprosol,self.findH2Ooffset,self.wobb,self.shimcmd,self.autogain = 0,0,0,'topshim tuneb tunea',0
        self.master_funclt = ['series_watstd','sample_num','sample_names','sample_solvs','sample_positions',\
                              'sample_parlts','sample_folderformat','sample_conds','sample_NSmult','sample_expadapt',\
                              'series_getprosol','series_findH2Ooffset','series_wobb','series_shimcmd','series_autogain']
        self.funcltrun = ['n','y','y','y','y','y','n','n','n','n','n','n','n','n','n']
        self.datetag = '%s'%get_timetag()[0:8]
        self.report = self.collect_sampleinfo()
    ## error out method
    def __errorexit__(self,text='Error!',exitnow=False):
        ERRMSG(text)
        if exitnow != False: EXIT()
    ## master method to coordinate collection of sample info        
    def collect_sampleinfo(self):
        self.txtin = SELECT(self.title+'-Inputs','Do you want to manually enter sample information\n'+\
                        'for your automated run, or do want to submit\na text file containing the pertinent'+\
                        ' information?',['Manual','Text File','Cancel'])
        if self.txtin == 2: self.__errorexit__('Sample input wizard cancelled',True)
        elif self.txtin == 1: self.sampleinfo_filein()
        else:
            if self.funclt == []:
                self.funclt = self.get_funclt()
            else: self.funclt = self.set_funcltrun()
            self.sampleinfo_dialogs()
        self.sampleobjlt = self.make_sampleobjs()
        if self.txtin == 0:
            self.starobj = StarFileInOut()
            self.starobj.out_starfile(self)
        report = '\n'
        for item in self.sampleobjlt:
            iteminfo = item.sampleinfo_report()
            report += iteminfo+'\n'
        if self.funcltrun[0] == 'y': report += '  #Water std sample at position %d used for shimming\n'%self.watstd
        if self.funcltrun[10] == 'y': report += '  #Each experiment will invoke GETPROSOL\n'
        if self.funcltrun[11] == 'y': report += '  #Offset for H2O and D2O samples will be automatically determined\n'
        if self.funcltrun[12] == 'y': report += '  #The probe will be automatically tuned for each new sample\n'
        if self.funcltrun[13] == 'y': report += '  #Each new sample will be shimmed with \'%s\'\n'%self.shimcmd
        if self.funcltrun[14] == 'y': report += '  #Receiver gain for each experiment will be automatically determined\n'
        return report
    ## method to determine which optional sample info functions user wants to modify    
    def get_funclt(self):
        questions = ['Using a water sample standard?',\
                     'Choose folder name format?',\
                     'Define sample conditions?',\
                     'Set sample scan multiplier?',\
                     'Set adaptive sweep-widths?',\
                     'Set prosol conditions?',\
                     'Set H2O offset calibration?',\
                     'Set channel tuning/matching?',\
                     'Set Topshim command?',\
                     'Set receiver gain control?']
        answers = [self.funcltrun[0],self.funcltrun[6],self.funcltrun[7],self.funcltrun[8],self.funcltrun[9],\
                   self.funcltrun[10],self.funcltrun[11],self.funcltrun[12],self.funcltrun[13],self.funcltrun[14]]
        canigonow = False
        result,button = INPUT_DIALOGmod(self.title+'-Get Info Functions','The initialization script did not specify the set of\n'+\
                                        'global parameters to be modified for this run of samples.\nAside from the required parameters'+\
                                        'to set, please indicate the optional global parameters you\n'+\
                                        'want a chance to modify for each sample. (y or n)',questions,answers,None,['1']*len(answers),\
                                        ['Next','Prev','Cancel'],['n','p','c'],4)
        if button >= 1: return button
        self.funcltrun[0],self.funcltrun[6],self.funcltrun[7],self.funcltrun[8],self.funcltrun[9],self.funcltrun[10],\
        self.funcltrun[11],self.funcltrun[12],self.funcltrun[13],self.funcltrun[14] = result[0],result[1],result[2],\
        result[3],result[4],result[5],result[6],result[7],result[8],result[9]
        newfunclt = []
        for x in range(len(self.master_funclt)):
            if self.funcltrun[x] == 'y':
                newfunclt.append(self.master_funclt[x])
        return newfunclt
    ## set info dialog method list
    def set_funcltrun(self):
        newfunclt = []
        for x in range(len(self.master_funclt)):
            if self.master_funclt[x] in self.funclt:
                newfunclt.append(self.master_funclt[x])
                self.funcltrun[x] = 'y'
            else:
                if x in [1,2,3,4,5]:
                    self.__errorexit__('Required function \"%s\" not \nin text file input function list.\n\nExiting...'%self.master_funclt[x],True)
                self.funcltrun[x] = 'n'
        return newfunclt
    ## run sample info dialog methods according to input function list    
    def sampleinfo_dialogs(self):
        ind = 0    
        while ind < len(self.funclt):
            func_name = self.funclt[ind]
            exec('button = self.%s()'%func_name)
            if button == 0: ind += 1
            elif button == 1: ind -= 1
            else:
                self.__errorexit__('Sample Info Input Wizard Cancelled.\nExiting...','Input Wizard Cancelled',True)
    ## ask about H2O standard for shimming
    def series_watstd(self):
        watstd_result = SELECT(self.title+'-H2O Shimming Standard?',\
                               'Do you have an H2O sample with DSS for 3D shimming?',['Yes','No','Cancel'])
        if watstd_result == 0:
            watposit_result,button = INPUT_DIALOGmod(self.title+'-H2O Std Position','In what position is the H2O sample?',\
                                                     ['H2O std position ->'],['101'],None,['1'],['Next','Cancel'],['n','c'],4)
            if button == 0:
                self.watstd = int(watposit_result[0])
                return button
            else: return -1
        elif watstd_result == 1:
            self.watstd = 0
            self.funcltrun[0] = 'n'
            return watstd_result-1
        else: return -1
    ## get number of samples in sample series
    def sample_num(self):
        samplenum_result = INPUT_DIALOG(self.title+'-Number of Samples', 'Please answer a few questions to begin.',\
                                        ['Number of samples to run experiment series for?\n(NOT including H2O standard)'],\
                                        ['%d'%self.samplenum],None,['1'],columns=10)
        if samplenum_result == None or samplenum_result[0] == '0':
            self.__errorexit__('No samples for series.\nExiting...','Input Error',True)
        else:
            self.samplenum = int(samplenum_result[0])
            return 0
    ## get sample names
    def sample_names(self):
        if len(self.samplenamelt) != self.samplenum: self.samplenamelt = self.mod_itemlt('sample%d',1,self.samplenum)
        sampleitemslt = self.mod_itemlt('Sample %d name ->',1,self.samplenum)
        namelt,button = INPUT_DIALOGmod(self.title+'-Sample Names', 'Please give a name for each sample.\n',\
                                                   sampleitemslt, self.samplenamelt,None,(['1']*self.samplenum),['Next','Prev','Cancel'],['n','p','c'],20)
        if namelt == None: self.samplenamelt = []
        else: self.samplenamelt = [x.replace(' ','_') for x in namelt]
        return button
    ## get solvent
    def sample_solvs(self):
        if self.solventlt == []: self.solventlt = ['']*self.samplenum
        solvbutt_result = SELECT(self.title+'-Solvent','Are all the samples in the same solvent?',['Yes','No','Prev','Cancel'])
        canigonow = False
        while canigonow == False:
            if solvbutt_result == 0:
                solv_result,button = INPUT_DIALOGmod(self.title+'-Solvent','What solvent is used for all samples?\n(Be sure to use CAPS when necessary)',\
                                                     ['Common Solvent ->'],[''],None,['1'],['Next','Prev','Cancel'],['n','p','c'],8)
                if button == 0:
                    if solv_result[0] == '' or solv_result[0] not in self.master_solvlt:
                        ERRMSG('You must specify a valid solvent:\n\n%s'%'\n'.join(self.master_solvlt),modal=1)
                    else:
                        self.solventlt = solv_result*self.samplenum
                        canigonow = True
                elif button >= 1: return button
            elif solvbutt_result == 1:
                solv_result,button = INPUT_DIALOGmod(self.title+'-Solvent','What solvent is used for each sample?\n(Be sure to use CAPS when necessary)',\
                                                     self.samplenamelt,self.solventlt,None,(['1']*self.samplenum),['Next','Prev','Cancel'],['n','p','c'],8)
                if button == 0:
                    for x in range(self.samplenum):
                        canigonow = True
                        if solv_result[x] == '' or solv_result[x] not in self.master_solvlt:
                            ERRMSG('You must specify a valid solvent\nfor %s:\n\n%s'%(self.samplenamelt[x],'\n'.join(self.master_solvlt)),modal=1)
                            canigonow = False
                    self.solventlt = solv_result
                elif button >= 1: return button
            else: return solvbutt_result-1
        return button
    ## get sample positions
    def sample_positions(self):
        if self.samplepositlt == []: self.samplepositlt = self.mod_itemlt('%d',101,self.samplenum)
        samplepositlt_result,button = INPUT_DIALOGmod(self.title+'-Sample Positions', 'Please give the position of each sample.\n',\
                                                      self.samplenamelt, self.samplepositlt,None,(['1']*self.samplenum),['Next','Prev','Cancel'],['n','p','c'],4)
        if samplepositlt_result != None:
            self.samplepositlt = samplepositlt_result
        return button
    ## get exp params to run
    def sample_parlts(self):
        self.expparlt = []         #list of lists of experiment parameters for each sample
        self.expadaptlt = []       #list of lists of which experiments to use for adaptive SW for each sample
        expdiffpar_result = SELECT(self.title+'-Run Different Experiments','Do you want to run the same\nexperiment set for each sample?',\
                                   ['Yes','No','Prev','Cancel'])
        if expdiffpar_result == 0:
            newparlt, button = self.parlt_adjust('Indicate the experiment parameter set to use for all samples.\n')
            if button == 0:
                for x in range(self.samplenum):
                    self.expparlt.append(newparlt)
                    self.expadaptlt.append(['0']*len(newparlt))
                self.expparsameforall = True
            return button
        elif expdiffpar_result == 1:
            for x in range(self.samplenum):
                newparlt, button = self.parlt_adjust('Indicate the experiment parameter set to use for %s.\n'%self.samplenamelt[x])
                if button == 0:
                    self.expparlt.append(newparlt)
                    self.expadaptlt.append(['0']*len(newparlt))
                else: return button
            self.expparsameforall = False
            return button
        elif expdiffpar_result >= 2: return expdiffpar_result-1
    ## dialog for recursive adjustment of parameter list 
    def parlt_adjust(self,header):
        newparlt = self.parlt[:]
        canigonow = False
        while canigonow is False:
            itemlt = self.mod_itemlt('Experiment %d -->',1,len(newparlt))
            result,button = INPUT_DIALOGmod(self.title+'-Experiment Series',header+'Clear fields for experiments you DO NOT want to run.\n'+\
                                            'Reset button will reset parameter list to default.',itemlt,newparlt,None,\
                                            ['1']*len(newparlt),['Accept','Add 1','Reset','Prev','Cancel'],['a','1','r','p','c'],20)
            if button >= 3:
                return result,button-2
            elif button == 2:
                newparlt = self.parlt[:]
                pass
            elif button == 1:
                newparlt += ['new']
                pass
            elif button == 0:
                if '' in result:
                    replaceparlt = []
                    for x in result:
                        if x == '': continue
                        else: 
                            replaceparlt.append(x)
                        newparlt = replaceparlt
                else:
                    newparlt = result
                    canigonow = True
        return newparlt,button
    ## choose experiment folder name constituents
    def sample_folderformat(self):
        set = False
        while set == False:
            format_result,button = INPUT_DIALOGmod(self.title+'-Folder Name Format','Please indicate the folder name format\n'+\
                                                   'generated for each sample to be tested.\nRank each item below (1-5) in the\n'+\
                                                   'order desired for the folder name.\n(1=highest rank, 0=do not use in folder name)\n',\
                                                    ['Sample Name','Sample Solvent','Sample Position','Sample Conditions','Date'],\
                                                    self.folderformat,None,(['1']*5),['Next','Prev','Cancel'],['n','p','c'],1)
            if button >= 1: return button
            elif '1' not in format_result:
                continue
            else:
                self.folderformat = format_result
            for x in range(1,6):
                try:
                    cnt = self.folderformat.count('%d'%x)
                except:
                    continue
                if cnt > 1:
                    ERRMSG('Please Try Again...',modal=1)
                    break
            if cnt <= 1: set = True
        if self.folderformat[4] != '0':
            button = self.sample_date()
            if button >= 1: return button
        return button
    ## check include date
    def sample_date(self):
        date_result,button = INPUT_DIALOGmod(self.title+'-Date','Specify the DATE tag to add',\
                                             ['Date ->'],[self.datetag],None,['1'],['Accept','Prev','Cancel'],['a','p','c'],10)
        if date_result != None:
            self.datetag = date_result[0]
        return button
    ## get sample conditions
    def sample_conds(self):
        if self.samplecondlt == []: self.samplecondlt = [' ']*self.samplenum
        condlt_result,button = INPUT_DIALOGmod(self.title+'-Sample Conditions', 'Enter text that denotes sample conditions.',\
                                               self.samplenamelt, self.samplecondlt,None,(['1']*self.samplenum),\
                                               ['Next','Prev','Cancel'],['n','p','c'],10)
        if condlt_result != None:
            testcont = ''.join([x for x in condlt_result])
            if testcont.replace(' ','') == '':
                self.funcltrun[7] = 'n'
            else:
                self.samplecondlt = [x.replace(' ','_') for x in condlt_result]
        return button
    ## get number of scans for each sample
    def sample_NSmult(self):
        if self.NSmultlt == []: self.NSmultlt = ['1']*self.samplenum
        NSmult_result,button = INPUT_DIALOGmod(self.title+'-Sample Scans Multiplier','Please indicate the NS multiplier for\neach sample to be tested.'+\
                                                '\n(1 for standard)\n(2 or more for low concentration)\n',\
                                                self.samplenamelt,self.NSmultlt,None,(['1']*self.samplenum),['Next','Prev','Cancel'],['n','p','c'],1)
        if NSmult_result != None:
            self.NSmultlt = NSmult_result
        return button
    ## choose whether to use adaptive sw and offset, and on which experiments
    def sample_expadapt(self):
        self.funcltrun[9] = 'y'
        adapt_result = SELECT(self.title+'-Adaptive SW and OFFSETs','Do you want to use certain 1D experiments to determine\n'+\
                              'the SWEEP WIDTH and OFFSET of experiments run afterwards?',['Yes','No','Prev','Cancel'])
        if adapt_result == 0:
            if self.expparsameforall == True:
                if len(self.expparlt[0]) == 1:
                    self.__errorexit__('This feature requires at least two\nexperiments run for each sample.')
                    self.funcltrun[9] = 'n'
                else: adaplt_result,button = self.expadapt_adjust('FOR ALL SAMPLES!\n',self.expparlt[0],self.expadaptlt[0])
                if button == 0:
                    self.expadaptlt = [adaplt_result]*self.samplenum
                return button
            elif self.expparsameforall == False:
                for x in range(self.samplenum):
                    if len(self.expparlt[x]) == 1:
                        self.__errorexit__('This feature requires at least two\nexperiments run for each sample.')
                        self.funcltrun[9] = 'n'
                        return 0
                    else: adaplt_result,button = self.expadapt_adjust('ONLY FOR %s!\n'%self.samplenamelt[x],self.expparlt[x],self.expadaptlt[x])
                    if button == 0:
                        self.expadaptlt[x] = adaplt_result
                    else: return button
                return button
        else:
            self.funcltrun[9] = 'n'
            return adapt_result-1
    ## adjust selection of which experimets to use to adapt SW and OFFSET
    def expadapt_adjust(self,header,parlt,paradaptlt):
        newitemlt = []
        [newitemlt.append('EXP %d-%s'%(par+1,parlt[par])) for par in range(0,len(parlt))]
        canigonow = False
        while canigonow == False:
            result,button = INPUT_DIALOGmod(self.title+'-Adaptive SW and OFFSETs',header+'Indicate the experiments that determine or use\n'+\
                                            'adaptive SW and OFFSET parameters for respective nucleii.\nNote: 1H OFFSET not changed by this.\n\n'+\
                                            '(1 = Use to determine SW and OFFSET in 1D)\n( 2 = Adapt SW and OFFSET to previously determined values)\n'+\
                                            '( 0 = DO NOT change SW and OFFSET from parameter set values)',newitemlt,paradaptlt,None,\
                                            ['1']*len(parlt),['Accept','Prev','Cancel'],['a','p','c'],3)
            if button >= 1:
                self.funcltrun[9] = 'n'
                return paradaptlt,button
            elif result.count('0') == len(parlt): return paradaptlt,0
            else:
                if '1' not in result:
                    ERRMSG('No experiments flagged for detecting SW',modal=1)
                    continue
                elif '2' not in result:
                    ERRMSG('No experiments flagged for adapting SW',modal=1)
                    continue
                inddet,indadap = result.index('1'),result.index('2')
                if inddet > indadap:
                    ERRMSG('1D experiments to determine SW and\nOFFSET must occur before other experiments\n'+\
                           'that adapt to those parameters',modal=1)
                    continue
                else: canigonow = True
        return result, button
    ## get user preference for getprosol 
    def series_getprosol(self):
        prosol_result = SELECT(self.title+'-Get Prosol Values','Do you want to load PROSOL values for experiments?',\
                                         ['Yes','No','Prev','Cancel'])
        if prosol_result == 0:
            self.funcltrun[10] = 'y'
            self.getprosol = 1
            return prosol_result
        else:
            self.funcltrun[10] = 'n'
            return prosol_result-1
    ## get user preference on automatically determining offset for H2O,D2O samples
    def series_findH2Ooffset(self):
        findoffset_result = SELECT(self.title+'-Find H2O Offset','Do you want 1H offset to be automatically determined\n'+\
                                         'for samples in H2O or D2O solvent?',['Yes','No','Prev','Cancel'])
        if findoffset_result == 0:
            self.findH2Ooffset = 1
            return findoffset_result
        else:
            self.funcltrun[11] = 'n'
            return findoffset_result-1
    ## get user preference on automatically tuning probe
    def series_wobb(self):
        wobb_result = SELECT(self.title+'-Probetune','Do you want to re-tune the probe for each new sample?',\
                                         ['Yes','No','Prev','Cancel'])
        if wobb_result == 0:
            self.wobb = 1
            return wobb_result
        else:
            self.funcltrun[12] = 'n'
            return wobb_result-1
    ## get user preference on topshim command to use for all samples
    def series_shimcmd(self):
        shimcmd_result,button = INPUT_DIALOGmod(self.title+'-Topshim','What TOPSHIM parameters should be run '+\
                                                'for each sample?',[''],['topshim tuneb tunea'],None,\
                                                ['1'],['Accept','Prev','Cancel'],['a','p','c'],25)
        if shimcmd_result != None:
            if shimcmd_result[0] != '': self.shimcmd = shimcmd_result[0]
            else: self.funcltrun[13] = 'n'
        return button
    ## get user preference on automated receiver gain
    def series_autogain(self):
        autogain_result = SELECT(self.title+'-Autogain','Do you want the receiver gain to be\n'+\
                                                   'automatically optimized for each experiment?',\
                                                   ['Yes','No','Prev','Cancel'])
        if autogain_result == 0:
            self.autogain = 1
            return autogain_result
        else:
            self.funcltrun[14] = 'n'
            return autogain_result-1
    ## method to collect sample info from text input file
    def sampleinfo_filein(self):
        filepathlt = ['%s/NMRbot.txt'%self.curdir]
        canigonow = False
        while canigonow == False:
            filepathlt = INPUT_DIALOG(self.title+'-File Input','Please indicate the path to the NMRbot text file.',['file path:'],\
                                      filepathlt,None,['1'],['Proceed','Cancel'],columns=30)
            if filepathlt == None: EXIT()
            self.starobj = StarFileInOut()
            canigonow = self.starobj.read_infile(filepathlt[0])
            if canigonow == False: ERRMSG('%s\nPath is invalid! Try again'%filepathlt[0],modal=1)
        self.decode_starobj()
    ## decode input star file variables to make sample objects
    def decode_starobj(self):
        try: self.samplenum = len(self.starobj.sample_info)
        except: self.__errorexit__('No entry for "sample_info" loop in input file.\nExiting...',True)
        namelt = self.starobj.sample_info.keys()
        namelt.sort()
        try: self.samplenamelt = [self.starobj.sample_info[x]['sample_name'] for x in namelt]
        except: self.__errorexit__('No entries for "sample_name" in input file.\nExiting...',True)
        try: self.solventlt = [self.starobj.sample_info[x]['sample_solvent'] for x in namelt]
        except: self.__errorexit__('No entries for "sample_solvent" in input file.\nExiting...',True)
        try: self.samplepositlt = [self.starobj.sample_info[x]['sample_position'] for x in namelt]
        except: self.__errorexit__('No entries for "sample_position" in input file.\nExiting...',True)
        try: self.expparlt = [self.starobj.sample_info[x]['sample_parlt'].split(',') for x in namelt]
        except: self.__errorexit__('No entries for "sample_parlt" in input file.\nExiting...',True)
        try:
            if self.starobj.series_params['series_watstd'] != '0':
                self.funcltrun[0] = 'y'
                self.watstd = int(self.starobj.series_params['series_watstd'])
        except: pass
        try:
            self.folderformat = [self.starobj.folder_format['sample_name'],self.starobj.folder_format['sample_solvent'],\
                                 self.starobj.folder_format['sample_position'],self.starobj.folder_format['sample_condition'],
                                 self.starobj.folder_format['date_tag']]
            self.funcltrun[6] = 'y'
        except: pass
        try:
            self.samplecondlt = [self.starobj.sample_info[x]['sample_condition'] for x in namelt]
            self.funcltrun[7] = 'y'
        except: pass
        try:
            self.NSmultlt = [self.starobj.sample_info[x]['sample_NSmult'] for x in namelt]
            self.funcltrun[8] = 'y'
        except: pass
        try:
            self.expadaptlt = [self.starobj.sample_info[x]['sample_adaptlt'].split(',') for x in namelt]
            self.funcltrun[9] = 'y'
        except: pass
        try:
            if self.starobj.series_params['series_getprosol'] == '1':
                self.funcltrun[10] = 'y'
                self.getprosol = 1
            elif self.starobj.series_params['series_getprosol'] == '0':
                self.funcltrun[10] = 'n'
                self.getprosol = 0
        except: pass
        try:
            if self.starobj.series_params['series_findH2Ooffset'] == '1':
                self.funcltrun[11] = 'y'
                self.findH2Ooffset = 1
            elif self.starobj.series_params['series_findH2Ooffset'] == '0':
                self.funcltrun[11] = 'n'
                self.findH2Ooffset = 0
        except: pass
        try:
            if self.starobj.series_params['series_wobb'] == '1':
                self.funcltrun[12] = 'y'
                self.wobb = 1
            elif self.starobj.series_params['series_wobb'] == '0':
                self.funcltrun[12] = 'n'
                self.wobb = 0
        except: pass
        try:
            if self.starobj.series_params['series_shimcmd'][:7] == 'topshim':
                self.funcltrun[13] = 'y'
                self.shimcmd = self.starobj.series_params['series_shimcmd']
            else:
                self.funcltrun[13] = 'n'
                self.shimcmd = self.starobj.series_params['series_shimcmd']
        except: pass
        try:
            if self.starobj.series_params['series_autogain'] == '1':
                self.funcltrun[14] = 'y'
                self.autogain = 1
            elif self.starobj.series_params['series_autogain'] == '0':
                self.funcltrun[14] = 'n'
                self.autogain = 0
        except: pass
    ## make Sample class objects and insert into object list           
    def make_sampleobjs(self):
        sampleobjlt = []      #list of sample objects to run, filled below
        if self.funcltrun[7] == 'n':
            self.samplecondlt = ['']*self.samplenum
        if self.funcltrun[8] == 'n':
            self.NSmultlt = ['1']*self.samplenum
        if self.funcltrun[9] == 'n':
            self.expadaptlt = []
            for k in range(self.samplenum):
                self.expadaptlt.append(([0]*len(self.expparlt[k])))
        if self.funcltrun[13] == 'n':
            self.shimcmd = ''
        for i in range(self.samplenum):
            nameparts = [self.samplenamelt[i],self.solventlt[i],self.samplepositlt[i],\
                         self.samplecondlt[i],self.datetag]
            folder = []
            for j in range(1,6):
                try:
                    rankind = self.folderformat.index('%d'%j)
                    folder.append(nameparts[rankind])
                except: continue
            foldername = '.'.join(folder)
            vars()[self.samplenamelt[i]] = Sample(self.samplenamelt[i],foldername,int(self.samplepositlt[i]),\
                                                  self.samplecondlt[i],self.solventlt[i],self.expparlt[i],\
                                                  int(self.NSmultlt[i]),self.expadaptlt[i],self.getprosol,\
                                                  self.findH2Ooffset,self.wobb,self.shimcmd)
            sampleobjlt.append(vars()[self.samplenamelt[i]])
        return sampleobjlt
    def mod_itemlt(self,txtin,strtnum=1,lenlt=10):
        itemlt=[]
        endnum = int(strtnum)+int(lenlt)
        for x in range(strtnum,endnum):
            itemlt.append(txtin%x)
        return itemlt


################################################################################
#### STAR Format Reader Object ####
class StarFileInOut(object):
    def __init__(self):
        self.datatypes = []
    def read_infile(self,filepath):
        self.filepath = filepath
        try:
            self.f = open(self.filepath,'r')
        except: return False
        self.decode_file()
        self.f.close()
    def decode_file(self):
        loop,linecnt = False,0
        valuekeys,values = [],[]
        datakeys,dataitem = [],[]
        for line in self.f:
            linecnt += 1
            if line[0] == '#': continue
            elif '#' in line: newline = line[:(line.index('#'))].split()
            else: newline = line.split()
            newlinelen = len(newline)
            if line == '\n': loop = False
            if loop == False:
                if newline == []:
                    if self.datatypes != []:
                        exec('self.%s = dict(zip(valuekeys,values))'%self.datatypes[-1])
                        valuekeys,values = [],[]
                        #datakeys,dataitems = [],[]
                        datakeys,dataitem = [],[]
                    else: continue
                elif len(newline) == 1:
                    if newline[0] == 'loop_':
                        loop,loopcnt,itemcnt = True,0,1
                        datakeys,dataitem = [],[]
                        continue
                    elif newline[0] == 'end_': return True
                    else:
                        self.datatypes.append(newline[0])
                elif newline[0][0].startswith('_'):
                    valuekeys.append(newline[0][1:])
                    #if newline[0] == '_series_shimcmd':
                    #    values.append(' '.join([x for x in newline[1:]]))
                    #    print 'shimcmd = ',values[-1]
                    #else: values.append(newline[1])
                    values.append(' '.join([x for x in newline[1:]]))
            elif loop == True:
                if line == '\n':
                    loop = False
                    #datakeys,dataitems = [],[]
                    datakeys,dataitem = [],[]
                    continue
                elif newline[0][0] == '_':
                    for x in newline:
                        datakeys.append(x[1:])
                        loopcnt += 1
                    continue
                else:
                    if len(dataitem) < loopcnt:
                        [dataitem.append(x) for x in newline]
                    if len(dataitem) == loopcnt:
                        exec('item_%03d = dict(zip(datakeys,dataitem))'%itemcnt)
                        valuekeys.append('item_%03d'%itemcnt)
                        exec('values.append(item_%03d)'%itemcnt)
                        dataitem = []
                        itemcnt += 1
                    elif len(dataitem) > loopcnt:
                        ERRMSG('Input file sample info columns in line %d\nexceed expected inputs.\n\nExiting...'%linecnt)
                        EXIT()
                    else:
                        continue
    def out_starfile(self,infoobj):
        path = infoobj.curdir
        funcltrun = infoobj.funcltrun
        sample_types = ['name','solvent','position','parlt','condition','NSmult','adaptlt']
        sample_funcmap = (funcltrun[2],funcltrun[3],funcltrun[4],funcltrun[5],funcltrun[7],funcltrun[8],funcltrun[9])
        samplewrite = []
        [samplewrite.append(sample_types[x]) for x in range(len(sample_types)) if sample_funcmap[x] == 'y']
        format_types = ['sample_name','sample_solvent','sample_position','sample_condition','date_tag']
        series_types = ['watstd','getprosol','findH2Ooffset','wobb','shimcmd','autogain']
        series_funcmap = (funcltrun[0],funcltrun[10],funcltrun[11],funcltrun[12],funcltrun[13],funcltrun[14])
        serieswrite = []
        [serieswrite.append(series_types[x]) for x in range(len(series_types)) if series_funcmap[x] == 'y']
        filename = 'NMRbot_%s.txt'%get_timetag()
        f = open(path+'/'+filename,'w')
        f.write('sample_info\nloop_\n')
        for ntype in samplewrite:
            f.write('_sample_%s\n'%ntype)
        for obj in infoobj.sampleobjlt:
            for itype in samplewrite:
                if itype in ['parlt','adaptlt']: exec('dataitem=",".join([str(x) for x in obj.%s])'%itype)
                else: exec('dataitem=obj.%s'%itype)
                f.write(str(dataitem)+'   ')
            f.write('\n')
        if funcltrun[6] == 'y':
            f.write('\nfolder_format\n')
            [f.write('_'+format_types[x]+(' '*(25-len(format_types[x])))+infoobj.folderformat[x]+'\n') for x in range(len(format_types))]
        if serieswrite != []:
            f.write('\nseries_params\n')
            for x in serieswrite:
                f.write('_series_%s'%x+(' '*(17-len(x))))
                exec('f.write(str(infoobj.%s))'%x)
                f.write('\n')
        f.write('\nend_')
        f.close()

################################################################################
#### functions to run experiments ####
# search for large H2O solvent peak
def get_solvent_offset(curdir):
    NEWDATASET(['CALIB_O1','1','1',curdir],None,'standard1D')
    RE(['CALIB_O1','1','1',curdir],'y')
    XCMD('getprosol',WAIT_TILL_DONE)
    PUTPAR('PULPROG','zg')
    PUTPAR('DS','0')
    PUTPAR('NS','1')
    PUTPAR('RG','1')
    PUTPAR('P 1','1u')
    PUTPAR('D 1','1s')
    PUTPAR('SW','11.0')
    PUTPAR('O1P','4.7')
    currO1p = 4.7
    for mod in [10,100,1000]:
        heightlt = []
        for O1p in range(-3,4):
            newO1p = currO1p+(float(O1p)/float(mod))
            #print 'newO1p =',newO1p
            PUTPAR('O1P',str(newO1p))
            XCPR('zg',WAIT_TILL_DONE)
            peaklt = get_peaklist(findref='no')
            if peaklt != []:
                intenslt = [x[1] for x in peaklt]
                intensind = intenslt.index(max(intenslt))
                heightlt.append([peaklt[intensind][0],peaklt[intensind][1]])
                #print peaklt[intensind]
            else:
                heightlt.append([6.66,1000000])
                print 'no peak found'
        if mod > 1:
            intenslt = [x[1] for x in heightlt]
            intensind = intenslt.index(min(intenslt))
        else:
            intenslt = [x[0] for x in heightlt]
            intensind = intenslt.index(min(intenslt))
        currO1p = heightlt[intensind][0]
        #else: EXIT()
    return currO1p

## run probe tuning for 1H 13C 15N
def run_probetune(dummydataset=True):
    curinfo = CURDATA()
    curdir = curinfo[3]
    if dummydataset == True:
        NEWDATASET(['wobb_test','1','1',curdir],None,'B_HNCOGP3D')
        RE(['wobb_test','1','1',curdir],'y')
    result = XCPR('atma',WAIT_TILL_DONE)
    return result
    
#### helper functions ####  

# status report tracking
def out_statusreport(statusreport,path,fname='AutoAudit'):
    f = open(path+'/'+fname,'w')
    [f.write(x+'\n') for x in statusreport]
    f.close()
    print '\n### Text audit of run output to %s/%s ###\n'%(path,fname)
    return

# calculate optimum sw and offset for current data set
def get_sw_o1(dimatm,offset,title=''):
    if 'MMCD' in title: peaklist = get_peaklist(frp=0.1,findref='no')
    else: peaklist = get_peaklist(findref='no')
    if len(peaklist) <= 1: sw = 0.0
    else:
        cslt = [x[0] for x in peaklist]
        maxcs, mincs = max(cslt), min(cslt)
        if dimatm == '1H':
            halfswlt = [abs(offset-maxcs),abs(offset-mincs)]
            sw = (max(halfswlt)*2)+1.0
        else:
            sw = (maxcs-mincs)+10.0
            offset = (maxcs+5.0)-(sw/2)
    return sw,offset

# get peaklist of 1D experiment though auto peak picking
def get_peaklist(flp=1000.0,frp=-1000.0,findref='yes'):
    offset = float(GETPAR('O1P'))
    sweepw = float(GETPAR('SW'))
    bf1 = float(GETPAR('BF1'))
    if flp == 1000.0 and frp == -1000.0:
        flp = offset+(sweepw/2)
        frp = offset-(sweepw/2)
    XCPR('ft',WAIT_TILL_DONE)
    XCPR('apk',WAIT_TILL_DONE)
    XCPR('absn',WAIT_TILL_DONE)
    PUTPAR('F1P',str(flp))
    PUTPAR('F2P',str(frp))
    PUTPAR('PSIGN','both')
    #had below = 'noise' for get_o1_p1, need to test
    PUTPAR('PSCAL','noise')
    PUTPAR('MI','0')
    PUTPAR('MAXI','1000000')
    PUTPAR('CY','15')
    PUTPAR('PC','1.5')
    if findref == 'yes': XCPR('sref',NO_WAIT_TILL_DONE)
    XCPR('pp',WAIT_TILL_DONE)
    list = GETPEAKSARRAY()
    peaklt = []
    if list == None:
        MSG('no peaks found')
    else:
        for peak in list:
            peaklt.append([peak.getPositions()[0],peak.getIntensity(),peak.getHalfWidth()*bf1])
            #print '  ',type(peak.getPositions()[0]),type(peak.getIntensity()),type(peak.getHalfWidth()*bf1)
    return peaklt
      
def set_title(dataset,text):
    outpath = dataset[3]+'/'+dataset[0]+'/'+dataset[1]+'/pdata/'+dataset[2]
    f = open(outpath+'/title','w')
    f.write(text)
    f.close()

def get_timetag():
    timevar = time.localtime()
    timetag = '%d%02d%02d_%02d%02d'%(timevar[0],timevar[1],timevar[2],timevar[3],timevar[4])
    return timetag


