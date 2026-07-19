#!/usr/bin/env python3
import json, re, shutil, sys
from pathlib import Path
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
OUT_DATA = ROOT / 'data'
OUT_IMG = ROOT / 'assets' / 'questions'
OUT_DATA.mkdir(exist_ok=True)
OUT_IMG.mkdir(parents=True, exist_ok=True)

EXAM_RE = re.compile(r'^EXAM\s+(\d+)\b(.*)$', re.I)
Q_RE = re.compile(r'^Câu\s*hỏi\s+(\d+)\b', re.I)
OPT_RE = re.compile(r'^([a-gA-G])[\.)]?\s*$')
ANS_RE = re.compile(r'^Đáp\s*án\s*:\s*(.+)$', re.I)
EXP_RE = re.compile(r'^Lời\s*giải\s*:\s*(.*)$', re.I)

def clean(s):
    return re.sub(r'\s+', ' ', s.replace('\xa0',' ')).strip()

def para_images(paragraph, doc, qid):
    paths=[]
    for blip in paragraph._p.xpath('.//a:blip'):
        rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        if not rid or rid not in doc.part.related_parts: continue
        part = doc.part.related_parts[rid]
        ext = Path(str(part.partname)).suffix or '.png'
        name = f'{qid}-{len(paths)+1}{ext}'
        dest = OUT_IMG / name
        dest.write_bytes(part.blob)
        paths.append(f'assets/questions/{name}')
    return paths

def convert(path):
    doc=Document(path)
    exams=[]; exam=None; q=None; mode='question'; pending_opt=None

    def finish_q():
        nonlocal q
        if not q: return
        q['question']=clean(' '.join(q['questionParts']))
        q['explanation']=clean(' '.join(q['explanationParts']))
        q.pop('questionParts',None); q.pop('explanationParts',None)
        q['options']=[o for o in q['options'] if o['text']]
        if q['question'] and q['options']:
            exam['questions'].append(q)
        q=None

    def finish_exam():
        nonlocal exam
        finish_q()
        if exam and exam['questions']: exams.append(exam)
        exam=None

    for p in doc.paragraphs:
        raw=p.text.strip(); text=clean(raw)
        m=EXAM_RE.match(text)
        if m:
            finish_exam(); num=int(m.group(1)); title=text
            exam={'id':f'exam-{num}','title':title,'questions':[]}; mode='question'; pending_opt=None
            continue
        m=Q_RE.match(text)
        if m and exam:
            finish_q(); n=int(m.group(1)); qid=f"{exam['id']}-q{n:03d}"
            q={'id':qid,'number':n,'questionParts':[],'options':[],'correctAnswers':[], 'explanationParts':[], 'images':[]}
            mode='question'; pending_opt=None
            q['images'] += para_images(p, doc, qid)
            continue
        if not q: continue
        q['images'] += para_images(p, doc, q['id'])
        if not text: continue
        m=ANS_RE.match(text)
        if m:
            q['correctAnswers']=[x.upper() for x in re.findall(r'[A-G]', m.group(1), re.I)]
            mode='after_answer'; pending_opt=None; continue
        m=EXP_RE.match(text)
        if m:
            mode='explanation'; pending_opt=None
            if m.group(1): q['explanationParts'].append(m.group(1))
            continue
        m=OPT_RE.match(text)
        if m and mode != 'explanation':
            pending_opt=m.group(1).upper(); q['options'].append({'id':pending_opt,'text':''}); mode='options'; continue
        if mode=='explanation': q['explanationParts'].append(text)
        elif mode=='options' and q['options']:
            if q['options'][-1]['text']:
                q['options'][-1]['text'] += ' ' + text
            else: q['options'][-1]['text']=text
        elif mode in ('question','after_answer'):
            if mode=='question': q['questionParts'].append(text)
    finish_exam()

    manifest={'source':Path(path).name,'examCount':len(exams),'questionCount':sum(len(e['questions']) for e in exams),'exams':[]}
    for e in exams:
        fn=f"{e['id']}.json"; (OUT_DATA/fn).write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf-8')
        manifest['exams'].append({'id':e['id'],'title':e['title'],'file':f'data/{fn}','questionCount':len(e['questions'])})
    (OUT_DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':
    src=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'input'/'EXAM 1.docx'
    convert(src)
