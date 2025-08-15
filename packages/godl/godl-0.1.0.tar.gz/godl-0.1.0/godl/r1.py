# godl/r1.py
def main():
    code = """1)vectors of a variable length program.

{
  x=c(4,5,6)
  y=c(12,1,2,3,4)
  if(length(x)==length(y))
  {
    print("both vectors of same length")
  }
  else
  {
    print("both vectors are not of same lenghth")
  }
}

"""
    print(code)

