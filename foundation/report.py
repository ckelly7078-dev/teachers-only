"""Export the audit and a consistent restartable database snapshot outside the repo."""
import argparse
import csv
import sqlite3
from pathlib import Path

from .db import connection

REPORTS = {
    'inventory.csv':"""SELECT f.path,f.sha,f.bytes,f.manifest_sha,f.manifest_match,f.declared_source,
        d.*,count(*) OVER(PARTITION BY f.sha) AS paths_with_same_hash FROM files f JOIN documents d USING(sha)
        ORDER BY f.unit,f.year,f.series,f.component,f.kind""",
    'pairing.csv':'SELECT * FROM pairs ORDER BY unit,year,series,component',
    'missing.csv':"""SELECT * FROM expected e WHERE NOT EXISTS(
        SELECT 1 FROM files f WHERE (f.unit,f.year,f.series,f.component,f.kind)=
        (e.unit,e.year,e.series,e.component,e.kind)) ORDER BY unit,year,series,component,kind""",
    'extraction-checks.csv':"""SELECT d.unit,d.year,d.series,d.total_marks,max(q.num) last_question_anchor,
        count(q.id) anchors,sum(q.marks) candidate_marks, count(q.scheme_page) linked_anchors,
        sum(q.status='verified') checked,
        CASE WHEN sum(q.marks)=d.total_marks THEN 'mark sum agrees; anchors still need review'
        ELSE 'review mark sum' END AS reconciliation FROM documents d JOIN questions q ON d.sha=q.paper
        GROUP BY d.sha ORDER BY d.year,d.series""",
}


def export(path,folder):
    folder = Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    snapshot = folder/'foundation.sqlite'
    if snapshot.resolve()==Path(path).resolve():
        raise ValueError('Choose a separate backup directory')
    with connection(path) as db:
        dest = sqlite3.connect(snapshot)
        try:
            db.backup(dest)
        finally:
            dest.close()
    with connection(snapshot) as db:
        for name,sql in REPORTS.items():
            with (folder/name).open('w',newline='',encoding='utf-8') as f:
                q=db.execute(sql)
                writer=csv.writer(f)
                writer.writerow(c[0] for c in q.description)
                writer.writerows(q)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',required=True); p.add_argument('--out',required=True)
    args=p.parse_args()
    export(args.db,args.out)
