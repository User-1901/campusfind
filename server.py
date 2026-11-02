"""
CampusFind Local Development & Production Server.

Serves the modern SaaS web application and provides REST API endpoints
backed by our InvertedIndex and manual Linear & Binary Search algorithms.
Uses only Python 3 standard library modules (zero external server dependencies).
"""

import http.server
import json
import os
import socketserver
import sys
import threading
import urllib.parse
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from indexing.text_indexer import TextIndexer
from search.search_engine import CampusSearchEngine
from benchmarking.benchmark import run_campus_benchmark

PORT = 5000

# Initialize in-memory indexer and search engine
print("Initializing CampusFind Inverted Index...")
indexer = TextIndexer()
docs_loaded = indexer.load_directory(os.path.join(BASE_DIR, "data", "documents"))
print(f"Indexed {docs_loaded} campus documents into memory.")
search_engine = CampusSearchEngine(indexer)


class CampusFindHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with REST API routing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS and caching headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # -------------------------------------------------------------
        # API ROUTE: /api/documents
        # -------------------------------------------------------------
        if path == "/api/documents":
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
            self.send_json_response(resp)
            return

        # -------------------------------------------------------------
        # API ROUTE: /api/search
        # -------------------------------------------------------------
        elif path == "/api/search":
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

            # Format items
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
            self.send_json_response(resp)
            return

        # -------------------------------------------------------------
        # API ROUTE: /api/benchmark
        # -------------------------------------------------------------
        elif path == "/api/benchmark":
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

            self.send_json_response({
                "scenario": report.scenario,
                "hardware_notes": report.hardware_notes,
                "points": points_data
            })
            return

        # Fallback to static file serving
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/upload":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(post_body)
                filename = data.get("filename", "uploaded_doc.txt")
                content = data.get("content", "")

                meta = indexer.add_document(filename, content)
                self.send_json_response({
                    "success": True,
                    "message": f"Successfully indexed {filename}",
                    "document": {
                        "title": meta.title,
                        "category": meta.category,
                        "total_words": meta.total_words
                    }
                })
            except Exception as e:
                self.send_json_response({"success": False, "error": str(e)}, status=400)
            return

        self.send_error(404, "Endpoint Not Found")

    def send_json_response(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def open_browser():
    """Opens user's default browser after the server is ready."""
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass


if __name__ == "__main__":
    # Ensure server port can be cleanly bound
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CampusFindHandler) as httpd:
        print("=" * 70)
        print("CAMPUSFIND WEB APPLICATION SERVER RUNNING")
        print(f"URL: http://localhost:{PORT}")
        print("Press Ctrl + C in the terminal to stop the server.")
        print("=" * 70)

        # Trigger automatic browser opening
        threading.Timer(1.0, open_browser).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down CampusFind server.")
            httpd.shutdown()

