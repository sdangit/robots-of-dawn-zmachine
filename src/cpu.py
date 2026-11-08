"""Bounded 6502 reference executor with explicit host callbacks.
Not a complete C64 emulator. Decimal N/Z/V flags are simplified; current
behavioral comparisons are not independent hardware-emulator validation.
"""
from collections import Counter
from mos6502 import decode

class TrackedRAM(bytearray):
    def __new__(cls, data, cpu): return super().__new__(cls)
    def __init__(self, data, cpu): super().__init__(data); self.cpu=cpu
    def __setitem__(self, key, value):
        if isinstance(key,int) and self.cpu.current_pc is not None:
            self.cpu.writes.append({'pc':self.cpu.current_pc,'address':key,'old':self[key],'new':value})
        super().__setitem__(key,value)

class CPU:
    def __init__(self, memory):
        self.current_pc=None;self.writes=[];self.reads=[];self.visits=Counter();self.hooks={};self.hook_log=[]
        self.m=TrackedRAM(memory,self);self.a=self.x=self.y=0;self.s=0xff
        self.c=self.z=self.n=self.v=self.d=0;self.pc=0;self.output=[];self.steps=0
    def nz(self,v):self.z=int((v&255)==0);self.n=(v>>7)&1;return v&255
    def push(self,v):self.m[0x100+self.s]=v&255;self.s=(self.s-1)&255
    def pop(self):self.s=(self.s+1)&255;return self.m[0x100+self.s]
    def ret(self):self.pc=((self.pop()+256*self.pop())+1)&65535
    def run(self,start,stop=0x0200,limit=300000):
        self.current_pc=None;run_start_steps=self.steps;self.pc=start
        self.push((stop-1)>>8);self.push((stop-1)&255)
        while self.pc!=stop:
            self.steps+=1
            if self.steps-run_start_steps>limit:raise AssertionError('Instruction limit')
            self.current_pc=self.pc;self.visits[self.pc]+=1
            if self.pc in self.hooks and self.hooks[self.pc](self):continue
            ins=decode(self.m,self.pc)
            if not ins:raise AssertionError(f'Undecodable ${self.pc:04X}')
            op,mode,value=ins['op'],ins['mode'],ins['value'];self.pc+=ins['size']
            address=None
            if mode in ('z','w'):address=value
            elif mode=='zx':address=(value+self.x)&255
            elif mode=='zy':address=(value+self.y)&255
            elif mode=='wx':address=(value+self.x)&65535
            elif mode=='wy':address=(value+self.y)&65535
            elif mode=='iy':address=(self.m[value]+256*self.m[(value+1)&255]+self.y)&65535
            elif mode=='ix':
                t=(value+self.x)&255;address=self.m[t]+256*self.m[(t+1)&255]
            operand=self.m[address] if address is not None else value
            if address is not None and op not in ('STA','STX','STY','JMP','JSR'):
                self.reads.append({'pc':ins['address'],'address':address,'value':operand})
            if op in ('LDA','LDX','LDY'):setattr(self,op[-1].lower(),self.nz(operand))
            elif op in ('STA','STX','STY'):self.m[address]=getattr(self,op[-1].lower())
            elif op in ('CMP','CPX','CPY'):
                reg=self.a if op=='CMP' else self.x if op=='CPX' else self.y
                self.c=int(reg>=operand);self.nz(reg-operand)
            elif op=='BIT':self.n=(operand>>7)&1;self.v=(operand>>6)&1;self.z=int((self.a&operand)==0)
            elif op in ('AND','ORA','EOR'):
                self.a=self.nz(self.a&operand if op=='AND' else self.a|operand if op=='ORA' else self.a^operand)
            elif op in ('ADC','SBC'):
                original=self.a;rhs=operand if op=='ADC' else operand^255
                result=original+rhs+self.c
                self.v=int(bool((~(original^rhs)&(original^result))&128))
                if self.d:
                    assert op=='ADC','Decimal subtraction not implemented/needed'
                    lo=(original&15)+(operand&15)+self.c
                    if lo>9:lo+=6
                    hi=(original>>4)+(operand>>4)+(lo>15)
                    if hi>9:hi+=6
                    self.c=int(hi>15);self.a=self.nz((hi<<4)|(lo&15))
                else:self.c=int(result>255);self.a=self.nz(result)
            elif op in ('ASL','LSR','ROL','ROR'):
                old=self.a if mode=='a' else operand;carry=self.c
                self.c=(old>>7)&1 if op in ('ASL','ROL') else old&1
                result=((old<<1)|(carry if op=='ROL' else 0)) if op in ('ASL','ROL') else ((old>>1)|(carry<<7 if op=='ROR' else 0))
                result=self.nz(result)
                if mode=='a':self.a=result
                else:self.m[address]=result
            elif op in ('INC','DEC'):self.m[address]=self.nz(operand+(1 if op=='INC' else -1))
            elif op in ('INX','INY','DEX','DEY'):
                reg=op[-1].lower();setattr(self,reg,self.nz(getattr(self,reg)+(1 if op.startswith('IN') else -1)))
            elif op in ('TAX','TAY','TXA','TYA','TSX','TXS'):
                source=op[1].lower();dest=op[2].lower();v=getattr(self,source);setattr(self,dest,v if dest=='s' else self.nz(v))
            elif op=='PHA':self.push(self.a)
            elif op=='PLA':self.a=self.nz(self.pop())
            elif op=='JSR':self.push((self.pc-1)>>8);self.push(self.pc-1);self.pc=value
            elif op=='RTS':self.ret()
            elif op=='JMP':
                assert mode=='w';self.pc=value
            elif mode=='r':
                condition={'BCC':not self.c,'BCS':self.c,'BEQ':self.z,'BNE':not self.z,'BMI':self.n,'BPL':not self.n,'BVC':not self.v,'BVS':self.v}[op]
                if condition:self.pc=ins['target']
            elif op=='CLC':self.c=0
            elif op=='SEC':self.c=1
            elif op=='CLD':self.d=0
            elif op=='SED':self.d=1
            elif op in ('SEI','CLI','NOP'):pass
            else:raise AssertionError(f'Unsupported harness opcode {op} at ${ins["address"]:04X}')
        self.current_pc=None
        return bytes(self.output)

