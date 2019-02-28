# Resolve the environment variable $ROBOT_ENV
l_envs = []
def load_knowledge(knowledge_item, print_knowledge=False):
	global l_envs
	import os, sys, imp
	directory = os.path.dirname(os.path.realpath(__file__)) + "/environments"
	envs_path = [x[0] for x in os.walk(directory)][1:]
	envs = [x.split('/')[-1] for x in envs_path]
	envs_s = sorted(envs, key=str.lower)
	knowleges = {}
	for _robot_env in envs_s:
		#_robot_env = path.split('/')[-1]
		# Look for the correct knowledge file
		#print(_robot_env)
		try:
			_knowledge_path = os.path.dirname(os.path.realpath(__file__)) + "/environments/%s/%s.py" % (_robot_env, knowledge_item)
			knowledge = imp.load_source(knowledge_item, _knowledge_path)

			knowledge_attrs = [attr for attr in dir(knowledge) if not callable(attr) and not attr.startswith("__")]
			knowledge_dict = {}
			if print_knowledge:
				print "====================================="
				print "==          KNOWLEDGE              =="
				print "====================================="
				for attr in knowledge_attrs:
					knowledge_dict[str(attr)] = getattr(knowledge, attr)
				print "====================================="

			knowleges[_robot_env] = knowledge_dict
			l_envs.append(_robot_env)
		except Exception as e:
			#print "Knowledge item '%s' for environment '%s' is incorrect at path '%s'! [Error = %s]"%(knowledge_item, _robot_env, _knowledge_path, e)
			#sys.exit(1)
			continue
	return knowleges
		
def containOnDict(element, _dict):
    exists = False
    for key in _dict:
        if(element in _dict[key]):
            exists = True
    return exists
	
import environments
knowleges = load_knowledge('common', print_knowledge=True)
attr = 'location_names'
dic={}
for key in l_envs:
	dic[key] = []
	#print('#'+key)
	knowledge = knowleges[key]
	#print(knowledge[attr])
	#attr_list = ['location_names','location_rooms', 'location_categories', 'grab_locations', 'put_locations', 'category_locations', 'inspect_areas', 'inspect_positions', 'rooms', 'location_manipulatable']
	#attr_list = ['object_names', 'object_categories', 'object_groups', 'object_placements', 'object_known_objects']
	#attr_list = ['female_names']
	attr_list = ['male_names', 'female_names']
	for attr in attr_list:
		try:
			for location in knowledge[attr]:
				element = (" ".join(location.split("_"))).lower()
				if(not containOnDict(element, dic)):
					dic[key].append(element)
		except Exception as e:
			continue
			
for key in l_envs:
    print('//'+key)
    for element in dic[key]:
        print(element)