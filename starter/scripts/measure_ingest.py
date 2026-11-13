"""One real, fresh ingestion measurement in a temporary pgvector table."""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

BASE=Path(__file__).resolve().parents[2]
STAGE=BASE
sys.path.insert(0,str(STAGE/'starter'))
from src.ingestion import load_pdf,normalize_text
from src.models import DocumentPage
from src.chunking import fixed_size,by_paragraph
from src.embeddings import MyEmbedder
from src.store import PgVectorStore


def read(path): return json.loads(path.read_text(encoding='utf-8'))


load_dotenv(BASE/'starter/.env')
store=PgVectorStore(os.environ['DATABASE_URL'],384,table_name='rag_chunks_ingest_measurement',temporary=True)
manifest=read(BASE/'data/manifest.json')
record={'captured_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Fresh replay into temporary table using pinned local model. Single run, warm files/cache. Excludes initial model/PDF downloads, dependency installation and Docker startup. Not original experiment ingest timing.'}
def fingerprint():
    rows=store.connection.execute('SELECT strategy,chunk_id,content,embedding::text AS vector FROM rag_chunks ORDER BY strategy,chunk_id').fetchall()
    store.connection.commit()
    return hashlib.sha256(json.dumps(rows,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
before=fingerprint()
wall=time.perf_counter()
try:
    start=time.perf_counter(); pages=[]
    for d in manifest['documents']:
        raw=load_pdf(BASE/d['source_path_or_url'],d['source_id'],d['source_path_or_url'])
        for n in d['included_pages']:
            text=normalize_text(raw[n-1].text,n)
            pages.append(DocumentPage(d['source_id'],d['source_path_or_url'],n,text,{'category':d['category'],'language':d['language']}))
    record['extract_normalize_seconds']=time.perf_counter()-start
    start=time.perf_counter(); model=MyEmbedder();record['model_load_seconds']=time.perf_counter()-start
    store.create_schema();record['strategies']={}
    for strategy,function in [('A',lambda p:fixed_size(p,500,50)),('B',lambda p:by_paragraph(p,500,50))]:
        start=time.perf_counter(); chunks=[c for p in pages for c in function(p)];chunk_seconds=time.perf_counter()-start
        token_lengths=[len(model.model.tokenizer('passage: '+c.text,truncation=False)['input_ids']) for c in chunks]
        start=time.perf_counter();vectors=model.embed_documents([c.text for c in chunks]);embedding_seconds=time.perf_counter()-start
        original=read(BASE/f'starter/results/embeddings_{strategy}.json')['chunks']
        assert len(chunks)==len(original)
        assert all(c.chunk_id==o['chunk_id'] and c.text==o['text'] for c,o in zip(chunks,original))
        max_diff=max(abs(a-b) for v,o in zip(vectors,original) for a,b in zip(v,o['embedding']))
        assert max_diff<1e-5
        start=time.perf_counter();store.upsert(strategy,chunks,vectors);store_seconds=time.perf_counter()-start
        record['strategies'][strategy]={'chunk_count':len(chunks),'chunk_seconds':chunk_seconds,'embedding_seconds':embedding_seconds,'store_seconds':store_seconds,'passage_tokens_total':sum(token_lengths),'passage_tokens_max':max(token_lengths),'vector_max_abs_diff':max_diff}
        print(strategy,'fresh ingest completed',flush=True)
    record['measured_wall_seconds']=time.perf_counter()-wall
    assert before==fingerprint();record['production_unchanged']=True
finally:store.close()
path=STAGE/('starter/results/final_audit/ingest_measurement_recheck_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')+'.json')
path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Fresh ingestion measured; production data unchanged.')
