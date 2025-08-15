import ast
from typing import Counter


class Rejections:
    def __init__(self):
        pass
    
    def number_of_objects(self,det_num_of_obj, orig_num_of_obj=1):
        print("it sherer ", len(det_num_of_obj))
        if orig_num_of_obj== len(det_num_of_obj):
            status = "good"
        else:
            status  = "not good"
        return status
    
    def multi_number_of_objects(self, det_num_of_obj, orig_num_of_obj={0: (0, 1)}):
        status = "good"
        print(orig_num_of_obj, type(orig_num_of_obj))
        orig_num_of_obj = ast.literal_eval(orig_num_of_obj)
        
        classes = [item['class_id'] for item in det_num_of_obj]
        class_count = dict(Counter(classes))

        print(class_count)
        print(orig_num_of_obj)
        
        for key in orig_num_of_obj:
            min_val, max_val = orig_num_of_obj[key]
            count = class_count.get(key, 0)
            if not (min_val <= count <= max_val):
                status = "not good"
                break

        return status
