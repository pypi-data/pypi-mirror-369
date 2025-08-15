# godl/r1.py
def main():
    code = """4)read&write a file program


output_file_path<-"D:\\out.txt"
data<-"hello,my name is virat"
paste("written successfully",writeLines(data,output_file_path))
paste("reading a file=",readLines("D:\\out.txt"))



"""
    print(code)

