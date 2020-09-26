# gr-em4100_decoder  
This is GRC (GNU Radio Conpanion) block for EM4100 (125kHz) RFID Cards.

## Flow graph  
![](https://github.com/7m4mon/gr-em4100_decoder/blob/master/EM4100_decoder.grc.png)

## Decoded result  
![](https://github.com/7m4mon/gr-em4100_decoder/blob/master/sc_gr-em4100_decoder.png)

## How to use  
1. Record RFID communication signals with AnalogDiscovery2 and Waveforms.  
![](https://github.com/7m4mon/gr-em4100_decoder/blob/master/em4100-ad2-reading.jpg)  
* Scope Mode @ 1Msps 
1. Export waveform as csv file.  
![](https://github.com/7m4mon/gr-em4100_decoder/blob/master/record_and_export_waveform.png)  
1. Convert csv file to IEEE754 single precision floating point binary file with [csv_to_ieee754_converter](https://github.com/7m4mon/convert_csv_to_ieee754).
1. Use this decoder block. The result ID is shown to std out.

