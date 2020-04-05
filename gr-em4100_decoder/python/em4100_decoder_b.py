#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2020 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr

class em4100_decoder_b(gr.sync_block):
    """
    docstring for block em4100_decoder_b
    """

    def print_decode_result(self):
        
        id_long = 0 #:long
        id_nib = 0
        lrc = 0
        vrc = 0
        
        for i in range(55-1):     #40bit分の結果格納とパリティチェック
            if (i+1) % 5 == 0:
                if lrc != self.dec_bit[i] :
                    print "LRC NG " + str((i+1)/5)
                lrc = 0
                vrc ^= id_nib
                id_long *= 16       # 4bit shift
                id_long += id_nib
                id_nib = 0
            else:
                lrc ^= self.dec_bit[i]
                #id_long *= 2     
                #id_long += self.dec_bit[i]
                id_nib *= 2     # bit_shift left
                id_nib += self.dec_bit[i]
        if id_nib != vrc :
            print "VRC NG " ,
        if self.dec_bit[54] != 0:
            print "STOP_BIT NG " ,
        
        #To Do LRC, VRC, Stop Bit all OKって出したいよね
        print "\nID:" ,
        print hex(id_long) 

        print "\nRaw bit :" ,
        for i in range(55):
            print str(self.dec_bit[i]) + "," , #中身を表示
            self.dec_bit[i] = 0                     #ついでに初期化
        print ("\n")
        
    '''--------------------------------------------------'''
    def em4100_decoder(self, input_sample) :
        self.clock_counter += 1
        if self.clock_counter < self.clock_quarte_position * 3 :
            pass
        elif self.clock_counter == self.clock_quarte_position * 3 :
            self.last_dec_bit = input_sample
            #非同期
            if self.sync_counter < self.bit_sync_num :
                if input_sample == 1 :              # high current = Low -> H なので3/4 symbole = 1
                    self.sync_counter +=1
                else:
                    self.sync_counter = 0   #同期外れ
            #同期中
            else:
                self.dec_bit[self.dec_counter] = input_sample     # high current = Low -> H なので3/4 symbole = 1
                self.dec_counter += 1
                if self.dec_counter == 55:      #規定のビット数デコードし終わった
                    self.print_decode_result()
                    self.sync_counter = 0
                    self.dec_counter = 0
        else :
            if self.last_dec_bit != input_sample:   
                if self.clock_counter > self.clock_quarte_position *  5 :    #間違っている方に同期してしまっている。ほぼclock_counter = 32
                    self.sync_counter = 0
                    self.dec_counter = 0
                self.clock_counter = 0          #いずれにせよ、クロックのリセット

        if self.clock_counter > self.clock_quarte_position *  5:
            #クロックが来なかったら初期化
            #print "time out"
            self.clock_counter = 0
            self.dec_counter = 0
            self.sync_counter = 0
            


    def __init__(self, sample_per_bit, bit_sync_num):
        gr.sync_block.__init__(self,
            name="em4100_decoder_b",
            in_sig=[numpy.int8],
            out_sig=None)
        self.clock_counter = 0
        self.dec_counter = 0
        self.sync_counter = 0
        self.last_dec_bit = 0
        self.dec_bit = [0] * 55
        self.bit_sync_num = bit_sync_num
        self.lrc = 0
        self.clock_quarte_position = int(sample_per_bit/4)

    def work(self, input_items, output_items):
        in0 = input_items[0]
        for input_sample in in0:
            self.em4100_decoder(input_sample)
        return len(input_items[0])

