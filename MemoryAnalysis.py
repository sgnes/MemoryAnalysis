__author__ = 'DZMP8F'

import re
import os
import sys
import time

# .text_vle       0012ac04	00000030 D:/Code/62.1G/10028809_MT62.1G_for_coding/Products/objs_MT62P1G_NA_CNG/dd_knock_ctc.o


class memory_analysis(object):
    def __init__(self, argv):
        self.argv = argv
        self.__str_wind_river_keyword = "Wind River DLD"
        self.__re_exp_obj = r"^\s+(\.[a-zA-Z_]{2,40})\s+([a-zA-Z0-9]{2,8})\s+([a-zA-Z0-9]{2,8})\s+([A-Za-z0-9:/\\_\.]{2,200}\.[oOaA])"
        self.__re_exp_dir = r"^-I([A-za-z0-9_\.:/]{2,200})"
        self.str_map_file_name = argv[0]
        self.str_file_text = ""
        self.dict_obj_list = {}
        self.dict_obj_dict = {}
        self.list_obj = []
        self.list_obj_sorted = []
        self.dict_sections = {}
        self.dict_sections_list_sorted = {}
        self.dict_sections_dir_size = {}
        self.dict_sections_list_dirs_sorted = {}
        self.file_map = open(self.str_map_file_name)
        pass

    def analysis_obj_size(self):
        if self.file_map:
            self.str_file_text = self.file_map.read()
            self.file_map.close()
            self.list_obj = re.findall(self.__re_exp_obj, self.str_file_text, re.M)
            # this for cycle change the re.findall output into a dict(self.dict_obj_size).
            # the object file name is the key and the value is a list
            # the value is a list of tuples(object file size, section name)
            for obj in self.list_obj:
                # self.list_obj is a list with tuples(section, address, size, object file name)
                section_name = obj[0].lower()
                obj_size = obj[2]
                obj_name = os.path.basename(obj[3])
#               not to calc the debug information
                if "debug" not in section_name:
                    if obj_name not in self.dict_obj_list:
                        self.dict_obj_list[obj_name] = []
                    self.dict_obj_list[obj_name].append((obj_size, section_name))

            # this for cycle calc the object file size for every section
            # self.dict_obj_dict is dict with a list of dicts
            # self.dict_obj_dict's key is the object file name
            # self.dict_obj_dict's value is also a dict,as follows
            #       key is section name
            #       value is object file size
            for obj in self.dict_obj_list:
                list_obj = self.dict_obj_list[obj]
                self.dict_obj_dict[obj] = {}
                for i in list_obj:
                    if i[1] in self.dict_obj_dict[obj]:
                        self.dict_obj_dict[obj][i[1]] += int(i[0], 16)
                    else :
                        self.dict_obj_dict[obj][i[1]] = int(i[0], 16)

    def calc_sections(self):
        # this for cycle will change self.dict_obj_dict to self.dict_sections
        # self.dict_sections is a dict
        #   key: section name
        #   value: type is dict
        #       key: object file name
        #       value: object file size
        for obj in self.dict_obj_dict:
            for section in self.dict_obj_dict[obj]:
                section_size = self.dict_obj_dict[obj][section]
                if section not in self.dict_sections:
                    self.dict_sections[section] = {}
                self.dict_sections[section][obj] = section_size
        # this for cycle will make the self.dict_sections sorted by every value
        # self.dict_sections_list_sorted type is dict
        #   key:    section name
        #   value:  type is list with tuples(object file name, object file size)
        for section in self.dict_sections:
                self.dict_sections_list_sorted[section] = sorted(self.dict_sections[section].items(),\
                                key=lambda x:x[1], reverse=True)

    def calc_obj_size_by_dir_usr(self):
        if len(self.argv) == 2:
            self.str_usr_file_name = self.argv[1]
            self.file_usr = open(self.str_usr_file_name)
            if self.file_usr:
                self.str_usr_text = self.file_usr.read()
                self.file_usr.close()
                self.list_re_usr_dirs = re.findall(self.__re_exp_dir, self.str_usr_text, re.M)
                for i in range(len(self.list_re_usr_dirs)):
                    self.list_re_usr_dirs[i] = self.list_re_usr_dirs[i].replace("\\", r"/")
                self.list_re_usr_dirs = list(set(self.list_re_usr_dirs))
                for dir in self.list_re_usr_dirs:
                    if os.path.exists(dir):
                        list_tmp = os.listdir(dir)
                        for f in list_tmp:
                            if f.lower().endswith(".c") or f.lower().endswith(".a"):
                                for section in self.dict_sections:
                                    if f.lower().endswith(".c") :
                                        fo = f.lower().replace(".c", ".o")
                                    if fo in self.dict_sections[section]:
                                        filesize = self.dict_sections[section][fo]
                                        if section not in self.dict_sections_dir_size:
                                            self.dict_sections_dir_size[section] = {}
                                        if dir not in self.dict_sections_dir_size[section]:
                                            self.dict_sections_dir_size[section][dir] = 0
                                        self.dict_sections_dir_size[section][dir] += filesize
        for section in self.dict_sections_dir_size:
                self.dict_sections_list_dirs_sorted[section] = sorted(self.dict_sections_dir_size[section].items(),\
                                key=lambda x:x[1], reverse=True)
    def generate_report(self):
            print("********************************************************************************")
            print("*object file name                       section name 	    size			   *")
            print("********************************************************************************")
            self.list_obj_sorted = [(k, self.dict_obj_dict[k]) for k in sorted(self.dict_obj_dict.keys())]
            for obj in self.list_obj_sorted:
                print(obj[0])
                for i in obj[1]:
                    print("{:<40s}{:20s}{:0>8x}".format("", i, obj[1][i]))

            print("********************************************************************************")
            print("*section name 	    object file name                         size			   *")
            print("********************************************************************************")


            for section in self.dict_sections_list_sorted:
                print(section)
                for obj in self.dict_sections_list_sorted[section]:
                    print("{:<20s}{:40s}{:0>8x}".format("", obj[0], obj[1]))

            print("********************************************************************************")
            print("*section name 	    dir name                                 size			   *")
            print("********************************************************************************")


            for section in self.dict_sections_list_dirs_sorted:
                print(section)
                for f in self.dict_sections_list_dirs_sorted[section]:
                    print("{:<20s}{:150s}{:0>8x}".format("", f[0], f[1]))



if __name__ == "__main__":
    if len(sys.argv) > 1:
        old_time = time.time()
        memana = memory_analysis(sys.argv[1:])
        memana.analysis_obj_size()
        memana.calc_sections()
        if len(sys.argv) == 3:
            memana.calc_obj_size_by_dir_usr()
        memana.generate_report()
        new_time = time.time()

        print(new_time-old_time)
    else:
        print("map analysis tool for Wind River compiler")
        print("Usage:")
        print("      MemoryAnalysis.py xxxxx.map yyyyy.usr")
