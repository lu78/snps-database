#!/usr/bin/env python
# Create a database for HGDP data
"""
This is the schema for a database designed to handle HGDP SNPs data.
To use it, you should better use 'from connection import *' (see connection.py
script) to use the existing MySql database on my computer.

Uses Elixir syntax instead of sqlalchemy
- http://elixir.ematia.de/

To make this example working on your system, you will need:
- sqllite
- sqllite bindings for python
- sqlalchemy (best if installed with easy_install. version 0.5)
- elixir plugin for sqlalchemy
On an Ubuntu installation, you will do:
$: sudo apt-get install python-setuptools sqlite python-sqlite2
$: sudo easy_install sqlalchemy Elixir

>>> from elixir import *
>>> metadata.bind = 'sqlite:///:memory:'

#>>> metadata.bind.echo = True

# Create SQLAlchemy Tables along with their mapper objects
>>> setup_all()

# Issue the SQL command to create the Tables
>>> create_all()


Here they are some examples on how to create some individuals 
objects and define their populations.
# Let's create a population:        # TODO: use best examples
>>> pop1 = Population('greeks')

# You can define an individual' population by 
# defining its population field
>>> ind1 = Individual('Archimede')
>>> ind1.population = pop1

# You can also do it by appending an individual to pop.individuals
>>> ind2 = Individual('Spartacus')
>>> pop1.individuals.append(ind2)

# You can also define population and individuals at the same time  
>>> ind3 = Individual('Democritus', population = 'greeks')
>>> ind4 = Individual('ET', population = 'aliens')

>>> pop1.individuals
[Mr. ARCHIMEDE (greeks), Mr. SPARTACUS (greeks), Mr. DEMOCRITUS (greeks)]

>>> session.commit()
>>> Population.query().all()
[greeks, aliens]
>>> print Population.get_by(original_name = 'aliens').individuals
[Mr. ET (aliens)]
"""

from elixir import Entity, Field, Unicode, Integer, UnicodeText, String, Text
from elixir import ManyToOne, OneToMany, DateTime
from elixir import metadata, using_options
from elixir.ext.versioned import acts_as_versioned
from config import connection_line
from datetime import datetime

#from PopGen.Gio.Individual import Individual
#from PopGen.Gio.SNP import SNP
#from PopGen.Gio.Individual import Individual


class SNP(Entity):
    """ Table 'SNPs'.
    
    This class represents both the table SNP, and the structure of an instance of a SNP object
    
    >>> rs1333 = SNP('rs1333')
    """
    using_options(tablename = 'snps')
    
    id                  = Field(String(10), primary_key=True, unique=True)
    chromosome          = Field(String(10))
    physical_position   = Field(Integer)
    haplotypes_index    = Field(Integer)

    reference_allele    = Field(String(1))
    derived_allele      = Field(String(1))
    original_strand     = Field(String(1))
    dbSNP_ref           = Field(String(10))
    
    genotypes1          = Field(Text(2000))
    genotypes2          = Field(Text(2000))
    haplotypes_index    = Field(Integer)
    
    refseqgene          = ManyToOne('RefSeqGene')
    last_modified       = Field(DateTime, onupdate=datetime.now,
                                default=datetime.now)
    def __init__(self, id):
        self.id = id
        self.chromosome = ''
        self.genotypes1 = ''
        self.genotypes2 = ''
            
    def __repr__(self):
        # this method will be called when, in python code, you will do 'print SNP'.
        return 'SNP '  + self.id 

