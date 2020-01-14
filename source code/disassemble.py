from func import *

def dis_R(data, instruct, dic):
	res = instruct
	rs = find_reg(data[6:11])
	rt = find_reg(data[11:16])
	rd = find_reg(data[16:21])
	shamt = str(bin2signed_dec(data[21:26]))
	if dic["pattern"]:
		res += ' ' + dic["pattern"]
	return res.replace("rd", rd).replace("rs", rs).replace("rt", rt).replace("shamt", shamt)

def dis_I(data, instruct, pat):
	if instruct == "bgez" and data[15] == '0':
		instruct = "bltz"
	res = instruct + ' ' + pat
	rs = find_reg(data[6:11])
	rt = find_reg(data[11:16])
	imm = str(bin2signed_dec(data[16:]))
	return res.replace("rs", rs).replace("rt", rt).replace("imm", imm).replace("label", imm)

def dis_J(addr, instruct):
	return instruct + ' ' + str(bin2signed_dec(addr))

def locate(data):
	count = 1
	flag = 0
	b_jump = ["beq ", "bne ", "blez ", "bgtz ", "bltz ", "bgez "]
	j_jump = ['jal ', 'j ']
	for i in range(len(data)):
		data[i] = '\t' + data[i]
	for i in range(len(data)):
		try:
			tmp = data[i].strip()
			index = -1
			for j in b_jump:
				if j in tmp:
					flag = 1
			if flag:
				while data[i].find(',', index+1, len(data[i])) != -1:
					index = data[i].find(',', index+1, len(data[i]))
				offset = c2d(data[i][index+1:]) + 1
				if 'LABEL' in data[i+offset]:
					data[i] = data[i][:index+1] + ' '+ data[i+offset][:data[i+offset].find(':')]
				else:
					data[i+offset] = "LABEL_%d:\n"%count + data[i+offset]
					data[i] = data[i][:index+1] + " LABEL_%d"%count
					count += 1
				flag = 0
				continue
			for j in j_jump:
				if j in tmp:
					flag = 1
			if flag:
				position = c2d(data[i][data[i].find(' ')+1:])
				if 'LABEL' in data[position]:
					data[i] = data[i][:data[i].find(' ')+1] + data[position][:data[position].find(':')]
				else:
					data[i] = data[i][:data[i].find(' ')+1] + " LABEL_%d"%count
					data[position] = "LABEL_%d:\n"%count + data[position]
					count +=1
				flag = 0
		except:
			data[i] = "\t<!-- Error in line %d -->" % (i+1)
	return data

def disassemble_piece(data):
	if len(data) == 8:
		data = hex2bin(data)
	if len(data) != 32:
		return "Error"
	else:
		op = data[:6]
		for x in instructions:
			if instructions[x]["opcode"] == op:
				code_type = instructions[x]["type"]
				if code_type == 'R':
					funct = data[-6:]
					for y in instructions:
						if instructions[y]["func"] == funct:
							return dis_R(data, y, instructions[y])
				elif code_type == 'I':
					return dis_I(data, x, instructions[x]["pattern"])
				elif code_type== 'J':
					return dis_J(data[6:], x)

### Top layer
def disassemble(data):
	tmp = []
	data = data.split('\n')
	while '' in data:
		data.remove('')
	for i in range(len(data)):
		try:
			tmp.append(disassemble_piece(data[i]).replace(',', ", "))
		except:
			tmp.append("<!-- Error in line %d -->" % (i+1))
	res = locate(tmp)
	return res

def calc_machine_offset(raw_data):
	raw_data = re.sub(r"\n\n+", '\n', raw_data, re.S)
	if raw_data[0] == '\n':
		raw_data = raw_data[1:]
	disasmed_data = disassemble(raw_data)
	for i in range(len(disasmed_data)):
		if "Error"  in disasmed_data[i]:
			disasmed_data[i] = "\t<!-- Error in line %d -->" % (i+1)
	return disasmed_data, raw_data
