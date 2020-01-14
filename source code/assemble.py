from func import *

def clear(data):
	new_data = []
	sub_pat1 = r" *, *"
	sub_pat2 = r": *\n+ *"
	sub_pat3 = r"#.*"
	sub_pat4 = r" +"
	sub_pat5 = '\t'
	split_pat = r"\n+"
	data = re.sub(sub_pat3, '', data)
	data = re.sub(sub_pat5, ' ', data)
	data = re.sub(sub_pat1, ',', data)
	data = re.sub(sub_pat2, ": ", data, re.S)
	data = re.split(split_pat, data)
	for i in data:
		tmp = i.strip()
		if tmp != '':
			tmp = re.sub(sub_pat4, ' ', tmp)
			new_data.append(tmp)
	return new_data

def calc_label(data):				# deal with labels
	abandon = {}					# index of labels
	new_data = []
	pat = r"(\w+) (\$\w+)?(,\$\w+)*,([A-Za-z]\w*)|(\w+) (\w+)"
	for i in range(len(data)):		# record labels' index at first
		try:
			tmp = data[i]
			if ':' in tmp:
				abandon[tmp[:tmp.find(':')]] = i
				for j in range(tmp.find(':')+1, len(tmp)):
					if tmp[j] != ' ' and tmp[j] != '\t':
						new_data.append(tmp[j:])
						break
			else:
				new_data.append(tmp)
		except:
			new_data.append("<!-- Error in line %d -->" % (i+1))
	for i in range(len(new_data)):	# then replace label with immediate number
		try:
			tmp = new_data[i]
			match = re.match(pat, tmp)
			if(match):
				group = match.groups()
				for j in range(-1, -1*len(group), -1):
					if(group[j]):
						sub = group[j]
						gaps = abandon[sub] - i - 1
						tmp = tmp.replace(sub, str(gaps))
						break
			new_data[i] = tmp.lower()	# do this after label is replaced
		except:
			new_data[i] = "<!-- Error in line %d -->" % (i+1)
	return new_data

def R(ins, opnum = ''):				# assemble class R
	tmp = {"op":instructions[ins]["opcode"], "rs":"00000", "rt":"00000",\
		"rd":"00000", "shamt":"00000", "funct":instructions[ins]["func"]}
	opnum = opnum.split(',')
	pattern = instructions[ins]["pattern"]
	if pattern:						# prevent from pattern == None
		pattern = pattern.split(',')
	else:
		pattern = ''
	for i in range(len(pattern)):
		if pattern[i] == "shamt":	# shamt is also an immediate operand
			shamt = c2d(opnum[i])
			if shamt > 2**5-1 or shamt < 0:
				shamt = "error"
			tmp["shamt"] = complement(shamt, 5)
		else:
			tmp[pattern[i]] = registers[opnum[i]]
	return get_payload(tmp)

def I(ins, opnum):					# assemble class I
	tmp = {"op":instructions[ins]["opcode"], "rs":"00000", "rt":"00000",\
			"imm":"%016d"%0}
	pattern = instructions[ins]["pattern"]
	if '(' in pattern:
		pattern = pattern[:-1].replace('(',',').split(',')
		opnum = opnum[:-1].replace('(',',').split(',')
	else:
		pattern = pattern.split(',')
		opnum = opnum.split(',')
	for i in range(len(pattern)):
		if pattern[i] == "imm" or pattern[i] == "label":
			imm = c2d(opnum[i])
			if imm>(2**15-1) or imm<(-2**15):
				imm = "error"
			tmp["imm"] = complement(imm, 16)
		else:
			tmp[pattern[i]] = registers[opnum[i]]
	if ins == "bgez":
		tmp["rt"] = "00001"
	return get_payload(tmp)

def J(ins, opnum, cur):			# assemble class J
	tmp = {"op":instructions[ins]["opcode"]}
	addr = complement(0x4 * (cur + c2d(opnum) + 1), 32)
	tmp["addr"] = addr[4:-2]
	return get_payload(tmp)

def assemble_piece(code, cur):		# assemble a single line
	tmp = code.split(' ')
	code_type = instructions[tmp[0]]["type"]
	if len(tmp) == 1:				# eg. syscall, only R has instructions like this
		return R(tmp[0])
	else:
		if code_type == 'R':
			return R(tmp[0], tmp[1])
		elif code_type == 'I':
			return I(tmp[0], tmp[1])
		elif code_type == 'J':
			return J(tmp[0], tmp[1], cur)
		else:
			return "Doesn't support this instruction."

### Top layer
def assemble(data):
	res = []
	data = clear(data)
	data = calc_label(data)
	for i in range(len(data)):
		try:
			res.append(bin2hex(assemble_piece(data[i], i)))
		except:
			res.append("<!-- Error in line %d -->" % (i+1))
	return res

def calc_instruction_offset(raw_data):
	record = -1
	asmed_data = assemble(raw_data)
	clear_data = re.sub(r".+: ", '', '\n'.join(clear(raw_data))).split('\n')
	raw_data = re.sub(r'\t', ' ', raw_data)
	raw_data = re.sub(r" +", ' ', raw_data)
	raw_data = re.sub(r" *, *", ',', raw_data)
	tmp = re.sub(r"\n+$", '', raw_data, re.S).split('\n')
	for i in range(len(asmed_data)):
		if "Error in line" in asmed_data[i]:
			for j in range(record+1, len(tmp)):
				if clear_data[i] in tmp[j]:
					record = j
					break
			asmed_data[i] = "<!-- Error in line %d -->" % (record+1)
	return asmed_data

def coe_format(data):
	error = ''
	res = "MEMORY_INITIALIZATION_RADIX=16;\nMEMORY_INITIALIZATION_VECTOR=\n"
	tmp = calc_instruction_offset(data)
	for i in range(len(tmp)):
		if 'Error' in tmp[i]:
			error += '    ' + tmp[i] + '\n'
		else:
			res += tmp[i]
			if i != len(tmp) - 1:
				res += ",\n"
			else:
				res += ';'
	return res, error
