import sqlite3
from pathlib import Path
DB_PATH=Path(__file__).resolve().parent/'learnsphere.db'
def connect():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    c=connect(); c.executescript('''CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,path TEXT NOT NULL,page_count INTEGER NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY AUTOINCREMENT,document_id INTEGER NOT NULL,page_number INTEGER NOT NULL,text TEXT NOT NULL,FOREIGN KEY(document_id) REFERENCES documents(id));CREATE TABLE IF NOT EXISTS concepts(id INTEGER PRIMARY KEY AUTOINCREMENT,document_id INTEGER NOT NULL,name TEXT NOT NULL,score REAL NOT NULL DEFAULT 0,mastery REAL NOT NULL DEFAULT .5,attempts INTEGER NOT NULL DEFAULT 0,correct INTEGER NOT NULL DEFAULT 0,last_practiced TEXT,FOREIGN KEY(document_id) REFERENCES documents(id));CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY AUTOINCREMENT,concept_id INTEGER NOT NULL,question TEXT NOT NULL,options TEXT NOT NULL,answer INTEGER NOT NULL,explanation TEXT NOT NULL,source_page INTEGER,FOREIGN KEY(concept_id) REFERENCES concepts(id));CREATE TABLE IF NOT EXISTS answers(id INTEGER PRIMARY KEY AUTOINCREMENT,question_id INTEGER NOT NULL,concept_id INTEGER NOT NULL,selected INTEGER NOT NULL,correct INTEGER NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);'''); c.commit(); c.close()
def add_document(name,path,pages):
    c=connect(); x=c.execute('INSERT INTO documents(name,path,page_count) VALUES(?,?,?)',(name,path,pages)); c.commit(); i=x.lastrowid;c.close();return i
def add_chunks(doc,pages):
    c=connect();c.executemany('INSERT INTO chunks(document_id,page_number,text) VALUES(?,?,?)',[(doc,p,t) for p,t in pages]);c.commit();c.close()
def add_concepts(doc,items):
    c=connect();c.executemany('INSERT INTO concepts(document_id,name,score,mastery) VALUES(?,?,?,.5)',[(doc,n,s) for n,s in items]);c.commit();c.close()
def get_concepts(doc):
    c=connect();r=c.execute('SELECT * FROM concepts WHERE document_id=? ORDER BY score DESC',(doc,)).fetchall();c.close();return r
def get_chunks(doc):
    c=connect();r=c.execute('SELECT page_number,text FROM chunks WHERE document_id=? ORDER BY page_number',(doc,)).fetchall();c.close();return r
def clear_questions(doc):
    c=connect();c.execute('DELETE FROM questions WHERE concept_id IN (SELECT id FROM concepts WHERE document_id=?)',(doc,));c.commit();c.close()
def add_question(cid,q,opts,ans,exp,page):
    c=connect();x=c.execute('INSERT INTO questions(concept_id,question,options,answer,explanation,source_page) VALUES(?,?,?,?,?,?)',(cid,q,'||'.join(opts),ans,exp,page));c.commit();i=x.lastrowid;c.close();return i
def get_questions(doc,limit=10):
    c=connect();r=c.execute('SELECT q.*,c.name concept_name,c.mastery FROM questions q JOIN concepts c ON q.concept_id=c.id WHERE c.document_id=? ORDER BY c.mastery ASC,q.id ASC LIMIT ?',(doc,limit)).fetchall();c.close();return r
def record_answer(qid,cid,selected,correct):
    c=connect();c.execute('INSERT INTO answers(question_id,concept_id,selected,correct) VALUES(?,?,?,?)',(qid,cid,selected,int(correct)));c.commit();c.close()
def update_concept(cid,mastery,correct):
    c=connect();c.execute('UPDATE concepts SET mastery=?,attempts=attempts+1,correct=correct+?,last_practiced=CURRENT_TIMESTAMP WHERE id=?',(mastery,int(correct),cid));c.commit();c.close()
