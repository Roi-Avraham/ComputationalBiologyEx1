# Computational Biology Ex1

In this exercise we have to write a cellular automaton in which we investigated how a rumor distribution network works.
For the sake of researching this style, we created a 100x100 grid where each cell can be occupied by one person.
We denoted the population density by the parameter P which we will change throughout the study.
Each person in the population has a level of skepticism that is one of {s_4,s_3,s_2,s_1}, 
where these indicate: a person who does not believe any rumor, a person whose basic probability of believing a rumor is 1/3,
a person whose basic probability of believing a rumor is 2/3 and a person who believes .
for each rumor respectively.
The level of skepticism of each person is fixed randomly, and the percentage of people from each group of level of 
skepticism was also a parameter that we investigated. We chose the percentage of each group from the population by
using parameters 1S, 2S, 3S and 4S when they are also in accordance with the different levels of skepticism defined.

Basic rules of the network
1. First, we will select one person from the entire population who will determine to be the one who starts the rumor (passes it to all his neighbors).
2. The person who receives a rumor decides according to his level of skepticism whether to pass on the rumor
    a. If you chose to transfer the rumor - the transfer is always carried out in the next generation immediately after receiving the rumor
    b. Otherwise, continue without spreading.
3. If in the same generation a person receives a rumor from at least 2 different neighbors - his level of skepticism will temporarily drop
   to that generation and will act in the form of one level of skepticism below.
4. If a person passed on the rumor, he will not pass it on for L generations (a learned parameter) and then only if he receives a rumor 
   again will he be able to pass it on.
   
#Table of Contents
  Installation
  Usage
  
#Installation
