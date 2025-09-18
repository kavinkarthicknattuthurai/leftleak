"""Clean CLI for simple Bluesky RAG (bsrag)."""

import argparse
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from simple_rag.config import get_cfg
from simple_rag.rag import SimpleRAG


console = Console()


def cmd_query(args: argparse.Namespace):
    cfg = get_cfg()
    rag = SimpleRAG(cfg)
    console.print("[cyan]Fetching and retrieving relevant Bluesky posts...[/cyan]")
    res = rag.ask(args.question, fresh=not args.no_fresh)
    if "answer" in res:
        console.print(Panel(res["answer"], title="Answer", border_style="green"))
        if res.get("sources"):
            console.print("\n[cyan]Sources:[/cyan]")
            for i, s in enumerate(res["sources"], 1):
                console.print(f"  {i}. {s}")
    else:
        console.print("[red]No answer returned[/red]")


def cmd_status(args: argparse.Namespace):
    cfg = get_cfg()
    rag = SimpleRAG(cfg)
    console.print(Panel(
        f"Models: {cfg.gemini.text_model} / {cfg.gemini.embedding_model}\n"
        f"DB: {cfg.chroma.db_path} ({cfg.chroma.collection})\n"
        f"Chunk: {cfg.rag.chunk_size}/{cfg.rag.chunk_overlap}  MaxResults: {cfg.rag.max_results}",
        title="Configuration",
    ))


def cmd_reset(args: argparse.Namespace):
    cfg = get_cfg()
    rag = SimpleRAG(cfg)
    rag.db.clear()
    console.print("[yellow]Vector store cleared.[/yellow]")


def main():
    parser = argparse.ArgumentParser(description="bsrag - Simple Bluesky RAG CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_q = sub.add_parser("query", help="Ask a question")
    p_q.add_argument("question")
    p_q.add_argument("--no-fresh", action="store_true", help="Do not fetch fresh posts before answering")

    sub.add_parser("status", help="Show configuration")
    sub.add_parser("reset", help="Clear vector store")

    p_ing = sub.add_parser("ingest-jetstream", help="Ingest live posts from Bluesky Jetstream")
    p_ing.add_argument("--keywords", type=str, help="Filter to posts containing these keywords (space-separated)")
    p_ing.add_argument("--max", type=int, default=200, help="Max posts to collect")
    p_ing.add_argument("--minutes", type=int, default=2, help="Max minutes to run")

    p_lq = sub.add_parser("jetstream-query", help="One-shot: stream with keywords then answer the question")
    p_lq.add_argument("question")
    p_lq.add_argument("--keywords", type=str, help="Override keywords to stream (default: extracted from question)")
    p_lq.add_argument("--max", type=int, default=200, help="Max posts to collect via Jetstream")
    p_lq.add_argument("--minutes", type=int, default=2, help="How long to stream")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    if args.cmd == "query":
        cmd_query(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "reset":
        cmd_reset(args)
    elif args.cmd == "ingest-jetstream":
        from simple_rag.ingest import stream_posts
        cfg = get_cfg()
        rag = SimpleRAG(cfg)
        import asyncio
        posts = asyncio.get_event_loop().run_until_complete(stream_posts(cfg, args.keywords, args.max, args.minutes))
        added = rag.ingest_posts(posts)
        console.print(f"[green]Jetstream ingested {added} chunks from {len(posts)} posts[/green]")
    elif args.cmd == "jetstream-query":
        cfg = get_cfg()
        rag = SimpleRAG(cfg)
        res = rag.ask_jetstream(args.question, keywords=args.keywords, max_posts=args.max, minutes=args.minutes)
        console.print(Panel(res["answer"], title="Answer", border_style="red"))
        if res.get("sources"):
            console.print("\n[cyan]Sources:[/cyan]")
            for i, s in enumerate(res["sources"], 1):
                console.print(f"  {i}. {s}")
        console.print(f"\n[cyan]Ingestion:[/cyan] {res.get('jetstream_ingested_posts', 0)} posts → {res.get('jetstream_chunks_added', 0)} chunks")


if __name__ == "__main__":
    main()
