import re
SWITCH = False
OUTER_INPUTS={}
REFLECT_INPUTS={}
PREPARE_INIT={}
VAR_LIST={}
class v_l:
    def __init__(self):
        self.l = []
    def __len__(self):
    	return len(self.l)

    def append(self,item):
        self.l.append(item)

    def pop(self):
        if self.l != []:
            self.l.pop(-1)

    def getLast(self,name):
        length = len(self.l)
        pattern = name + '\d+$'
        p = re.compile(pattern)
        for i in range(1,length+1):
            if p.match(self.l[-i]) != None:
                return self.l[-i]
        return None
    def clear(self):
        self.l = []

    def copy(self):
        return list(self.l)

VARNAME_LIST = v_l()
SWITCH_LIST = {}
VARNAME_BACK = []
API_TRACK = []
