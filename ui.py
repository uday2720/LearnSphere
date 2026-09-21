from pathlib import Path
from PySide6.QtWidgets import QApplication,QFileDialog,QFrame,QHBoxLayout,QLabel,QMainWindow,QMessageBox,QProgressBar,QPushButton,QRadioButton,QScrollArea,QStackedWidget,QTextEdit,QVBoxLayout,QWidget
from concept_extractor import extract_concepts
from config import APP_NAME,APP_VERSION,DEFAULT_TOP_CONCEPTS,DIAGNOSTIC_QUESTIONS
from db import init_db,add_document,add_chunks,add_concepts,get_concepts,get_chunks,clear_questions,add_question,get_questions,record_answer,update_concept
from pdf_processor import extract_pdf
from mastery import label,next_best_concept,update_mastery
from quiz import generate_questions
from rag import LocalRetriever,answer_locally
from snapdragon import system_summary,acceleration_status

class MainWindow(QMainWindow):
 def __init__(self):
  super().__init__();init_db();self.doc=None;self.retriever=None;self.questions=[];self.qi=0;self.score=0
  self.setWindowTitle(f'{APP_NAME} {APP_VERSION}');self.resize(1120,760)
  root=QWidget();self.setCentralWidget(root);main=QVBoxLayout(root)
  head=QHBoxLayout();t=QLabel('🧠 LearnSphere');t.setObjectName('title');head.addWidget(t);head.addStretch();head.addWidget(QLabel('Private • Adaptive • Local-first'));main.addLayout(head)
  nav=QHBoxLayout();self.stack=QStackedWidget()
  for text,i in [('Knowledge Map',0),('Diagnostic',1),('Tutor',2),('System',3)]:
   b=QPushButton(text);b.clicked.connect(lambda _,x=i:self.stack.setCurrentIndex(x));nav.addWidget(b)
  main.addLayout(nav);main.addWidget(self.stack)
  self.map_page();self.quiz_page();self.tutor_page();self.system_page();self.style()
 def map_page(self):
  p=QWidget();l=QVBoxLayout(p);self.status=QLabel('Upload a study PDF to begin.');l.addWidget(self.status)
  row=QHBoxLayout();b=QPushButton('＋ Add Study PDF');b.clicked.connect(self.import_pdf);row.addWidget(b);self.gen=QPushButton('Generate Diagnostic');self.gen.setEnabled(False);self.gen.clicked.connect(self.prepare_quiz);row.addWidget(self.gen);row.addStretch();l.addLayout(row)
  f=QFrame();r=QVBoxLayout(f);h=QLabel('🎯 Next Best Learning Activity');h.setObjectName('section');r.addWidget(h);self.rec=QLabel('Upload a PDF first.');self.rec.setWordWrap(True);r.addWidget(self.rec);l.addWidget(f)
  l.addWidget(self.section('🧠 Knowledge Map'));self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.cards=QWidget();self.cardsl=QVBoxLayout(self.cards);self.cardsl.addStretch();self.scroll.setWidget(self.cards);l.addWidget(self.scroll);self.stack.addWidget(p)
 def section(self,x):
  q=QLabel(x);q.setObjectName('section');return q
 def quiz_page(self):
  p=QWidget();l=QVBoxLayout(p);self.qtitle=QLabel('📝 Diagnostic Assessment');self.qtitle.setObjectName('section');l.addWidget(self.qtitle);self.qq=QLabel('Generate a diagnostic from your study material.');self.qq.setWordWrap(True);l.addWidget(self.qq);self.rad=[]
  for _ in range(4):r=QRadioButton();r.setMinimumHeight(34);self.rad.append(r);l.addWidget(r)
  self.feedback=QLabel('');self.feedback.setWordWrap(True);l.addWidget(self.feedback);row=QHBoxLayout();self.check=QPushButton('Check Answer');self.check.clicked.connect(self.check_answer);self.check.setEnabled(False);self.next=QPushButton('Next');self.next.clicked.connect(self.next_q);self.next.setEnabled(False);row.addWidget(self.check);row.addWidget(self.next);l.addLayout(row);l.addStretch();self.stack.addWidget(p)
 def tutor_page(self):
  p=QWidget();l=QVBoxLayout(p);l.addWidget(self.section('🤖 Private Study Tutor'));self.tin=QTextEdit();self.tin.setPlaceholderText('Ask about your uploaded study material…');self.tin.setMaximumHeight(120);l.addWidget(self.tin);b=QPushButton('Ask LearnSphere');b.clicked.connect(self.ask);l.addWidget(b);self.tout=QTextEdit();self.tout.setReadOnly(True);l.addWidget(self.tout);self.stack.addWidget(p)
 def system_page(self):
  p=QWidget();l=QVBoxLayout(p);l.addWidget(self.section('⚡ Device & Privacy'));self.sys=QTextEdit();self.sys.setReadOnly(True);info=system_summary();self.sys.setText('Local-first runtime\n\n'+'\n'.join(f'{k}: {v}' for k,v in info.items())+'\n\n'+acceleration_status()+'\n\nPrivacy: the MVP performs document processing, retrieval and quiz storage locally; it does not require an external API key.');l.addWidget(self.sys);self.stack.addWidget(p)
 def import_pdf(self):
  path,_=QFileDialog.getOpenFileName(self,'Choose study PDF',str(Path.home()),'PDF files (*.pdf)')
  if not path:return
  try:
   res=extract_pdf(path)
   if not res['pages']:raise ValueError('No extractable text was found. This may be an image-only PDF.')
   self.doc=add_document(res['name'],res['path'],res['page_count']);add_chunks(self.doc,res['pages']);items=extract_concepts(res['pages'],DEFAULT_TOP_CONCEPTS);add_concepts(self.doc,items);self.retriever=LocalRetriever(get_chunks(self.doc));self.render();self.gen.setEnabled(bool(items));self.status.setText(f'✓ {res["name"]} processed locally — {res["page_count"]} pages, {len(items)} concepts.')
  except Exception as e:QMessageBox.critical(self,'LearnSphere error',str(e))
 def render(self):
  while self.cardsl.count():
   it=self.cardsl.takeAt(0)
   if it.widget():it.widget().deleteLater()
  cs=get_concepts(self.doc)
  for c in cs:
   f=QFrame();v=QVBoxLayout(f);v.addWidget(QLabel(f'<b>{c["name"]}</b>'));bar=QProgressBar();bar.setValue(int(c['mastery']*100));bar.setFormat(f'{int(c["mastery"]*100)}% — {label(c["mastery"])}');v.addWidget(bar);self.cardsl.addWidget(f)
  self.cardsl.addStretch();best=next_best_concept(cs)
  if best:self.rec.setText(f'<b>{best["name"]}</b><br>Current status: {label(best["mastery"])}.<br>Priority is driven by current mastery and retention.')
 def prepare_quiz(self):
  clear_questions(self.doc);items=generate_questions(get_concepts(self.doc),get_chunks(self.doc))
  for x in items:add_question(x['concept_id'],x['question'],x['options'],x['answer'],x['explanation'],x['source_page'])
  self.questions=get_questions(self.doc,DIAGNOSTIC_QUESTIONS);self.qi=0;self.score=0
  if not self.questions:QMessageBox.warning(self,'Diagnostic unavailable','Try a text-rich study PDF.');return
  self.stack.setCurrentIndex(1);self.show_q()
 def show_q(self):
  if self.qi>=len(self.questions):return self.finish()
  q=self.questions[self.qi];self.qtitle.setText(f'📝 Diagnostic — {self.qi+1}/{len(self.questions)} • {q["concept_name"]}');self.qq.setText(q['question']);opts=q['options'].split('||')
  for i,r in enumerate(self.rad):r.setText(opts[i] if i<len(opts) else '');r.setVisible(i<len(opts));r.setChecked(False)
  self.feedback.setText('');self.check.setEnabled(True);self.next.setEnabled(False)
 def selected(self):
  for i,r in enumerate(self.rad):
   if r.isChecked():return i
  return None
 def check_answer(self):
  s=self.selected()
  if s is None:return QMessageBox.information(self,'Choose an answer','Please select an option.')
  q=self.questions[self.qi];ok=s==q['answer'];old=q['mastery'];new=update_mastery(old,ok);record_answer(q['id'],q['concept_id'],s,ok);update_concept(q['concept_id'],new,ok);self.score+=int(ok);self.feedback.setText(('✅ Correct. ' if ok else '❌ Not quite. ')+q['explanation']+f'\n\nMastery: {old:.0%} → {new:.0%}');self.check.setEnabled(False);self.next.setEnabled(True)
 def next_q(self):self.qi+=1;self.show_q()
 def finish(self):
  cs=get_concepts(self.doc);best=next_best_concept(cs);self.qtitle.setText('🎉 Diagnostic Complete');self.qq.setText(f'Score: {self.score}/{len(self.questions)}\n\nNext best topic: {best["name"] if best else "—"}');[r.setVisible(False) for r in self.rad];self.feedback.setText('Your mastery profile has been updated. Return to Knowledge Map to see the changes.');self.check.setEnabled(False);self.next.setEnabled(False);self.render()
 def ask(self):
  q=self.tin.toPlainText().strip();self.tout.setText('Upload a study PDF first.' if not self.retriever else answer_locally(q,self.retriever.search(q,3)))
 def style(self):
  self.setStyleSheet('''QWidget{font-family:Segoe UI;font-size:14px}QMainWindow{background:#f5f7fb}QFrame{background:white;border:1px solid #e1e5ec;border-radius:10px}#title{font-size:28px;font-weight:700}#section{font-size:19px;font-weight:700}QPushButton{background:#202938;color:white;border:none;border-radius:8px;padding:9px 14px;font-weight:600}QProgressBar{border:1px solid #d8dde6;border-radius:6px;text-align:center;height:24px}QProgressBar::chunk{background:#64748b;border-radius:5px}''')
def run():
 app=QApplication([]);w=MainWindow();w.show();app.exec()
