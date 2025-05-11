MERGE (r:Root {name:'فعل'})

MERGE (t0:Tense {name:'Perfect', root: r.name})
MERGE (t1:Tense {name:'Present', root: r.name})
MERGE (t2:Tense {name:'Imperative', root: r.name})
MERGE (t3:Tense {name:'VerbalNoun', root: r.name})
MERGE (t4:Tense {name:'ActiveParticiple', root: r.name})
MERGE (t5:Tense {name:'PassiveParticiple', root: r.name})

WITH r, ['Perfect', 'Present', 'Imperative'] AS tenses,
    ['First', 'Second', 'Third'] AS persons,
    ['Singular', 'Dual', 'Plural'] AS numbers,
    ['Masculine', 'Feminine'] AS genders

UNWIND tenses AS tense
UNWIND persons AS person
UNWIND numbers AS number
UNWIND genders AS gender
MERGE (p:Person {name: person, tense: tense, root: r.name})
MERGE (n:Number {name: number, root: r.name, tense: tense, person: p.name})
MERGE (g:Gender {name: gender, root: r.name, tense: tense, person: p.name, number: n.name})
MERGE (p)-[:HAS_NUMBER {root: r.name}]->(n)
MERGE (n)-[:HAS_GENDER {root: r.name}]->(g)

WITH r
MATCH (t:Tense)
MERGE (r)-[:HAS_TENSE {root:r.name}]->(t)

WITH t, r
MATCH (p:Person)
WHERE p.tense = t.name
MERGE (t)-[:HAS_PERSON {root:r.name}]->(p)

WITH r, ['ActiveParticiple', 'PassiveParticiple'] AS tenses,
    ['First', 'Second', 'Third'] AS persons,
    ['Singular', 'Dual', 'Plural'] AS numbers,
    ['Masculine', 'Feminine'] AS genders
UNWIND tenses AS tense
UNWIND persons AS person
UNWIND numbers AS number
UNWIND genders AS gender
MERGE (p:Person {name: person, tense: tense, root: r.name})
MERGE (n:Number {name: number, root: r.name, tense: tense, person: p.name})
MERGE (g:Gender {name: gender, root: r.name, tense: tense, person: p.name, number: n.name})
MERGE (p)-[:HAS_NUMBER {root: r.name}]->(n)
MERGE (p)-[:HAS_GENDER {root: r.name}]->(g)