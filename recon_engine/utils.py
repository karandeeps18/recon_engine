# utils.py holds reusable utility functions 

# read json and convert into pd.dataFrame 

def read_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
        df = pd.DataFrame(data['data'])
        return df


