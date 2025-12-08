# Auto-generated Python translation of Pine Script indicator
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Any


class Inputs:
    def int(self, default: int, *_args, **_kwargs) -> int: return default
    def bool(self, default: bool, *_args, **_kwargs) -> bool: return default
    def color(self, default: Any, *_args, **_kwargs) -> Any: return default
    def string(self, default: str, *_args, **_kwargs) -> str: return default
    def float(self, default: float, *_args, **_kwargs) -> float: return default


class Color:
    @staticmethod
    def rgb(r, g, b, a=255): return (r, g, b, a)


def array_push(arr: List[Any], value: Any) -> None: arr.append(value)
def array_insert(arr: List[Any], idx: int, value: Any) -> None: arr.insert(idx, value)
def array_remove(arr: List[Any], idx: int) -> Any: return arr.pop(idx)


class TA:
    @staticmethod
    def highest(length: int): return 0
    @staticmethod
    def lowest(length: int): return 0


inputs = Inputs()
ta = TA()


# This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
# © TFlab
#@version=5
indicator("Smart Money Concept [TradingFinder] Major Minor OB + FVG (SMC)" ,'SMC TFlab', overlay = true, max_bars_back = 5000, max_boxes_count = 500,max_labels_count = 500, max_lines_count = 500 )

#import Libraries
    #import Order Block Refiner
import TFlab/OrderBlockRefiner_TradingFinder/2 as Refiner
    #import Order Block Drawing  Library
import TFlab/OrderBlockDrawing_TradingFinder/1 as Drawing
    #import FVG  Library
import TFlab/FVGDetectorLibrary/1 as FVG
    #import Liquidity Library
import TFlab/LiquidityFinderLibrary/1 as Liq
    #import Alert Sender Library
import TFlab/AlertSenderLibrary_TradingFinder/1 as Alert
    #import Tradingview Technical Analysis Library
import TradingView/ta/7


#Input

    #Pivot Period of Order Blocks Detector
PP = inputs.int(5, 'Pivot Period of Order Blocks Detector' , group = 'Logic Parameter' , minval = 1)
OBVaP = inputs.int(500, 'Order Block Validity Period (Bar)' , group = 'Logic Parameter' , maxval = 4998 , minval = 10,
 tooltip = 'You can set the validity period of each Order Block based on the number of candles that have passed since the origin of the Order Block.')
    #Display Order Blocks

ShowDmainCh = inputs.bool(true, 'Demand Main Zone, "ChoCh" Origin.', 
 'Using this button, you can control whether the' + 
 '"Demand Main Order Blocks" originating to "ChoCh" are displayed.' , group = 'Order Blocks Display', inline = 'OB 1')

ColorDmainCh = inputs.color(Color.rgb(60, 176, 68, 65) , '' , group = 'Order Blocks Display', inline = 'OB 1')


ShowDsubCh  = inputs.bool(true, 'Demand Sub Zone, "ChoCh" Origin..', 
 'Using this button, you can control whether the' + 
 '"Demand Sub Order Blocks" originating to "ChoCh" are displayed.' , group ='Order Blocks Display', inline = 'OB 2')

ColorDsubCh = inputs.color(Color.rgb(123, 180, 227, 65) , '' , group = 'Order Blocks Display', inline = 'OB 2')


ShowDBoS    = inputs.bool(true, 'Demand All Zone, "BoS" Origin.......', 
 'Using this button, you can control whether the' + 
 '"Demand Order Blocks" originating to "BoS" are displayed.' , group ='Order Blocks Display', inline = 'OB 3')

ColorDBoS = inputs.color(Color.rgb(153, 237, 195, 75) , '' , group = 'Order Blocks Display', inline = 'OB 3')


ShowSmainCh = inputs.bool(true, 'Supply Main Zone, "ChoCh" Origin...', 
 'Using this button, you can control whether the' + 
 '"Supply Main Order Blocks" originating to "ChoCh" are displayed.' , group ='Order Blocks Display', inline = 'OB 4')

ColorSmainCh = inputs.color(Color.rgb(191, 10, 48 , 75) , '' , group = 'Order Blocks Display', inline = 'OB 4')


ShowSsubCh  = inputs.bool(true, 'Supply Sub Zone, "ChoCh" Origin....', 
 'Using this button, you can control whether the' + 
 '"Supply Sub Order Blocks" originating to "ChoCh" are displayed.' , group ='Order Blocks Display', inline = 'OB 5')

ColorSsubCh = inputs.color(Color.rgb(243, 189, 74, 75) , '' , group = 'Order Blocks Display', inline = 'OB 5')


ShowSBoS    = inputs.bool(true, 'Supply All Zone,  "BoS"  Origin.........', 
 'Using this button, you can control whether the' + 
 '"Supply Order Blocks" originating to "BoS" are displayed.' , group ='Order Blocks Display', inline = 'OB 6')

ColorSBoS = inputs.color(Color.rgb(255, 105, 97, 85) , '' , group = 'Order Blocks Display', inline = 'OB 6')

    #Refinement Order Blocks, display and Method

RefineDmainCh = inputs.bool(true, 'Refine Demand Main', 
 'If you want this "Demand Main Order Block, ChoCh Origin" to be refined to display a optimal range,' +
 'you should select "On" and if you want to see the original' +
 'range of the block order, you should select "Off".' + 
 '\nAlso, if you are a risk taker, you can choose the "Aggressive" Refine method,' + 
 'and if you are risk averse, you can choose the "Defensive" Refine method.'
 , group ='Order Blocks Refinement ', inline = 'Refine 1')

RefineMeDmainCh = inputs.string('Defensive', '', ['Defensive', 'Aggressive'] , 
 group = 'Order Blocks Refinement ' , inline = 'Refine 1')

RefineDsubCh  = inputs.bool(true, 'Refine Demand Sub.',
 'If you want this "Demand Sub Order Block, ChoCh Origin" to be refined to display a optimal range,' +
 'you should select "On" and if you want to see the original' +
 'range of the block order, you should select "Off".' + 
 '\nAlso, if you are a risk taker, you can choose the "Aggressive" Refine method,' + 
 'and if you are risk averse, you can choose the "Defensive" Refine method.' 
 , group ='Order Blocks Refinement ', inline = 'Refine 2')

RefineMeDsubCh  = inputs.string('Defensive', '', ['Defensive', 'Aggressive'] , 
 group = 'Order Blocks Refinement ', inline = 'Refine 2')

RefineDBoS    = inputs.bool(true, 'Refine Demand BoS.', 
 'If you want this "Demand Order Block, BoS Origin" to be refined to display a optimal range,' +
 'you should select "On" and if you want to see the original' +
 'range of the block order, you should select "Off".' + '\n' +
 '\nAlso, if you are a risk taker, you can choose the "Aggressive" Refine method,' + 
 'and if you are risk averse, you can choose the "Defensive" Refine method.'
 , group ='Order Blocks Refinement ', inline = 'Refine 3')

RefineMeDBoS    =  inputs.string('Defensive', '', ['Defensive', 'Aggressive'] , 
 group = 'Order Blocks Refinement ', inline = 'Refine 3')

RefineSmainCh = inputs.bool(true, 'Refine Supply Main..', 
 'If you want this "Supply Main Order Block, ChoCh Origin" to be refined to display a optimal range,' +
 'you should select "On" and if you want to see the original' +
 'range of the block order, you should select "Off".' + 
 '\nAlso, if you are a risk taker, you can choose the "Aggressive" Refine method,' + 
 'and if you are risk averse, you can choose the "Defensive" Refine method.' 
 , group ='Order Blocks Refinement ', inline = 'Refine 4')

RefineMeSmainCh = inputs.string('Defensive', '', ['Defensive', 'Aggressive'] , 
 group = 'Order Blocks Refinement ', inline = 'Refine 4')

RefineSsubCh  = inputs.bool(true, 'Refine Supply Sub...', 
 'If you want this "Supply Sub Order Block, ChoCh Origin" to be refined to display a optimal range,' +
 'you should select "On" and if you want to see the original' +
 'range of the block order, you should select "Off".' + 
 '\nAlso, if you are a risk taker, you can choose the "Aggressive" Refine method,' + 
 'and if you are risk averse, you can choose the "Defensive" Refine method.' 
 , group ='Order Blocks Refinement ', inline = 'Refine 5')

RefineMeSsubCh  =  inputs.string('Defensive', '', ['Defensive', 'Aggressive'] , 
 group = 'Order Blocks Refinement ', inline = 'Refine 5')

RefineSBoS    = inputs.bool(true, 'Refine Supply BoS...', 
 'If you want this "Supply Order Block, BoS Origin" to be refined to display a optimal range,' +
 'you should select "On" and if you want to see the original' +
 'range of the block order, you should select "Off".' + '\n' +
 '\nAlso, if you are a risk taker, you can choose the "Aggressive" Refine method,' + 
 'and if you are risk averse, you can choose the "Defensive" Refine method.' 
 , group ='Order Blocks Refinement ', inline = 'Refine 6')

RefineMeSBoS    =  inputs.string('Defensive', '', ['Defensive', 'Aggressive'] , 
 group = 'Order Blocks Refinement ', inline = 'Refine 6')


    #FVG

PShowDeFVG = inputs.bool(true, ' Show Demand FVG', group = 'FVG')
PShowSuFVG = inputs.bool(true, ' Show Supply FVG', group = 'FVG')
PFVGFilter = inputs.bool(true, 'FVG Filter ............',  group = 'FVG' , inline = 'FVG Filter')
PFVGFilterType = inputs.string('Very Defensive', '', 
 ['Very Aggressive' , 'Aggressive' , 'Defensive' , 'Very Defensive'], group = 'FVG', inline = 'FVG Filter' ,
 tooltip = 'If it is "On", this filter will filter "FVGs" based on the width of the Zone.'  + 
 'From "Very Aggressive" to "Very Defensive" the width of the "FVG" decreases.')


    #Liquidity

ShowSHLL = inputs.bool(true , 'Show Statics High Liquidity Line',group = 'Liquidity')
ShowSLLL = inputs.bool(true , 'Show Statics Low Liquidity Line',group = 'Liquidity')
ShowDHLL = inputs.bool(true , 'Show Dynamics High Liquidity Line',group = 'Liquidity')
ShowDLLL = inputs.bool(true , 'Show Dynamics Low Liquidity Line',group = 'Liquidity')

SPP = inputs.int(8 , 'Statics Period Pivot',group = 'Liquidity') // Statics Period Pivot
DPP = inputs.int(3 , 'Dynamics Period Pivot',group = 'Liquidity') // Dynamics Period Pivot

