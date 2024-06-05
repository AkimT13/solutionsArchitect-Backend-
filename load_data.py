import json 

#this node loads the company data that the user is working for
def load_data(file_path):
    with open(file_path,'r') as file:
        data = json.load(file)
    return data
