

class EventIndex:
    def __init__(self,run,subrun,event,subevent=0):
        self.run = run
        self.subrun = subrun
        self.event = event
        self.subevent = subevent
    def __lt__(self,evt):
        for (a,b) in [(self.run,evt.run),(self.subrun,evt.subrun),(self.event,evt.event),(self.subevent,evt.subevent)]:
            if a<b:
                return True
            elif a>b:
                return False
            # then a=b

        return False
    def __eq__(self,evt):
        if self.__key()==evt.__key():
            return True
        return False
    def __str__(self):
        return "(%d,%d,%d,%d)"%(self.run,self.subrun,self.event,self.subevent)
    def __key(self):
        return (self.run,self.subrun,self.event,self.subevent)
    def __hash__(self):
        return hash(self.__key())

if __name__ == "__main__":
    # unit test
    a = EventIndex( 1, 2, 3 )
    b = EventIndex( 1, 2, 5 )
    c = EventIndex( 1, 2, 3 )
    d = EventIndex( 3, 2, 1 )
    print a<b
    print a>b
    print a==c

    v = [d,a,b,c]
    for x in v:
        print x,
    print
    v.sort()
    for x in v:
        print x,
    print