SLLS = inputs.float(0.30 , 'Statics Liquidity Line Sensitivity', 
 maxval = 0.4 ,minval = 0.0, step = 0.01,group = 'Liquidity') // Statics Liquidity Line Sensitivity
DLLS = inputs.float(1.00 , 'Dynamics Liquidity Line Sensitivity',
 maxval = 1.95 ,minval = 0.4, step = 0.01,group = 'Liquidity') // Dynamics Liquidity Line Sensitivity


    #Alert
AlertName = inputs.string('Smart Money Concept [TradingFinder]', 'Alerts Name', group = 'Alert')

Alert_DMM = inputs.string('On' , 'Alert Demand Main Mitigation' , ['On', 'Off'], 'If you turn on the Alert Demand Main ChoCh Origin Mitigation,' + 
 'you can receive alerts and notifications after setting the "Alert".' , group = 'Alert')
MessageBull_DMM = inputs.text_area('Long Position in Demand Main Zone ChoCh Origin.', 'Long Signal Message' ,group = 'Alert')

Alert_DSM = inputs.string('On' , 'Alert Demand Sub Mitigation' , ['On', 'Off'], 'If you turn on the Alert Demand Sub ChoCh Origin Mitigation,' +
 'you can receive alerts and notifications after setting the "Alert".' , group = 'Alert')
MessageBull_DSM = inputs.text_area('Long Position in Demand Sub Zone ChoCh Origin.', 'Long Signal Message' ,group = 'Alert')

Alert_DAM = inputs.string('On' , 'Alert Demand BoS Mitigation' , ['On', 'Off'], 'If you turn on the Alert Demand All BoS Origin Mitigation,' +
 'you can receive alerts and notifications after setting the "Alert".' , group = 'Alert')
MessageBull_DAM = inputs.text_area('Long Position in Demand Zone BoS Origin.', 'Long Signal Message' ,group = 'Alert')

Alert_SMM = inputs.string('On' , 'Alert Supply Main Mitigation', ['On', 'Off'], 'If you turn on the Alert Supply Main ChoCh Origin Mitigation,' +
 'you can receive alerts and notifications after setting the "Alert".' , group = 'Alert')
MessageBear_SMM = inputs.text_area('Short Position in Supply Main Zone ChoCh Origin.','Short Signal Message' , group = 'Alert')

Alert_SSM = inputs.string('On' , 'Alert Supply Sub Mitigation' , ['On', 'Off'], 'If you turn on the Alert Supply Sub ChoCh Origin Mitigation,' +
 'you can receive alerts and notifications after setting the "Alert".' , group = 'Alert')
MessageBear_SSM = inputs.text_area('Short Position in Supply Sub Zone ChoCh Origin.','Short Signal Message' , group = 'Alert')

Alert_SAM = inputs.string('On' , 'Alert Supply BoS Mitigation' , ['On', 'Off'], 'If you turn on the Alert Supply All BoS Origin Mitigation,' +
 'you can receive alerts and notifications after setting the "Alert".' , group = 'Alert')
MessageBear_SAM = inputs.text_area('Short Position in Supply Zone BoS Origin.','Short Signal Message' , group = 'Alert')


Frequncy = inputs.string('Once Per Bar' , 'Message Frequency' , ['All', 'Once Per Bar' , 'Per Bar Close'], 'The triggering frequency. Possible values are: All'+ 
 ' (all function calls trigger the alert), Once Per Bar (the first function call during the bar triggers the alert), ' +  
 ' Per Bar Close (the function call triggers the alert only when it occurs during the last script iteration of the real-time bar,' +  
 ' when it closes). The default is alert.freq_once_per_bar.)', group = 'Alert')
UTC = inputs.string('UTC' , 'Show Alert time by Time Zone', group = 'Alert')
MoreInfo = inputs.string('On', 'Display More Info', ['On', 'Off'], group = 'Alert')



    #Lines

        #Bos Lines
            #Major Line
                #Bullish
MajorBuBoSLine_Show       = inputs.string('Off'  ,'Show Major Bullish BoS Lines', ['On', 'Off'] , group = 'Major Bullish "BoS" Lines')
MajorBuBoSLine_Style    = inputs.string(line.style_dashed ,'Style Major Bullish BoS Lines', 
 [line.style_solid, line.style_dashed, line.style_dotted]  , group = 'Major Bullish "BoS" Lines')
MajorBuBoSLine_Color    = inputs.color(color.black ,'Color Major Bullish BoS Lines'  , group = 'Major Bullish "BoS" Lines')


                #Bearish
MajorBeBoSLine_Show       = inputs.string('Off'  ,'Show Major Bearish BoS Lines', ['On', 'Off'] , group = 'Major Bearish "BoS" Lines')
MajorBeBoSLine_Style    = inputs.string(line.style_dashed ,'Style Major Bearish BoS Lines', 
 [line.style_solid, line.style_dashed, line.style_dotted]  , group = 'Major Bearish "BoS" Lines')
MajorBeBoSLine_Color    = inputs.color(color.black ,'Color Major Bearish BoS Lines'  , group = 'Major Bearish "BoS" Lines')


            #Minor
                #Bullish
MinorBuBoSLine_Show       = inputs.string('Off'  ,'Show Minor Bullish BoS  Lines', ['On', 'Off'] , group = 'Minor Bullish "BoS"  Lines')
MinorBuBoSLine_Style    = inputs.string(line.style_dotted ,'Style Minor Bullish BoS  Lines', 
 [line.style_solid, line.style_dashed, line.style_dotted]  , group = 'Minor Bullish "BoS"  Lines')
MinorBuBoSLine_Color    = inputs.color(color.black ,'Color Minor Bullish BoS  Lines' , group = 'Minor Bullish "BoS"  Lines' )


                #Bearish
MinorBeBoSLine_Show       = inputs.string('Off'  ,'Show Minor Bearish BoS Lines', ['On', 'Off'] , group = 'Minor Bearish "BoS" Lines' )
MinorBeBoSLine_Style    = inputs.string(line.style_dotted ,'Style inor Bearish BoS Lines', 
 [line.style_solid, line.style_dashed, line.style_dotted] , group = 'Minor Bearish "BoS" Lines')
MinorBeBoSLine_Color    = inputs.color(color.black ,'Color inor Bearish BoS Lines' , group = 'Minor Bearish "BoS" Lines')

        #ChoCh Lines
            #Major Line
                #Bullish
MajorBuChoChLine_Show     = inputs.string('Off'  ,'Show Major Bullish ChoCh Lines', ['On', 'Off'] , group = 'Major Bullish "ChoCh" Lines')
MajorBuChoChLine_Style    = inputs.string(line.style_dashed ,'Style Major Bullish ChoCh Lines', 
 [line.style_solid, line.style_dashed, line.style_dotted] , group = 'Major Bullish "ChoCh" Lines')
MajorBuChoChLine_Color    = inputs.color(color.black ,'Color Major Bullish ChoCh Lines' , group = 'Major Bullish "ChoCh" Lines')

                #Bearish
MajorBeChoChLine_Show     = inputs.string('Off'  ,'Show Major Bearish ChoCh Lines', ['On', 'Off'] , group = 'Major Bearish "ChoCh" Lines')
MajorBeChoChLine_Style    = inputs.string(line.style_dashed ,'Style Major Bearish ChoCh Lines', 
 [line.style_solid, line.style_dashed, line.style_dotted]  , group = 'Major Bearish "ChoCh" Lines')
MajorBeChoChLine_Color    = inputs.color(color.black ,'Color Major Bearish ChoCh Lines'  , group = 'Major Bearish "ChoCh" Lines')

            #Minor
                #Bullish
MinorBuChoChLine_Show     = inputs.string('Off'  ,'Show Minor Bullish ChoCh Lines', ['On', 'Off'] , group = 'Minor Bullish "ChoCh" Lines')
MinorBuChoChLine_Style    = inputs.string(line.style_dotted ,'Style Minor Bullish ChoCh Lines', 
 [line.style_solid, line.style_dashed, line.style_dotted] , group = 'Minor Bullish "ChoCh" Lines')
MinorBuChoChLine_Color    = inputs.color(color.black ,'Color Minor Bullish ChoCh Lines' , group = 'Minor Bullish "ChoCh" Lines')

                #Bearish           
MinorBeChoChLine_Show     = inputs.string('Off'  ,'Show Minor Bearish ChoCh Lines', ['On', 'Off'] , group = 'Minor Bearish "ChoCh" Lines')
MinorBeChoChLine_Style    = inputs.string(line.style_dotted ,'Style Minor Bearish ChoCh Lines', 
 [line.style_solid, line.style_dashed, line.style_dotted]  , group = 'Minor Bearish "ChoCh" Lines')
MinorBeChoChLine_Color    = inputs.color(color.black ,'Color Minor Bearish ChoCh Lines'  , group = 'Minor Bearish "ChoCh" Lines')

        #Support & Resistance Lines
            #Major Line
                #Support
LastMajorSupportLine_Show    = inputs.string('Off' ,'Show Last Major Support Line', ['On', 'Off'], group = 'Last Major Support Line' )
LastMajorSupportLine_Style    = inputs.string(line.style_solid ,'Style Last Major Support Line', 
 [line.style_solid, line.style_dashed, line.style_dotted] , group = 'Last Major Support Line')
LastMajorSupportLine_Color    = inputs.color(color.black ,'Color Last Major Support Line' , group = 'Last Major Support Line')
                #Resistance
LastMajorResistanceLine_Show = inputs.string('Off' ,'Show Last Major Resistance Line', ['On', 'Off'] , group = 'Last Major Resistance Line')
LastMajorResistanceLine_Style    = inputs.string(line.style_solid ,'Style Last Major Resistance Line', 
 [line.style_solid, line.style_dashed, line.style_dotted] , group = 'Last Major Resistance Line')
LastMajorResistanceLine_Color    = inputs.color(color.black ,'Color Last Major Resistance Line' , group = 'Last Major Resistance Line')

            #Minor Line
                #Support
LastMinorSupportLine_Show    = inputs.string('Off' ,'Show Last Minor Support Line', ['On', 'Off'] , group = 'Last Minor Support Line')
LastMinorSupportLine_Style    = inputs.string(line.style_dashed ,'Style Last Minor Support Line', 
 [line.style_solid, line.style_dashed, line.style_dotted] , group = 'Last Minor Support Line')
LastMinorSupportLine_Color    = inputs.color(color.black ,'Color Last Minor Support Line', group = 'Last Minor Support Line')

                #Resistance
