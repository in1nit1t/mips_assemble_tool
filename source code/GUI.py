# coding = utf-8
from assemble import *
from disassemble import *
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename

def ChangeLineNumStat(block):
	global asm_line_flag, mac_line_flag
	if block == "asm":
		area = assemble_code_text
		flag = asm_line_flag
	else:
		area = machine_code_text
		flag = mac_line_flag
	data = area.get("1.0", "end")
	area.delete("1.0", "end")
	if data == '\n':
		return
	data = re.sub(r"\n+$", '', data, re.S)
	data = data.split('\n')
	if not flag:
		pos1 = pos2 = pos3 = "1.0"
		area.tag_add("tag1", pos1)
		area.tag_config("tag1",foreground="dimgray", background="gainsboro" , font =("Arial", 12))
		area.tag_add("tag2", pos2)
		area.tag_config("tag2",foreground="black" ,font =("Arial", 12))
		area.tag_add("tag3", pos3)
		area.tag_config("tag3",foreground="gainsboro", background="gainsboro" , font =("Arial", 12))
		for i in range(len(data)):
			if i+1 < 10:
				area.insert("end", '00', "tag3")
			elif i+1 < 100:
				area.insert("end", '0', "tag3")
			if i+1 > 999:
				area.delete(str(i+1)+'.0', "end")
				break
			area.insert("end", " %d "%(i+1), "tag1")
			area.insert("end", '|', "tag3")
			area.insert("end", " "+data[i]+'\n', "tag2")
		area.delete(str(i+2)+'.0', "end")
	else:
		for i in range(len(data)):
			data[i] = data[i][7:]
		area.insert("end", '\n'.join(data))

def CheckStat():
	global asm_line_flag, mac_line_flag
	asm_data = assemble_code_text.get("1.0", "end")
	mac_data = machine_code_text.get("1.0", "end")
	asm_hasline = re.findall(r"[\d ]{4} \| ", asm_data)
	mac_hasline = re.findall(r"[\d ]{4} \| ", mac_data)
	if asm_hasline:
		asm_line_flag = True
	else:
		asm_line_flag = False
	if mac_hasline:
		mac_line_flag = True
	else:
		mac_line_flag = False

def SetStat(asm, mac):		# may need to set flag on purpose
	global asm_line_flag, mac_line_flag
	asm_line_flag = asm
	mac_line_flag = mac

def TopChange():			# change output according to flags
	global asm_line_flag, mac_line_flag
	if asm_line_flag:
		if mac_line_flag:
			ChangeLineNumStat("asm")
			ChangeLineNumStat("mac")
		else:
			ChangeLineNumStat("asm")
	else:
		if mac_line_flag:
			ChangeLineNumStat("mac")
		else:
			ChangeLineNumStat("asm")
			ChangeLineNumStat("mac")

def LineNum():
	CheckStat()				# check flags at first
	TopChange()

def KeepPre(pre_asm, pre_mac, asm_data, mac_data):		# keep previous line status
	SetStat(False, False)
	mac_data = re.sub("\n+$", '', mac_data, re.S)
	assemble_code_text.delete("1.0", "end")
	machine_code_text.delete("1.0", "end")
	assemble_code_text.insert("end", asm_data)
	machine_code_text.insert("end", mac_data)
	if pre_asm:
		ChangeLineNumStat("asm")
	if pre_mac:
		ChangeLineNumStat("mac")

def GetData():
	global asm_line_flag, mac_line_flag
	CheckStat()
	pre_asm_flag = asm_line_flag
	pre_mac_flag = mac_line_flag
	if asm_line_flag or mac_line_flag:
		LineNum()
	asm_code = assemble_code_text.get("1.0", "end")
	mac_code = machine_code_text.get("1.0", "end")
	return pre_asm_flag, pre_mac_flag, asm_code, mac_code

def GUI_assemble():
	global asm_line_flag
	pre_asm_flag, pre_mac_flag, tmp, mac_data = GetData()
	res = '\n'.join(calc_instruction_offset(tmp))
	KeepPre(pre_asm_flag, pre_mac_flag, tmp, res)
	CheckStat()
	if not asm_line_flag and 'Error' in res:
		ChangeLineNumStat("asm")

