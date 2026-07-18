from sys import argv

allowed=("expr","add","sub","mul","div","const","name")
keyword=("fn","return","let","use")

def err(msg):
 print(msg)
 exit(-1)

var={}
def run(ast):
 i=0
 res=("const",0)
 done=False

 while i<len(ast):
  if ast[i][0]=="const":
   res=ast[i]
  elif ast[i][0]=="name":
   try:
    res=var[ast[i][1]]
   except:
    err("Undefined variable %s" % ast[i][1])
  elif ast[i][0]=="call":
   if ast[i][1]=="print":
    for j in ast[i][2]:
     print(run((j,))[1],end="")
    print()
   done=True
  elif ast[i][0]=="dec":
   if ast[i][2]==None:
    var[ast[i][1]]=("undefined",)
   else:
    var[ast[i][1]]=ast[i][2]
  elif ast[i][0]=="add":
   lhs=run([ast[i][1]])
   rhs=run([ast[i][2]])
   if lhs[0]!=rhs[0] or type(lhs[1])!=type(rhs[1]): err("Unmatched type")
   res=("const",lhs[1]+rhs[1])
   done=True
  elif ast[i][0]=="sub":
   lhs=run([ast[i][1]])
   rhs=run([ast[i][2]])
   if lhs[0]!=rhs[0] or type(lhs[1])!=type(rhs[1]): err("Unmatched type")
   res=("const",lhs[1]-rhs[1])
   done=True
  elif ast[i][0]=="mul":
   lhs=run([ast[i][1]])
   rhs=run([ast[i][2]])
   if lhs[0]!=rhs[0] or type(lhs[1])!=type(rhs[1]): err("Unmatched type")
   res=("const",lhs[1]*rhs[1])
   done=True
  elif ast[i][0]=="div":
   lhs=run([ast[i][1]])
   rhs=run([ast[i][2]])
   if lhs[0]!=rhs[0] or type(lhs[1])!=type(rhs[1]): err("Unmatched type")
   res=("const",lhs[1]/rhs[1])
   done=True

  if done:
   i+=1
   if i<len(ast) and ast[i][0]!=';': err("Expected ';'")
   done=False
  i+=1

 return res

def parse(tokens):
 res=tokens
 res=parseUse(res)
 res=parseParen(res)
 res=parseMD(res)
 res=parseAS(res)
 res=parseKeyword(res)
 res=parseEq(res)
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

 return tuple(res)

def parseEq(tokens):
 res=[]
 i=0

 while i<len(tokens):
  if tokens[i][0]=='=':
   i+=1
   if i>=len(tokens) or tokens[i][0]==';': err("Unfinished statement")
   if tokens[i-2][0]!="name": err("Expected a name")
   name=tokens[i-2][1]
   res.append(("def",name,tokens[i]))
  else:
   res.append(tokens[i])
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
    res.append(("name",name))
  else: res.append(tokens[i])
  i+=1

 return tuple(res)

lib=[]
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
   res.append(("fn",name,tuple(a),tokens[i][1]))
  elif tokens[i][0]=="return":
   i+=1
   if i>=len(tokens): err("Return value expected")
   res.append(("ret",tokens[i]))
  elif tokens[i][0]=="let":
   i+=1
   if i>=len(tokens) or tokens[i][0]!="name": err("Expected name")
   name=tokens[i][1]
   i+=1
   if i>=len(tokens) or tokens[i][0]==';':
    res.append(("dec",name,None))
    continue
   if tokens[i][0]!='=': err("Expected '='")
   i+=1
   if i>=len(tokens): err("Expected a value to assign")
   res.append(("dec",name,tokens[i]))
  else: res.append(tokens[i])
  i+=1

 return tuple(res)

def parseUse(tokens):
 i=0
 res=[]

 while i<len(tokens):
  if tokens[i][0]=="use":
   i+=1
   if i>=len(tokens) or tokens[i][0]!="name": err("Expected a name")
   if tokens[i][0]=="name" and not tokens[i][1] in lib:
    lib.append(tokens[i][1])
    _tokens=()
    with open(tokens[i][1]+".acedia","r") as fin:
     _tokens=lex(fin.read())
     ast=parse(_tokens)
     res=list(ast+tuple(res))
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
   while i<len(code) and code[i].isdigit():
    word+=code[i]
    i+=1
    if code[i]=='.':
     i+=1
     c+=1
    if c>1: err("Unexpected '.' in number")
   res.append(("const",float(word)))
   word=""

  if code[i]=='.':
   i+=1
   if i>=len(code) and not code[i].isdigit(): err("Expected digit after '.'")
   while i<len(code) and code[i].isdigit():
    word+=code[i]
    i+=1
    if code[i]=='.': err("Unexpected '.' in number")
   res.append(("const",float('.'+word)))
   word=""
  elif code[i]=='#':
   while i<len(code) and code[i]!='\n':
    i+=1

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
   if i+1>=len(code): err("Unexpected end")
   if (not (code[i-1].isalnum() or code[i-1]=='_')) and (code[i+1].isdigit() or code[i+1]=='.'):
    i+=1
    c=0
    if code[i]=='.':
     word+=code[i]
     c+=1
     i+=1
    while i<len(code) and code[i].isdigit():
     word+=code[i]
     i+=1
     if code[i]=='.':
      i+=1
      c+=1
     if c>1: err("Unexpected '.' in number")
    res.append(("const",float(word)))
    word=""
    i-=1
   else:
    res.append((code[i],))

  i+=1
 return tuple(res)

def main():
 if len(argv)==1: err("Expected a file")
 tokens=()
 with open(argv[1],"r") as fin:
  tokens=lex(fin.read())
  print(tokens)
 ast=parse(tokens)
 print(ast)
 run(ast)
 return

if __name__=="__main__":
 main()
