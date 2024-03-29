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

"""
This module is intended for general purpose functions that are only used in qiling.os
"""

from unicorn import *
from unicorn.arm_const import *
from unicorn.x86_const import *
from unicorn.arm64_const import *
from unicorn.mips_const import *

from capstone import *
from capstone.arm_const import *
from capstone.x86_const import *
from capstone.arm64_const import *
from capstone.mips_const import *

from keystone import *

from qiling.arch.filetype import *
from qiling.exception import *
from qiling.utils import *

import struct
import os


def ql_definesyscall_return(ql, uc, regreturn):
    if (ql.arch == QL_ARM): # QL_ARM
        uc.reg_write(UC_ARM_REG_R0, regreturn)
        #ql.nprint("|--->>> Write %i to UC_ARM_REG_R0" % regreturn)

    elif (ql.arch == QL_ARM64): # QL_ARM64
        uc.reg_write(UC_ARM64_REG_X0, regreturn)

    elif (ql.arch == QL_X86): # QL_X86
        uc.reg_write(UC_X86_REG_EAX, regreturn)

    elif (ql.arch == QL_X8664): # QL_X86_64
        uc.reg_write(UC_X86_REG_RAX, regreturn)

    elif (ql.arch == QL_MIPS32EL): # QL_MIPSE32EL
        if regreturn == -1:
            a3return = 1
        elif regreturn == 2:
            regreturn = 2
            a3return = 1
        else:    
            a3return = 0
        #if ql.output == QL_OUT_DEBUG:    
        #    print(">>> A3 is %d" % a3return)
        uc.reg_write(UC_MIPS_REG_V0, regreturn)
        uc.reg_write(UC_MIPS_REG_A3, a3return)

def ql_bin_to_ipv4(ip):
    return "%d.%d.%d.%d" % (
        (ip & 0xff000000) >> 24,
        (ip & 0xff0000) >> 16,
        (ip & 0xff00) >> 8,
        (ip & 0xff))


def ql_read_string(ql, uc, address):
    ret = ""
    c = uc.mem_read(address, 1)[0]
    read_bytes = 1

    while c != 0x0:
        ret += chr(c)
        c = uc.mem_read(address + read_bytes, 1)[0]
        read_bytes += 1
    return ret


def ql_parse_sock_address(sock_addr):
    sin_family, = struct.unpack("<h", sock_addr[:2])

    if sin_family == 2:  # AF_INET
        port, host = struct.unpack(">HI", sock_addr[2:8])
        return "%s:%d" % (ql_bin_to_ipv4(host), port)
    elif sin_family == 6:  # AF_INET6
        return ""


def ql_hook_block(uc, address, size, user_data):
    pass


def ql_hook_code(uc, address, size, user_data):
    pass


def ql_hook_block_disasm(uc, address, size, ql):
    if ql.output == QL_OUT_DUMP:
        ql.nprint(">>> Tracing basic block at 0x%x" %(address))


