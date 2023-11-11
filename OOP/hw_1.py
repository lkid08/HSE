

in_file = "path"
out_file = "hw_1_keys.txt"

regs = {
    "reg_1": "\d+\.\d+", 
    "reg_2": "\d+\.\d+", 
    "reg_3": "\w+\@\w+\.\w+", 
    "reg_4": "\w+\.?\w+\@\.?\w+\.?\.\w+", 
    "reg_5": "\W?\W?\ \W\w+\ \W?\W?", 
    "reg_6": "\d\d\.\d\d\.\d\d", 
    "reg_7": ""}

with open(f"{in_file}", "r") as f:
    for line in f.readlines():
        for key in regs:
            if regs[key] in line:
                out_file.write(regs[key])