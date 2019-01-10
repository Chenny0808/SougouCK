# _*_ encoding: utf-8 _*_
"""
 @File Name: convert
 @Author:    Chenny
 @email:     15927299723@163.com
 @date:      2018/12/11
 @software:  PyCharm
"""

import struct
import os


# 由于原代码不适用python3且有大量bug
# 以及有函数没有必要使用且一些代码书写不太规范或冗余
# 所以本人在原有的大框架基本不动的情况下作了大量的细节更改。
# 使得没有乱码出现，文件夹导入更方便等等。
# Author：Ling Yue, Taiyuan U of Tech
# Blog: http://blog.yueling.me


# 原作者：
# 搜狗的scel词库就是保存的文本的unicode编码，每两个字节一个字符（中文汉字或者英文字母）
# 找出其每部分的偏移位置即可
# 主要两部分
# 1.全局拼音表，貌似是所有的拼音组合，字典序
#       格式为(index,len,pinyin)的列表
#       index: 两个字节的整数 代表这个拼音的索引
#       len: 两个字节的整数 拼音的字节长度
#       pinyin: 当前的拼音，每个字符两个字节，总长len
#
# 2.汉语词组表
#       格式为(same,py_table_len,py_table,{word_len,word,ext_len,ext})的一个列表
#       same: 两个字节 整数 同音词数量
#       py_table_len:  两个字节 整数
#       py_table: 整数列表，每个整数两个字节,每个整数代表一个拼音的索引
#
#       word_len:两个字节 整数 代表中文词组字节数长度
#       word: 中文词组,每个中文汉字两个字节，总长度word_len
#       ext_len: 两个字节 整数 代表扩展信息的长度，好像都是10
#       ext: 扩展信息 前两个字节是一个整数(不知道是不是词频) 后八个字节全是0
#
#      {word_len,word,ext_len,ext} 一共重复same次 同音词 相同拼音表

class Converter(object):
    def __init__(self):
        # 拼音表偏移
        self.startPy = 0x1540
        # 汉语词组表偏移
        self.startChinese = 0x2628
        # 全局拼音表
        self.GPy_Table = {}
        # 解析结果: 元组(词频,拼音,中文词组)的列表
        self.GTable = []

    # 原始字节码转为字符串
    def byte2str(self, data):
        pos = 0
        str = ''
        while pos < len(data):
            c = chr(struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0])
            if c != chr(0):
                str += c
            pos += 2
        return str

    # 获取拼音表
    def get_pyTable(self, data):
        data = data[4:]
        pos = 0
        while pos < len(data):
            index = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
            pos += 2
            lenPy = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
            pos += 2
            py = self.byte2str(data[pos:pos + lenPy])
            self.GPy_Table[index] = py
            pos += lenPy

    # 获取一个词组的拼音
    def get_wordPy(self, data):
        pos = 0
        ret = ''
        while pos < len(data):
            index = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
            ret += self.GPy_Table[index]
            pos += 2
        return ret

    # 读取中文表
    def get_chinese(self, data):
        pos = 0
        while pos < len(data):
            # 同音词数量
            same = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]

            # 拼音索引表长度
            pos += 2
            py_table_len = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]

            # 拼音索引表
            pos += 2
            py = self.get_wordPy(data[pos: pos + py_table_len])

            # 中文词组
            pos += py_table_len
            for i in range(same):
                # 中文词组长度
                c_len = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
                # 中文词组
                pos += 2
                word = self.byte2str(data[pos: pos + c_len])
                # 扩展数据长度
                pos += c_len
                ext_len = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
                # 词频
                pos += 2
                count = struct.unpack('H', bytes([data[pos], data[pos + 1]]))[0]
                # 保存
                self.GTable.append((count, py, word))
                # 到下个词的偏移位置
                pos += ext_len

    def scel2txt(self, file_name, out_name):
        # print('-' * 60)
        with open(file_name, 'rb') as f:
            data = f.read()

        # print("词库名：", self.byte2str(data[0x130:0x338]))  # .encode('GB18030')
        # print("词库类型：", self.byte2str(data[0x338:0x540]))
        # print("描述信息：", self.byte2str(data[0x540:0xd40]))
        # print("词库示例：", self.byte2str(data[0xd40:self.startPy]))

        self.get_pyTable(data[self.startPy:self.startChinese])
        self.get_chinese(data[self.startChinese:])
        with open(out_name, 'w', encoding='utf8') as f:
            f.writelines([word + ' ' + str(count) + ' ' + py + '\n' for count, py, word in self.GTable])
        print(out_name, ' was saved!')


if __name__ == '__main__':

    # main_dir_in = "E:/词库/搜狗细胞词库/scel/城市信息/211院校名单"
    # main_dir_out = "E:/词库/搜狗细胞词库/txt/城市信息/211院校名单.txt"

    main_dir_in = "data/scel/"
    main_dir_out = "data/scel2txt/"

    wrong = 0
    for p_cate in os.listdir(main_dir_in):
        cate_dir_in = main_dir_in + p_cate + '/'
        cate_dir_out = main_dir_out + p_cate + '/'
        if not os.path.exists(cate_dir_out): os.makedirs(cate_dir_out)
        print('\n', cate_dir_out, '*' * 50)
        for p_item in os.listdir(cate_dir_in):
            try:
                convert = Converter()
                convert.scel2txt(cate_dir_in + p_item, cate_dir_out + p_item + '.txt')
            except:
                wrong += 1
                print(str(wrong), cate_dir_in + p_item)
                continue
            del convert
    print('wrong:', wrong)
