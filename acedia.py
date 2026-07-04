from sys import argv

class Opcode:
 call='\x00'
 push='\x10'
 pushs='\x11'

allowed=("name","const","expr","add","sub","mul","div",)
keyword=("fn","return","let")

def err(a):
 print(a)
 exit(-1)
 return

header="ACE\x27"
data=""
code=""
def codegen(ast,l=False):
 global code,data
 i=0

 while i<len(ast):
  if ast[i][0]=="call":
   code+=codegen(ast[i][2][::-1],True)
   data+=chr(len(ast[i][1]))+ast[i][1]
   code+=Opcode.pushs+chr(data.find(ast[i][1]))+Opcode.call
   i+=1
  elif ast[i][0]=="const":
   if isinstance(ast[i][1],int): code+=Opcode.push+chr(ast[i][1])
   else:
    data+=chr(len(ast[i][1]))+ast[i][1]
    code+=Opcode.pushs+chr(data.find(ast[i][1])-1)
  i+=1

 entry=6+len(data)

 if l: return code
 else: return header+chr(entry)+data+code

def parse(tokens):
 res=tokens
 res=parseParen(res)
 res=parseMD(res)
 res=parseAS(res)
 res=parseKeyword(res)
 res=parseCall(res)
 return res

def parseParen(tokens):
 res=[]
 i=0

 while i<len(tokens):
  if tokens[i][0]=='(':
   if tokens[i-1][0]!="name":
    i+=1
    c=1
    a=[]
    while i<len(tokens):
     if tokens[i][0]=='(': c+=1
     elif tokens[i][0]==')': c-=1
     if c==0: break
     a.append(tokens[i])
     i+=1
    if c!=0: err("Unfinished expression")
    res.append(("expr",parse(a)))
   else: res.append(tokens[i])
  elif tokens[i][0]=='{':
   i+=1
   c=1
   a=[]
   while i<len(tokens):
    if tokens[i][0]=='{': c+=1
    elif tokens[i][0]=='}': c-=1
    if c==0: break
    a.append(tokens[i])
    i+=1
   if c!=0: err("Unfinished block")
   res.append(("block",parse(a)))
  elif tokens[i][0]=='}': err("Unexpected '}'")
  else: res.append(tokens[i])
  i+=1

 return res

def parseAS(tokens):
 res=[]
 i=0

 while i<len(tokens):
  if tokens[i][0] in "+-":
   op=tokens[i][0]
   a=res.pop()
   if not a[0] in allowed: err("Expected a name, a constant, or an expression")
   i+=1
   if i>=len(tokens): err("Unfinished operaton")
   b=tokens[i]
   if not b[0] in allowed: err("Expected a name, a constant, or an expression")
   res.append(("add" if op=='+' else "sub",a,b))
  else: res.append(tokens[i])
  i+=1

 return res

def parseMD(tokens):
 res=[]
 i=0

 while i<len(tokens):
  if tokens[i][0] in "*/":
   op=tokens[i][0]
   a=res.pop()
   if not a[0] in allowed: err("Expected a name, a constant, or an expression")
   i+=1
   if i>=len(tokens): err("Unfinished operaton")
   b=tokens[i]
   if not b[0] in allowed: err("Expected a name, a constant, or an expression")
   res.append(("mul" if op=='*' else "div",a,b))
  else: res.append(tokens[i])
  i+=1

 return tuple(res)

def parseCall(tokens):
 res=[]
 i=0

 while i<len(tokens):
  if tokens[i][0]=="name":
   name=tokens[i][1]
   i+=1
   if i<len(tokens) and tokens[i][0]=='(':
    i+=1
    a=[]
    b=i
    c=1
    while i<len(tokens):
     di=i-b
     if tokens[i][0]=='(': c+=1
     elif tokens[i][0]==')': c-=1
     elif di%2==0 and tokens[i][0]==',': err("Unexpected ','")
     elif tokens[i][0]==';': err("Unexpected ';'")
     if c==0: break
     if di%2==1 and tokens[i][0]!=',': err("Expected ','")
     elif di%2==0: a.append(tokens[i])
     i+=1
    if c!=0: err("Unfinished function call")
    res.append(("call",name,tuple(a)))
   else:
    i-=1
    res.append(name)
  else: res.append(tokens[i])
  i+=1

 return tuple(res)

