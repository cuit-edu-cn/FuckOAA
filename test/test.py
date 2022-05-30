import sys 
sys.path.append("..") 
from cuit import FC


if __name__ == "__main__":
    print("test")
    cuit = FC("1234", "2342")
    courseList = cuit.courseName2Id("数字孪生技术")
    print(courseList)
    pass