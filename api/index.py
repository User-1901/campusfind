"""
Vercel Serverless Function Entry Point for CampusFind.

Provides serverless REST API endpoints on Vercel:
- /api/search
- /api/benchmark
- /api/documents
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import urllib.parse

# Setup pathing for Vercel serverless environment
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from indexing.text_indexer import TextIndexer
from search.search_engine import CampusSearchEngine
from benchmarking.benchmark import run_campus_benchmark

# Initialize and cache indexer for serverless reuse
indexer = TextIndexer()
docs_path = os.path.join(ROOT_DIR, "data", "documents")
if os.path.exists(docs_path):
    indexer.load_directory(docs_path)

search_engine = CampusSearchEngine(indexer)


class handler(BaseHTTPRequestHandler):
    """Vercel serverless HTTP request handler."""

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.endswith("/documents"):
            stats = indexer.get_statistics()
            docs_list = []
            for meta in indexer.documents_metadata.values():
                docs_list.append({
                    "doc_id": meta.doc_id,
                    "filename": meta.filename,
                    "title": meta.title,
                    "category": meta.category,
                    "doc_type": meta.doc_type,
                    "department": meta.department,
                    "date": meta.date,
                    "total_words": meta.total_words,
                    "unique_words": meta.unique_words,
                    "body": indexer.documents_body.get(meta.doc_id, "")
                })

            resp = {
                "statistics": {
                    "total_documents": stats["total_documents"],
                    "unique_words": stats["unique_words"],
                    "total_terms": stats["total_terms"],
                    "categories": stats["categories"],
                    "category_counts": stats["category_counts"],
                    "doc_types": stats["doc_types"]
                },
                "documents": docs_list
            }
            self.send_json(resp)
            return

        elif path.endswith("/search"):
            q = query.get("q", [""])[0]
            algo = query.get("algo", ["compare_both"])[0]
            cat = query.get("category", [None])[0]
            doc_type = query.get("doc_type", [None])[0]

            response = search_engine.search(
                keyword=q,
                algorithm=algo,
                category_filter=cat,
                doc_type_filter=doc_type
            )

            items_data = []
            for it in response.items:
                items_data.append({
                    "doc_id": it.doc_id,
                    "title": it.metadata.title,
                    "category": it.metadata.category,
                    "doc_type": it.metadata.doc_type,
                    "department": it.metadata.department,
                    "date": it.metadata.date,
                    "occurrences_count": it.occurrences_count,
                    "positions": it.positions,
                    "snippet": it.snippet
                })

            lin_data = None
            if response.linear_metrics:
                lin = response.linear_metrics
                lin_data = {
                    "found": lin.found,
                    "index": lin.index,
                    "comparisons": lin.comparisons,
                    "execution_time_ms": lin.execution_time_ms,
                    "trace": lin.trace[:50]
                }

            bin_data = None
            if response.binary_metrics:
                b = response.binary_metrics
                bin_data = {
                    "found": b.found,
                    "index": b.index,
                    "comparisons": b.comparisons,
                    "execution_time_ms": b.execution_time_ms,
                    "trace": b.trace
                }

            resp = {
                "query": response.query,
                "found": response.found,
                "algorithm_mode": response.algorithm_mode,
                "total_matching_documents": response.total_matching_documents,
                "total_occurrences": response.total_occurrences,
                "linear_metrics": lin_data,
                "binary_metrics": bin_data,
                "items": items_data
            }
            self.send_json(resp)
            return

        elif path.endswith("/benchmark"):
            sizes_str = query.get("sizes", ["100,500,1000,5000,10000"])[0]
            sizes = [int(s.strip()) for s in sizes_str.split(",") if s.strip().isdigit()]
            scenario = query.get("scenario", ["average"])[0]
            iterations = int(query.get("iterations", ["5"])[0])

            report = run_campus_benchmark(
                sizes=sizes,
                scenario=scenario,
                iterations=iterations,
                seed_words=list(indexer.inverted_index.index.keys())
            )

            points_data = []
            for p in report.points:
                points_data.append({
                    "size": p.size,
                    "linear_time_ms": p.linear_time_ms,
                    "binary_time_ms": p.binary_time_ms,
                    "linear_comparisons": p.linear_comparisons,
                    "binary_comparisons": p.binary_comparisons,
                    "theoretical_linear_ops": p.theoretical_linear_ops,
                    "theoretical_binary_ops": p.theoretical_binary_ops
                })

            self.send_json({
                "scenario": report.scenario,
                "hardware_notes": report.hardware_notes,
                "points": points_data
            })
            return

        self.send_json({"error": "Endpoint not found"}, status=404)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

