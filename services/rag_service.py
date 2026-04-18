"""RAG: retrieve context + generate answer with Gemini."""
from typing import Dict, List
import json
import re
from config import settings
from services import vector_store

_genai_client = None


def _gc():
    global _genai_client
    if _genai_client is None:
        from google import genai
        _genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _genai_client


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
    """Translate Thai text to English using Gemini. Returns original on failure."""
    if not _is_thai(text) or not settings.GEMINI_API_KEY:
        return text
    try:
        resp = _gc().models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=f"Translate this Thai text to English. Output only the translation, nothing else.\n\n{text}",
        )
        result = (resp.text or "").strip()
        return result if result else text
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return text  # ใช้ Thai query ตรง ๆ แทน
        return text


def build_context(hits: List[Dict]) -> str:
    return "\n\n".join(f"[Page {h['page']}]\n{h['text']}" for h in hits)


def generate_answer(game_name: str, question: str, hits: List[Dict]) -> str:
    if not hits:
        return "ไม่พบข้อมูลในคู่มือ กรุณาลองถามใหม่หรือเพิ่มเติมรายละเอียด"

    context = build_context(hits)

    if not settings.GEMINI_API_KEY:
        return (
            f"(โหมดทดสอบ: ไม่ได้ตั้ง GEMINI_API_KEY)\n\n"
            f"ตามคู่มือที่เกี่ยวข้อง:\n\n{context[:800]}..."
        )

    # translate Thai question → English for the prompt
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
            resp = _gc().models.generate_content(model=settings.GEMINI_MODEL, contents=prompt)
            result = (resp.text or "").strip()
            if not result or result == "NO_INFO":
                return "ไม่พบข้อมูลในคู่มือ"
            return result
        except Exception as e:
            last_err = e
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
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
    # translate Thai → English for TF-IDF search (English rulebooks match better)
    search_query = translate_th_to_en(question) if _is_thai(question) else question

    hits = vector_store.search(game_id, search_query, top_k=5)
    # fallback: also search with original Thai in case PDF is Thai
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
