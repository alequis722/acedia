use std::fs::read_to_string;
use std::fmt;

#[derive(Debug,Clone,PartialEq)]
enum Type {
 Atom,
 List,
 LP,
 RP,
}

#[derive(Debug,Clone)]
struct Ast {
 kind:Type,
 sval:Option<String>,
 ival:Option<i32>,
 lval:Option<Vec<Ast>>,
}

#[derive(Debug)]
struct Token {
 kind:Type,
 sval:Option<String>,
 ival:Option<i32>,
}

impl fmt::Display for Ast {
 fn fmt(&self,f:&mut fmt::Formatter<'_>)->Result<(),fmt::Error> {
  match self.kind {
   Type::Atom=>{
    if self.sval.is_some() {
     let _=write!(f,"{}",self.sval.clone().unwrap());
    } else {
     let _=write!(f,"{}",self.ival.unwrap());
    }
   },
   Type::List=>{
    let _=write!(f,"( ");
    for i in self.lval.clone().unwrap() {
     let _=write!(f,"{} ",run(vec![i.clone()]));
    }
    let _=write!(f,")");
   },
   _=>return Ok(()),
  }
  Ok(())
 }
}

fn run(ast:Vec<Ast>)->Ast {
 let mut i:usize=0;
 let mut res=Ast{kind:Type::Atom,sval:None,ival:Some(0),lval:None};
 let len=ast.len();

 while i<len {
  if ast[i].kind==Type::List {
   res=run_list(ast[i].lval.clone().unwrap());
  } else if ast[i].kind==Type::Atom {
   if ast[i].sval.is_some() || ast[i].ival.is_some() {
    res=ast[i].clone();
   } else {
    panic!("Unknown type");
   }
  }
  i+=1;
 }

 return res;
}

fn run_list(ast:Vec<Ast>)->Ast{
 let mut i:usize=0;
 let mut res=Ast{kind:Type::Atom,sval:None,ival:Some(0),lval:None};
 let len=ast.len();

 while i<len {
  if ast[i].kind==Type::List {
   run_list(ast[i].lval.clone().unwrap());
  } else if ast[i].kind==Type::Atom {
   if ast[i].sval.is_some() {
    if ast[i].sval.clone().unwrap()=="print" {
     i+=1;
     let mut b:i32=0;
     while i<len {
      print!("{} ",run(vec![ast[i].clone()]));
      i+=1;
      b+=1;
     }
     res=Ast{kind:Type::Atom,sval:None,ival:Some(b),lval:None};
    } else if ast[i].sval.clone().unwrap()=="println" {
     i+=1;
     let mut b:i32=0;
     while i<len {
      print!("{} ",run(vec![ast[i].clone()]));
      i+=1;
      b+=1;
     }
     println!();
     res=Ast{kind:Type::Atom,sval:None,ival:Some(b),lval:None};
    } else if ast[i].sval.clone().unwrap()=="+" {
     i+=1;
     let mut a=run(vec![ast[i].clone()]);
     if a.kind!=Type::Atom || a.ival.is_none() {
      panic!("Expected a number");
     }
     let mut b:i32=a.ival.unwrap();
     i+=1;
     while i<len {
      a=run(vec![ast[i].clone()]);
      if a.kind!=Type::Atom || a.ival.is_none() {
       panic!("Expected a number");
      }
      b+=a.ival.unwrap();
      i+=1;
     }
     res=Ast{kind:Type::Atom,sval:None,ival:Some(b),lval:None};
    } else if ast[i].sval.clone().unwrap()=="-" {
     i+=1;
     let mut a=run(vec![ast[i].clone()]);
     if a.kind!=Type::Atom || a.ival.is_none() {
      panic!("Expected a number");
     }
     let mut b:i32=a.ival.unwrap();
     i+=1;
     while i<len {
      a=run(vec![ast[i].clone()]);
      if a.kind!=Type::Atom || a.ival.is_none() {
       panic!("Expected a number");
      }
      b-=a.ival.unwrap();
      i+=1;
     }
     res=Ast{kind:Type::Atom,sval:None,ival:Some(b),lval:None};
    } else if ast[i].sval.clone().unwrap()=="*" {
     i+=1;
     let mut a=run(vec![ast[i].clone()]);
     if a.kind!=Type::Atom || a.ival.is_none() {
      panic!("Expected a number");
     }
     let mut b:i32=a.ival.unwrap();
     i+=1;
     while i<len {
      a=run(vec![ast[i].clone()]);
      if a.kind!=Type::Atom || a.ival.is_none() {
       panic!("Expected a number");
      }
      b*=a.ival.unwrap();
      i+=1;
     }
     res=Ast{kind:Type::Atom,sval:None,ival:Some(b),lval:None};
    } else if ast[i].sval.clone().unwrap()=="/" {
     i+=1;
     let mut a=run(vec![ast[i].clone()]);
     if a.kind!=Type::Atom || a.ival.is_none() {
      panic!("Expected a number");
     }
     let mut b:i32=a.ival.unwrap();
     i+=1;
     while i<len {
      a=run(vec![ast[i].clone()]);
      if a.kind!=Type::Atom || a.ival.is_none() {
       panic!("Expected a number");
      }
      b/=a.ival.unwrap();
      i+=1;
     }
     res=Ast{kind:Type::Atom,sval:None,ival:Some(b),lval:None};
    } else {
     res=ast[i].clone();
    }
   }
  }

  i+=1;
 }

 return res;
}

