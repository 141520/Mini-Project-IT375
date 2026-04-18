"""RAG: retrieve context + generate answer with Groq (LLaMA 3)."""
from typing import Dict, List
import json
import re
from config import settings
from services import vector_store

_groq_client = None


def _gc():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client


PROMPT_TEMPLATE = """You are a board game rules assistant for "{game_name}".
The context below is extracted from the official rulebook.
Answer the user's question clearly and concisely based ONLY on the context.
Always cite the page number, e.g. (page 7).
If the context has no relevant information, reply exactly: NO_INFO

Context:
{context}

Question: {question_en}
(Original question in Thai: {question_th})

Answer in Thai language:"""


def _is_thai(text: str) -> bool:
    return bool(re.search(r'[\u0e00-\u0e7f]', text))


def translate_th_to_en(text: str) -> str:
    """Translate Thai text to English using Groq. Returns original on failure."""
    if not _is_thai(text) or not settings.GROQ_API_KEY:
        return text
    try:
        resp = _gc().chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": f"Translate this Thai text to English. Output only the translation, nothing else.\n\n{text}"}],
            max_tokens=200,
        )
        result = (resp.choices[0].message.content or "").strip()
        return result if result else text
    except Exception:
        return text


def build_context(hits: List[Dict]) -> str:
    return "\n\n".join(f"[Page {h['page']}]\n{h['text']}" for h in hits)


def generate_answer(game_name: str, question: str, hits: List[Dict]) -> str:
    if not hits:
        return "ไม่พบข้อมูลในคู่มือ กรุณาลองถามใหม่หรือเพิ่มเติมรายละเอียด"

    context = build_context(hits)

    if not settings.GROQ_API_KEY:
        return (
            f"(โหมดทดสอบ: ไม่ได้ตั้ง GROQ_API_KEY)\n\n"
            f"ตามคู่มือที่เกี่ยวข้อง:\n\n{context[:800]}..."
        )

    question_en = translate_th_to_en(question) if _is_thai(question) else question
    question_th = question if _is_thai(question) else ""

    prompt = PROMPT_TEMPLATE.format(
        game_name=game_name,
        context=context,
        question_en=question_en,
        question_th=question_th,
    )

    import time
    last_err = None
    for attempt in range(2):
        try:
            resp = _gc().chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
            )
            result = (resp.choices[0].message.content or "").strip()
            if not result or result == "NO_INFO":
                return "ไม่พบข้อมูลในคู่มือ"
            return result
        except Exception as e:
            last_err = e
            if "429" in str(e) or "rate_limit" in str(e).lower():
                if attempt == 0:
                    time.sleep(5)
                    continue
                lines = [f"📖 หน้า {h['page']}: {h['text'][:300]}" for h in hits]
                return (
                    "⚠️ AI ถึงโควต้าฟรีชั่วคราว — ข้อมูลจากคู่มือที่เกี่ยวข้อง:\n\n"
                    + "\n\n".join(lines)
                )
            break
    return f"เกิดข้อผิดพลาดในการเรียก AI: {last_err}"


def answer_question(game_id: int, game_name: str, question: str) -> Dict:
    search_query = translate_th_to_en(question) if _is_thai(question) else question

    hits = vector_store.search(game_id, search_query, top_k=5)
    if not hits or hits[0].get("score", 0) < 0.01:
        hits_th = vector_store.search(game_id, question, top_k=5)
        if hits_th and (not hits or hits_th[0].get("score", 0) > hits[0].get("score", 0)):
            hits = hits_th

    answer = generate_answer(game_name, question, hits[:4])
    citations = [{"page": h["page"], "snippet": h["text"][:150]} for h in hits[:4]]
    return {
        "answer": answer,
        "citations": citations,
        "citations_json": json.dumps(citations, ensure_ascii=False),
    }
