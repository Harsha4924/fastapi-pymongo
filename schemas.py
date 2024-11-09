

def individual(t):
    return{
        'id':str(t['_id']),
        'name':t['name'],
        'description':t['description'],
        'createdby':t['created_by']
    }

def all_tasks(todos):
    return [individual(i) for i in todos]