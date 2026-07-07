from sys import argv

class Num:
 def __init__(self,nat,fix=0):
  self.val=(int(nat)&0xff)*0x100
  if fix!=0 and fix!='':
   self.val+=int(fix)&0xff

 def __str__(self):
  res=""
  if self.val&0x8000:
   res+='-'
  res+=str((self.val>>8)&0x7f)
  a=self.val&0xff
  if a:
   res+='.'
   res+=str(a)

  return res

 def __repr__(self):
  return self.__str__()

 def __add__(self,rhs):
  if isinstance(rhs,Num): return self.val+rhs.val
  elif isinstance(rhs,int): return self.__add__(Num(rhs))

 def __sub__(self,rhs):
  if isinstance(rhs,Num): return self.val-rhs.val
  elif isinstance(rhs,int): return self.__sub__(Num(rhs))

class opcode:
 pushn='\x00'
 pushs='\x01'
 call='\x10'
 add='\x20'
 sub='\x21'

allowed=("name","const","expr","add","sub",)
keyword=("fn","return","let")

def err(a):
 print(a)
 exit(-1)
 return

data=""
def codegen(ast,codeonly=False):
 global data
 i=0
 header="NIL\x27"
 code=""

 while i<len(ast):
  if ast[i][0]=="const":
   if isinstance(ast[i][1],str):
    data+=chr(len(ast[i][1]))+ast[i][1]
    code+=opcode.pushs+chr(data.find(ast[i][1])-1)
   elif isinstance(ast[i][1],Num):
    code+=opcode.pushn+chr(ast[i][1].val>>8)+chr(ast[i][1].val&0xff)
  elif ast[i][0]=="call":
   code+=codegen(ast[i][2][::-1],True)
   data+=chr(len(ast[i][1]))+ast[i][1]
   code+=opcode.call
   i+=1
   if i>=len(ast) or ast[i][0]!=';': err("Expected ';'")
  elif ast[i][0]=="add":
   code+=codegen((ast[i][2],),True)
   code+=codegen((ast[i][1],),True)
   code+=opcode.add
  elif ast[i][0]=="sub":
   code+=codegen((ast[i][2],),True)
   code+=codegen((ast[i][1],),True)
   code+=opcode.sub
  i+=1

 if codeonly: return code
 start=5+len(data)
 return header+chr(start)+data+code

def parse(tokens):
 res=tokens
 res=parseParen(res)
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
   c=0
   fix=""
   while i<len(code) and code[i].isdigit():
    if c!=1:
     word+=code[i]
    else:
     fix+=code[i]
    i+=1
    if code[i]=='.':
     i+=1
     c+=1
    if c>1: err("Unexpected '.' in number")
   res.append(("const",Num(word,fix)))
   word=""

  if code[i]=='.':
   i+=1
   if i>=len(code) and not code[i].isdigit(): err("Expected digit after '.'")
   while i<len(code) and code[i].isdigit():
    word+=code[i]
    i+=1
    if code[i]=='.': err("Unexpected '.' in number")
   res.append(("const",Num(0,int(word))))
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
  elif code[i] in "(){};+=,": res.append((code[i],))
  elif code[i]=='-':
   if i+1>=len(code): err("Interupted parsing")
   if (not (code[i-1].isalnum() or code[i-1]=='_')) and code[i+1].isdigit():
    i+=1
    c=0
    fix=""
    while i<len(code) and code[i].isdigit():
     if c!=1:
      word+=code[i]
     else:
      fix+=code[i]
     i+=1
     if code[i]=='.':
      i+=1
      c+=1
     if c>1: err("Unexpected '.' in number")
    res.append(("const",Num((int(word)&0x7f)+0x80,fix&0xff)))
    word=""
   else:
    res.append((code[i],))

  i+=1
 return tuple(res)

def main():
 if len(argv)==1: err("Expected a file")
 with open(argv[1],"r") as fin:
  tokens=lex(fin.read())
  ast=parse(tokens)
  code=codegen(ast)
  print(bytes(code,"utf-8"))
 return

if __name__=="__main__":
 main()