LastMinorResistanceLine_Show = inputs.string('Off' ,'Show Last Minor Resistance Line', ['On', 'Off'] , group = 'Last Minor Resistance Line')
LastMinorResistanceLine_Style    = inputs.string(line.style_dashed ,'Style Last Minor Resistance Line', 
 [line.style_solid, line.style_dashed, line.style_dotted]  , group = 'Last Minor Resistance Line')
LastMinorResistanceLine_Color    = inputs.color(color.black ,'Color Last Minor Resistance Line'  , group = 'Last Minor Resistance Line')

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#Variables

    #ZigZag Data
Open = open
High = high
Low = low
Close = close 
Bar_Index = bar_index
ATR =ta.atr(55)
ArrayType = array.new_string()
ArrayValue = array.new_float()
ArrayIndex =  array.new_int()
ArrayTypeAdv  = array.new_string()
ArrayValueAdv = array.new_float()
ArrayIndexAdv =  array.new_int()  
line ZZLine = na
line Sline = na 
line Rline = na 
label Label  = na
PASS = 0
HighPivot = ta.pivothigh(PP,PP)
LowPivot = ta.pivotlow(PP,PP)
HighValue = ta.valuewhen(HighPivot ,High[PP], 0)
LowValue = ta.valuewhen(LowPivot ,Low[PP], 0)
HighIndex = ta.valuewhen(HighPivot ,Bar_Index[PP], 0)
LowIndex = ta.valuewhen(LowPivot ,Bar_Index[PP], 0)
Correct_HighPivot = 0.0
Correct_LowPivot =  0.0

    #Major Levels
float Major_HighLevel = na
float Major_LowLevel  = na

int Major_HighIndex = na
int Major_LowIndex = na

string Major_HighType= na
string Major_LowType = na

    #Minor Levels
float Minor_HighLevel = na
float Minor_LowLevel  = na

int Minor_HighIndex   = na
int Minor_LowIndex    = na

string Minor_HighType = na
string Minor_LowType  = na

int LockDetecteM_MinorLvL = 0

    #
bool Lock0 = true
bool Lock1 = true

# Detecte Major & Minor Pivot
# Order Blocks Data
    #Major
int LastMHH = 0
int Last02MHH = 0
int LastMLH = 0

int LastMLL = 0
int Last02MLL = 0
int LastMHL = 0
    #Minor
int LastmHH = 0
int Last02mHH = 0
int LastmLH = 0

int LastmLL = 0
int Last02mLL = 0
int LastmHL = 0

#///////////////////////////
# Last Pivot First Point////
#///////////////////////////
string LastPivotType = na
int LastPivotIndex = 0

string LastPivotType02 = na
int LastPivotIndex02 = 0

    #Major 01
float MajorHighValue01 = na
int   MajorHighIndex01 = na
string MajorHighType01 = ''

float MajorLowValue01  = na
int   MajorLowIndex01 =  na
string MajorLowType01 =  ''

    #Minor 01
float MinorHighValue01 = na
int   MinorHighIndex01 = na
string MinorHighType01 = ''

float MinorLowValue01  = na
int   MinorLowIndex01  = na
string MinorLowType01 =  ''

#///////////////////////////////////
#One to the Last Pivot First Point//
#///////////////////////////////////
    #Major 02
float MajorHighValue02 = na
int   MajorHighIndex02 = na
string MajorHighType02 = ''

float MajorLowValue02  = na
int   MajorLowIndex02 =  na
string MajorLowType02 =  ''

    #Minor 02
float MinorHighValue02 = na
int   MinorHighIndex02 = na
string MinorHighType02 = ''

float MinorLowValue02  = na
int   MinorLowIndex02  = na
string MinorLowType02 =  ''

    #Major 02 Change Type Pivot
float MajorHighValue02Ch = na
int   MajorHighIndex02Ch = na
string MajorHighType02Ch = ''

float MajorLowValue02Ch  = na
int   MajorLowIndex02Ch =  na
string MajorLowType02Ch =  ''

    #Lines Data
line MajorLine_ChoChBull   = na
label MajorLabel_ChoChBull = na

line MajorLine_ChoChBear   = na
label MajorLabel_ChoChBear = na

line MajorLine_BoSBull     = na
label MajorLabel_BoSBull   = na

line MajorLine_BoSBear     = na
label MajorLabel_BoSBear   = na

line MinorLine_ChoChBull   = na
label MinorLabel_ChoChBull = na

line MinorLine_ChoChBear   = na
label MinorLabel_ChoChBear = na

line MinorLine_BoSBull     = na
label MinorLabel_BoSBull   = na

line MinorLine_BoSBear     = na
label MinorLabel_BoSBear   = na

    # BoS & ChoCh Data
        #Major
bool Bullish_Major_ChoCh = false
bool Bullish_Major_BoS = false

bool Bearish_Major_ChoCh = false
bool Bearish_Major_BoS = false

BoS_MajorType  = array.new_string()
BoS_MajorIndex = array.new_int()

ChoCh_MajorType  = array.new_string()
ChoCh_MajorIndex = array.new_int()

int LockBreak_M = 0 

        #Minor
bool Bullish_Minor_ChoCh = false
bool Bullish_Minor_BoS = false

bool Bearish_Minor_ChoCh = false
bool Bearish_Minor_BoS = false

BoS_MinorType  = array.new_string()
BoS_MinorIndex = array.new_int()

ChoCh_MinorType  = array.new_string()
ChoCh_MinorIndex = array.new_int()

int LockBreak_m = 0 


    #Support & Resistance Line

        #Major
line Support_LineMajor = na 
line Resistance_LineMajor = na 
        #Minor
line Support_LineMinor = na
line Resistance_LineMinor = na

    #Trend Data

string ExternalTrend = 'No Trend'
string InternalTrend = 'No Trend'

    #Order Blocks Data

        #Bullish Major ChoCh Main
bool  BuMChMain_Trigger = false
int   BuMChMain_Index     = 0

        #Bullish Major ChoCh Sub
bool  BuMChSub_Trigger = false
int   BuMChSub_Index     = 0

        #Bullish Major BoS
bool  BuMBoS_Trigger = false
int   BuMBoS_Index     = 0

        #Bearish Major ChoCh Main
bool  BeMChMain_Trigger = false
int   BeMChMain_Index     = 0

        #Bearish Major ChoCh Sub
bool  BeMChSub_Trigger = false
int   BeMChSub_Index     = 0

        #Bearish Major BoS
bool  BeMBoS_Trigger = false
int   BeMBoS_Index     = 0

    #Correction OB
        #Bullish Major ChoCh 

float ChBuLowest = 0.0
float ChBuLowestSub = 0.0

int CorrectBuIndex = 0
int CorrectBuIndexSub = 0

        #Bullish Major BoS

float BoSBuLowest = 0.0
float BoSBuLowest02 = 0.0

int CorrectBuBoSIndex = 0
int CorrectBuBoSIndex02 = 0

        #Bearish Major ChoCh 

float ChBeHighest = 0.0
float ChBeHighestSub = 0.0

int CorrectBeIndex = 0
int CorrectBeIndexSub = 0

        #Bearish Major BoS 

float BoSBeHighest = 0.0
float BoSBeHighest02 = 0.0

int CorrectBeBoSIndex = 0
int CorrectBeBoSIndex02 = 0


