import re
from collections import Counter

def sentences(text):
    return [p.strip() for p in re.split(r'(?<=[.!?])\s+',' '.join(text.split())) if len(p.strip())>=45]

def generate_questions(concepts,chunks):
    result=[]
    for c in concepts:
        matches=[]
        for row in chunks:
            for s in sentences(row['text']):
                if any(t.lower() in s.lower() for t in c['name'].split() if len(t)>3): matches.append((row['page_number'],s))
        if not matches: continue
        page,s=matches[0]
        words=re.findall(r'\b[A-Za-z][A-Za-z-]{4,}\b',s)
        distractors=[w.title() for w,_ in Counter(w.lower() for w in words).most_common() if w.lower()!=c['name'].lower()][:3]
        opts=[c['name']]+distractors
        for filler in ['Definition','Example','Algorithm','Property']:
            if len(opts)<4 and filler not in opts:opts.append(filler)
        result.append({'concept_id':c['id'],'concept':c['name'],'question':f"Which concept is most directly associated with this passage?\n\n{s[:350]}",'options':opts[:4],'answer':0,'explanation':f"The passage on page {page} was matched to '{c['name']}'.",'source_page':page})
        if len(result)>=10:break
    return result