fn parse_from_token(tokens:Vec<Token>)->Vec<Ast> {
 let mut res=to_ast(tokens);
 res=parse(res);

 return res;
}

fn parse(ast:Vec<Ast>)->Vec<Ast> {
 let mut res=parse_list(ast);

 return res;
}

fn parse_list(ast:Vec<Ast>)->Vec<Ast> {
 let mut res=Vec::<Ast>::with_capacity(16);
 let mut i:usize=0;
 let len=ast.len();

 while i<len {
  if ast[i].kind==Type::LP {
   i+=1;
   let mut a=Vec::<Ast>::with_capacity(8);
   let mut b=1;
   while i<len {
    if ast[i].kind==Type::LP { b+=1; }
    else if ast[i].kind==Type::RP { b-=1; }

    if b==0 { break; }

    a.push(ast[i].clone());
    i+=1;
   }
   if b!=0 {
    panic!("Unmatched '('");
   }
   res.push(Ast{kind:Type::List,sval:None,ival:None,lval:Some(parse(a))});
  } else if ast[i].kind==Type::RP {
   panic!("Unexpected ')'");
  } else {
   res.push(ast[i].clone());
  }

  i+=1;
 }

 res.shrink_to_fit();
 return res;
}

fn to_ast(tokens:Vec<Token>)->Vec<Ast> {
 let mut res=Vec::<Ast>::with_capacity(16);
 let len=tokens.len();
 let mut i:usize=0;

 while i<len {
  res.push(Ast{kind:tokens[i].kind.clone(),sval:tokens[i].sval.clone(),ival:tokens[i].ival,lval:None});
  i+=1;
 }

 res.shrink_to_fit();
 return res;
}

fn lex(code:String) -> Vec<Token> {
 let mut i:usize=0;
 let mut word=String::new();
 let mut res=Vec::<Token>::with_capacity(8);
 let chars=code.chars().collect::<Vec<char>>();
 let len=code.len();

 while i<len {
  if chars[i]=='(' {
   res.push(Token{kind:Type::LP,sval:None,ival:None});
  } else if chars[i]==')' {
   res.push(Token{kind:Type::RP,sval:None,ival:None});
  } else if chars[i].is_ascii_digit() {
   while i<len && chars[i].is_ascii_digit() {
    word.push(chars[i]);
    i+=1;
   }
   res.push(Token{kind:Type::Atom,sval:None,ival:Some(word.parse::<i32>().unwrap())});
   word.clear();
   i-=1;
  } else if chars[i]=='"' {
   i+=1;
   let mut add:bool=true;
   while i<len && chars[i]!='"' {
    if chars[i]=='\\' {
     i+=1;
     match chars[i] {
      'n'=>word.push('\n'),
      't'=>word.push('\t'),
      '"'=>word.push('"'),
      _=>word.push_str(&format!("\\{}",chars[i])),
     }
     add=false;
    }
    if add { word.push(chars[i]); }
    i+=1;
    add=true;
   }
   res.push(Token{kind:Type::Atom,sval:Some(word.clone()),ival:None});
   word.clear();
  } else if !chars[i].is_ascii_whitespace() {
   while i<len && !chars[i].is_ascii_whitespace() {
    word.push(chars[i]);
    i+=1;
   }
   res.push(Token{kind:Type::Atom,sval:Some(word.clone()),ival:None});
   word.clear();
   i-=1;
  }

  i+=1;
 }

 res.shrink_to_fit();
 return res;
}

fn main() {
 let code=read_to_string("main.acedia").unwrap();
 let tokens=lex(code);
 let ast=parse_from_token(tokens);
 run(ast);
 return;
}
