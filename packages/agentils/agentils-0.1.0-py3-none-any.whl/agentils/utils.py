import json

class Utils:
    @staticmethod
    def string_to_dict(s):
        try:
            # Remove any ```python``` or ``` markers if present
            s = s.replace('```python', '').replace('```', '').strip()
            return json.loads(s)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid string format: {str(e)}"}
        
        
    @staticmethod
    def dict_to_string(d):
        try:
            return json.dumps(d, indent=2)
        except TypeError as e:
            return f"Error: Invalid dictionary format: {str(e)}"
        
        
        
    @staticmethod
    def save_dict_to_file(d, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(d, f, indent=2)
    
        except IOError as e:
            print(f"Error saving dictionary to file: {str(e)}")
            
            
    
    @staticmethod
    def load_dict_from_file(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading dictionary from file: {str(e)}")
            return None
        
    @staticmethod
    def save_string_to_file(s, filename):
        try:
            with open(filename, 'w') as f:
                f.write(s)
        except IOError as e:
            print(f"Error saving string to file: {str(e)}")

    
    