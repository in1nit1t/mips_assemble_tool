import re

def init_instructions(op_path, func_path):			# generate instruction dictionary
	instructions = {}
	pat1 = r"(\d{6})  (\w+)( (\w+(,\w+(\(\w+\))?)*))?(;(\w+) (\w+(,\w+)*))?"
	pat2 = r"(\d{6})  (\w+)( (\w+(,\w+)*))?"
	pat3 = r"(\d{6})  (\w+(\.\w+)*)( (\w+(,\w+)*))?;(\w+(\.\w+)*)( (\w+(,\w+)*))?"
	with open(op_path,'r') as f:
		op_dt = f.read()
	with open(func_path) as  f:
		func = f.read()
		fb = func.find("Fbegin")
		Rfunc_dt = func[:fb]
		Ffunc_dt = func[fb+6:]
	match1 = re.finditer(pat1, op_dt)				# 1,2,4,8,9
	for i in match1:
		if i.group(2) == "Rtype":
			match2 = re.finditer(pat2, Rfunc_dt)	# 1,2,4
			for j in match2:
				instructions[j.group(2)] = {"type":'R', "opcode":i.group(1), "func":j.group(1), "pattern":j.group(4)}
		if i.group(2) == "Ftype":
			match3 = re.finditer(pat3, Ffunc_dt)	# 1,2,5,7,10
			for k in match3:
				instructions[k.group(2)] = {"type":'F', "opcode":i.group(1), "func":k.group(1), "pattern":k.group(5)}
				instructions[k.group(7)] = {"type":'F', "opcode":i.group(1), "func":k.group(1), "pattern":k.group(10)}
		else:
			if i.group(8):
				instructions[i.group(8)] = {"type":"I", "opcode":i.group(1), "pattern":i.group(9)}
			if i.group(4):
				if "imm" in i.group(4):
					tmp_type = 'I'
				elif "label" in i.group(4):
					if ',' not in i.group(4):
						tmp_type = 'J'
					else:
						tmp_type = 'I'
				else:				# abandon mfc0 and mul, deal with them later
					continue
				instructions[i.group(2)] = {"type":tmp_type, "opcode":i.group(1), "pattern":i.group(4)}
	instructions["mul"] = {"type":'R', "opcode":"011100", "func":"000010", "pattern":"rd,rs,rt"}
	del instructions["mtc0"], instructions["bclf"], instructions["bclt"], instructions["lwcl"], instructions["swcl"]
	return instructions

def generate_register():			# generate register dictionary, no need to deal error
	registers = {"$0":"00000", "$at":"00001", "$gp":"11100", \
				"$sp":"11101", "$fp":"11110", "$ra":"11111"}
	for i in range(8):
		if i < 2:
			registers['$v'+str(i)] = complement(2 + i, 5)
			registers['$k'+str(i)] = complement(26 + i, 5)
			registers['$t'+str(i+8)] = complement(24 + i, 5)
		if i < 4:
			registers['$a'+str(i)] = complement(4 + i, 5)
		registers['$t'+str(i)] = complement(8 + i, 5)
		registers['$s'+str(i)] = complement(16 + i, 5)
	return registers

def c2d(n):							# convert 2,8,16-based to dec
	if n[0:2] == "0x": 
		return int(n, 16)
	elif n[-1] == 'h':
		return int(n[:-1], 16)
	elif n[0] == "0":
		return int(n, 8)
	elif n[-1] == 'b' or n[0:2] == "0b":
		return int(n, 2)
	return int(n)

def hex2bin(string):
	res = ''
	for i in range(len(string)):
		res += bin(int(string[i], 16))[2:].rjust(4, '0')
	return res

def bin2hex(string):
	res = ''
	for i in range(0, len(string), 4):
		res += str(hex(int(string[i:i+4], 2)))[2:]
	return res

def get_payload(dic):				# montage machine codes
	payload = ''
	for i in dic.values():
		payload += i
	return payload

def complement(n, size):			# find binary complement and fill in binary digits
	if n < 0:
		return "{0:0{1}b}".format((n^((1<<size)-1))+1, size)[1:]
	else:
		return "{0:0{1}b}".format(n, size)

def find_reg(string):
	for x, y in registers.items():
		if y == string:
			return x

def bin2signed_dec(string):
	if string[0] == '1':
		return -1 * int(complement(-1*int(string, 2), 16), 2)
	else:
		return int(string, 2)

def format_assemble(data):
	res = ''
	if ':' in ''.join(data):
		for i in data:
			if ':' not in i:
				res += "\t%s\n" % i
			else:
				res += i + '\n'
	else:
		for i in data:
			if ':' not in i:
				res += "%s\n" % i
			else:
				res += i + '\n'
	res = res.replace(": ", ":\n\t").replace(',', ", ")[:-1]
	return res

def show_message(area, mes, color):
	pos = "1.0"
	area.delete("1.0", "end")
	area.tag_add("tag", pos)
	area.tag_config("tag",foreground=color, font =("Arial", 12))
	area.insert(pos, mes, "tag")

opfile = r"data\opcode.txt"
funcfile = r"data\funct.txt"
instructions = init_instructions(opfile, funcfile)
registers = generate_register()
