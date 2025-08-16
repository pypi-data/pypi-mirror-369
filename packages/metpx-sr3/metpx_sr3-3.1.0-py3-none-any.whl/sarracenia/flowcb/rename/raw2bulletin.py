"""
Description:
    sr3 equivalent of the V2 configuration cvt_bulletin_filename_from_content
    Add bulletin data (full header, timestamp, station ID, BBB) to incomplete filename

    Works essentially the same way as its v2 counterpart, except it can get the bulletin file contents 2 ways.
       1. By the sr3 message content
       2. By opening and reading the path to the file directly.
    The plugin captures what was done on the V2 converter and ties it up with Sundew source code logic to make it more generalized.
    What it can do that the V2 plugin cannot:
        - Add the station ID in the filename
        - Add the BBB in the filename
        - Fetch bulletin data multiple ways

    Decoding of the data is done in the same way of the encoder in flowcb/gather/am.py


Examples:

    RAW Ninjo file (4 letter station ID)
       WACN07 CWAO 082327
       CZEG AIRMET E1 VALID 080105/080505 CWEG-

       Output filename: WACN07_CWAO_082327__CZEG_00001
    
    Another RAW Ninjo file
       FTCN32 CWAO 100500 AAM
       (...)

       Output filename: FTCN32_CWAO_100500_AAM__00002

    A CACN bulletin missing the correct filename
       Input filename: CA__12345

       Contents:
        CACN00 CWAO 141600
        PQU

       Output filename: CACN00_CWAO_141600__PQU_00003

    A ISA binary bulletin
       Input filename: ISAA41_CYZX_162000__00035 

       Contents:
        ISAA41_CYZX_162000
        BUFR

       Output filename: ISAA41_CYZX_162000___00004  

Usage:
    callback rename.raw2bulletin
    --- OR (inside callback) ---
    from sarracenia.flowcb.rename.raw2bulletin import Raw2bulletin
    def __init__():
        super().__init__(options,logger)
        self.renamer = Raw2bulletin(self.o)


Contributions:
    Andre LeBlanc - First author (2024/02)

Improvements:
    Delegate some of the generalized methods to a parent class. To be callable by other plugins.
"""

from sarracenia.flowcb import FlowCB
from sarracenia.bulletin import Bulletin
import logging
import datetime

logger = logging.getLogger(__name__)

class Raw2bulletin(FlowCB):

    def __init__(self,options) :
        super().__init__(options,logger)
        self.seq = 0
        self.binary = 0
        self.bulletinHandler = Bulletin(self.o)
        # Need to redeclare these options to have their default values be initialized.
        self.o.add_option('inputCharset', 'str', 'utf-8')
        self.o.add_option('binaryInitialCharacters', 'list', [b'BUFR' , b'GRIB', b'\211PNG'])

    # If file was converted, get rid of extensions it had
    def after_gather(self,worklist):

        new_worklist = []

        for msg in worklist.incoming:

            # If called by a sarra, should always have post_baseDir, so should be OK in specifying it
            path = self.o.post_baseDir + '/' + msg['relPath']

            # Determine if bulletin is binary or not
            # From sundew source code
            try:
                data = msg.getContent(self.o)

                # Also accept bulletins that only have one line (health check bulletins)
                if len(data.splitlines()) == 1 or data.splitlines()[1][:4] in self.o.binaryInitialCharacters:
                    # Decode data, only text. The raw binary data contains the header in which we're interested. Only get that header.
                    data = data.splitlines()[0].decode('ascii')
                else:
                    # Data is not binary
                    data = data.decode(self.o.inputCharset)
            except Exception as e:
                logger.error(f"Error encountered trying to fetch or decode data. Error message: {e}")
                worklist.rejected.append(msg)
                continue


            if not data:
                logger.error("No data was found. Skipping message")
                worklist.rejected.append(msg)
                continue
            
            lines  = data.split('\n')
            #first_line  = lines[0].strip('\r')
            #first_line  = first_line.strip(' ')
            #first_line  = first_line.strip('\t')
            first_line  = lines[0].split(' ')

            # Sometimes bulletins have carriage returns at the end of the first line. Remove if applicable
            first_line[-1]  = first_line[-1].replace('\r', '')

            # Build header from bulletin
            header = self.bulletinHandler.buildHeader(first_line)
            if header == None:
                logger.error("Unable to fetch header contents. Skipping message")
                worklist.rejected.append(msg)
                continue
            
            # Get the station timestamp from bulletin
            if len(header.split('_')) == 2:
                ddhhmm = self.bulletinHandler.getTime(data)
                if ddhhmm == None:
                    logger.error("Unable to get julian time.")
            else:
                ddhhmm = ''
            
            # Get the BBB from bulletin
            BBB = self.bulletinHandler.getBBB(first_line)

            # Get the station ID from bulletin
            if not len(data.splitlines()) == 1:
                stn_id = self.bulletinHandler.getStation(data)
            else: stn_id = ''

            # Generate a sequence (random ints)
            seq = self.bulletinHandler.getRandom()

            # Assign a default value for messages not coming from AM
            if 'isProblem' not in msg:
                msg['isProblem'] = False


            # Rename file with data fetched
            try:
                # We can't disseminate bulletins downstream if they're missing the timestamp, but we want to keep the bulletins to troubleshoot source problems
                # We'll append "_PROBLEM" to the filename to be able to identify erronous bulletins
                if ddhhmm == None or msg['isProblem']:
                    timehandler = datetime.datetime.now()

                    # Add current time as new timestamp to filename
                    new_file = header + "_" + timehandler.strftime('%d%H%M') + "_" + BBB + "_" + stn_id + "_" + seq + "_PROBLEM"
                    logger.error(f"New filename (for problem file): {new_file}")

                elif stn_id == None:
                    new_file = header + "_" + BBB + "_" + '' + "_" + seq + "_PROBLEM"
                    logger.error(f"New filename (for problem file): {new_file}")
                elif ddhhmm == '':
                    new_file = header + "_" + BBB + "_" + stn_id + "_" + seq
                else:
                    new_file = header + "_" + ddhhmm + "_" + BBB + "_" + stn_id + "_" + seq

                # No longer needed
                if 'isProblem' in msg:
                    del(msg['isProblem'])

                msg['rename'] = new_file

                logger.info(f"New filename: {new_file}")
                new_worklist.append(msg)
                
            except Exception as e:
                logger.error(f"Error in renaming the filename. Error message: {e}")
                worklist.rejected.append(msg)
                continue

        worklist.incoming = new_worklist
