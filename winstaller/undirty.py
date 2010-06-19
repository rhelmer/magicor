import sys

def move_replace(srcName, dstName, replace): 
    fsrc = file(srcName, 'r') 
    s=fsrc.read() 
    fsrc.close() 
    if replace is not None: 
        s=s.replace(replace[0],replace[1]) 
    fdst=file(dstName,'w') 
    fdst.write(s) 
    fdst.close() 

src=r'..\magicor\__init__.py'
dst=r'.\magi\magicor\__init__.py'
replace=["warnings.warn(\"error loading config '%s'; %s\"%(filename, ie))", "pass" ]

move_replace( src, dst, replace ) 
