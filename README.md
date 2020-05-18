# revolver-pin-combinator
### What this is
A small program for generating pin combinations for the sparrows revolver lock.
It comes with a pin database filled with pins and springs from my sparrows revolver.
It is likely that your lock came with a slightly different pin set. But you should
be able to modify the pin database according to your lock with the information
on this page.

### Purpose
This tool creates all possible key pin, driver pin, spring combinations for the
pins and springs you put into the pin file.  
There are several pin files included with the program.  
Originally this program was written for the revolver training lock, but it can 
be used with any lock and any pin or spring type since pin naming in the pin file
is completely up to the user.  
See the included yml pin databases for more examples.

#### Pin description
A pin is stored in the pin file like this:  
Pick two letters as the name, followed by the pin size and how many of such 
pins you have.    

This is a description of four standard pins of size 2:  
ST-2-4  
This is a description of six spool pins of size 1:  
SP-1-6

#### Spring description
A spring is stored in the pin file like this:
Pick two letters as the name, followed by the spring strength and how many of such 
springs you have.  

This is a description of a four copper springs of strength 1:  
CO-1-4  
This is a description of a five steel springs of strength 2:  
ST-2-5

#### Pin file structure
The pin file is divided into 3 sections:  
key-pins:  
driver-pins:  
springs:  
Each section contains a list of either pins or springs as described above. 