#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////Calculation/////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    #{Zig Zag}
if HighPivot  and  LowPivot:
    if len(ArrayType) == 0:
        PASS = 1
    elif len(ArrayType) >= 1:
        if ((ArrayType[len(ArrayType) - 1] == "L" or:
             (ArrayType[len(ArrayType) - 1] == "LL"
            if LowPivot < ArrayValue[len(ArrayType) - 1]:
                array_remove(ArrayType,len(ArrayType) - 1)
                array_remove(ArrayValue,len(ArrayValue) - 1)
                array_remove(ArrayIndex,len(ArrayIndex) - 1) 
                ("HL" if array_push(ArrayType,len(ArrayType)>2 else "LL") if (ArrayValue[len(ArrayType) - 2) < LowValue else "L")///////////////////////////////Here]
                array_push(ArrayValue, LowValue)
                array_push(ArrayIndex, LowIndex)
                Correct_LowPivot =  LowValue
            else 
                ("HH" if array_push(ArrayType,len(ArrayType)>2 else "LH") if (ArrayValue[len(ArrayType) - 2) < HighValue else "H" ) ///////////////////////////////Here]
                array_push(ArrayValue, HighValue)
                array_push(ArrayIndex, HighIndex)
            Correct_HighPivot = HighValue  
        elif (ArrayType[len(ArrayType) - 1] == "H" or :
             (ArrayType[len(ArrayType) - 1] == "HH"
            if HighPivot > ArrayValue[len(ArrayType) - 1]:
                array_remove(ArrayType,len(ArrayType) - 1)
                array_remove(ArrayValue,len(ArrayValue) - 1)
                array_remove(ArrayIndex,len(ArrayIndex) - 1)
                ("HH" if array_push(ArrayType,len(ArrayType)>2 else "LH") if (ArrayValue[len(ArrayType) - 2) < HighValue else "H")///////////////////////////////Here]
                array_push(ArrayValue, HighValue)
                array_push(ArrayIndex, HighIndex)
                Correct_HighPivot = HighValue  
            else 
                ("HL" if array_push(ArrayType,len(ArrayType)>2 else "LL") if (ArrayValue[len(ArrayType) - 2) < LowValue else "L")///////////////////////////////Here]
                array_push(ArrayValue, LowValue)
                array_push(ArrayIndex, LowIndex)
            Correct_LowPivot =  LowValue    
        elif (ArrayType[len(ArrayType) - 1] == "LH":
            if HighPivot < ArrayValue[len(ArrayType) - 1]:
                ("HL" if array_push(ArrayType,len(ArrayType)>2 else "LL") if (ArrayValue[len(ArrayType) - 2) < LowValue else "L")///////////////////////////////Here]
                array_push(ArrayValue, LowValue)
                array_push(ArrayIndex, LowIndex)
                Correct_LowPivot =  LowValue 
            elif HighPivot > ArrayValue[len(ArrayType) - 1]:
                if close < ArrayValue[len(ArrayType) - 1]:
                    array_remove(ArrayType,len(ArrayType) - 1)
                    array_remove(ArrayValue,len(ArrayValue) - 1)
                    array_remove(ArrayIndex,len(ArrayIndex) - 1)
                    ("HH" if array_push(ArrayType,len(ArrayType)>2 else "LH") if (ArrayValue[len(ArrayType) - 2) < HighValue else "H")///////////////////////////////Here]
                    array_push(ArrayValue, HighValue)
                    array_push(ArrayIndex, HighIndex)
                    Correct_HighPivot = HighValue  
                elif close > ArrayValue[len(ArrayType) - 1]:
                    ("HL" if array_push(ArrayType,len(ArrayType)>2 else "LL") if (ArrayValue[len(ArrayType) - 2) < LowValue else "L")///////////////////////////////Here]
                    array_push(ArrayValue, LowValue)
                    array_push(ArrayIndex, LowIndex)
                    Correct_LowPivot =  LowValue
        elif (ArrayType[len(ArrayType) - 1] == "HL":
            if LowPivot > ArrayValue[len(ArrayType) - 1]:
                ("HH" if array_push(ArrayType,len(ArrayType)>2 else "LH") if (ArrayValue[len(ArrayType) - 2) < HighValue else "H" ) ///////////////////////////////Here]
                array_push(ArrayValue, HighValue)
                array_push(ArrayIndex, HighIndex)
                Correct_HighPivot = HighValue                       
            elif LowPivot < ArrayValue[len(ArrayType) - 1]:
                if close > ArrayValue[len(ArrayType) - 1]:
                    array_remove(ArrayType,len(ArrayType) - 1)
                    array_remove(ArrayValue,len(ArrayValue) - 1)
                    array_remove(ArrayIndex,len(ArrayIndex) - 1) 
                    ("HL" if array_push(ArrayType,len(ArrayType)>2 else "LL") if (ArrayValue[len(ArrayType) - 2) < LowValue else "L")///////////////////////////////Here]
                    array_push(ArrayValue, LowValue)
                    array_push(ArrayIndex, LowIndex)
                    Correct_LowPivot =  LowValue
                elif close < ArrayValue[len(ArrayType) - 1]:
                    ("HH" if array_push(ArrayType,len(ArrayType)>2 else "LH") if (ArrayValue[len(ArrayType) - 2) < HighValue else "H")///////////////////////////////Here]
                    array_push(ArrayValue, HighValue)
                    array_push(ArrayIndex, HighIndex)
                    Correct_HighPivot = HighValue                         
elif  HighPivot :
    if len(ArrayType) == 0:
        array_insert(ArrayType, 0, "H")
        array_insert(ArrayValue, 0, HighValue)
        array_insert(ArrayIndex, 0, HighIndex)
        Correct_HighPivot = HighValue
    elif len(ArrayType) >= 1:
        if ((ArrayType[len(ArrayType) - 1] == "L" or:
             (ArrayType[len(ArrayType) - 1] == "HL" or
             (ArrayType[len(ArrayType) - 1] == "LL"
            if HighPivot > ArrayValue[len(ArrayType) - 1]:
                ("HH" if array_push(ArrayType,len(ArrayType)>2 else "LH") if (ArrayValue[len(ArrayType) - 2) < HighValue else "H" ) ///////////////////////////////Here]
                array_push(ArrayValue, HighValue)
                array_push(ArrayIndex, HighIndex)
                Correct_HighPivot = HighValue
            elif  HighPivot < ArrayValue[len(ArrayType) - 1]:
                array_remove(ArrayType,len(ArrayType) - 1)
                array_remove(ArrayValue,len(ArrayValue) - 1)
                array_remove(ArrayIndex,len(ArrayIndex) - 1) 
                ("HL" if array_push(ArrayType,len(ArrayType)>2 else "LL") if (ArrayValue[len(ArrayType) - 2) < LowValue else "L")///////////////////////////////Here]
                array_push(ArrayValue, LowValue)
                array_push(ArrayIndex, LowIndex)
                Correct_LowPivot =  LowValue                         
        elif (ArrayType[len(ArrayType) - 1] == "H" or :
             (ArrayType[len(ArrayType) - 1] == "HH" or 
             (ArrayType[len(ArrayType) - 1] == "LH"
            if (ArrayValue[len(ArrayValue) - 1] < HighValue:
                array_remove(ArrayType,len(ArrayType) - 1)
                array_remove(ArrayValue,len(ArrayValue) - 1)
                array_remove(ArrayIndex,len(ArrayIndex) - 1)
                ("HH" if array_push(ArrayType,len(ArrayType)>2 else "LH") if (ArrayValue[len(ArrayType) - 2) < HighValue else "H")///////////////////////////////Here]
                array_push(ArrayValue, HighValue)
                array_push(ArrayIndex, HighIndex)
                Correct_HighPivot = HighValue               
elif LowPivot :
    if len(ArrayType) == 0:
        array_insert(ArrayType, 0, "L")
        array_insert(ArrayValue, 0, LowValue)
        array_insert(ArrayIndex, 0, LowIndex)
        Correct_LowPivot =  LowValue
    elif len(ArrayType) >= 1:
        if (ArrayType[len(ArrayType) - 1] == "H" or :
             (ArrayType[len(ArrayType) - 1] == "HH" or 
             (ArrayType[len(ArrayType) - 1] == "LH"
            if LowPivot < ArrayValue[len(ArrayType) - 1]:
                ("HL" if array_push(ArrayType,len(ArrayType)>2 else "LL") if (ArrayValue[len(ArrayType) - 2) < LowValue else "L")///////////////////////////////Here]
                array_push(ArrayValue, LowValue)
                array_push(ArrayIndex, LowIndex)
                Correct_LowPivot =  LowValue
            elif LowPivot > ArrayValue[len(ArrayType) - 1]:
                array_remove(ArrayType,len(ArrayType) - 1)
                array_remove(ArrayValue,len(ArrayValue) - 1)
                array_remove(ArrayIndex,len(ArrayIndex) - 1)
                ("HH" if array_push(ArrayType,len(ArrayType)>2 else "LH") if (ArrayValue[len(ArrayType) - 2) < HighValue else "H")///////////////////////////////Here]
                array_push(ArrayValue, HighValue)
                array_push(ArrayIndex, HighIndex)
                Correct_HighPivot = HighValue                        
        elif (ArrayType[len(ArrayType) - 1] == "L" or :
             (ArrayType[len(ArrayType) - 1] == "HL" or 
             (ArrayType[len(ArrayType) - 1] == "LL"
            if (ArrayValue[len(ArrayValue) - 1] > LowValue:
                array_remove(ArrayType,len(ArrayType) - 1)
                array_remove(ArrayValue,len(ArrayValue) - 1)
                array_remove(ArrayIndex,len(ArrayIndex) - 1) 
                ("HL" if array_push(ArrayType,len(ArrayType)>2 else "LL") if (ArrayValue[len(ArrayType) - 2) < LowValue else "L")///////////////////////////////Here]
                array_push(ArrayValue, LowValue)
                array_push(ArrayIndex, LowIndex)
                Correct_LowPivot =  LowValue

    #{Zig Zag Advance}

        #first Major & Minor Detector
if len(ArrayType) ==  2:
    if ArrayType[0] == 'H':
        Major_HighLevel = ArrayValue[0]
        Major_LowLevel  = ArrayValue[1]
        Major_HighIndex = ArrayIndex[0]
        Major_LowIndex  = ArrayIndex[1]
        Major_HighType = ArrayType[0]
        Major_LowType  = ArrayType[1]
    elif ArrayType[0] == 'L':
        Major_HighLevel = ArrayValue[1]
        Major_LowLevel  = ArrayValue[0] 
        Major_HighIndex = ArrayIndex[1]
        Major_LowIndex  = ArrayIndex[0]
        Major_HighType = ArrayType[1]
        Major_LowType  = ArrayType[0]

        #Making Copies of Arrays


if  len(ArrayValue) == 1:
    if Lock0:
        array_insert(ArrayTypeAdv ,0 ,'M' +  ArrayType[0]
        array_insert(ArrayValueAdv,0 ,ArrayValue[0]
        array_insert(ArrayIndexAdv,0 ,ArrayIndex[0]   
        Lock0 = false

if  len(ArrayValue) == 2:
    if Lock1:
        array_insert(ArrayTypeAdv ,1 ,'M' +  ArrayType[1]
        array_insert(ArrayValueAdv,1 ,ArrayValue[1]
        array_insert(ArrayIndexAdv,1 ,ArrayIndex[1]   
        Lock1 = false

if len(ArrayValue) > 1:
    if ArrayValue[len(ArrayValue)-1)[1] != ArrayValue.get(len(ArrayValue)-1]:
        if str.substring(ArrayType[len(ArrayType)-1)[1], str.length(ArrayType.get(len(ArrayType)-1))-1] != :
             str.substring(ArrayType[len(ArrayType)-1), str.length(ArrayType.get(len(ArrayType)-1]-1
            array_push(ArrayTypeAdv ,'m' +  ArrayType[len(ArrayType)   - 1]
            array_push(ArrayValueAdv, ArrayValue[len(ArrayValue) - 1]
            array_push(ArrayIndexAdv, ArrayIndex[len(ArrayIndex) - 1]
        elif str.substring(ArrayType[len(ArrayType)-1)[1], str.length(ArrayType.get(len(ArrayType)-1))-1] == :
             str.substring(ArrayType[len(ArrayType)-1), str.length(ArrayType.get(len(ArrayType)-1]-1
            array_remove(ArrayValueAdv, len(ArrayValueAdv) - 1)
            array_remove(ArrayIndexAdv, len(ArrayIndexAdv) - 1)
            array_push(ArrayValueAdv, ArrayValue[len(ArrayValue) - 1]
            array_push(ArrayIndexAdv, ArrayIndex[len(ArrayIndex) - 1]

        #All Major & Minor Pivot Detector 

if len(ArrayValueAdv) > 1:
            #High Major Detector
    if close > Major_HighLevel:
        if ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mL':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('ML')
            Major_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mHL':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('M' + ArrayType[len(ArrayType) - 1]      
            Major_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1] 
        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mLL':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('M'  + ArrayType[len(ArrayType) - 1] 
            Major_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1) == 'mLH' or ArrayTypeAdv.get(len(ArrayTypeAdv) - 1] == 'mHH' or :
             ArrayTypeAdv[len(ArrayTypeAdv) - 1) == 'MLH' or ArrayTypeAdv.get(len(ArrayTypeAdv) - 1] == 'MHH' 
            if ArrayTypeAdv[len(ArrayTypeAdv) - 2] == 'mHL':
                ArrayTypeAdv.remove(len(ArrayTypeAdv) - 2)
                ArrayTypeAdv.insert(len(ArrayValueAdv) - 2 , 'M' + ArrayType[len(ArrayType) - 2]      
                Major_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                Major_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                Major_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]
            elif ArrayTypeAdv[len(ArrayTypeAdv) - 2] == 'mLL':
                ArrayTypeAdv.remove(len(ArrayTypeAdv) - 2)
                ArrayTypeAdv.insert(len(ArrayValueAdv) - 2 , 'M' + ArrayType[len(ArrayType) - 2]
                Major_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                Major_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                Major_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    if  ArrayValueAdv[len(ArrayValueAdv) - 1] > Major_HighLevel:
        if ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mH':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('MH')
            Major_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mLH':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('M' + ArrayType[len(ArrayType) - 1]  
            Major_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]     
        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1) == 'mHH' or ArrayTypeAdv.get(len(ArrayTypeAdv) - 1] == 'MHH':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('M' + ArrayType[len(ArrayType) - 1]
            Major_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]

            #Low Major Detector
    if close < Major_LowLevel:
        if ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mH':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('MH')
            Major_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mLH':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('M' +  ArrayType[len(ArrayType) - 1]      
            Major_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mHH':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('M' + ArrayType[len(ArrayType) - 1]
            Major_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1) == 'mHL' or ArrayTypeAdv.get(len(ArrayTypeAdv) - 1] == 'mLL' or :
             ArrayTypeAdv[len(ArrayTypeAdv) - 1) == 'MHL' or ArrayTypeAdv.get(len(ArrayTypeAdv) - 1] == 'MLL'
            if ArrayTypeAdv[len(ArrayTypeAdv) - 2] == 'mLH':
                ArrayTypeAdv.remove(len(ArrayTypeAdv) - 2)
                ArrayTypeAdv.insert(len(ArrayValueAdv) - 2 , 'M' + ArrayType[len(ArrayType) - 2]      
                Major_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                Major_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                Major_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]
            elif ArrayTypeAdv[len(ArrayTypeAdv) - 2] == 'mHH':
                ArrayTypeAdv.remove(len(ArrayTypeAdv) - 2)
                ArrayTypeAdv.insert(len(ArrayValueAdv) - 2 , 'M' + ArrayType[len(ArrayType) - 2]
                Major_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                Major_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                Major_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    if ArrayValueAdv[len(ArrayValueAdv) - 1] < Major_LowLevel:
        if ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mL':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('ML')
            Major_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]

        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mHL':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('M' + ArrayType[len(ArrayType) - 1) ] 
            Major_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        elif ArrayTypeAdv[len(ArrayTypeAdv) - 1) == 'mLL' or ArrayTypeAdv.get(len(ArrayTypeAdv) - 1] == 'MLL':
            ArrayTypeAdv.remove(len(ArrayTypeAdv) - 1)
            ArrayTypeAdv.push('M' + ArrayType[len(ArrayType) - 1]
            Major_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
            Major_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
            Major_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]



#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


    #Get Pivot Data
        #Last Pivot Data
if len(ArrayTypeAdv) > 1:
    LastPivotType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
    LastPivotIndex = ArrayIndexAdv[len(ArrayTypeAdv) - 1]
    LastPivotType02 = ArrayTypeAdv[len(ArrayTypeAdv) - 2]
    LastPivotIndex02 = ArrayIndexAdv[len(ArrayTypeAdv) - 2]
        #Major
    if  ArrayTypeAdv[len(ArrayTypeAdv) - 1] ==  'MHH':
        MajorHighValue01   =  ArrayValueAdv[len(ArrayTypeAdv) - 1]
        MajorHighIndex01   =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
        MajorHighType01    =  ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        LastMHH            =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]

    if  ArrayTypeAdv[len(ArrayTypeAdv) - 1] ==  'MLH':
        MajorHighValue01   =  ArrayValueAdv[len(ArrayTypeAdv) - 1]
        MajorHighIndex01   =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
        MajorHighType01    =  ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        LastMLH            =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
    if  ArrayTypeAdv[len(ArrayTypeAdv) - 1] ==  'MLL':
        MajorLowValue01   =  ArrayValueAdv[len(ArrayTypeAdv) - 1]
        MajorLowIndex01   =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
        MajorLowType01    =  ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        LastMLL            =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
    if  ArrayTypeAdv[len(ArrayTypeAdv) - 1] ==  'MHL':
        MajorLowValue01   =  ArrayValueAdv[len(ArrayTypeAdv) - 1]
        MajorLowIndex01   =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
        MajorLowType01    =  ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        LastMHL            =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
    
        #Minor
    if  ArrayTypeAdv[len(ArrayTypeAdv) - 1] ==  'mHH':
        MinorHighValue01   =  ArrayValueAdv[len(ArrayTypeAdv) - 1]
        MinorHighIndex01   =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
        MinorHighType01    =  ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        LastmHH            =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
    if  ArrayTypeAdv[len(ArrayTypeAdv) - 1] ==  'mLH':
        MinorHighValue01   =  ArrayValueAdv[len(ArrayTypeAdv) - 1]
        MinorHighIndex01   =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
        MinorHighType01    =  ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        LastmLH            =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
    if  ArrayTypeAdv[len(ArrayTypeAdv) - 1] ==  'mLL':
        MinorLowValue01   =  ArrayValueAdv[len(ArrayTypeAdv) - 1]
        MinorLowIndex01   =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
        MinorLowType01    =  ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        LastmLL           =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
    if  ArrayTypeAdv[len(ArrayTypeAdv) - 1] ==  'mHL':
        MinorLowValue01   =  ArrayValueAdv[len(ArrayTypeAdv) - 1]
        MinorLowIndex01   =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]
        MinorLowType01    =  ArrayTypeAdv[len(ArrayTypeAdv) - 1]
        LastmHL           =  ArrayIndexAdv[len(ArrayTypeAdv) - 1]

    #One to the Last Pivot Data
if len(ArrayTypeAdv) > 1:
        #Major
    if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'MHH':
        MajorHighValue02   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
        MajorHighIndex02   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
        MajorHighType02    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'MLH':
        MajorHighValue02   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
        MajorHighIndex02   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
        MajorHighType02    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'MLL':
        MajorLowValue02   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
        MajorLowIndex02   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
        MajorLowType02    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'MHL':
        MajorLowValue02   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
        MajorLowIndex02   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
        MajorLowType02    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    
        #Minor
    if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'mHH':
        MinorHighValue02   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
        MinorHighIndex02   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
        MinorHighType02    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'mLH':
        MinorHighValue02   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
        MinorHighIndex02   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
        MinorHighType02    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'mLL':
        MinorLowValue02   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
        MinorLowIndex02   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
        MinorLowType02    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'mHL':
        MinorLowValue02   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
        MinorLowIndex02   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
        MinorLowType02    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

        # Change Pivot Type to Major
    if ArrayTypeAdv[len(ArrayTypeAdv)-2) != ArrayTypeAdv.get(len(ArrayTypeAdv)-2][1] // Change Pivot Type to Major:
        #Major
        if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'MHH':
            MajorHighValue02Ch   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
            MajorHighIndex02Ch   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
            MajorHighType02Ch    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

        if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'MLH':
            MajorHighValue02Ch   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
            MajorHighIndex02Ch   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
            MajorHighType02Ch    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

        if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'MLL':
            MajorLowValue02Ch   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
            MajorLowIndex02Ch   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
            MajorLowType02Ch    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

        if  ArrayTypeAdv[len(ArrayTypeAdv) - 2] ==  'MHL':
            MajorLowValue02Ch   =  ArrayValueAdv[len(ArrayTypeAdv) - 2]
            MajorLowIndex02Ch   =  ArrayIndexAdv[len(ArrayTypeAdv) - 2]
            MajorLowType02Ch    =  ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    # Detecte Minor level

if len(ArrayTypeAdv) > 2  :
    LockDetecteM_MinorLvL = 1
    if str.pos(ArrayTypeAdv[len(ArrayTypeAdv) - 1),'m'] == 0 and:
     str.pos(ArrayTypeAdv[len(ArrayTypeAdv) - 2),'m'] == 0   and
     str.pos(ArrayTypeAdv[len(ArrayTypeAdv) - 3),'M'] == 0
        if str.pos(ArrayTypeAdv[len(ArrayTypeAdv) - 1),'H'] == 2:
            Minor_HighLevel = ArrayValueAdv[len(ArrayTypeAdv) - 1]
            Minor_LowLevel  = ArrayValueAdv[len(ArrayTypeAdv) - 2]
            Minor_HighIndex = ArrayIndexAdv[len(ArrayTypeAdv) - 1]
            Minor_LowIndex  = ArrayIndexAdv[len(ArrayTypeAdv) - 2]
            Minor_HighType  = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
            Minor_LowType   = ArrayTypeAdv[len(ArrayTypeAdv) - 2]
        elif str.pos(ArrayTypeAdv[len(ArrayTypeAdv) - 1),'L'] == 2:
            Minor_HighLevel = ArrayValueAdv[len(ArrayTypeAdv) - 2]
            Minor_LowLevel  = ArrayValueAdv[len(ArrayTypeAdv) - 1] 
            Minor_HighIndex = ArrayIndexAdv[len(ArrayTypeAdv) - 2]
            Minor_LowIndex  = ArrayIndexAdv[len(ArrayTypeAdv) - 1]
            Minor_HighType  = ArrayTypeAdv[len(ArrayTypeAdv) - 2]
            Minor_LowType   = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
    if LockDetecteM_MinorLvL == 1:
        #High Minor Detector
        if close > Minor_HighLevel:

            if ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mHL'     :
                Minor_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
                Minor_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
                Minor_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1] 
            elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mLL':
                Minor_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
                Minor_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
                Minor_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
            elif ArrayTypeAdv[len(ArrayTypeAdv) - 1) == 'mLH' or ArrayTypeAdv.get(len(ArrayTypeAdv) - 1] == 'mHH':
                if ArrayTypeAdv[len(ArrayTypeAdv) - 2] == 'mHL'     :
                    Minor_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                    Minor_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                    Minor_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]
                elif ArrayTypeAdv[len(ArrayTypeAdv) - 2] == 'mLL':
                    Minor_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                    Minor_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                    Minor_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]
                    

        if  ArrayValueAdv[len(ArrayValueAdv) - 1] > Minor_HighLevel:

            if ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mLH' :
                Minor_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
                Minor_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
                Minor_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1] 
                Minor_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                Minor_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                Minor_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]                    
            elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mHH':
                Minor_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
                Minor_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
                Minor_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
                Minor_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                Minor_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                Minor_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]

        #Low Minor Detector
        if close < Minor_LowLevel:

            if ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mLH'     :
                Minor_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
                Minor_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
                Minor_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
            elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mHH':
                Minor_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
                Minor_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
                Minor_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
            elif ArrayTypeAdv[len(ArrayTypeAdv) - 1) == 'mHL' or ArrayTypeAdv.get(len(ArrayTypeAdv) - 1] == 'mLL':
                if ArrayTypeAdv[len(ArrayTypeAdv) - 2] == 'mLH'     :
                    Minor_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                    Minor_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                    Minor_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]
                elif ArrayTypeAdv[len(ArrayTypeAdv) - 2] == 'mHH':
                    Minor_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                    Minor_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                    Minor_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]

        if ArrayValueAdv[len(ArrayValueAdv) - 1] < Minor_LowLevel:
            if ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mHL' :
                Minor_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
                Minor_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
                Minor_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
                Minor_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                Minor_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                Minor_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]
            elif ArrayTypeAdv[len(ArrayTypeAdv) - 1] == 'mLL' :
                Minor_LowLevel = ArrayValueAdv[len(ArrayValueAdv) - 1]
                Minor_LowIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 1]
                Minor_LowType = ArrayTypeAdv[len(ArrayTypeAdv) - 1]
                Minor_HighLevel = ArrayValueAdv[len(ArrayValueAdv) - 2]
                Minor_HighIndex = ArrayIndexAdv[len(ArrayIndexAdv) - 2]
                Minor_HighType = ArrayTypeAdv[len(ArrayTypeAdv) - 2]

    #Reset Minor Levels
    if str.pos(ArrayTypeAdv[len(ArrayTypeAdv) - 1),'M'] == 0:
        LockDetecteM_MinorLvL = 0
        Minor_HighLevel = na
        Minor_LowLevel  = na
        Minor_HighIndex = na
        Minor_LowIndex  = na
        Minor_HighType  = na
        Minor_LowType   = na
        InternalTrend   = 'No Trend'


    #ChoCh and BoS Detector
        #Bos and ChoCh Line
            #Major

if  ta.crossover(close , Major_HighLevel) and  LockBreak_M != Major_HighIndex // Bullish BoS Detector:
    if (ExternalTrend == 'No Trend' or ExternalTrend == 'Up Trend'):
        Bullish_Major_BoS = true
        BoS_MajorType.push('Bull Major BoS')
        BoS_MajorIndex.push(bar_index)
        LockBreak_M = Major_HighIndex
        ExternalTrend = 'Up Trend'
        if MajorBuBoSLine_Show == 'On':
            MajorLine_BoSBull     = line.new(Major_HighIndex, Major_HighLevel , bar_index , Major_HighLevel , style = MajorBuBoSLine_Style , color = MajorBuBoSLine_Color)
            MajorLabel_BoSBull    = label.new((Major_HighIndex + bar_index) / 2 , Major_HighLevel   , 
             text = 'Major BoS' , color = Color.rgb(0,0,0,100), textcolor = color.black ,size = size.normal )
    elif ExternalTrend == 'Down Trend' // Bullish ChoCh Detector:
        Bullish_Major_ChoCh = true
        ChoCh_MajorType.push('Bull Major ChoCh')
        ChoCh_MajorIndex.push(bar_index)
        LockBreak_M = Major_HighIndex
        ExternalTrend = 'Up Trend'
        if MajorBuChoChLine_Show == 'On':
            MajorLine_ChoChBull    = line.new(Major_HighIndex, Major_HighLevel , bar_index , Major_HighLevel , style = MajorBuChoChLine_Style , color = MajorBuChoChLine_Color)
            MajorLabel_ChoChBull   = label.new((Major_HighIndex + bar_index) / 2 , Major_HighLevel   , 
             text = 'Major ChoCh' , color = Color.rgb(0,0,0,100), textcolor = color.black ,size = size.normal )
else:
    Bullish_Major_ChoCh = false
    Bullish_Major_BoS   = false 


if  ta.crossunder(close, Major_LowLevel) and  LockBreak_M!= Major_LowIndex // Bearish BoS Detector:
    if ExternalTrend == 'No Trend' or ExternalTrend == 'Down Trend':
        Bearish_Major_BoS = true
        BoS_MajorType.push('Bear Major BoS')
        BoS_MajorIndex.push(bar_index)
        LockBreak_M = Major_LowIndex
        ExternalTrend = 'Down Trend'
        if MajorBeBoSLine_Show == 'On':
            MajorLine_BoSBear     = line.new(Major_LowIndex, Major_LowLevel , bar_index , Major_LowLevel , style = MajorBeBoSLine_Style , color = MajorBeBoSLine_Color)
            MajorLabel_BoSBear    = label.new((Major_LowIndex + bar_index) / 2 , Major_LowLevel   , 
             text = 'Major BoS' , color = Color.rgb(0,0,0,100), 
             textcolor = color.black , style = label.style_label_up ,size = size.normal)        
    elif ExternalTrend == 'Up Trend' // Bearish ChoCh Detector:
        Bearish_Major_ChoCh = true
        ChoCh_MajorType.push('Bear Major ChoCh')
        ChoCh_MajorIndex.push(bar_index)
        LockBreak_M = Major_LowIndex
        ExternalTrend = 'Down Trend'
        if MajorBeChoChLine_Show == 'On':
            MajorLine_ChoChBear    = line.new(Major_LowIndex, Major_LowLevel , bar_index , Major_LowLevel , style = MajorBeChoChLine_Style , color = MajorBeChoChLine_Color)
            MajorLabel_ChoChBear   = label.new((Major_LowIndex + bar_index) / 2 , Major_LowLevel   , 
             text = 'Major ChoCh' , color = Color.rgb(0,0,0,100), textcolor = color.black, style = label.style_label_up ,size = size.normal)
else 
    Bearish_Major_ChoCh = false 
    Bearish_Major_BoS   = false 


            #Minor

if  Minor_HighLevel < close  and  LockBreak_m != Minor_HighIndex // Bullish BoS Detector:
    if (InternalTrend == 'No Trend' or InternalTrend == 'Up Trend') :
        Bullish_Minor_BoS   = true
        BoS_MinorType.push('Bull Minor BoS')
        BoS_MinorIndex.push(bar_index)
        LockBreak_m = Minor_HighIndex
        InternalTrend = 'Up Trend'
        if MinorBuBoSLine_Show  == 'On' :
            MinorLine_BoSBull     = line.new(Minor_HighIndex, Minor_HighLevel , bar_index , Minor_HighLevel , style = MinorBuBoSLine_Style , color = MinorBuBoSLine_Color)
            MinorLabel_BoSBull    = label.new((Minor_HighIndex + bar_index) / 2 , Minor_HighLevel   , text = 'Minor BoS' , color = Color.rgb(0,0,0,100), textcolor = color.black ,size = size.tiny )        
    elif InternalTrend == 'Down Trend' // Bullish ChoCh Detector:
        Bullish_Minor_ChoCh = true
        ChoCh_MinorType.push('Bull Minor ChoCh')
        ChoCh_MinorIndex.push(bar_index)
        LockBreak_m = Minor_HighIndex
        InternalTrend = 'Up Trend'
        if MinorBuChoChLine_Show  == 'On'         :
            MinorLine_ChoChBull    = line.new(Minor_HighIndex, Minor_HighLevel , bar_index , Minor_HighLevel , style = MinorBuChoChLine_Style , color = MinorBuChoChLine_Color)
            MinorLabel_ChoChBull   = label.new((Minor_HighIndex + bar_index) / 2 , Minor_HighLevel   , text = 'Minor ChoCh' , color = Color.rgb(0,0,0,100), textcolor = color.black ,size = size.tiny )
else 
    Bullish_Minor_ChoCh = false
    Bullish_Minor_BoS   = false


if  Minor_LowLevel > close and  LockBreak_m!= Minor_LowIndex // Bearish BoS Detector:
    if InternalTrend == 'No Trend' or InternalTrend == 'Down Trend':
        Bearish_Minor_BoS   = true
        BoS_MinorType.push('Bear Minor BoS')
        BoS_MinorIndex.push(bar_index)
        LockBreak_m = Minor_LowIndex
        InternalTrend = 'Down Trend'
        if MinorBeBoSLine_Show  == 'On' :
            MinorLine_BoSBear     = line.new(Minor_LowIndex, Minor_LowLevel , bar_index , Minor_LowLevel , style = MinorBeBoSLine_Style , color = MinorBeBoSLine_Color)
            MinorLabel_BoSBear    = label.new((Minor_LowIndex + bar_index) / 2 , Minor_LowLevel   , text = 'Minor BoS' , color = Color.rgb(0,0,0,100), 
             textcolor = color.black , style = label.style_label_up ,size = size.tiny) 
    elif InternalTrend == 'Up Trend' // Bearish ChoCh Detector:
        Bearish_Minor_ChoCh = true
        ChoCh_MinorType.push('Bear Minor ChoCh')
        ChoCh_MinorIndex.push(bar_index)
        LockBreak_m = Minor_LowIndex
        InternalTrend = 'Down Trend'
        if MinorBeChoChLine_Show  == 'On' :
            MinorLine_ChoChBear    = line.new(Minor_LowIndex, Minor_LowLevel , bar_index , Minor_LowLevel , style = MinorBeChoChLine_Style , color = MinorBeChoChLine_Color)
            MinorLabel_ChoChBear   = label.new((Minor_LowIndex + bar_index) / 2 , Minor_LowLevel   , text = 'Minor ChoCh' , color = Color.rgb(0,0,0,100), 
             textcolor = color.black, style = label.style_label_up ,size = size.tiny)
else:
    Bearish_Minor_ChoCh = false
    Bearish_Minor_BoS   = false
    

    #Support and Resistance Line

    #Drawing Major Resistance Line
if Major_HighIndex != Major_HighIndex[1] and LastMajorResistanceLine_Show == 'On':
    Resistance_LineMajor = line.new(Major_HighIndex,Major_HighLevel , Major_HighIndex + 1 , Major_HighLevel , style = LastMajorResistanceLine_Style ,color = LastMajorResistanceLine_Color)
    line.delete(Resistance_LineMajor[1])

if Major_HighIndex == Major_HighIndex[1] and high < Major_HighLevel:
    line.set_x2(Resistance_LineMajor, bar_index + 1 )
elif Major_HighIndex == Major_HighIndex[1] and high > Major_HighLevel:
    line.delete(Resistance_LineMajor)

#Drawing Major Support Line
if Major_LowIndex != Major_LowIndex[1] and LastMajorSupportLine_Show == 'On':
    Support_LineMajor = line.new(Major_LowIndex,Major_LowLevel , Major_LowIndex + 1 , Major_LowLevel, style = LastMajorSupportLine_Style ,color = LastMajorSupportLine_Color)
    line.delete(Support_LineMajor[1])

if Major_LowIndex == Major_LowIndex[1] and low > Major_LowLevel:
    line.set_x2(Support_LineMajor, bar_index + 1 )
elif Major_LowIndex == Major_LowIndex[1] and low < Major_LowLevel:
    line.delete(Support_LineMajor)


#Drawing Minor Resistance Line
if Minor_HighIndex != Minor_HighIndex[1] and LastMinorResistanceLine_Show == 'On':
    Resistance_LineMinor = line.new(Minor_HighIndex,Minor_HighLevel , Minor_HighIndex + 1 , Minor_HighLevel , style = LastMinorResistanceLine_Style, color = LastMinorResistanceLine_Color )
    line.delete(Resistance_LineMinor[1])

if Minor_HighIndex == Minor_HighIndex[1] and high < Minor_HighLevel:
    line.set_x2(Resistance_LineMinor, bar_index + 1 )
elif Minor_HighIndex == Minor_HighIndex[1] and high > Minor_HighLevel:
    line.delete(Resistance_LineMinor)
elif len(ArrayTypeAdv) > 0:
    if str.pos(ArrayTypeAdv[len(ArrayTypeAdv) - 1),'M'] == 0:
        line.delete(Resistance_LineMinor)


#Drawing Minor Support Line
if Minor_LowIndex != Minor_LowIndex[1] and LastMinorSupportLine_Show == 'On':
    Support_LineMinor = line.new(Minor_LowIndex,Minor_LowLevel , Minor_LowIndex + 1 , Minor_LowLevel , style = LastMinorSupportLine_Style, color = LastMinorSupportLine_Color)
    line.delete(Support_LineMinor[1])

if Minor_LowIndex == Minor_LowIndex[1] and low > Minor_LowLevel:
    line.set_x2(Support_LineMinor, bar_index + 1 )
elif (Minor_LowIndex == Minor_LowIndex[1] and low < Minor_LowLevel):
    line.delete(Support_LineMinor)
elif len(ArrayTypeAdv) > 0:
    if str.pos(ArrayTypeAdv[len(ArrayTypeAdv) - 1),'M'] == 0:
        line.delete(Support_LineMinor)


#Order Block Data
    #Demand Major Main and Sub Order Blocks Data , ChoCh Origin

if len(ArrayIndexAdv) > 4 :
    ChBuLowest = ta.lowest(bar_index - LastMLL)
    for i in range(0, (bar_index - LastMLL) + 1):
        if low[i] > ChBuLowest:
            CorrectBuIndex =  CorrectBuIndex + 1
        else     
            CorrectBuIndex = 0 

    ChBuLowest = ta.lowest(bar_index - LastPivotIndex02)
    for i in range(0, (bar_index - LastPivotIndex02) + 1):
        if low[i] > ChBuLowest:
            CorrectBuIndexSub =  CorrectBuIndexSub + 1
        else     
            CorrectBuIndexSub = 0

if Bullish_Major_ChoCh and len(ArrayIndexAdv) > 2:
    Last02MLL = LastMLL[1]
    if LastPivotType == 'MLL' and low[bar_index - LastMLL] <= ChBuLowest:
        if LastPivotType == LastPivotType[1] :
            BuMChMain_Trigger = true
            BuMChMain_Index     = LastMLL

        elif LastPivotType != LastPivotType[1] //Change Last Pivot from mLL to MLL:
            if low[bar_index - Last02MLL] < low[bar_index - LastMLL]:
                BuMChMain_Trigger = true
                BuMChMain_Index     = Last02MLL               
                BuMChSub_Trigger = true
                BuMChSub_Index     = LastMLL
                
            elif low[bar_index - Last02MLL] > low[bar_index - LastMLL]:
                BuMChMain_Trigger = true
                BuMChMain_Index     = LastMLL
              
    elif LastPivotType == 'MLL' and low[bar_index - LastMLL] > ChBuLowest:
        if LastPivotType == LastPivotType[1] :
            BuMChMain_Trigger = true
            BuMChMain_Index     = LastMLL+ CorrectBuIndex

        elif LastPivotType != LastPivotType[1] //Change Last Pivot from mLL to MLL:
            BuMChMain_Trigger  = true
            BuMChMain_Index     = LastMLL+ CorrectBuIndex
            if LastMHL > LastMLL + CorrectBuIndex:
                BuMChSub_Trigger = true
                BuMChSub_Index     = LastMLL

    elif LastPivotType == 'MHL' and low[bar_index - LastMLL] <= ChBuLowest:
        BuMChMain_Trigger = true
        BuMChMain_Index     = LastMLL
        BuMChSub_Trigger = true
        BuMChSub_Index     = LastMHL
    
    elif LastPivotType == 'MHL' and low[bar_index - LastMLL] > ChBuLowest:
        BuMChMain_Trigger = true
        BuMChMain_Index     = LastMLL + CorrectBuIndex

        if LastMHL > LastMLL + CorrectBuIndex:
            BuMChSub_Trigger = true
            BuMChSub_Index     = LastMHL
 
    elif LastPivotType == 'mHH' or LastPivotType == 'mLH'  or LastPivotType == 'MLH'  or LastPivotType == 'MHH' :
        if low[bar_index - LastMLL] <= ChBuLowest:
            if LastPivotIndex02 == LastMLL:
                BuMChMain_Trigger = true
                BuMChMain_Index     = LastMLL
    
            elif LastPivotIndex02 > LastMLL:
                BuMChMain_Trigger = true
                BuMChMain_Index     = LastMLL
                if low[bar_index - LastPivotIndex02] <= ChBuLowestSub:
                    BuMChSub_Trigger = true
                    BuMChSub_Index     = LastPivotIndex02  
                elif   low[bar_index - LastPivotIndex02] > ChBuLowestSub       :
                    BuMChSub_Trigger = true
                    BuMChSub_Index     = LastPivotIndex02 +  CorrectBuIndexSub       
            elif LastPivotIndex02 < LastMLL:
                BuMChMain_Trigger = true
                BuMChMain_Index     = LastMLL

        elif  low[bar_index - LastMLL] > ChBuLowest:
            BuMChMain_Trigger   = true
            BuMChMain_Index     = LastMLL  + CorrectBuIndex
else:
    BuMChMain_Trigger = false
    BuMChSub_Trigger  = false


    #Demand Major Order Blocks Data ,BoS Origin

if len(ArrayIndexAdv) > 10 :
    BoSBuLowest = ta.lowest(bar_index - LastPivotIndex)
    for i in range(0, (bar_index - LastPivotIndex) + 1):
        if low[i] > BoSBuLowest:
            CorrectBuBoSIndex =  CorrectBuBoSIndex + 1
        else     
            CorrectBuBoSIndex = 0 

if len(ArrayIndexAdv) > 10:
    BoSBuLowest02 = ta.lowest(bar_index - LastPivotIndex02)
    for i in range(0, (bar_index - LastPivotIndex02) + 1):
        if low[i] > BoSBuLowest02:
            CorrectBuBoSIndex02 =  CorrectBuBoSIndex02 + 1
        else     
            CorrectBuBoSIndex02 = 0 


if Bullish_Major_BoS and len(ArrayIndexAdv) > 2 :

    if (LastPivotType == 'MHL' or LastPivotType == 'mHL' or :
         LastPivotType == 'MLL' or LastPivotType == 'mLL') and low[bar_index - LastPivotIndex] <= BoSBuLowest

        BuMBoS_Trigger = true
        BuMBoS_Index   = LastPivotIndex 

    if (LastPivotType == 'MHL' or LastPivotType == 'mHL' or :
         LastPivotType == 'MLL' or LastPivotType == 'mLL') and low[bar_index - LastPivotIndex] > BoSBuLowest

        BuMBoS_Trigger = true
        BuMBoS_Index   = LastPivotIndex + CorrectBuBoSIndex    

    if (LastPivotType == 'mHH' or LastPivotType == 'mLH' or :
     LastPivotType == 'MHH' or LastPivotType == 'MLH') and low[bar_index - LastPivotIndex02] <= BoSBuLowest02

        BuMBoS_Trigger = true
        BuMBoS_Index   = LastPivotIndex02

    if (LastPivotType == 'mHH' or LastPivotType == 'mLH' or :
     LastPivotType == 'MHH' or LastPivotType == 'MLH') and low[bar_index - LastPivotIndex02] > BoSBuLowest02

        BuMBoS_Trigger = true
        BuMBoS_Index   = LastPivotIndex02 + CorrectBuBoSIndex02

else:
    BuMBoS_Trigger = false


    #Supply Major Main and Sub Order Blocks Data , ChoCh Origin

if len(ArrayIndexAdv) > 4 :
    ChBeHighest = ta.highest(bar_index - LastMHH)
    for i in range(0, (bar_index - LastMHH) + 1):
        if high[i] < ChBeHighest:
            CorrectBeIndex =  CorrectBeIndex + 1
        else     
            CorrectBeIndex = 0 

    ChBeHighestSub = ta.highest(bar_index - LastPivotIndex02)
    for i in range(0, (bar_index - LastPivotIndex02) + 1):
        if high[i] < ChBeHighestSub:
            CorrectBeIndexSub =  CorrectBeIndexSub + 1
        else     
            CorrectBeIndexSub = 0 


if Bearish_Major_ChoCh and len(ArrayIndexAdv) > 2:
    Last02MHH = LastMHH[1]
    if LastPivotType == 'MHH' and high[bar_index - LastMHH] >= ChBeHighest:
        if LastPivotType == LastPivotType[1]:
            BeMChMain_Trigger =  true
            BeMChMain_Index   =  LastMHH

        elif LastPivotType != LastPivotType[1] //Change Last Pivot from MHH to MHH:
            if high[bar_index - Last02MHH] > high[bar_index - LastMHH]:
                BeMChMain_Trigger = true
                BeMChMain_Index   = Last02MHH
                BeMChSub_Trigger  = true
                BeMChSub_Index    = LastMHH

            elif high[bar_index - Last02MHH] < high[bar_index - LastMHH]:
                BeMChMain_Trigger =  true
                BeMChMain_Index   =  LastMHH

    elif LastPivotType == 'MHH' and high[bar_index - LastMHH] < ChBeHighest:
        if LastPivotType == LastPivotType[1] :
            BeMChMain_Trigger =  true
            BeMChMain_Index   =  LastMHH + CorrectBeIndex

        elif LastPivotType != LastPivotType[1] //Change Last Pivot from MHH to MHH:
            BeMChMain_Trigger =  true
            BeMChMain_Index   =  LastMHH + CorrectBeIndex
            if  LastMLH > LastMHH + CorrectBuIndex:
                BeMChSub_Trigger  = true
                BeMChSub_Index    = LastMHH


    elif LastPivotType == 'MLH' and  high[bar_index - LastMHH] >= ChBeHighest:
        
        BeMChMain_Trigger =  true
        BeMChMain_Index   =  LastMHH
        BeMChSub_Trigger  =  true
        BeMChSub_Index    =  LastMLH

    elif LastPivotType == 'MLH' and high[bar_index - LastMHH] < ChBeHighest:
        BeMChMain_Trigger =  true
        BeMChMain_Index   =  LastMHH + CorrectBeIndex

        if LastMLH > LastMHH + CorrectBeIndex:
            BeMChSub_Trigger  = true
            BeMChSub_Index    = LastMLH

    elif LastPivotType == 'mLL' or LastPivotType == 'mHL' or LastPivotType == 'MHL' or  LastPivotType == 'MLL':
        if high[bar_index - LastMHH] >= ChBeHighest:
            if LastPivotIndex02 == LastMHH:
                BeMChMain_Trigger =  true
                BeMChMain_Index   =  LastMHH
    
            elif LastPivotIndex02 > LastMHH:
                BeMChMain_Trigger  =  true
                BeMChMain_Index   =  LastMHH
                if high[bar_index -  LastPivotIndex02] >= ChBeHighestSub:
                    BeMChSub_Trigger  = true
                    BeMChSub_Index    = LastPivotIndex02
                elif high[bar_index - LastPivotIndex02] < ChBeHighestSub:
                    BeMChSub_Trigger  = true
                    BeMChSub_Index    = LastPivotIndex02 + CorrectBeIndexSub            

            elif LastPivotIndex02 < LastMHH:
                BeMChMain_Trigger =  true
                BeMChMain_Index   =  LastMHH
        elif high[bar_index - LastMHH] < ChBeHighest:
            BeMChMain_Trigger =  true
            BeMChMain_Index   =  LastMHH + CorrectBeIndex
else 
    BeMChMain_Trigger =  false
    BeMChSub_Trigger  =  false


    #Supply Major Order Blocks Data , BoS Origin

if len(ArrayIndexAdv) > 10 :
    BoSBeHighest = ta.highest(bar_index - LastPivotIndex)
    for i in range(0, (bar_index - LastPivotIndex) + 1):
        if high[i] < BoSBeHighest:
            CorrectBeBoSIndex =  CorrectBeBoSIndex + 1
        else     
            CorrectBeBoSIndex = 0 

if len(ArrayIndexAdv) > 10 :
    BoSBeHighest02 = ta.highest(bar_index - LastPivotIndex02)
    for i in range(0, (bar_index - LastPivotIndex02) + 1):
        if high[i] < BoSBeHighest02:
            CorrectBeBoSIndex02 =  CorrectBeBoSIndex02 + 1
        else     
            CorrectBeBoSIndex02 = 0 

if Bearish_Major_BoS and len(ArrayIndexAdv) > 2  :

    if (LastPivotType == 'mLH' or LastPivotType == 'mHH' or :
         LastPivotType == 'MLH' or LastPivotType == 'MHH') and high[bar_index - LastPivotIndex] >= BoSBeHighest
        BeMBoS_Trigger = true
        BeMBoS_Index    = LastPivotIndex
    
    if (LastPivotType == 'mLH' or LastPivotType == 'mHH' or :
         LastPivotType == 'MLH' or LastPivotType == 'MHH') and high[bar_index - LastPivotIndex] < BoSBeHighest
        BeMBoS_Trigger = true
        BeMBoS_Index     = LastPivotIndex + CorrectBeBoSIndex

    if (LastPivotType == 'mLL' or LastPivotType == 'mHL' or :
     LastPivotType == 'MLL' or LastPivotType == 'MHL') and high[bar_index - LastPivotIndex02] >= BoSBeHighest02
        BeMBoS_Trigger = true
        BeMBoS_Index     = LastPivotIndex02

    if (LastPivotType == 'mLL' or LastPivotType == 'mHL' or :
     LastPivotType == 'MLL' or LastPivotType == 'MHL') and high[bar_index - LastPivotIndex02] < BoSBeHighest02
        BeMBoS_Trigger = true
        BeMBoS_Index     = LastPivotIndex02 + CorrectBeBoSIndex02

else 
    BeMBoS_Trigger = false


#//////////////////////////////////////////////////
#/////////////Order Block Refinement///////////////
#//////////////////////////////////////////////////

    #Demand
        #Demand Main Zone, ChoCh Origin
[BuMChMain_Xd1, BuMChMain_Xd2, BuMChMain_Yd12, BuMChMain_Xp1, BuMChMain_Xp2, BuMChMain_Yp12] = 
 ('On' if Refiner.OBRefiner('Demand', RefineDmainCh else 'Off', RefineMeDmainCh ,BuMChMain_Trigger,  BuMChMain_Index))
        #Demand Sub Zone, ChoCh Origin
[BuMChSub_Xd1 , BuMChSub_Xd2 ,  BuMChSub_Yd12, BuMChSub_Xp1 , BuMChSub_Xp2 , BuMChSub_Yp12] = 
 ('On' if Refiner.OBRefiner('Demand', RefineDsubCh else 'Off', RefineMeDsubCh ,BuMChSub_Trigger,  BuMChSub_Index))
        #Demand All Zone, BoS Origin
[BuMBoS_Xd1, BuMBoS_Xd2, BuMBoS_Yd12, BuMBoS_Xp1, BuMBoS_Xp2, BuMBoS_Yp12] = 
 ('On' if Refiner.OBRefiner('Demand', RefineDBoS else 'Off', RefineMeDBoS,BuMBoS_Trigger, BuMBoS_Index))

    #Supply
        #Supply Main Zone, ChoCh Origin    
[BeMChMain_Xd1, BeMChMain_Xd2, BeMChMain_Yd12, BeMChMain_Xp1, BeMChMain_Xp2, BeMChMain_Yp12] = 
 ('On' if Refiner.OBRefiner('Supply', RefineSmainCh else 'Off', RefineMeSmainCh ,BeMChMain_Trigger,  BeMChMain_Index))
        #Supply Sub Zone, ChoCh Origin
[BeMChSub_Xd1 , BeMChSub_Xd2 ,  BeMChSub_Yd12, BeMChSub_Xp1 , BeMChSub_Xp2 , BeMChSub_Yp12] = 
 ('On' if Refiner.OBRefiner('Supply', RefineSsubCh else 'Off', RefineMeSsubCh ,BeMChSub_Trigger,  BeMChSub_Index))
        #Supply All Zone, BoS Origin
[BeMBoS_Xd1, BeMBoS_Xd2, BeMBoS_Yd12, BeMBoS_Xp1, BeMBoS_Xp2, BeMBoS_Yp12] = 
 ('On' if Refiner.OBRefiner('Supply', RefineSBoS else 'Off', RefineMeSBoS,BeMBoS_Trigger, BeMBoS_Index))


#///////////////////////////////////
#/////////////Drawing///////////////
#///////////////////////////////////

        #OUTPUT ==> Alert Trigger
[Alert_DMMM] = Drawing.OBDrawing('Demand', BuMChMain_Trigger ,BuMChMain_Yd12, BuMChMain_Yp12 ,BuMChMain_Xd1 , OBVaP  , ShowDmainCh, ColorDmainCh)
[Alert_DSMM] = Drawing.OBDrawing('Demand', BuMChSub_Trigger  ,BuMChSub_Yd12 , BuMChSub_Yp12  ,BuMChSub_Xd1  , OBVaP  , ShowDsubCh , ColorDsubCh)
[Alert_DAMM] = Drawing.OBDrawing('Demand', BuMBoS_Trigger    , BuMBoS_Yd12  , BuMBoS_Yp12    , BuMBoS_Xd1   , OBVaP  , ShowDBoS   , ColorDBoS )

[Alert_SMMM] = Drawing.OBDrawing('Supply', BeMChMain_Trigger ,BeMChMain_Yd12, BeMChMain_Yp12 ,BeMChMain_Xd1, OBVaP   , ShowSmainCh, ColorSmainCh)
[Alert_SSMM] = Drawing.OBDrawing('Supply', BeMChSub_Trigger  ,BeMChSub_Yd12 , BeMChSub_Yp12  ,BeMChSub_Xd1 , OBVaP   , ShowSsubCh , ColorSsubCh)
[Alert_SAMM] = Drawing.OBDrawing('Supply', BeMBoS_Trigger    , BeMBoS_Yd12  , BeMBoS_Yp12    ,BeMBoS_Xd1   , OBVaP   , ShowSBoS   , ColorSBoS )
 
#///////////////////////////////
#/////////////FVG///////////////
#///////////////////////////////

('On' if FVG.FVGDetector(PFVGFilter else 'Off' , PFVGFilterType, PShowDeFVG, PShowSuFVG))


#/////////////////////////////////////
#/////////////Liquidity///////////////
#/////////////////////////////////////

Liq.LLF(SPP,DPP,SLLS,DLLS,ShowSHLL,ShowSLLL,ShowDHLL,ShowDLLL)

#/////////////////////////////////
#/////////////Alert///////////////
#/////////////////////////////////

Alert.AlertSender(Alert_DMMM  , Alert_DMM, AlertName, 'Bullish', 'Order Block Signal', 'Full' ,Frequncy, UTC, MoreInfo, MessageBull_DMM, open, high, low, close,0,0,0, BuMChMain_Yd12 , BuMChMain_Yp12)
Alert.AlertSender(Alert_DSMM  , Alert_DSM, AlertName, 'Bullish', 'Order Block Signal', 'Full' ,Frequncy, UTC, MoreInfo, MessageBull_DSM, open, high, low, close,0,0,0, BuMChSub_Yd12  , BuMChSub_Yp12)
Alert.AlertSender(Alert_DAMM  , Alert_DAM, AlertName, 'Bullish', 'Order Block Signal', 'Full' ,Frequncy, UTC, MoreInfo, MessageBull_DAM, open, high, low, close,0,0,0, BuMBoS_Yd12    , BuMBoS_Yp12)

Alert.AlertSender(Alert_SMMM  , Alert_SMM, AlertName, 'Bearish', 'Order Block Signal', 'Full' ,Frequncy, UTC, MoreInfo, MessageBear_SMM, open, high, low, close,0,0,0, BeMChMain_Yd12 , BeMChMain_Yp12)
Alert.AlertSender(Alert_SSMM  , Alert_SSM, AlertName, 'Bearish', 'Order Block Signal', 'Full' ,Frequncy, UTC, MoreInfo, MessageBear_SSM, open, high, low, close,0,0,0, BeMChSub_Yd12  , BeMChSub_Yp12)
Alert.AlertSender(Alert_SAMM  , Alert_SAM, AlertName, 'Bearish', 'Order Block Signal', 'Full' ,Frequncy, UTC, MoreInfo, MessageBear_SAM, open, high, low, close,0,0,0, BeMBoS_Yd12    , BeMBoS_Yp12)