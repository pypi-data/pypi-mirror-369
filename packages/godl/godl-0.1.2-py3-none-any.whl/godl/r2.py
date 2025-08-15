# godl/r1.py
def main():
    code = """2)print error msg program


{
  for(i in 1:10)
  {
    print(paste("i=",i))
    if(i==5)
      stop("iteration stopped(on condition at i=5")
  }
}


"""
    print(code)