def ql_hook_code_disasm(uc, address, size, ql):
    tmp = uc.mem_read(address, size)

    if (ql.arch == QL_ARM): # QL_ARM
        reg_cpsr = uc.reg_read(UC_ARM_REG_CPSR)
        mode = CS_MODE_ARM
        # ql.nprint("cpsr : " + bin(reg_cpsr))
        if reg_cpsr & 0b100000 != 0:
            mode = CS_MODE_THUMB
        md = Cs(CS_ARCH_ARM, mode)
        syscall_num = [uc.reg_read(UC_ARM_REG_R7),"R7"]
        arg_0 = [uc.reg_read(UC_ARM_REG_R0),"R0"]
        arg_1 = [uc.reg_read(UC_ARM_REG_R1),"R1"]
        arg_2 = [uc.reg_read(UC_ARM_REG_R2),"R2"]
        arg_3 = [uc.reg_read(UC_ARM_REG_R3),"R3"]
        arg_4 = [uc.reg_read(UC_ARM_REG_R4),"R4"]
        arg_5 = [uc.reg_read(UC_ARM_REG_R5),"R5"]

    elif (ql.arch == QL_X86): # QL_X86
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        if ql.ostype == QL_MACOS:
            syscall_num = [uc.reg_read(UC_X86_REG_EAX),"EAX"]
            arg_0 = [uc.reg_read(UC_X86_REG_ESP + 4 * 1),"ESP_1"]
            arg_1 = [uc.reg_read(UC_X86_REG_ESP + 4 * 2),"ESP_2"]
            arg_2 = [uc.reg_read(UC_X86_REG_ESP + 4 * 3),"ESP_3"]
            arg_3 = [uc.reg_read(UC_X86_REG_ESP + 4 * 4),"ESP_4"]
            arg_4 = [uc.reg_read(UC_X86_REG_ESP + 4 * 5),"ESP_5"]
            arg_5 = [uc.reg_read(UC_X86_REG_ESP + 4 * 6),"ESP_6"]
        else:
            syscall_num = [uc.reg_read(UC_X86_REG_EAX),"EAX"]
            arg_0 = [uc.reg_read(UC_X86_REG_EBX),"EBX"]
            arg_1 = [uc.reg_read(UC_X86_REG_ECX),"ECX"]
            arg_2 = [uc.reg_read(UC_X86_REG_EDX),"EDX"]
            arg_3 = [uc.reg_read(UC_X86_REG_ESI),"ESI"]
            arg_4 = [uc.reg_read(UC_X86_REG_EDI),"EDI"]
            arg_5 = [uc.reg_read(UC_X86_REG_EBP),"EBP"]

    elif (ql.arch == QL_X8664): # QL_X86_64
        md = Cs(CS_ARCH_X86, CS_MODE_64)
        syscall_num = [uc.reg_read(UC_X86_REG_RAX),"RAX"]
        arg_0 = [uc.reg_read(UC_X86_REG_RDI),"RDI"]
        arg_1 = [uc.reg_read(UC_X86_REG_RSI),"RSI"]
        arg_2 = [uc.reg_read(UC_X86_REG_RDX),"RDX"]
        arg_3 = [uc.reg_read(UC_X86_REG_R10),"R10"]
        arg_4 = [uc.reg_read(UC_X86_REG_R8),"R8"]
        arg_5 = [uc.reg_read(UC_X86_REG_R9),"R9"]

    elif (ql.arch == QL_ARM64): # QL_ARM64
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        syscall_num = [uc.reg_read(UC_ARM64_REG_X0),"X7"]
        arg_0 = [uc.reg_read(UC_ARM64_REG_X0),"X0"]
        arg_1 = [uc.reg_read(UC_ARM64_REG_X1),"X1"]
        arg_2 = [uc.reg_read(UC_ARM64_REG_X2),"X2"]
        arg_3 = [uc.reg_read(UC_ARM64_REG_X3),"X3"]
        arg_4 = [uc.reg_read(UC_ARM64_REG_X4),"X4"]
        arg_5 = [uc.reg_read(UC_ARM64_REG_X5),"X5"]

    elif (ql.arch == QL_MIPS32EL): # QL_MIPS32EL
        md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
        syscall_num = [uc.reg_read(UC_MIPS_REG_V0),"V0"]
        arg_0 = [uc.reg_read(UC_MIPS_REG_A0),"A0"]
        arg_1 = [uc.reg_read(UC_MIPS_REG_A1),"A1"]
        arg_2 = [uc.reg_read(UC_MIPS_REG_A2),"A2"]
        arg_3 = [uc.reg_read(UC_MIPS_REG_A3),"A3"]
        arg_4 = uc.reg_read(UC_MIPS_REG_SP)
        arg_4 = [arg_4 + 0x10, "SP+0x10"]
        arg_5 = uc.reg_read(UC_MIPS_REG_SP)
        arg_5 = [arg_5 + 0x14, "SP+0x14"]

    else:
        raise QlErrorArch("Unknown arch defined in utils.py (debug output mode)")

    ql.nprint("|--->>> %s= 0x%x %s= 0x%x %s= 0x%x %s= 0x%x %s= 0x%x %s= 0x%x %s= 0x%x" % \
            (syscall_num[1], syscall_num[0], arg_0[1], arg_0[0], arg_1[1], arg_1[0], arg_2[1], arg_2[0], arg_3[1], arg_3[0], arg_4[1], arg_4[0], arg_5[1], arg_5[0]))

    insn = md.disasm(tmp, address)
    opsize = int(size)
    ql.nprint(">>> 0x%x\t " %(address), end = "")

    for i in tmp:
        ql.nprint(" %02x" %i, end = "")
    if opsize < 4:
        ql.nprint("\t  ", end ="")
    for i in insn:
        ql.nprint('\t%s \t%s' %(i.mnemonic, i.op_str))

def ql_setup(ql):
    if ql.output in (QL_OUT_DISASM, QL_OUT_DUMP):
        if ql.ostype != QL_WINDOWS:
            ql.hook_block(ql_hook_block_disasm, ql)
        ql.hook_code(ql_hook_code_disasm, ql)


def ql_asm2bytes(ql, archtype, runcode, arm_thumb):

    def ks_convert(arch):
        adapter = {
            QL_X86: (KS_ARCH_X86, KS_MODE_32),
            QL_X8664: (KS_ARCH_X86, KS_MODE_64),
            QL_MIPS32EL: (KS_ARCH_MIPS, KS_MODE_MIPS32 + KS_MODE_LITTLE_ENDIAN),
            QL_ARM: (KS_ARCH_ARM, KS_MODE_ARM),
            QL_ARM_THUMB: (KS_ARCH_ARM, KS_MODE_THUMB),
            QL_ARM64: (KS_ARCH_ARM64, KS_MODE_ARM),
            }

        if arch in adapter:
            return adapter[arch]
        # invalid
        return None, None

    def compile_instructions(runcode, archtype, archmode):
    
        ks = Ks(archtype, archmode)

        shellcode = ''
        try:
            encoding, count = ks.asm(runcode)
            shellcode = [str(f"0x{i:02x}") for i in encoding]
            shellcode = "".join(shellcode).replace('0x', '')
            shellcode = bytes.fromhex(shellcode)
        except KsError as e:
            ql.print("ERROR Keystone Compile Error: %s" % e)

        return shellcode    

    if arm_thumb == 1 and archtype == QL_ARM:
        archtype = QL_ARM_THUMB
    
    archtype, archmode = ks_convert(archtype)
    return compile_instructions(runcode, archtype, archmode)

