"""Small dependency-free NMOS 6502 instruction decoder. No CPU emulation.

Only documented instructions are accepted; illegal opcodes stop analysis.
The table is organized by opcode, so audit and correction are straightforward.
"""
ROWS = {
0x00:'BRK:i ORA:ix - - - ORA:z ASL:z - PHP:i ORA:n ASL:a - - ORA:w ASL:w -',
0x10:'BPL:r ORA:iy - - - ORA:zx ASL:zx - CLC:i ORA:wy - - - ORA:wx ASL:wx -',
0x20:'JSR:w AND:ix - - BIT:z AND:z ROL:z - PLP:i AND:n ROL:a - BIT:w AND:w ROL:w -',
0x30:'BMI:r AND:iy - - - AND:zx ROL:zx - SEC:i AND:wy - - - AND:wx ROL:wx -',
0x40:'RTI:i EOR:ix - - - EOR:z LSR:z - PHA:i EOR:n LSR:a - JMP:w EOR:w LSR:w -',
0x50:'BVC:r EOR:iy - - - EOR:zx LSR:zx - CLI:i EOR:wy - - - EOR:wx LSR:wx -',
0x60:'RTS:i ADC:ix - - - ADC:z ROR:z - PLA:i ADC:n ROR:a - JMP:ind ADC:w ROR:w -',
0x70:'BVS:r ADC:iy - - - ADC:zx ROR:zx - SEI:i ADC:wy - - - ADC:wx ROR:wx -',
0x80:'- STA:ix - - STY:z STA:z STX:z - DEY:i - TXA:i - STY:w STA:w STX:w -',
0x90:'BCC:r STA:iy - - STY:zx STA:zx STX:zy - TYA:i STA:wy TXS:i - - STA:wx - -',
0xa0:'LDY:n LDA:ix LDX:n - LDY:z LDA:z LDX:z - TAY:i LDA:n TAX:i - LDY:w LDA:w LDX:w -',
0xb0:'BCS:r LDA:iy - - LDY:zx LDA:zx LDX:zy - CLV:i LDA:wy TSX:i - LDY:wx LDA:wx LDX:wy -',
0xc0:'CPY:n CMP:ix - - CPY:z CMP:z DEC:z - INY:i CMP:n DEX:i - CPY:w CMP:w DEC:w -',
0xd0:'BNE:r CMP:iy - - - CMP:zx DEC:zx - CLD:i CMP:wy - - - CMP:wx DEC:wx -',
0xe0:'CPX:n SBC:ix - - CPX:z SBC:z INC:z - INX:i SBC:n NOP:i - CPX:w SBC:w INC:w -',
0xf0:'BEQ:r SBC:iy - - - SBC:zx INC:zx - SED:i SBC:wy - - - SBC:wx INC:wx -',
}
OPS = {}
for start,row in ROWS.items():
    assert len(row.split()) == 16
    for i,item in enumerate(row.split()):
        if item != '-': OPS[start+i] = tuple(item.split(':'))
assert len(OPS) == 151
SIZE = dict(i=1,a=1,n=2,z=2,zx=2,zy=2,ix=2,iy=2,r=2,w=3,wx=3,wy=3,ind=3)

def decode(mem, pc, known=None):
    if pc not in range(65536) or (known is not None and not known[pc]): return None
    if mem[pc] not in OPS: return None
    op,mode=OPS[mem[pc]]; size=SIZE[mode]
    if pc+size>65536 or (known is not None and not all(known[pc:pc+size])): return None
    raw=mem[pc:pc+size]; value=int.from_bytes(raw[1:],'little')
    target=(pc+2+(value if value<128 else value-256))&65535 if mode=='r' else value
    fmts={'i':'','a':'A','n':f'#$%02X'%value,'z':f'$%02X'%value,'zx':f'$%02X,X'%value,'zy':f'$%02X,Y'%value,
          'ix':f'($%02X,X)'%value,'iy':f'($%02X),Y'%value,'r':f'$%04X'%target,'w':f'$%04X'%value,
          'wx':f'$%04X,X'%value,'wy':f'$%04X,Y'%value,'ind':f'($%04X)'%value}
    return dict(address=pc,op=op,mode=mode,size=size,value=value,target=target,raw_hex=raw.hex(),asm=(op+' '+fmts[mode]).strip())

def linear(mem,start,end,known=None):
    pc=start
    while pc<end:
        inst=decode(mem,pc,known)
        if inst is None:
            yield dict(address=pc,asm=f'.byte ${mem[pc]:02X} ; undecoded',size=1,raw_hex=bytes([mem[pc]]).hex())
            pc+=1
        else:
            yield inst;pc+=inst['size']
