State Array: The state array will be passed around from node to node, and each index will contain important information to be read/changed by the nodes

state[0] = the question by the user : string
state[1] = the company data : json/string
state[2] = if the question is general or not : bool
state[3] = filepath for json file : string
state[4] = the llm's answer to the question