def ql_transform_to_link_path(ql, uc, path):
    if ql.thread_management != None:
        cur_path = ql.thread_management.cur_thread.get_current_path()
    else:
        cur_path = ql.current_path

    rootfs = ql.rootfs

    if path[0] == '/':
        relative_path = os.path.abspath(path)
    else:
        relative_path = os.path.abspath(cur_path + '/' + path)

    from_path = None
    to_path = None
    for fm, to in ql.fs_mapper:
        fm_l = len(fm)
        if len(relative_path) >= fm_l and relative_path[ : fm_l] == fm:
            from_path = fm
            to_path = to
            break

    if from_path != None:
        real_path = os.path.abspath(to_path + relative_path[fm_l : ])
    else:
        real_path = os.path.abspath(rootfs + '/' + relative_path)

    return real_path

def ql_transform_to_real_path(ql, uc, path):
    if ql.thread_management != None:
        cur_path = ql.thread_management.cur_thread.get_current_path()
    else:
        cur_path = ql.current_path

    rootfs = ql.rootfs

    if path[0] == '/':
        relative_path = os.path.abspath(path)
    else:
        relative_path = os.path.abspath(cur_path + '/' + path)

    from_path = None
    to_path = None
    for fm, to in ql.fs_mapper:
        fm_l = len(fm)
        if len(relative_path) >= fm_l and relative_path[ : fm_l] == fm:
            from_path = fm
            to_path = to
            break

    if from_path != None:
        real_path = os.path.abspath(to_path + relative_path[fm_l : ])
    else:
        if rootfs == None:
            rootfs = ""
        real_path = os.path.abspath(rootfs + '/' + relative_path)
            

        if os.path.islink(real_path):
            link_path = os.readlink(real_path)
            if link_path[0] == '/':
                real_path = ql_transform_to_real_path(ql, uc, link_path)
            else:
                real_path = ql_transform_to_real_path(ql, uc, os.path.dirname(relative_path) + '/' + link_path)

    return real_path


def ql_transform_to_relative_path(ql, uc, path):
    if ql.thread_management != None:
        cur_path = ql.thread_management.cur_thread.get_current_path()
    else:
        cur_path = ql.current_path

    if path[0] == '/':
        relative_path = os.path.abspath(path)
    else:
        relative_path = os.path.abspath(cur_path + '/' + path)

    return relative_path

def flag_mapping(flags, mapping_name, mapping_from, mapping_to):
    ret = 0
    for n in mapping_name:
        if mapping_from[n] & flags == mapping_from[n]:
            ret = ret | mapping_to[n]
    return ret

def open_flag_mapping(flags, ql):
    if ql.platform == None or ql.platform == ql.ostype:
        return flags
        
    open_flags_name = [
        "O_RDONLY",
        "O_WRONLY",
        "O_RDWR",
        "O_NONBLOCK",
        "O_APPEND",
        "O_ASYNC",
        "O_SYNC",
        "O_NOFOLLOW",
        "O_CREAT",
        "O_TRUNC",
        "O_EXCL",
        "O_NOCTTY",
        "O_DIRECTORY",
    ]

    mac_open_flags = {
        "O_RDONLY" : 0x0000,
        "O_WRONLY" : 0x0001,
        "O_RDWR"   : 0x0002,
        "O_NONBLOCK" : 0x0004,
        "O_APPEND" : 0x0008,
        "O_ASYNC" : 0x0040,
        "O_SYNC" : 0x0080,
        "O_NOFOLLOW" : 0x0100,
        "O_CREAT" : 0x0200,
        "O_TRUNC" : 0x0400,
        "O_EXCL" : 0x0800,
        "O_NOCTTY" : 0x20000,
        "O_DIRECTORY" : 0x100000
    }

    linux_open_flags = {
        'O_RDONLY' : 0,
        'O_WRONLY' : 1,
        'O_RDWR' : 2,
        'O_NONBLOCK' : 2048,
        'O_APPEND' : 1024,
        'O_ASYNC' : 8192,
        'O_SYNC' : 1052672,
        'O_NOFOLLOW' : 131072,
        'O_CREAT' : 64,
        'O_TRUNC' : 512,
        'O_EXCL' : 128,
        'O_NOCTTY' : 256,
        'O_DIRECTORY' : 65536
    }

    if ql.platform == QL_MACOS:
        f = linux_open_flags
        t = mac_open_flags
    else:
        f = mac_open_flags
        t = linux_open_flags
    return flag_mapping(flags, open_flags_name, f, t)
    