# file handling

# RAM ---> volatile
# ROM ---> 
# folder\abc.txt ---> "this is me"

# READ mode
# file = open("abc.txt", 'r')
# data = file.read()
# file.close()
# print(data)


# WRITE mode
# data = "hello how are you"
# file = open("abc.txt","w")
# file.write(data)
# file.close()

# append mode

# data = "\nhello how are you"
# file = open("abc.txt","a")
# file.write(data)
# file.close()


# ╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩╦╩

# path = r"""D:\workspace\python\dipak\interview-questions\demo.txt"""

# myText = "this ne new sentance for overwriting file using W mode"
# myText2 = "\nthis is sample text"
# print(f"total length of string :{len(myText)}")

# with open(path,'a') as myFile:
#     print(myFile.write(myText2))

# path = r"D:\workspace\python\dipak\interview-questions\users.csv"

# with open(path,'r') as csvFile:
#     reader = csvFile.read().split("\n")
#     # columns = [ col for col in reader[0].split(",")]
#     # print(columns)
    
#     columns = []
#     userData = []
#     fullnames = []
#     for index,row in enumerate(reader):
#         if index ==0:
#             columns = row.split(",")
#         else:
#             userData.append(row.split(","))

#     firstIndex = columns.index("firstname")
#     lastIndex = columns.index("lastname")
#     for user in userData:
#         fullnames.append(user[firstIndex] + " " + user[lastIndex])


#     print(columns)
#     print(userData)
#     print(fullnames)