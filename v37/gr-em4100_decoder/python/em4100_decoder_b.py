#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2020 <7M4MON>.
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

''' EM4100 という RFIDタグの通信波形をデコードするGRCブロック '''
''' 2020.Apr.4 7M4MON '''

class em4100_decoder_b(gr.sync_block):
    
    ''' デコード結果を表示する関数 '''
    def print_decode_result(self):
        
        id_long = 0         # 最終的にデコードした40bitのID
        id_nib = 0          # 4ビットずつ処理するための変数
        lrc = 0             # 水平パリティ
        vrc = 0             # 垂直パリティ
        
        for i in range(55-1):       # 40bit分の結果格納とパリティチェック
            if (i+1) % 5 == 0:      # 5ビット分のデータを処理する
                if lrc != self.dec_bit[i] :
                    print "LRC NG " + str((i+1)/5)
                lrc = 0             # 次の行に備えて水平パリティをクリア
                vrc ^= id_nib       # EXORをとって垂直パリティを計算していく
                id_long *= 16       # 左に4ビットシフト
                id_long += id_nib   # LSBにIDを4ビット分追記
                id_nib = 0          # 次の行に備えて4ビット分のIDをクリア
            else:
                lrc ^= self.dec_bit[i]      # 1ビットずつEXORをとって水平パリティを計算していく
                id_nib *= 2                 # 左に1ビットシフト
                id_nib += self.dec_bit[i]   # LSBに1ビット追記
                
        if id_nib != vrc :                  # 垂直パリティを検査
            print "VRC NG " ,
        if self.dec_bit[54] != 0:           # ストップビットを確認
            print "STOP_BIT NG " ,
            
        print "\nID:" ,                     # IDを表示
        print hex(id_long) 

        print "\nRaw bit :" ,
        for i in range(55):
            print str(self.dec_bit[i]) + "," ,      # デバッグ用に中身を表示
            self.dec_bit[i] = 0                     # 終了時に初期化
        print ("\n")
        
        
    ''' EM4100 デコーダ本体 '''
    def em4100_decoder(self, input_sample) :
        self.clock_counter += 1
        if self.clock_counter < self.clock_quarte_position * 3 :    # 前回のエッジから 192us (3/4 cycle)までは何もしない
            pass
        elif self.clock_counter == self.clock_quarte_position * 3 : # 取り込みポイントに到達した
            self.last_dec_bit = input_sample                        # 1ビット取り込む
            #非同期
            if self.sync_counter < self.bit_sync_num :              # 非同期のときは1が連続するのを待つ
                if input_sample == 1 :                              
                    self.sync_counter +=1                           # 1が連続している数をインクリメント
                else:
                    self.sync_counter = 0                           # 1が連続していないので同期外れ
            #同期中
            else:
                self.dec_bit[self.dec_counter] = input_sample       # 1ビット取り込む
                self.dec_counter += 1
                if self.dec_counter == 55:                          # 規定のビット数デコードし終わった
                    self.print_decode_result()                      # 結果を表示してリセット
                    self.sync_counter = 0
                    self.dec_counter = 0
        else :
            if self.last_dec_bit != input_sample:                   # クロックエッジの検出
                if self.clock_counter > self.clock_quarte_position *  5 :   # 前回のクロックエッジから1.25周期以上クロックが来ないということは
                                                                            # 間違った方に同期してしまっている
                    self.sync_counter = 0                           # 今までのデータを捨ててやり直し。
                    self.dec_counter = 0
                self.clock_counter = 0                              # クロックを同期を最新のエッジで更新

        if self.clock_counter > self.clock_quarte_position *  5:    # 1.25周期以上クロックが来なかったら初期化
            self.clock_counter = 0
            self.dec_counter = 0
            self.sync_counter = 0
            

    ''' 初期化関数 '''
    def __init__(self, sample_per_bit, bit_sync_num):
        gr.sync_block.__init__(self,
            name="em4100_decoder_b",
            in_sig=[numpy.int8],
            out_sig=None)
        self.clock_counter = 0
        self.dec_counter = 0
        self.sync_counter = 0
        self.last_dec_bit = 0
        self.dec_bit = [0] * 55                             # 64bitのうち、9ビットはヘッダなので 64-9 = 55
        self.bit_sync_num = bit_sync_num
        self.lrc = 0
        self.clock_quarte_position = int(sample_per_bit/4)

    ''' 実行中の処理 '''
    def work(self, input_items, output_items):
        in0 = input_items[0]
        for input_sample in in0:
            self.em4100_decoder(input_sample)               # 入力されたビットストリームを1ビットずつデコーダに入力
        return len(input_items[0])