class Individual(Entity):
    """ Table 'Individuals'
    
    >>> ind = Individual('Einstein')
    >>> ind                              # Test __repr__ method
    Mr. EINSTEIN (None)
    >>> print ind + ' Albert'            # Test __add__ method
    EINSTEIN Albert
    >>> print ind in ('Einstein', )      # Test __eq__ method
    True
    
    # You can define an individual and a population in the same statement.
    # If the given population doesn't exists, a new record is initiated
    >>> ind2 = Individual('Spock', 'Vesuvians')
    >>> print ind2.population
    vesuvians
    
    """
    using_options(tablename = 'individuals')
    
    name                = Field(String(10), unique=True,)    # name?
    population          = ManyToOne('Population', )
    sex                 = Field(String(1), default='u')
    
    haplotypes          = Field(Text(650000))
    genotypes_index     = Field(Integer, unique=True)
    
    last_modified       = Field(DateTime, onupdate=datetime.now, 
                          default=datetime.now)
    
    def __init__(self, name, population = None, sex = None,
                 region = 'undef', macroarea = 'undef', working_unit = 'undef'):
        
        self.name = str(name).upper() # the individual's name
        
        # checks whether a population with the same name already exists.
        # If not, create it. 
        if population is not None:
            popname = str(population).lower()
            poprecord = Population.get_by(original_name = popname)
            if poprecord is None:
                poprecord = Population(original_name=popname, region=region, 
                                                continent_macroarea=macroarea, 
                                                working_unit = working_unit) 
            self.population = poprecord
            
        if sex is not None:
            sex = str(sex).lower()
            if sex in (1, '1', 'm', 'male',):
                self.sex = 'm'
            elif sex in (2, '2', 'f', 'female'):
                self.sex = 'f'
            else:
                self.sex = 'u'
        else:
            self.sex = 'u'
        
    def __repr__(self):
        if self.sex in ('m', 'u'):
            rep = "Mr. %s (%s)" % (self.name, self.population)
        else:
            rep = "Mrs. %s (%s)" % (self.name, self.population)
        return rep
    def __str__(self):
        return self.name
    def __add__(self, other):
        return str(self.name) + other 
    def __eq__(self, other):
        return self.name == str(other).upper()
    def __ne__(self, other):
        return self.name != str(other).upper()
    
    
class Population(Entity):
    """ Table 'Population'
    
    Population supports a methods called 'get_by_or_init', which enable you 
    to create an object in case it doesn't exists already.
    >>> martians = Population('martians')
    
    # It is recommended to use the 'set' method to modify a population's 
    # attribute after it has already been created.
    >>> martians.set('continent_macroarea', 'mars')
    >>> martians.continent_macroarea
    'mars'
    
    # You can also modify a pop's attributes manually, but remenber to use 
    # lower case strings 
    >>> martians.continent_macroarea = 'Mars'    # will give you trouble
    ...                                          # because is not lowercase.
    
    """
    using_options(tablename = 'populations')
    
#    id = Field(Integer, primary_key = True)    # created automatically
    individuals         = OneToMany('Individual')
    original_name       = Field(String(50), unique=True)
    region              = Field(String(50))
    working_unit        = Field(String(50))
    continent_macroarea = Field(String(30))
    
#    version                 = Column(Integer, ForeignKey('versions.id'))
    last_modified       = Field(DateTime, onupdate=datetime.now,
                                default = datetime.now)
    
    def __init__(self, original_name, working_unit='undef', 
                 region = 'undef', continent_macroarea='undef'):
        #TODO: add a set method
        self.original_name = str(original_name).lower()
        self.working_unit = str(working_unit).lower()
        self.region = str(region.lower())
        self.continent_macroarea = str(continent_macroarea).lower()
        
    def set(self, name, value):
        setattr(self, name, str(value).lower())        
        
    def __repr__(self):
        return self.original_name
    
    def __str__(self):
        return str(self.original_name)
    
    def __eq__(self, other):
        return str(self.original_name) == str(other).lower()
    def __ne__(self, other):
        return str(self.original_name) == str(other).lower()

class RefSeqGene(Entity):
    """ Table 'RefSeqGene'
    """
    using_options(tablename = 'refseqgenes')
    pass    
    
    
    
def _test():
    """ test the current module"""
    import doctest
    doctest.testmod()
    
if __name__ == '__main__':
    _test()
    # could launch test_insert_data here?
#    from elixir import setup_all, create_all, session
        
        
        