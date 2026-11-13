import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parents[2]
STAGE = BASE
sys.path.insert(0, str(STAGE / "starter"))
sys.path.insert(0, str(STAGE / "starter/scripts"))
from validate_artifacts import validate
from src.models import Chunk
from src.embeddings import MyEmbedder
from src.store import PgVectorStore


def read(relative):
    return json.loads((BASE / relative).read_text(encoding="utf-8"))


def fingerprint(connection):
    rows = connection.execute("SELECT strategy,chunk_id,document_id,source,page,category,language,content,embedding_model,model_revision,embedding::text AS vector FROM rag_chunks ORDER BY strategy,chunk_id").fetchall()
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


record = {"captured_at_utc": datetime.now(timezone.utc).isoformat(), "artifacts": validate(BASE)}
print('Artifact and new src parity checks passed.', flush=True)
load_dotenv(BASE / "starter/.env")
url = os.environ["DATABASE_URL"]
store = PgVectorStore(url, 384, table_name="rag_chunks_lab_validation", temporary=True)
try:
    before = fingerprint(store.connection)
    record["database"] = dict(store.connection.execute("SELECT version() AS postgres, (SELECT extversion FROM pg_extension WHERE extname='vector') AS pgvector").fetchone())
    record["database"]["counts"] = store.connection.execute("SELECT strategy,count(*) AS rows,count(DISTINCT chunk_id) AS distinct_ids FROM rag_chunks GROUP BY strategy ORDER BY strategy").fetchall()
    store.connection.commit()
    store.create_schema()
    sets = {}
    for strategy in "AB":
        artifact = read(f"starter/results/embeddings_{strategy}.json")
        cs = [Chunk(c["chunk_id"], c["document_id"], c["source"], c["page"], c["text"], {"category": c["category"], "language": c["language"]}) for c in artifact["chunks"]]
        vs = [c["embedding"] for c in artifact["chunks"]]
        sets[strategy] = cs, vs
    record["new_temp_ingestion_measurements"] = []
    for repeat in [1,2]:
        for strategy in "AB":
            start = time.perf_counter()
            store.upsert(strategy, *sets[strategy])
            elapsed = time.perf_counter()-start
            counts = store.connection.execute("SELECT count(*) AS rows,count(DISTINCT chunk_id) AS ids FROM rag_chunks_lab_validation WHERE strategy=%s", (strategy,)).fetchone()
            assert counts["rows"] == counts["ids"] == len(sets[strategy][0])
            store.connection.commit()
            record["new_temp_ingestion_measurements"].append({"repeat":repeat,"strategy":strategy,"seconds":elapsed,**counts})
    cs, vs = sets["A"]
    store.upsert("A", cs[:-1], vs[:-1])
    assert store.connection.execute("SELECT count(*) AS n FROM rag_chunks_lab_validation WHERE strategy='A'").fetchone()["n"] == len(cs)-1
    store.connection.commit()
    store.upsert("A",cs,vs)
    record["stale_snapshot_check"] = {"scope":"temporary table only", "original_A":len(cs), "shortened_A":len(cs)-1, "restored_A":len(cs), "passed":True}
    print('Temporary DB repeat and stale-chunk checks passed.', flush=True)
    model = MyEmbedder()
    generated = model.embed_documents([cs[0].text])[0]
    max_diff = max(abs(a-b) for a,b in zip(generated,vs[0]))
    assert max_diff < 1e-5
    record["adapter_document_vector_max_abs_diff"] = max_diff
    record["dev_query_parity"] = []
    dev = read("starter/results/dev_20261113_210325/traces.json")["traces"]
    for qid in ["Q01","Q06"]:
        traces = [r for r in dev if r["question_id"] == qid]
        vector = model.embed_query(traces[0]["question"])
        for original in traces:
            results = store.search(original["strategy"], vector, filters=original["applied_filter"])
            assert [r["chunk_id"] for r in results] == [r["chunk_id"] for r in original["results"]]
            record["dev_query_parity"].append({"question_id":qid,"strategy":original["strategy"],"chunk_ids":[r["chunk_id"] for r in results]})
    assert before == fingerprint(store.connection)
    record["production_table_unchanged"] = True
    record["production_table_fingerprint_sha256"] = before
finally:
    store.close()
record["measurement_scope"] = "New validation run; timings measure database upsert of already embedded artifacts into temporary table. Not the original ingest time or full end-to-end pipeline time. No test retrieval rerun or tuning. Temporary table removed on connection close."
output = STAGE / ("starter/results/final_audit/runtime_validation_recheck_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f") + ".json")
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({"production_table_unchanged":record["production_table_unchanged"],"adapter_vector_max_diff":max_diff,"validation_file":str(output)},ensure_ascii=False))