def parseKeyword(tokens):
 res=[]
 i=0

 while i<len(tokens):
  if tokens[i][0]=="fn":
   i+=1
   if i>len(tokens) or tokens[i][0]!="name": err("Expected a name")
   name=tokens[i][1]
   i+=1
   if i>=len(tokens) or tokens[i][0]!='(': err("Expected '('")
   i+=1
   c=1
   a=[]
   d=i
   while i<len(tokens):
    di=i-d
    if tokens[i][0]=='(': err("Unexpected '('")
    elif tokens[i][0]==')': c-=1
    elif di%2==0 and tokens[i][0]==',': err("Unexpected ','")
    elif di%2==1 and tokens[i][0]!=',': err("Expected ','")
    if c==0: break
    if di%2==0:
     if tokens[i][0]!="name": err("Expected name")
     a.append(tokens[i][1])
    i+=1
   if c!=0: err("Unclosed '('")
   i+=1
   if i>=len(tokens) or tokens[i][0]!="block": err("Expected block")
   res.append(("def",name,tuple(a),tokens[i][1]))
  elif tokens[i][0]=="return":
   i+=1
   if i>=len(tokens): err("Return value expected")
   res.append(("ret",tokens[i]))
  elif tokens[i][0]=="let":
   i+=1
   if i>=len(tokens) or tokens[i][0]!="name": err("Expected name")
   name=tokens[i][1]
   i+=1
   if i>=len(tokens) or tokens[i][0]!='=': err("Expected '='")
   i+=1
   if i>=len(tokens): err("Expected a value to assign")
   res.append(("let",name,tokens[i]))
  else: res.append(tokens[i])
  i+=1

 return tuple(res)

def lex(code):
 res=[]
 word=""
 i=0

 while i<len(code):
  if code[i].isalpha() or code[i]=='_':
   while i<len(code) and (code[i].isalnum() or code[i]=='_'):
    word+=code[i]
    i+=1
   if word in keyword: res.append((word,))
   else: res.append(("name",word))
   word=""
  elif code[i].isdigit():
   while i<len(code) and code[i].isdigit():
    word+=code[i]
    i+=1
   res.append(("const",int(word)))
   word=""

  if code[i] in "'\"":
   a=code[i]
   i+=1
   c=1
   while i<len(code):
    if code[i]==a: c-=1
    if c==0: break
    word+=code[i]
    i+=1
   if c!=0: err("Unclosed string")
   res.append(("const",word))
   word=""
  elif code[i] in "(){};+*/=,": res.append((code[i],))
  elif code[i]=='-':
   if i+1>=len(code): err("Interupted parsing")
   if (not (code[i-1].isalnum() or code[i-1]=='_')) and code[i+1].isdigit():
    i+=1
    while i<len(code) and code[i].isdigit():
     word+=code[i]
     i+=1
    res.append(("const",int('-'+word)))
    word=""
   else:
    res.append((code[i],))

  i+=1
 return tuple(res)

def main():
 if len(argv)==1: err("Expected a file")
 elif not (argv[1].endswith(".acedia") or argv[1].endswith(".aceout")): err("File must end with '.acedia' or '.aceout'")
 n=argv[1].endswith(".acedia")
 with open(argv[1],"r") as fin:
  if n:
   tokens=lex(fin.read())
   ast=parse(tokens)
   code=codegen(ast)
   with open(argv[1].replace(".acedia",".aceout"),"w") as fout:
    fout.write(code)
  else:
   code=fin.read()
   if code[0:4]!=header: err("Unknown header")
   print(*list(hex(ord(x)) for x in code))
 return

if __name__=="__main__":
 main()
