# revolver-pin-combinator
### Software requirements:
Requires python3-more-itertools version 8.3.0+

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
Originally this program was written for the sparrows revolver training lock, but it can 
be used with any lock and any pin or spring type since pin naming in the pin file
is completely up to the user.  
See the included yml pin databases for more examples.

#### Included files
* **pin-combinator.py** - The program for calculating combinations.
* **pinfile-general-example.yml** - An example file showing how a pin database may look like.  
* **pinfile-revolver-all.yml** - Database of pins that came with my revolver lock.  
* **pinfile-revolver-standard.yml** - Modified database that creates all standard only 
pin combinations for my lock.  
* **Revolver-standard-only-locks.txt** - Example of standard only locks.  

#### Pin description
A pin is stored in the pin file like this:  
Pick two letters as the name, followed by the pin size and how many of such 
pins you have.    

This is a description of four standard pins of size 2:  
**ST-2-4**  
This is a description of six spool pins of size 1:  
**SP-1-6**

#### Spring description
A spring is stored in the pin file like this:
Pick two letters as the name, followed by the spring strength and how many of such 
springs you have.  

This is a description of a four copper springs of strength 1:  
**CO-1-4**  
This is a description of a five steel springs of strength 2:  
**ST-2-5**

#### Pin file structure
The pin file is divided into 3 sections:  
* **key-pins:**  
* **driver-pins:**  
* **springs:**
  
Each section contains a list of either pins or springs as described above. 

#### Output
The program saves lock combinations into bz2 compressed zip files in the same directory. 
Zip files are created from **600 MB** source text files. Each contains 5 000 000 lock 
combinations. At least 1 GB MB must be available on disk. The zips are up to **12 MB** 
each. A finished lock looks like this:  
```
Lock: 66:  
springs:     |CO1|CO1|ST1|ST2|CO1|ST1|  
driver pins: |MU1|SP1|MU1|SE1|MU1|ST1|  
key pins:    |ST1|ST2|ST5|ST2|ST3|ST3|  
```

### Usage
Create a pin database or use one of the examples from here.  
Run the pin-combinator.py program like this:  
```
Usage: pin-combinator.py -f PIN_FILE [options]

pin-combinator.py -f pinfile-example.yml -l 4
pin-combinator.py -f pinfile-example.yml -l 5 -s

For more information visit: https://github.com/Athwale/revolver-pin-combinator

Options:
  -h, --help            show this help message and exit
  -f PIN_FILE, --file=PIN_FILE
                        Select a pin database to use
  -l LOCK_SIZE, --lock=LOCK_SIZE
                        Select a lock size 1-20 pins (default 6)
  -s, --save            Do not print lock combinations on screen, save them
                        into files
```
Depending on how many different pin/spring types you have in your pin file, the 
selected lock size and the speed of your computer, the calculation may take several 
hours and a several GB of disk space.