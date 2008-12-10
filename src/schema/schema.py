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

>>> pop1 = Population('martians')
>>> ind1 = Individual('Einstein')
>>> ind1.population = pop1

>>> ind2 = Individual('Marx')
>>> pop1.individuals.append(ind2)

>>> pop1.individuals
[Mr. Einstein (martians), Mr. Marx (martians)]

>>> session.commit()
>>> Individual.query().all()
[Mr. Einstein (martians), Mr. Marx (martians)]
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

# add the get_by_or_init method to entity, see recipe
# http://elixir.ematia.de/trac/wiki/Recipes/GetByOrAddPattern#GetByorAddPattern
def get_by_or_init(cls, if_new_set={}, **params):
    """Call get_by; if no object is returned, initialize an
    object with the same parameters.  If a new object was
    created, set any initial values."""
    
    result = cls.get_by(**params)
    if not result:
        result = cls(**params)
        result.set(**if_new_set)
    return result

Entity.get_by_or_init = classmethod(get_by_or_init)


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
    
    genotypes           = Field(Text(2000))
    haplotypes_index    = Field(Integer)
    
    refseqgene          = ManyToOne('RefSeqGene')
    last_modified       = Field(DateTime, onupdate=datetime.now,
                                default = datetime.now)
    def __init__(self, snp_id):
        self.id = snp_id
        self.chromosome = ''
            
    def __repr__(self):
        # this method will be called when, in python code, you will do 'print SNP'.
        return 'SNP '  + self.id 

class Individual(Entity):
    """ Table 'Individuals'
    
    >>> ind = Individual('Einstein')
    >>> ind                              # Test __repr__ method
    Mr. Einstein (None)
    >>> print ind + ' Albert'            # Test __add__ method
    Einstein Albert
    >>> print ind in ('Einstein', )      # Test __eq__ method
    True
    """
    using_options(tablename = 'individuals')
    
    identificator       = Field(String(10), unique=True)
    population          = ManyToOne('Population', )
    sex                 = Field(String(1), default='u')
    
    haplotypes          = Field(Text(650000))
    genotypes_index     = Field(Integer, unique=True)
    
    last_modified       = Field(DateTime, onupdate=datetime.now, 
                          default = datetime.now)
    
    def __init__(self, identificator = None, population = None, sex = None):
        self.identificator = identificator
        if population is not None:
            population = str(population).lower()
            self.population = Population.get_by_or_init(population)
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
            rep = "Mr. %s (%s)" % (self.identificator, self.population)
        else:
            rep = "Mrs. %s (%s)" % (self.identificator, self.population)
        return rep
    def __str__(self):
        return self.identificator
    def __add__(self, other):
        return str(self.identificator) + other 
    def __eq__(self, other):
        return self.identificator == other
    def __ne__(self, other):
        return self.identificator != other
    
    
class Population(Entity):
    """ Table 'Population'
    
    Population support a methods called 'get_by_or_init', which enable you 
    to create an object in case it doesn't exists already.
    >>> martians = Population('martians')
    >>> martians.continent_macroarea = 'Mars'
    >>> print martians.continent_macroarea
    Mars
    
    >>> martians_again = Population.get_by_or_init('martians')
    >>> print martians_again.continent_macroarea
    Mars
    """
    using_options(tablename = 'populations')
    
#    id = Field(Integer, primary_key = True)    # created automatically
    individuals         = OneToMany('Individual')
    original_name       = Field(String(50), unique=True)
    working_unit        = Field(String(50))
    continent_macroarea = Field(String(30))
    
#    version                 = Column(Integer, ForeignKey('versions.id'))
    last_modified       = Field(DateTime, onupdate=datetime.now,
                                default = datetime.now)
    
    def __init__(self, original_name=None, working_unit=None, continent_macroarea=None):
        self.original_name = str(original_name).lower()
        self.working_unit = str(working_unit).lower()
        self.continent_macroarea = str(continent_macroarea).lower()
        
    def __repr__(self):
        return str(self.original_name)

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
#    from elixir import setup_all, create_all, session
        
        
        