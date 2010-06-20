import os

def freplace(fName,  replace): 
    fsrc = file(fName, 'rb') 
    s=fsrc.read() 
    fsrc.close() 
    if replace is not None: 
        s=s.replace(replace[0],replace[1]) 
    fdst=file(fName,'wb') 
    fdst.write(s) 
    fdst.close() 
 
replace = [ "\n" , '\r\n' ] 
path = r".\magi\dist"
freplace( os.path.join(path,'LICENCE.TXT'), replace )
