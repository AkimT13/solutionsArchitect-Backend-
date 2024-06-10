import json 

#this node loads the company data that the user is working for
def load_data(state):
    with open(state[4],'r') as file:
        data = json.load(file)
    return data
