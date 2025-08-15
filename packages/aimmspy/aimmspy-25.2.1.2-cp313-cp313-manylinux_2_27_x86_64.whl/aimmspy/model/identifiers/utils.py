from varname import varname

def varname_or_default(**kwargs):
    name = kwargs.get('name', None)
    if name is None:
        name = varname( frame=2 )
    #remove name from kwargs
    if 'name' in kwargs:
        del kwargs['name']
    
    return (name, kwargs)