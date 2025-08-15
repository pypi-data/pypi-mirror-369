# godl/r1.py
def main():
    code = """5) find a factorial using recursation program
    

{
  fact<-function(n)
  {
    if(n<=1)
      return(1)
    else
      return(n*factorial(n-1))
  }
  n<-as.numeric(readline("enter n value:"))
  print(paste("fact of number is:",fact(n)))
} 


"""
    print(code)