def GUI_disassemble():
	global mac_line_flag
	pre_asm_flag, pre_mac_flag, tmp, data = GetData()
	disasm, data = calc_machine_offset(data)
	res = '\n'.join(disasm)
	if ':' not in res:
		res = res.replace('\t', '')
	KeepPre(pre_asm_flag, pre_mac_flag, res, data)
	CheckStat()
	if not mac_line_flag and 'Error' in res:
		ChangeLineNumStat("mac")

def Format():
	pre_asm_flag, pre_mac_flag, data, mac_data = GetData()
	res = format_assemble(clear(data))
	KeepPre(pre_asm_flag, pre_mac_flag, res, mac_data)

def ClearAll():
	assemble_code_text.delete("1.0", "end")
	machine_code_text.delete("1.0", "end")

def LoadFile():
	file_path = askopenfilename().replace('/', "\\\\")
	if file_path != '':
		try:
			with open(file_path, 'r', encoding="utf-8") as f:
				data = f.read()
			ClearAll()
			assemble_code_text.insert("end", data)
		except:
			show_message(assemble_code_text, "Can't load this file!", "red")

def GenerateCOE():
	global asm_line_flag
	pre_asm_flag, pre_mac_flag, data, mac_data = GetData()
	COE_path = askdirectory().replace('/', "\\\\")
	if COE_path == '':
		show_message(machine_code_text, "Operation canceled.", "orange")
	else:
		tmp = re.findall(r"\w+", data)
		if tmp == []:
			show_message(machine_code_text, "Plz input assemble code.", "red")
		else:
			data, error = coe_format(data)
			try:
				if error == '':
					with open( COE_path+r"\\output.COE", 'w') as f:
						f.write(data)
					show_message(machine_code_text, "Done!", "green")
				else:
					machine_code_text.delete("1.0", "end")
					pos = "1.0"
					machine_code_text.tag_add("tag", pos)
					machine_code_text.tag_config("tag",foreground="red", font =("Arial", 12))
					machine_code_text.insert(pos, "Errors occured in following lines:\n", "tag")
					machine_code_text.insert("end", error)
					machine_code_text.insert("end", "Plz correct them to generate .COE")
					CheckStat()
					ChangeLineNumStat("asm")
			except:
				show_message(machine_code_text, "Generate failed!", "red")

asm_line_flag = False
mac_line_flag = False
window = tk.Tk()
window.iconbitmap(r".\\data\\mips.ico")
window.config(background="lightsteelblue")
window.title("Mips Assemble Tool")
window.minsize(800, 400)
window.maxsize(800, 400)

# Text area
assemble_code_text = tk.Text(window, font=("Arial", 12), width=40, wrap="none", undo=True, background="floralwhite")
machine_code_text = tk.Text(window, font=("Arial", 12), width=27, wrap="none", undo=True, background="floralwhite")

# Button
a2m_button = tk.Button(window, text="Assemble >>", font=("Arial", 12), width=12, height=1, command=GUI_assemble)
m2a_button = tk.Button(window, text="<< Disassemble", font=("Arial", 12), width=12, height=1, command=GUI_disassemble)
format_button = tk.Button(window, text="Format asm", font=("Arial", 12), width=12, height=1, command=Format)
linenumber_button = tk.Button(window, text="Show/Hide Line", font=("Arial", 12), width=12, height=1, command=LineNum)
clear_button = tk.Button(window, text="Clear All", font=("Arial", 12), width=12, height=1, command=ClearAll)
load_file_button = tk.Button(window, text="Load asm File", font=("Arial", 12), width=12, height=1, command=LoadFile)
generate_coe_button = tk.Button(window, text="Generate .COE", font=("Arial", 12), width=12, height=1, command=GenerateCOE)

# Scroll bar
assemble_code_scroll = tk.Scrollbar(command=assemble_code_text.yview)
assemble_code_text.config(yscrollcommand=assemble_code_scroll.set)
machine_code_scroll = tk.Scrollbar(command=machine_code_text.yview)
machine_code_text.config(yscrollcommand=machine_code_scroll.set)

# Pack
machine_code_scroll.pack(side="right", fill='y')
machine_code_text.pack(side="right", fill='y')
assemble_code_text.pack(side="left", fill='y')
assemble_code_scroll.pack(side="left", fill='y')
a2m_button.pack(pady=25)
m2a_button.pack()
format_button.pack(pady=20)
linenumber_button.pack()
clear_button.pack(pady=20)
load_file_button.pack()
generate_coe_button.pack(pady=20)
window.mainloop()
