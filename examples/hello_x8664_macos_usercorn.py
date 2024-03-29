#!/usr/bin/env python3
# 
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
# Built on top of Unicorn emulator (www.unicorn-engine.org) 
#
# LAU kaijern (xwings) <kj@qiling.io>
# NGUYEN Anh Quynh <aquynh@gmail.com>
# DING tianZe (D1iv3) <dddliv3@gmail.com>
# SUN bowen (w1tcher) <w1tcher.bupt@gmail.com>
# CHEN huitao (null) <null@qiling.io>
# YU tong (sp1ke) <spikeinhouse@gmail.com>
import sys
sys.path.append("..")
from qiling import *

from capstone import *
from unicorn.x86_const import *

sys.path.append("..")

md = Cs(CS_ARCH_X86, CS_MODE_64)

def dump_everything(uc, address, size, user_data):
    buf = ql.uc.mem_read(address, size)
    for i in md.disasm(buf, address):
        print(":: 0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
    eax = uc.reg_read(UC_X86_REG_RAX)
    ebx = uc.reg_read(UC_X86_REG_RBX)
    ecx = uc.reg_read(UC_X86_REG_RCX)
    edx = uc.reg_read(UC_X86_REG_RDX)
    edi = uc.reg_read(UC_X86_REG_RDI)
    esi = uc.reg_read(UC_X86_REG_RSI)
    ebp = uc.reg_read(UC_X86_REG_RBP)
    esp = uc.reg_read(UC_X86_REG_RSP)
    ds = uc.reg_read(UC_X86_REG_DS)
    gs = uc.reg_read(UC_X86_REG_GS)
    ss = uc.reg_read(UC_X86_REG_SS)
    cs = uc.reg_read(UC_X86_REG_CS)

    stack_info = uc.mem_read(esp, 40)
    print(">>> RAX= 0x%lx, RBX= 0x%lx, RCX= 0x%lx, RDX= 0x%lx, RDI= 0x%lx, RSI= 0x%lx, RBP= 0x%lx, RSP= 0x%lx, DS= 0x%lx, GS= 0x%lx, SS= 0x%lx, CS= 0x%lx " % (eax, ebx, ecx, edx, edi, esi, ebp, esp,ds,gs,ss,cs))
    print(stack_info)
    print ("")
    input()

if __name__ == "__main__":
    ql = Qiling(["rootfs/x8664_macos/bin/x8664_hello_usercorn"], "rootfs/x8664_macos", output = "debug")
    # ql.hook_code(dump_everything)
    ql.run()
